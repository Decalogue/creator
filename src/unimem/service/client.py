"""
UniMem HTTP Service 客户端

用于通过 HTTP API 调用 UniMem 服务
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import requests

from ..memory_types import Experience, Context, Memory, Task, RetrievalResult, MemoryType

logger = logging.getLogger(__name__)


class UniMemServiceClient:
    """UniMem HTTP 服务客户端"""
    
    def __init__(self, base_url: str = "http://localhost:9622", timeout: int = 30):
        """
        初始化客户端
        
        Args:
            base_url: UniMem 服务的基础 URL
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.health_check_url = f"{self.base_url}/unimem/health"
        self.retain_url = f"{self.base_url}/unimem/retain"
        self.recall_url = f"{self.base_url}/unimem/recall"
        self.reflect_url = f"{self.base_url}/unimem/reflect"
        
        ***REMOVED*** 检查服务是否可用
        if not self.check_health():
            raise ConnectionError(f"UniMem service not available at {self.base_url}")
        
        logger.info(f"UniMem HTTP client initialized: {self.base_url}")
    
    def check_health(self) -> bool:
        """检查服务健康状态"""
        try:
            response = requests.get(self.health_check_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get("unimem_initialized", False)
            return False
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False
    
    def retain(self, experience: Experience, context: Context, operation_id: Optional[str] = None) -> Memory:
        """
        RETAIN 操作：存储新记忆
        
        Args:
            experience: 经验数据
            context: 上下文信息
            operation_id: 操作ID（可选）
            
        Returns:
            存储的记忆对象
        """
        payload = {
            "experience": {
                "content": experience.content,
                "timestamp": experience.timestamp.isoformat() if experience.timestamp else datetime.now().isoformat(),
                "context": experience.context or "",
                "metadata": experience.metadata or {},
            },
            "context": {
                "session_id": context.session_id,
                "user_id": context.user_id,
                "metadata": context.metadata or {},
            }
        }
        
        if operation_id:
            payload["operation_id"] = operation_id
        
        try:
            response = requests.post(self.retain_url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            
            if not result.get("success"):
                raise RuntimeError(f"RETAIN failed: {result.get('error', 'Unknown error')}")
            
            memory_dict = result.get("memory", {})
            return self._dict_to_memory(memory_dict)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"RETAIN request failed: {e}")
            raise ConnectionError(f"Failed to call UniMem service: {e}") from e
    
    def recall(
        self,
        query: str,
        context: Optional[Context] = None,
        memory_type: Optional[MemoryType] = None,
        top_k: int = 10
    ) -> List[RetrievalResult]:
        """
        RECALL 操作：检索相关记忆
        
        Args:
            query: 查询字符串
            context: 上下文信息（可选）
            memory_type: 记忆类型过滤（可选）
            top_k: 返回结果数量
            
        Returns:
            检索结果列表
        """
        payload = {
            "query": query,
            "top_k": top_k,
        }
        
        if context:
            payload["context"] = {
                "session_id": context.session_id,
                "user_id": context.user_id,
                "metadata": context.metadata or {},
            }
        
        if memory_type:
            payload["memory_type"] = memory_type.value
        
        try:
            response = requests.post(self.recall_url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            
            if not result.get("success"):
                raise RuntimeError(f"RECALL failed: {result.get('error', 'Unknown error')}")
            
            results = result.get("results", [])
            return [self._dict_to_retrieval_result(r) for r in results]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"RECALL request failed: {e}")
            raise ConnectionError(f"Failed to call UniMem service: {e}") from e
    
    def reflect(
        self,
        memories: List[Memory],
        task: Task,
        context: Optional[Context] = None
    ) -> List[Memory]:
        """
        REFLECT 操作：优化记忆
        
        Args:
            memories: 要优化的记忆列表
            task: 任务信息
            context: 上下文信息（可选）
            
        Returns:
            优化后的记忆列表
        """
        payload = {
            "memories": [self._memory_to_dict(m) for m in memories],
            "task": {
                "id": task.id,
                "description": task.description,
                "context": task.context or "",
                "metadata": task.metadata or {},
            }
        }
        
        if context:
            payload["context"] = {
                "session_id": context.session_id,
                "user_id": context.user_id,
                "metadata": context.metadata or {},
            }
        
        try:
            response = requests.post(self.reflect_url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            
            if not result.get("success"):
                raise RuntimeError(f"REFLECT failed: {result.get('error', 'Unknown error')}")
            
            updated = result.get("updated_memories", [])
            return [self._dict_to_memory(m) for m in updated]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"REFLECT request failed: {e}")
            raise ConnectionError(f"Failed to call UniMem service: {e}") from e
    
    def _memory_to_dict(self, memory: Memory) -> Dict[str, Any]:
        """将 Memory 对象转换为字典"""
        return {
            "id": memory.id,
            "content": memory.content,
            "timestamp": memory.timestamp.isoformat() if memory.timestamp else None,
            "memory_type": memory.memory_type.value if memory.memory_type else None,
            "layer": memory.layer.value if memory.layer else None,
            "keywords": memory.keywords or [],
            "tags": memory.tags or [],
            "context": memory.context or "",
            "links": list(memory.links) if memory.links else [],
            "entities": memory.entities or [],
            "retrieval_count": memory.retrieval_count or 0,
            "last_accessed": memory.last_accessed.isoformat() if memory.last_accessed else None,
            "metadata": memory.metadata or {},
        }
    
    def _dict_to_memory(self, data: Dict[str, Any]) -> Memory:
        """将字典转换为 Memory 对象"""
        from ..memory_types import MemoryLayer
        
        ***REMOVED*** 解析时间戳
        timestamp = None
        if data.get("timestamp"):
            if isinstance(data["timestamp"], str):
                timestamp = datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
            else:
                timestamp = data["timestamp"]
        
        last_accessed = None
        if data.get("last_accessed"):
            if isinstance(data["last_accessed"], str):
                last_accessed = datetime.fromisoformat(data["last_accessed"].replace('Z', '+00:00'))
            else:
                last_accessed = data["last_accessed"]
        
        ***REMOVED*** 解析枚举类型
        memory_type = None
        if data.get("memory_type"):
            try:
                memory_type = MemoryType(data["memory_type"])
            except (ValueError, TypeError):
                pass
        
        layer = None
        if data.get("layer"):
            try:
                layer = MemoryLayer(data["layer"])
            except (ValueError, TypeError):
                pass
        
        return Memory(
            id=data.get("id", ""),
            content=data.get("content", ""),
            timestamp=timestamp,
            memory_type=memory_type,
            layer=layer,
            keywords=data.get("keywords", []),
            tags=data.get("tags", []),
            context=data.get("context", ""),
            links=set(data.get("links", [])),
            entities=data.get("entities", []),
            retrieval_count=data.get("retrieval_count", 0),
            last_accessed=last_accessed,
            metadata=data.get("metadata", {}),
        )
    
    def _dict_to_retrieval_result(self, data: Dict[str, Any]) -> RetrievalResult:
        """将字典转换为 RetrievalResult 对象"""
        memory = self._dict_to_memory(data.get("memory", {}))
        return RetrievalResult(
            memory=memory,
            score=float(data.get("score", 0.0)),
            retrieval_method=data.get("retrieval_method", "unknown"),
            metadata=data.get("metadata", {}),
        )
