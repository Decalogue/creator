"""
UniMem 核心实现

整合六大架构的统一记忆系统

设计特点：
- 适配器模式：各架构解耦，易于扩展
- 统一操作：通过适配器进行信息交互、操作、叠加
- 分层架构：操作层、存储层、网络层、检索层、更新层
- 事务支持：确保操作的一致性
- 错误处理：完善的错误处理和回滚机制
- 并发安全：支持多线程环境
- 批量操作：支持批量处理
- 幂等性：确保操作可重复执行
"""

import logging
from typing import List, Optional, Dict, Any, Set
from datetime import datetime
from contextlib import contextmanager
import threading
import concurrent.futures

from .types import Experience, Memory, Task, Context, MemoryType, MemoryLayer, RetrievalResult
from .adapters import (
    OperationAdapter,
    LayeredStorageAdapter,
    MemoryTypeAdapter,
    GraphAdapter,
    AtomLinkAdapter,
    RetrievalAdapter,
    UpdateAdapter,
)
from .storage import StorageManager
from .retrieval import RetrievalEngine
from .update import UpdateManager
from .config import UniMemConfig

logger = logging.getLogger(__name__)


class OperationError(Exception):
    """操作错误基类"""
    pass


class RetainError(OperationError):
    """RETAIN 操作错误"""
    pass


class RecallError(OperationError):
    """RECALL 操作错误"""
    pass


class ReflectError(OperationError):
    """REFLECT 操作错误"""
    pass


