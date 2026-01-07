"""
图结构适配器

实现 UniMem 的实体-关系建模和图结构管理
参考架构：LightRAG（图结构 + 双层检索）

设计原则：
- 通过 HTTP API 调用 LightRAG 服务（而非直接使用 Python 库）
- 保留双层检索机制（entity_retrieval 和 abstract_retrieval）
- 图谱数据通过 API 更新，无需本地化
- API 调用简单、轻量，避免复杂的本地依赖

工业级特性：
- 连接池复用（requests.Session）
- 自动重试机制（指数退避）
- 请求监控和指标收集
- 配置验证
- 完善的错误处理
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import json
import time
from dataclasses import dataclass, field

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None

try:
    from tenacity import (
        retry,
        stop_after_attempt,
        wait_exponential,
        retry_if_exception_type
    )
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False
    retry = None
    stop_after_attempt = None
    wait_exponential = None
    retry_if_exception_type = None

from .base import (
    BaseAdapter,
    AdapterConfigurationError,
    AdapterNotAvailableError,
    AdapterError
)
from ..types import Entity, Relation, Memory
import logging

logger = logging.getLogger(__name__)


@dataclass
class RequestMetrics:
    """请求指标数据类"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency: float = 0.0
    
    @property
    def average_latency(self) -> float:
        """平均延迟（毫秒）"""
        if self.total_requests == 0:
            return 0.0
        return (self.total_latency / self.total_requests) * 1000
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    def reset(self) -> None:
        """重置指标"""
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_latency = 0.0