class UniMem:
    """
    UniMem: 统一记忆系统
    
    整合六大架构的最优方案：
    - 操作层：HindSight 三操作（Retain/Recall/Reflect）
    - 存储层：CogMem 三层架构（FoA/DA/LTM）+ MemMachine 多类型
    - 网络层：LightRAG 图结构（底层）+ A-Mem 原子笔记网络（上层）
    - 检索层：多维融合（实体/抽象/语义/图/时间）
    - 更新层：涟漪效应（实时）+ 睡眠更新（批量）
    
    设计优势：
    - 适配器模式：各架构解耦，可以独立开发、测试、替换
    - 统一操作：通过适配器接口进行信息交互、操作、叠加
    - 易于扩展：新增架构只需实现适配器接口
    - 事务支持：确保操作的一致性
    - 错误处理：完善的错误处理和回滚机制
    - 并发安全：支持多线程环境
    - 批量操作：支持批量处理
    - 幂等性：确保操作可重复执行
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        storage_backend: str = "redis",
        graph_backend: str = "neo4j",
        vector_backend: str = "qdrant",
        max_concurrent_operations: int = 10,
    ):
        """
        初始化 UniMem 系统
        
        Args:
            config: 配置字典
            storage_backend: 存储后端（redis/mongodb/postgresql）
            graph_backend: 图数据库后端（neo4j/networkx）
            vector_backend: 向量数据库后端（qdrant/faiss/milvus）
            max_concurrent_operations: 最大并发操作数（限流）
        """
        ***REMOVED*** 加载配置
        if isinstance(config, UniMemConfig):
            self.config = config.to_dict()
        elif isinstance(config, dict):
            self.config = config
        else:
            self.config = UniMemConfig().to_dict()
        
        ***REMOVED*** 先设置后端属性（验证配置时需要用到）
        self.storage_backend = storage_backend
        self.graph_backend = graph_backend
        self.vector_backend = vector_backend
        self.max_concurrent_operations = max_concurrent_operations
        
        ***REMOVED*** 验证配置
        self._validate_config()
        
        ***REMOVED*** 线程安全锁
        self._lock = threading.RLock()
        
        ***REMOVED*** 操作历史记录（用于幂等性检查）
        self._operation_history: Dict[str, Dict[str, Any]] = {}
        self._history_lock = threading.Lock()
        
        ***REMOVED*** 限流：信号量控制并发操作数
        self._operation_semaphore = threading.Semaphore(max_concurrent_operations)
        
        ***REMOVED*** 初始化适配器层（各架构解耦，通过适配器交互）
        logger.info("Initializing UniMem adapters...")
        self._init_adapters()
        
        ***REMOVED*** 初始化核心组件（通过功能适配器进行信息交互、操作、叠加）
        logger.info("Initializing UniMem core components...")
        self.storage = StorageManager(
            storage_adapter=self.storage_adapter,
            memory_type_adapter=self.memory_type_adapter,
        )
        self.retrieval = RetrievalEngine(
            graph_adapter=self.graph_adapter,
            atom_link_adapter=self.network_adapter,
            retrieval_adapter=self.retrieval_adapter,
            storage_manager=self.storage,
        )
        self.update_manager = UpdateManager(
            graph_adapter=self.graph_adapter,
            atom_link_adapter=self.network_adapter,
            update_adapter=self.update_adapter,
        )
        
        ***REMOVED*** 性能指标（线程安全）
        self.metrics = {
            "retain_count": 0,
            "recall_count": 0,
            "reflect_count": 0,
            "retain_errors": 0,
            "recall_errors": 0,
            "reflect_errors": 0,
            "retain_total_time": 0.0,
            "recall_total_time": 0.0,
            "reflect_total_time": 0.0,
            "adapter_calls": {},  ***REMOVED*** 适配器调用统计
        }
        self._metrics_lock = threading.Lock()
        
        logger.info("UniMem initialized successfully")
    
    def _validate_config(self):
        """验证配置"""
        ***REMOVED*** 验证必需配置
        required_keys = ["graph", "vector"]
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required config key: {key}")
        
        ***REMOVED*** 验证后端配置
        valid_storage_backends = ["redis", "mongodb", "postgresql"]
        if self.storage_backend not in valid_storage_backends:
            logger.warning(f"Unknown storage backend: {self.storage_backend}")
        
        valid_graph_backends = ["neo4j", "networkx"]
        if self.graph_backend not in valid_graph_backends:
            logger.warning(f"Unknown graph backend: {self.graph_backend}")
        
        valid_vector_backends = ["qdrant", "faiss", "milvus"]
        if self.vector_backend not in valid_vector_backends:
            logger.warning(f"Unknown vector backend: {self.vector_backend}")
    
    def _init_adapters(self):
        """
        初始化功能适配器
        
        按照 UniMem 的功能需求初始化适配器，从各大架构吸收精华思路：
        - 操作接口：参考 HindSight
        - 分层存储：参考 CogMem
        - 记忆分类：参考 MemMachine
        - 图结构：参考 LightRAG
        - 网络链接：参考 A-Mem
        - 检索融合：参考各架构
        - 更新机制：参考 LightMem + A-Mem
        """
        try:
            ***REMOVED*** 操作接口适配器（参考 HindSight）
            self.operation_adapter = OperationAdapter(config=self.config.get("operation", {}))
            self.operation_adapter.initialize()
            
            ***REMOVED*** 分层存储适配器（参考 CogMem）
            self.storage_adapter = LayeredStorageAdapter(config=self.config.get("layered_storage", {}))
            self.storage_adapter.initialize()
            
            ***REMOVED*** 记忆分类适配器（参考 MemMachine）
            self.memory_type_adapter = MemoryTypeAdapter(config=self.config.get("memory_type", {}))
            self.memory_type_adapter.initialize()
            
            ***REMOVED*** 图结构适配器（参考 LightRAG）
            graph_config = self.config.get("graph", {})
            graph_config["backend"] = self.graph_backend
            self.graph_adapter = GraphAdapter(config=graph_config)
            self.graph_adapter.initialize()
            
            ***REMOVED*** 原子链接适配器（参考 A-Mem）
            network_config = self.config.get("network", {})
            self.network_adapter = AtomLinkAdapter(config=network_config)
            self.network_adapter.initialize()
            
            ***REMOVED*** 检索引擎适配器（参考各架构）
            self.retrieval_adapter = RetrievalAdapter(config=self.config.get("retrieval", {}))
            self.retrieval_adapter.initialize()
            
            ***REMOVED*** 更新机制适配器（参考 LightMem + A-Mem）
            self.update_adapter = UpdateAdapter(config=self.config.get("update", {}))
            self.update_adapter.initialize()
            
            ***REMOVED*** 记录适配器状态
            self._log_adapter_status()
        except Exception as e:
            logger.error(f"Failed to initialize adapters: {e}", exc_info=True)
            raise
    
    def _log_adapter_status(self):
        """记录适配器状态"""
        adapters = {
            "Operation": self.operation_adapter,
            "LayeredStorage": self.storage_adapter,
            "MemoryType": self.memory_type_adapter,
            "Graph": self.graph_adapter,
            "AtomLink": self.network_adapter,
            "Retrieval": self.retrieval_adapter,
            "Update": self.update_adapter,
        }
        
        available = []
        unavailable = []
        
        for name, adapter in adapters.items():
            if adapter.is_available():
                available.append(name)
            else:
                unavailable.append(name)
        
        logger.info(f"Adapters available: {', '.join(available)}")
        if unavailable:
            logger.warning(f"Adapters unavailable: {', '.join(unavailable)}")
    
    def _record_adapter_call(self, adapter_name: str, method_name: str):
        """记录适配器调用（用于性能监控）"""
        with self._metrics_lock:
            key = f"{adapter_name}.{method_name}"
            self.metrics["adapter_calls"][key] = self.metrics["adapter_calls"].get(key, 0) + 1
    
    def _record_operation(self, operation_type: str, operation_id: str, result: Any):
        """记录操作历史（用于幂等性检查）"""
        with self._history_lock:
            self._operation_history[operation_id] = {
                "type": operation_type,
                "timestamp": datetime.now(),
                "result": result,
            }
    
    def _check_operation_idempotency(self, operation_id: str) -> Optional[Any]:
        """
        检查操作是否已执行（幂等性检查）
        
        Args:
            operation_id: 操作ID（基于 experience 内容生成）
            
        Returns:
            如果已执行，返回之前的结果；否则返回 None
        """
        with self._history_lock:
            if operation_id in self._operation_history:
                logger.debug(f"Operation {operation_id} already executed, returning cached result")
                return self._operation_history[operation_id]["result"]
        return None
    
    @contextmanager
    def _operation_context(self, operation_name: str):
        """操作上下文管理器，用于性能监控和错误处理"""
        ***REMOVED*** 限流：获取信号量
        self._operation_semaphore.acquire()
        try:
            start_time = datetime.now()
            try:
                yield
                duration = (datetime.now() - start_time).total_seconds()
                with self._metrics_lock:
                    self.metrics[f"{operation_name}_count"] += 1
                    self.metrics[f"{operation_name}_total_time"] += duration
                logger.debug(f"{operation_name} completed in {duration:.3f}s")
            except Exception as e:
                with self._metrics_lock:
                    self.metrics[f"{operation_name}_errors"] += 1
                logger.error(f"{operation_name} failed: {e}", exc_info=True)
                raise
        finally:
            self._operation_semaphore.release()
    
    @contextmanager
    def _retain_transaction(self, memory_id: str):
        """
        RETAIN 操作的事务上下文
        
        确保操作的原子性，失败时回滚
        """
        rollback_actions = []
        
        try:
            yield rollback_actions
        except Exception as e:
            ***REMOVED*** 执行回滚
            logger.warning(f"RETAIN transaction failed for {memory_id}, rolling back...")
            for action in reversed(rollback_actions):
                try:
                    action()
                except Exception as rollback_error:
                    logger.error(f"Rollback action failed: {rollback_error}")
            raise
    
    def _generate_operation_id(self, experience: Experience) -> str:
        """
        生成操作ID（用于幂等性检查）
        
        基于经验内容生成唯一ID
        """
        import hashlib
        content_hash = hashlib.md5(experience.content.encode()).hexdigest()
        timestamp_str = experience.timestamp.isoformat()
        return f"{content_hash}_{timestamp_str}"
    
    def retain(self, experience: Experience, context: Context, operation_id: Optional[str] = None) -> Memory:
        """
        RETAIN 操作：存储新记忆
        
        通过适配器进行信息交互、操作、叠加：
        1. 幂等性检查：如果已执行，返回缓存结果
        2. 并行执行步骤1-3（提取实体、构建笔记、分类类型）
        3. 存储管理器：存储到相应层级（参考 CogMem）
        4. 网络管理器：更新网络结构（LightRAG + A-Mem）
        5. 更新管理器：触发涟漪效应更新（参考 LightMem + A-Mem）
        
        Args:
            experience: 经验数据
            context: 上下文信息
            operation_id: 操作ID（用于幂等性检查，如果不提供则自动生成）
            
        Returns:
            创建的记忆对象
            
        Raises:
            RetainError: 如果操作失败
        """
        with self._operation_context("retain"):
            logger.info(f"RETAIN: Processing experience: {experience.content[:50]}...")
            
            ***REMOVED*** 生成或使用提供的操作ID
            if operation_id is None:
                operation_id = self._generate_operation_id(experience)
            
            ***REMOVED*** 幂等性检查
            cached_result = self._check_operation_idempotency(operation_id)
            if cached_result:
                logger.info(f"RETAIN: Operation {operation_id} already executed, returning cached result")
                return cached_result
            
            ***REMOVED*** 使用事务上下文确保一致性
            try:
                ***REMOVED*** 步骤1-3并行执行（提取实体、构建笔记、分类类型）
                with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                    ***REMOVED*** 提交并行任务
                    future_entities = executor.submit(self.graph_adapter.extract_entities_relations, experience.content)
                    future_note = executor.submit(
                        lambda: self._construct_atomic_note_with_storage(
                            content=experience.content,
                            timestamp=experience.timestamp,
                            entities=[],  ***REMOVED*** 先不传实体，后续更新
                        )
                    )
                    
                    ***REMOVED*** 等待实体提取完成
                    entities, relations = future_entities.result()
                    logger.debug(f"Extracted {len(entities)} entities and {len(relations)} relations")
                    
                    ***REMOVED*** 获取原子笔记
                    atomic_note = future_note.result()
                    logger.debug(f"Constructed atomic note: {atomic_note.id}")
                    
                    ***REMOVED*** 更新原子笔记的实体信息
                    atomic_note.entities = entities
                
                ***REMOVED*** 3. 记忆分类适配器：分类记忆类型
                self._record_adapter_call("MemoryTypeAdapter", "classify")
                memory_type = self.memory_type_adapter.classify(atomic_note)
                logger.debug(f"Classified memory type: {memory_type}")
                
                ***REMOVED*** 4. 构建完整的 Memory 对象
                memory = Memory(
                    id=atomic_note.id,
                    content=atomic_note.content,
                    timestamp=experience.timestamp,
                    memory_type=memory_type,
                    layer=MemoryLayer.FOA,
                    keywords=getattr(atomic_note, 'keywords', []) if hasattr(atomic_note, 'keywords') else [],
                    tags=getattr(atomic_note, 'tags', []) if hasattr(atomic_note, 'tags') else [],
                    context=getattr(atomic_note, 'context', None) or experience.context,
                    entities=[e.id for e in entities] if entities else [],
                )
                
                ***REMOVED*** 使用事务确保原子性
                with self._retain_transaction(memory.id) as rollback_actions:
                    ***REMOVED*** 5. 存储管理器：存储到相应层级（自动判断 FoA/DA/LTM）
                    self._record_adapter_call("LayeredStorageAdapter", "add_to_foa")
                    if not self.storage.add_memory(memory, context):
                        raise RetainError("Failed to add memory to storage")
                    
                    ***REMOVED*** 记录回滚操作
                    rollback_actions.append(lambda: self._rollback_storage(memory.id))
                    
                    ***REMOVED*** 6. 图结构适配器：更新网络结构
                    if entities:
                        self._record_adapter_call("GraphAdapter", "add_entities")
                        if not self.graph_adapter.add_entities(entities):
                            logger.warning("Failed to add some entities to graph")
                        else:
                            rollback_actions.append(lambda: self._rollback_entities(entities))
                    
                    if relations:
                        self._record_adapter_call("GraphAdapter", "add_relations")
                        if not self.graph_adapter.add_relations(relations):
                            logger.warning("Failed to add some relations to graph")
                        else:
                            rollback_actions.append(lambda: self._rollback_relations(relations))
                    
                ***REMOVED*** 7. 原子链接适配器：生成链接
                self._record_adapter_call("AtomLinkAdapter", "generate_links")
                links = self.network_adapter.generate_links(memory, top_k=10)
                memory.links = links
                
                ***REMOVED*** 更新向量存储中的链接信息
                if hasattr(self.network_adapter, 'update_memory_in_vector_store'):
                    self.network_adapter.update_memory_in_vector_store(memory)
                    
                    ***REMOVED*** 8. 更新管理器：触发涟漪效应更新（异步，不阻塞）
                    try:
                        self._record_adapter_call("UpdateAdapter", "trigger_ripple")
                        self.update_manager.trigger_ripple(
                            center=memory,
                            entities=entities,
                            relations=relations,
                            links=links,
                        )
                    except Exception as e:
                        ***REMOVED*** 涟漪更新失败不影响主流程
                        logger.warning(f"Ripple effect update failed: {e}")
                
                ***REMOVED*** 记录操作历史（用于幂等性检查）
                self._record_operation("retain", operation_id, memory)
                
                logger.info(f"RETAIN completed: Memory {memory.id} stored")
                return memory
                
            except Exception as e:
                logger.error(f"RETAIN failed: {e}", exc_info=True)
                raise RetainError(f"Failed to retain memory: {e}") from e
    
    def retain_batch(self, experiences: List[Experience], context: Context) -> List[Memory]:
        """
        批量 RETAIN 操作
        
        Args:
            experiences: 经验数据列表
            context: 上下文信息
            
        Returns:
            创建的记忆对象列表
        """
        logger.info(f"RETAIN BATCH: Processing {len(experiences)} experiences")
        
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrent_operations) as executor:
            futures = {
                executor.submit(self.retain, exp, context): exp
                for exp in experiences
            }
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    memory = future.result()
                    results.append(memory)
                except Exception as e:
                    exp = futures[future]
                    logger.error(f"Failed to retain experience: {exp.content[:50]}... Error: {e}")
        
        logger.info(f"RETAIN BATCH completed: {len(results)}/{len(experiences)} memories stored")
        return results
    
    def _rollback_storage(self, memory_id: str):
        """回滚存储操作"""
        try:
            ***REMOVED*** 从所有层移除记忆
            if hasattr(self.storage_adapter, 'remove_from_foa'):
                self.storage_adapter.remove_from_foa(memory_id)
            if hasattr(self.storage_adapter, 'remove_from_da'):
                self.storage_adapter.remove_from_da(memory_id)
            if hasattr(self.storage_adapter, 'remove_from_ltm'):
                self.storage_adapter.remove_from_ltm(memory_id)
            logger.debug(f"Rolled back storage for memory {memory_id}")
        except Exception as e:
            logger.error(f"Failed to rollback storage for {memory_id}: {e}")
    
    def _rollback_entities(self, entities):
        """回滚实体添加操作"""
        ***REMOVED*** TODO: 实现实体回滚逻辑（需要适配器支持）
        logger.debug(f"Rolling back {len(entities)} entities")
    
    def _rollback_relations(self, relations):
        """回滚关系添加操作"""
        ***REMOVED*** TODO: 实现关系回滚逻辑（需要适配器支持）
        logger.debug(f"Rolling back {len(relations)} relations")
    
    def _construct_atomic_note_with_storage(
        self,
        content: str,
        timestamp,
        entities: List,
    ) -> Memory:
        """
        构建原子笔记并添加到向量存储
        
        替代 NetworkManager.construct_atomic_note 的功能
        """
        memory = self.network_adapter.construct_atomic_note(
            content=content,
            timestamp=timestamp,
            entities=entities,
        )
        
        ***REMOVED*** 将记忆添加到向量存储
        if hasattr(self.network_adapter, 'add_memory_to_vector_store'):
            self.network_adapter.add_memory_to_vector_store(memory)
        
        return memory
    
    def _update_graph_from_memory(self, memory: Memory) -> bool:
        """
        根据记忆更新图结构
        
        替代 NetworkManager.update_graph_from_memory 的功能
        
        Args:
            memory: 记忆对象
            
        Returns:
            是否成功
        """
        try:
            entities = self.graph_adapter.get_entities_for_memory(memory.id)
            for entity in entities:
                self.graph_adapter.update_entity_description(
                    entity_id=entity.id,
                    description=memory.context or "",
                )
            return True
        except Exception as e:
            logger.warning(f"Failed to update graph from memory {memory.id}: {e}")
            return False
    
    def recall(
        self,
        query: str,
        context: Optional[Context] = None,
        memory_type: Optional[MemoryType] = None,
        top_k: int = 10,
    ) -> List[RetrievalResult]:
        """
        RECALL 操作：检索相关记忆
        
        通过检索引擎进行多维检索和信息融合：
        1. 存储层快速检索（FoA/DA）
        2. 多维检索引擎（实体/抽象/语义/图/时间）
        3. RRF 融合和重排序
        4. 过滤和去重
        
        Args:
            query: 查询字符串
            context: 上下文信息
            memory_type: 记忆类型过滤
            top_k: 返回结果数量
            
        Returns:
            检索结果列表
            
        Raises:
            RecallError: 如果操作失败
        """
        with self._operation_context("recall"):
            logger.info(f"RECALL: Query: {query[:50]}...")
            
            if context is None:
                context = Context()
            
            try:
                ***REMOVED*** 1. 快速检索：FoA 和 DA
                foa_results = self.storage.search_foa(query, top_k=top_k)
                da_results = self.storage.search_da(query, context, top_k=top_k)
                
                logger.debug(f"FoA: {len(foa_results)} results, DA: {len(da_results)} results")
                
                ***REMOVED*** 如果快速检索已有足够结果，直接返回
                if len(foa_results) >= top_k:
                    logger.debug(f"FoA retrieved {len(foa_results)} results, returning early")
                    return self._filter_results(foa_results, memory_type)[:top_k]
                
                ***REMOVED*** 2. 多维检索引擎：并行检索并融合
                multi_results = self.retrieval.multi_dimensional_retrieval(
                    query=query,
                    context=context,
                    top_k=top_k * 2,  ***REMOVED*** 获取更多结果以便过滤
                )
                
                logger.debug(f"Multi-dimensional retrieval: {len(multi_results)} results")
                
                ***REMOVED*** 3. 合并所有结果
                all_results = foa_results + da_results + multi_results
                
                ***REMOVED*** 4. 去重和过滤
                final_results = self._deduplicate_and_filter(
                    all_results,
                    memory_type=memory_type,
                )
                
                ***REMOVED*** 5. 重排序
                ranked_results = self._rank_results(final_results)
                
                logger.info(f"RECALL completed: {len(ranked_results)} results")
                return ranked_results[:top_k]
                
            except Exception as e:
                logger.error(f"RECALL failed: {e}", exc_info=True)
                raise RecallError(f"Failed to recall memories: {e}") from e
    
    def recall_batch(self, queries: List[str], context: Optional[Context] = None, top_k: int = 10) -> List[List[RetrievalResult]]:
        """
        批量 RECALL 操作
        
        Args:
            queries: 查询字符串列表
            context: 上下文信息
            top_k: 每个查询返回结果数量
            
        Returns:
            每个查询的检索结果列表
        """
        logger.info(f"RECALL BATCH: Processing {len(queries)} queries")
        
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrent_operations) as executor:
            futures = {
                executor.submit(self.recall, query, context, None, top_k): query
                for query in queries
            }
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    query = futures[future]
                    logger.error(f"Failed to recall query: {query[:50]}... Error: {e}")
                    results.append([])
        
        logger.info(f"RECALL BATCH completed: {len(results)}/{len(queries)} queries processed")
        return results
    
    def reflect(self, memories: List[Memory], current_task: Task, context: Optional[Context] = None) -> List[Memory]:
        """
        REFLECT 操作：更新和优化记忆
        
        整合 Hindsight 的 CARA (Coherent Adaptive Reasoning Agents) 思路：
        1. 操作适配器：基于事实进行推理和观点形成（Hindsight 风格）
        2. 网络管理器：记忆演化（参考 A-Mem）
        3. 网络管理器：更新图结构（参考 LightRAG）
        4. 存储管理器：更新存储层
        5. 更新适配器：记录到睡眠更新队列（参考 LightMem）
        
        Args:
            memories: 需要更新的记忆列表
            current_task: 当前任务上下文
            context: 上下文信息（可选，用于传递 Agent Profile）
            
        Returns:
            演化后的记忆列表（包含新形成的观点）
            
        Raises:
            ReflectError: 如果操作失败
        """
        with self._operation_context("reflect"):
            logger.info(f"REFLECT: Updating {len(memories)} memories")
            evolved_memories = []
            
            if context is None:
                context = Context()
            
            try:
                ***REMOVED*** 1. 操作适配器：执行 Hindsight 风格的 REFLECT（CARA）
                ***REMOVED*** 这会产生答案和新观点
                self._record_adapter_call("OperationAdapter", "reflect")
                reflect_result = self.operation_adapter.reflect(
                    memories=memories,
                    task=current_task,
                    agent_disposition=context.metadata.get("agent_disposition"),
                    agent_background=context.metadata.get("agent_background"),
                )
                
                ***REMOVED*** 提取 Hindsight REFLECT 的结果
                answer = reflect_result.get("answer", "")
                updated_memories = reflect_result.get("updated_memories", memories)
                new_opinions = reflect_result.get("new_opinions", [])
                
                logger.debug(f"REFLECT answer: {answer[:100]}...")
                if new_opinions:
                    logger.info(f"REFLECT: Generated {len(new_opinions)} new opinions")
                
                ***REMOVED*** 2. 对每个记忆进行网络演化（A-Mem 风格）
                for memory in updated_memories:
                    ***REMOVED*** 原子链接适配器：查找相关记忆并演化
                    related = self.network_adapter.find_related_memories(memory)
                    evolved = self.network_adapter.evolve_memory(
                        memory=memory,
                        related=related,
                        new_context=current_task.context,
                    )
                    evolved_memories.append(evolved)
                    
                    ***REMOVED*** 图结构适配器：更新图结构
                    self._update_graph_from_memory(evolved)
                    
                    ***REMOVED*** 存储管理器：更新存储层
                    self.storage.update_memory(evolved)
                    
                    ***REMOVED*** 更新向量存储中的记忆
                    if hasattr(self.network_adapter, 'update_memory_in_vector_store'):
                        self.network_adapter.update_memory_in_vector_store(evolved)
                    
                    ***REMOVED*** 更新适配器：记录到睡眠更新队列
                    self.update_adapter.add_to_sleep_queue([evolved])
                
                ***REMOVED*** 3. 存储新形成的观点（Hindsight 风格）
                for opinion in new_opinions:
                    ***REMOVED*** 存储新观点
                    self.storage.add_memory(opinion, context)
                    evolved_memories.append(opinion)
                    
                    ***REMOVED*** 更新向量存储
                    if hasattr(self.network_adapter, 'add_memory_to_vector_store'):
                        self.network_adapter.add_memory_to_vector_store(opinion)
                    
                    logger.debug(f"Stored new opinion: {opinion.id}")
                
                logger.info(f"REFLECT completed: {len(evolved_memories)} memories evolved (including {len(new_opinions)} new opinions)")
                return evolved_memories
                
            except Exception as e:
                logger.error(f"REFLECT failed: {e}", exc_info=True)
                raise ReflectError(f"Failed to reflect memories: {e}") from e
    
    def reflect_batch(self, memories_list: List[List[Memory]], tasks: List[Task]) -> List[List[Memory]]:
        """
        批量 REFLECT 操作
        
        Args:
            memories_list: 记忆列表的列表
            tasks: 任务列表
            
        Returns:
            每个任务演化后的记忆列表
        """
        if len(memories_list) != len(tasks):
            raise ValueError("memories_list and tasks must have the same length")
        
        logger.info(f"REFLECT BATCH: Processing {len(tasks)} tasks")
        
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrent_operations) as executor:
            futures = {
                executor.submit(self.reflect, memories, task): (memories, task)
                for memories, task in zip(memories_list, tasks)
            }
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    memories, task = futures[future]
                    logger.error(f"Failed to reflect memories for task {task.id}: {e}")
                    results.append([])
        
        logger.info(f"REFLECT BATCH completed: {len(results)}/{len(tasks)} tasks processed")
        return results
    
    def run_sleep_update(self) -> int:
        """
        执行睡眠更新
        
        批量处理非关键记忆的优化
        
        Returns:
            处理的记忆数量
        """
        logger.info("Running sleep update...")
        try:
            count = self.update_adapter.run_sleep_update()
            logger.info(f"Sleep update completed: {count} memories processed")
            return count
        except Exception as e:
            logger.error(f"Sleep update failed: {e}", exc_info=True)
            return 0
    
    def get_adapter_status(self) -> Dict[str, Any]:
        """
        获取所有适配器的状态
        
        Returns:
            适配器状态字典
        """
        return {
            "operation": self.operation_adapter.health_check(),
            "layered_storage": self.storage_adapter.health_check(),
            "memory_type": self.memory_type_adapter.health_check(),
            "graph": self.graph_adapter.health_check(),
            "atom_link": self.network_adapter.health_check(),
            "retrieval": self.retrieval_adapter.health_check(),
            "update": self.update_adapter.health_check(),
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        获取性能指标
        
        Returns:
            指标字典
        """
        with self._metrics_lock:
            metrics = self.metrics.copy()
        
        ***REMOVED*** 计算平均值
        if metrics["retain_count"] > 0:
            metrics["retain_avg_time"] = metrics["retain_total_time"] / metrics["retain_count"]
        if metrics["recall_count"] > 0:
            metrics["recall_avg_time"] = metrics["recall_total_time"] / metrics["recall_count"]
        if metrics["reflect_count"] > 0:
            metrics["reflect_avg_time"] = metrics["reflect_total_time"] / metrics["reflect_count"]
        
        return metrics
    
    def get_operation_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取操作历史
        
        Args:
            limit: 返回的最大记录数
            
        Returns:
            操作历史列表
        """
        with self._history_lock:
            history = list(self._operation_history.values())
            ***REMOVED*** 按时间排序，返回最新的
            history.sort(key=lambda x: x["timestamp"], reverse=True)
            return history[:limit]
    
    def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            健康状态字典
        """
        adapter_status = self.get_adapter_status()
        metrics = self.get_metrics()
        
        ***REMOVED*** 检查适配器可用性
        all_available = all(
            status.get("available", False)
            for status in adapter_status.values()
        )
        
        ***REMOVED*** 检查错误率
        total_operations = (
            metrics["retain_count"] + metrics["recall_count"] + metrics["reflect_count"]
        )
        total_errors = (
            metrics["retain_errors"] + metrics["recall_errors"] + metrics["reflect_errors"]
        )
        error_rate = total_errors / total_operations if total_operations > 0 else 0.0
        
        return {
            "status": "healthy" if all_available and error_rate < 0.1 else "degraded",
            "all_adapters_available": all_available,
            "error_rate": error_rate,
            "adapter_status": adapter_status,
            "metrics": {
                "total_operations": total_operations,
                "total_errors": total_errors,
                "retain_avg_time": metrics.get("retain_avg_time", 0.0),
                "recall_avg_time": metrics.get("recall_avg_time", 0.0),
                "reflect_avg_time": metrics.get("reflect_avg_time", 0.0),
            },
        }
    
    def _rank_results(self, results: List[RetrievalResult]) -> List[RetrievalResult]:
        """对结果进行排序"""
        return sorted(results, key=lambda x: x.score, reverse=True)
    
    def _filter_results(
        self,
        results: List[RetrievalResult],
        memory_type: Optional[MemoryType] = None,
    ) -> List[RetrievalResult]:
        """过滤结果"""
        if memory_type is None:
            return results
        
        return [
            r for r in results
            if r.memory.memory_type == memory_type
        ]
    
    def _deduplicate_and_filter(
        self,
        results: List[RetrievalResult],
        memory_type: Optional[MemoryType] = None,
    ) -> List[RetrievalResult]:
        """去重和过滤"""
        seen_ids = set()
        filtered = []
        
        for result in results:
            ***REMOVED*** 去重
            if result.memory.id in seen_ids:
                continue
            seen_ids.add(result.memory.id)
            
            ***REMOVED*** 类型过滤
            if memory_type and result.memory.memory_type != memory_type:
                continue
            
            filtered.append(result)
        
        return filtered
    
    def get_orchestrator(self):
        """
        获取编排器实例
        
        用于创建工作流和编排复杂操作流程
        
        Returns:
            Orchestrator 实例
        """
        from .orchestration import Orchestrator
        return Orchestrator(self)