class GraphAdapter(BaseAdapter):
    """
    图结构适配器
    
    功能需求：实体-关系建模和图结构管理
    参考架构：LightRAG（图结构 + 双层检索）
    
    实现方式：
    - 通过 HTTP API 调用 LightRAG 服务
    - 支持双层检索机制（entity_retrieval 和 abstract_retrieval）
    - 图谱数据通过 API 更新，无需本地化
    """
    
    def _do_initialize(self) -> None:
        """
        初始化图结构适配器
        
        通过 HTTP API 连接到 LightRAG 服务，使用连接池和重试机制。
        
        Raises:
            AdapterConfigurationError: 如果配置无效
        """
        if not REQUESTS_AVAILABLE:
            logger.warning("requests library not available, GraphAdapter will not work")
            self._available = False
            return
        
        ***REMOVED*** API 配置
        api_base_url = self.config.get("api_base_url", "http://localhost:9621")
        api_timeout = float(self.config.get("api_timeout", 30.0))
        api_key = self.config.get("api_key")  ***REMOVED*** 可选，用于认证
        
        ***REMOVED*** 配置验证
        if not api_base_url or not isinstance(api_base_url, str):
            raise AdapterConfigurationError(
                "api_base_url must be a non-empty string",
                adapter_name=self.__class__.__name__
            )
        if api_timeout <= 0:
            raise AdapterConfigurationError(
                f"api_timeout must be positive, got {api_timeout}",
                adapter_name=self.__class__.__name__
            )
        
        self.api_base_url = api_base_url
        self.api_timeout = api_timeout
        self.api_key = api_key
        
        ***REMOVED*** 初始化连接池（Session）
        self._session = requests.Session()
        if self.api_key:
            self._session.headers.update({
                "Authorization": f"Bearer {self.api_key}"
            })
        self._session.headers.update({
            "Content-Type": "application/json"
        })
        
        ***REMOVED*** 重试配置
        self.max_retries = int(self.config.get("max_retries", 3))
        self.retry_delay = float(self.config.get("retry_delay", 1.0))
        
        ***REMOVED*** 初始化请求指标
        self.metrics = RequestMetrics()
        
        ***REMOVED*** 健康检查
        try:
            health_url = f"{self.api_base_url}/health"
            response = self._session.get(health_url, timeout=5.0)
            if response.status_code == 200:
                logger.info(f"Graph adapter initialized (LightRAG API: {self.api_base_url})")
                self._available = True
            else:
                logger.warning(f"LightRAG API health check failed: {response.status_code}")
                self._available = False
        except Exception as e:
            logger.warning(f"LightRAG API not available at {self.api_base_url}: {e}")
            self._available = False
    
    def _make_api_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        retry_on_failure: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        发起 API 请求（带重试机制和指标收集）
        
        Args:
            method: HTTP 方法（GET, POST, PUT, DELETE）
            endpoint: API 端点（如 "/query", "/entities"）
            data: 请求体数据（用于 POST/PUT）
            params: URL 参数（用于 GET）
            retry_on_failure: 是否在失败时重试，默认 True
            
        Returns:
            API 响应的 JSON 数据，如果失败则返回 None
        """
        if not self.is_available():
            logger.warning(f"Cannot make API request: adapter not available")
            return None
        
        url = f"{self.api_base_url}{endpoint}"
        start_time = time.time()
        self.metrics.total_requests += 1
        
        try:
            ***REMOVED*** 使用连接池发送请求
            if method.upper() == "GET":
                response = self._session.get(
                    url, params=params, timeout=self.api_timeout
                )
            elif method.upper() == "POST":
                response = self._session.post(
                    url, json=data, timeout=self.api_timeout
                )
            elif method.upper() == "PUT":
                response = self._session.put(
                    url, json=data, timeout=self.api_timeout
                )
            elif method.upper() == "DELETE":
                response = self._session.delete(url, timeout=self.api_timeout)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                self.metrics.failed_requests += 1
                return None
            
            response.raise_for_status()
            result = response.json() if response.content else {}
            
            ***REMOVED*** 记录成功
            latency = time.time() - start_time
            self.metrics.successful_requests += 1
            self.metrics.total_latency += latency
            
            logger.debug(
                f"API request succeeded: {method} {endpoint} "
                f"({latency*1000:.2f}ms)"
            )
            return result
            
        except requests.exceptions.Timeout as e:
            self.metrics.failed_requests += 1
            self.metrics.total_latency += time.time() - start_time
            logger.error(f"API request timeout: {method} {endpoint} - {e}")
            if retry_on_failure and TENACITY_AVAILABLE:
                return self._retry_api_request(method, endpoint, data, params)
            return None
        except requests.exceptions.ConnectionError as e:
            self.metrics.failed_requests += 1
            self.metrics.total_latency += time.time() - start_time
            logger.error(f"API connection error: {method} {endpoint} - {e}")
            if retry_on_failure and TENACITY_AVAILABLE:
                return self._retry_api_request(method, endpoint, data, params)
            return None
        except requests.exceptions.HTTPError as e:
            self.metrics.failed_requests += 1
            self.metrics.total_latency += time.time() - start_time
            logger.error(
                f"API HTTP error: {method} {endpoint} - {e.response.status_code}",
                exc_info=True
            )
            ***REMOVED*** HTTP 错误（如 4xx, 5xx）通常不重试，除非是 5xx
            if retry_on_failure and e.response.status_code >= 500:
                if TENACITY_AVAILABLE:
                    return self._retry_api_request(method, endpoint, data, params)
            return None
        except requests.exceptions.RequestException as e:
            self.metrics.failed_requests += 1
            self.metrics.total_latency += time.time() - start_time
            logger.error(f"API request failed: {method} {endpoint} - {e}", exc_info=True)
            if retry_on_failure and TENACITY_AVAILABLE:
                return self._retry_api_request(method, endpoint, data, params)
            return None
        except json.JSONDecodeError as e:
            self.metrics.failed_requests += 1
            self.metrics.total_latency += time.time() - start_time
            logger.error(f"Failed to parse API response JSON: {e}")
            return None
    
    def _retry_api_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        带重试的 API 请求（使用 tenacity）
        
        仅在 tenacity 可用时使用，否则直接返回 None
        """
        if not TENACITY_AVAILABLE:
            logger.warning("tenacity not available, skipping retry")
            return None
        
        @retry(
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(multiplier=self.retry_delay, min=1, max=10),
            retry=retry_if_exception_type((
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
            )),
            reraise=True,
        )
        def _do_request():
            return self._make_api_request(
                method, endpoint, data, params, retry_on_failure=False
            )
        
        try:
            return _do_request()
        except Exception as e:
            logger.error(f"API request failed after retries: {method} {endpoint} - {e}")
            return None
    
    def extract_entities_relations(self, text: str) -> Tuple[List[Entity], List[Relation]]:
        """
        从文本中提取实体和关系
        
        通过 LightRAG API 的提取端点获取实体和关系
        
        Args:
            text: 输入文本
            
        Returns:
            (实体列表, 关系列表) 元组
        """
        if not self.is_available():
            logger.warning("GraphAdapter not available for extraction")
            return [], []
        
        if not text or not text.strip():
            logger.warning("Empty text provided for entity relation extraction")
            return [], []
        
        try:
            ***REMOVED*** 调用 LightRAG API 的提取端点
            ***REMOVED*** 注意：具体端点名称可能需要根据实际 API 文档调整
            response = self._make_api_request(
                method="POST",
                endpoint="/extract",
                data={"text": text}
            )
            
            if not response:
                return [], []
            
            ***REMOVED*** 解析响应并转换为 UniMem 类型
            entities = self._parse_entities_from_api(response)
            relations = self._parse_relations_from_api(response)
            
            logger.debug(f"Extracted {len(entities)} entities and {len(relations)} relations")
            return entities, relations
            
        except Exception as e:
            logger.error(f"Error extracting entities and relations: {e}", exc_info=True)
            return [], []
    
    def add_entities(self, entities: List[Entity]) -> bool:
        """
        添加实体到图结构
        
        通过 LightRAG API 添加实体
        
        Args:
            entities: 实体列表
            
        Returns:
            是否成功添加
        """
        if not self.is_available():
            return False
        
        if not entities:
            logger.warning("Empty entities list provided")
            return True  ***REMOVED*** 空列表视为成功
        
        try:
            ***REMOVED*** 转换为 API 格式
            entities_data = [self._entity_to_api_format(entity) for entity in entities]
            
            ***REMOVED*** 调用 LightRAG API
            response = self._make_api_request(
                method="POST",
                endpoint="/entities",
                data={"entities": entities_data}
            )
            
            if response is None:
                return False
            
            logger.debug(f"Added {len(entities)} entities to graph via API")
            return True
            
        except Exception as e:
            logger.error(f"Error adding entities: {e}", exc_info=True)
            return False
    
    def add_relations(self, relations: List[Relation]) -> bool:
        """
        添加关系到图结构
        
        通过 LightRAG API 添加关系
        
        Args:
            relations: 关系列表
            
        Returns:
            是否成功添加
        """
        if not self.is_available():
            return False
        
        if not relations:
            logger.warning("Empty relations list provided")
            return True  ***REMOVED*** 空列表视为成功
        
        try:
            ***REMOVED*** 转换为 API 格式
            relations_data = [self._relation_to_api_format(relation) for relation in relations]
            
            ***REMOVED*** 调用 LightRAG API
            response = self._make_api_request(
                method="POST",
                endpoint="/relations",
                data={"relations": relations_data}
            )
            
            if response is None:
                return False
            
            logger.debug(f"Added {len(relations)} relations to graph via API")
            return True
            
        except Exception as e:
            logger.error(f"Error adding relations: {e}", exc_info=True)
            return False
    
    def entity_retrieval(self, query: str, top_k: int = 10) -> List[Memory]:
        """
        实体级检索（低级别检索）
        
        通过 LightRAG API 进行实体级检索（局部检索）
        返回与查询相关的实体及其直接关联信息
        
        Args:
            query: 查询字符串
            top_k: 返回结果数量
            
        Returns:
            检索到的记忆列表（从实体信息转换而来）
        """
        if not self.is_available():
            return []
        
        if not query or not query.strip():
            logger.warning("Empty query provided for entity retrieval")
            return []
        
        try:
            ***REMOVED*** 调用 LightRAG API 的查询端点，使用 entity 模式
            response = self._make_api_request(
                method="POST",
                endpoint="/query",
                data={
                    "query": query,
                    "mode": "entity",  ***REMOVED*** 实体级检索（低级别）
                    "top_k": top_k
                }
            )
            
            if not response:
                return []
            
            ***REMOVED*** 解析响应并转换为 Memory 列表
            memories = self._parse_memories_from_query_response(response, query)
            
            logger.debug(f"Entity retrieval returned {len(memories)} memories")
            return memories
            
        except Exception as e:
            logger.error(f"Error in entity retrieval: {e}", exc_info=True)
            return []
    
    def abstract_retrieval(self, query: str, top_k: int = 10) -> List[Memory]:
        """
        抽象概念检索（高级别检索）
        
        通过 LightRAG API 进行抽象概念检索（全局检索）
        返回与查询相关的抽象概念、模式和全局结构
        
        Args:
            query: 查询字符串
            top_k: 返回结果数量
            
        Returns:
            检索到的记忆列表（从抽象概念转换而来）
        """
        if not self.is_available():
            return []
        
        if not query or not query.strip():
            logger.warning("Empty query provided for abstract retrieval")
            return []
        
        try:
            ***REMOVED*** 调用 LightRAG API 的查询端点，使用 abstract 模式
            response = self._make_api_request(
                method="POST",
                endpoint="/query",
                data={
                    "query": query,
                    "mode": "abstract",  ***REMOVED*** 抽象概念检索（高级别）
                    "top_k": top_k
                }
            )
            
            if not response:
                return []
            
            ***REMOVED*** 解析响应并转换为 Memory 列表
            memories = self._parse_memories_from_query_response(response, query)
            
            logger.debug(f"Abstract retrieval returned {len(memories)} memories")
            return memories
            
        except Exception as e:
            logger.error(f"Error in abstract retrieval: {e}", exc_info=True)
            return []
    
    def get_entities_for_memory(self, memory_id: str) -> List[Entity]:
        """
        获取记忆关联的实体
        
        通过 LightRAG API 查询与指定记忆关联的实体
        
        Args:
            memory_id: 记忆 ID
            
        Returns:
            关联的实体列表
        """
        if not self.is_available():
            return []
        
        if not memory_id or not memory_id.strip():
            logger.warning("Empty memory_id provided")
            return []
        
        try:
            ***REMOVED*** 调用 LightRAG API 查询关联实体
            response = self._make_api_request(
                method="GET",
                endpoint=f"/memories/{memory_id}/entities"
            )
            
            if not response:
                return []
            
            ***REMOVED*** 解析响应并转换为 Entity 列表
            entities = self._parse_entities_from_api(response)
            
            logger.debug(f"Found {len(entities)} entities for memory {memory_id}")
            return entities
            
        except Exception as e:
            logger.error(f"Error getting entities for memory: {e}", exc_info=True)
            return []
    
    def update_entity_description(self, entity_id: str, description: str) -> bool:
        """
        更新实体描述
        
        通过 LightRAG API 更新实体的描述信息
        
        Args:
            entity_id: 实体 ID
            description: 新的描述
            
        Returns:
            是否成功更新
        """
        if not self.is_available():
            return False
        
        if not entity_id or not entity_id.strip():
            logger.warning("Empty entity_id provided")
            return False
        
        if not description or not description.strip():
            logger.warning("Empty description provided")
            return False
        
        try:
            ***REMOVED*** 调用 LightRAG API 更新实体
            response = self._make_api_request(
                method="PUT",
                endpoint=f"/entities/{entity_id}",
                data={"description": description}
            )
            
            if response is None:
                return False
            
            logger.debug(f"Updated entity {entity_id} description via API")
            return True
            
        except Exception as e:
            logger.error(f"Error updating entity description: {e}", exc_info=True)
            return False
    
    ***REMOVED*** ==================== 类型转换辅助方法 ====================
    
    def _entity_to_api_format(self, entity: Entity) -> Dict[str, Any]:
        """
        将 UniMem Entity 转换为 LightRAG API 格式
        
        Args:
            entity: UniMem Entity 对象
            
        Returns:
            API 格式的实体字典
        """
        return {
            "id": entity.id,
            "name": entity.name,
            "type": entity.entity_type,
            "description": entity.description,
            "retrieval_key": entity.retrieval_key,
            "retrieval_value": entity.retrieval_value,
            "neighbors": entity.neighbors,
        }
    
    def _relation_to_api_format(self, relation: Relation) -> Dict[str, Any]:
        """
        将 UniMem Relation 转换为 LightRAG API 格式
        
        Args:
            relation: UniMem Relation 对象
            
        Returns:
            API 格式的关系字典
        """
        return {
            "source": relation.source,
            "target": relation.target,
            "keywords": relation.keywords,
            "description": relation.description,
            "retrieval_key": relation.retrieval_key,
            "retrieval_value": relation.retrieval_value,
        }
    
    def _parse_entities_from_api(self, api_response: Dict[str, Any]) -> List[Entity]:
        """
        从 API 响应解析 Entity 列表
        
        Args:
            api_response: API 响应字典
            
        Returns:
            Entity 列表
        """
        entities = []
        
        ***REMOVED*** 支持多种响应格式
        entities_data = api_response.get("entities") or api_response.get("data", {}).get("entities") or []
        
        if not isinstance(entities_data, list):
            logger.warning(f"Unexpected entities format in API response: {type(entities_data)}")
            return []
        
        for entity_data in entities_data:
            try:
                entity = Entity(
                    id=entity_data.get("id", ""),
                    name=entity_data.get("name", ""),
                    entity_type=entity_data.get("type", entity_data.get("entity_type", "")),
                    description=entity_data.get("description", ""),
                    retrieval_key=entity_data.get("retrieval_key", ""),
                    retrieval_value=entity_data.get("retrieval_value", ""),
                    neighbors=entity_data.get("neighbors", []),
                )
                if entity.id and entity.name:
                    entities.append(entity)
            except Exception as e:
                logger.warning(f"Failed to parse entity from API response: {e}")
                continue
        
        return entities
    
    def _parse_relations_from_api(self, api_response: Dict[str, Any]) -> List[Relation]:
        """
        从 API 响应解析 Relation 列表
        
        Args:
            api_response: API 响应字典
            
        Returns:
            Relation 列表
        """
        relations = []
        
        ***REMOVED*** 支持多种响应格式
        relations_data = api_response.get("relations") or api_response.get("data", {}).get("relations") or []
        
        if not isinstance(relations_data, list):
            logger.warning(f"Unexpected relations format in API response: {type(relations_data)}")
            return []
        
        for relation_data in relations_data:
            try:
                relation = Relation(
                    source=relation_data.get("source", ""),
                    target=relation_data.get("target", ""),
                    keywords=relation_data.get("keywords", []),
                    description=relation_data.get("description", ""),
                    retrieval_key=relation_data.get("retrieval_key", ""),
                    retrieval_value=relation_data.get("retrieval_value", ""),
                )
                if relation.source and relation.target:
                    relations.append(relation)
            except Exception as e:
                logger.warning(f"Failed to parse relation from API response: {e}")
                continue
        
        return relations
    
    def _parse_memories_from_query_response(
        self,
        api_response: Dict[str, Any],
        query: str
    ) -> List[Memory]:
        """
        从查询 API 响应解析 Memory 列表
        
        Args:
            api_response: API 查询响应字典
            query: 原始查询字符串
            
        Returns:
            Memory 列表
        """
        memories = []
        
        ***REMOVED*** 支持多种响应格式
        results = api_response.get("results") or api_response.get("data", {}).get("results") or []
        
        if not isinstance(results, list):
            logger.warning(f"Unexpected results format in API response: {type(results)}")
            return []
        
        for idx, result_data in enumerate(results):
            try:
                ***REMOVED*** 从结果中提取内容
                content = result_data.get("text") or result_data.get("content") or result_data.get("description") or ""
                if not content:
                    continue
                
                ***REMOVED*** 创建 Memory 对象
                memory = Memory(
                    id=result_data.get("id", f"graph_mem_{datetime.now().timestamp()}_{idx}"),
                    content=content,
                    timestamp=datetime.now(),  ***REMOVED*** API 可能不提供时间戳
                    context=f"Graph retrieval result for query: {query[:50]}",
                    metadata={
                        "source": "graph_retrieval",
                        "query": query,
                        "score": result_data.get("score", 0.0),
                        "entity_id": result_data.get("entity_id"),
                        "entity_type": result_data.get("entity_type"),
                    }
                )
                
                memories.append(memory)
                
            except Exception as e:
                logger.warning(f"Failed to parse memory from query response: {e}")
                continue
        
        return memories
    
    def health_check(self):
        """
        健康检查（包含请求指标）
        
        Returns:
            AdapterHealthStatus: 健康状态，包含请求指标详情
        """
        base_status = super().health_check()
        
        ***REMOVED*** 添加请求指标详情
        details = {
            "api_base_url": self.api_base_url,
            "request_metrics": {
                "total_requests": self.metrics.total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "success_rate": self.metrics.success_rate,
                "average_latency_ms": self.metrics.average_latency,
            }
        }
        
        base_status.details = details
        return base_status
    
    def reset_metrics(self) -> None:
        """重置请求指标"""
        if hasattr(self, 'metrics'):
            self.metrics.reset()
            logger.info("Request metrics reset")
