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

工业级特性：
- 统一异常处理（使用适配器异常体系）
- 完善的线程安全机制
- 健康检查机制
- 性能监控和指标收集
- 优雅降级支持
"""

import logging
import time
from typing import List, Optional, Dict, Any, Set, Tuple
from datetime import datetime
from contextlib import contextmanager
import threading
import concurrent.futures
from dataclasses import dataclass, field

from .memory_types import Experience, Memory, Task, Context, MemoryType, MemoryLayer, RetrievalResult
from .adapters import (
    OperationAdapter,
    LayeredStorageAdapter,
    MemoryTypeAdapter,
    GraphAdapter,
    AtomLinkAdapter,
    RetrievalAdapter,
    UpdateAdapter,
)
from .adapters.base import (
    AdapterError,
    AdapterConfigurationError,
    AdapterNotAvailableError,
)
from .storage import StorageManager
from .retrieval import RetrievalEngine
from .update import UpdateManager
from .config import UniMemConfig

logger = logging.getLogger(__name__)


***REMOVED*** 操作特定异常（继承自适配器异常体系）
class OperationError(AdapterError):
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


@dataclass
class OperationMetrics:
    """操作性能指标"""
    count: int = 0
    errors: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    
    @property
    def average_time(self) -> float:
        """平均耗时（秒）"""
        if self.count == 0:
            return 0.0
        return self.total_time / self.count
    
    @property
    def error_rate(self) -> float:
        """错误率"""
        total = self.count + self.errors
        if total == 0:
            return 0.0
        return self.errors / total
    
    def record(self, duration: float, success: bool = True) -> None:
        """记录操作指标"""
        if success:
            self.count += 1
        else:
            self.errors += 1
        self.total_time += duration
        self.min_time = min(self.min_time, duration)
        self.max_time = max(self.max_time, duration)


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
        
        ***REMOVED*** 先设置基本属性（验证配置时需要用到）
        self.storage_backend = storage_backend
        self.max_concurrent_operations = max_concurrent_operations
        self.operation_timeout = float(self.config.get("operation_timeout", 300.0))
        
        ***REMOVED*** 如果配置中指定了后端，使用配置中的值
        if "graph" in self.config and "backend" in self.config["graph"]:
            self.graph_backend = self.config["graph"]["backend"]
        else:
            self.graph_backend = graph_backend
            
        if "vector" in self.config and "backend" in self.config["vector"]:
            self.vector_backend = self.config["vector"]["backend"]
        else:
            self.vector_backend = vector_backend
        
        ***REMOVED*** 验证配置（会自动补充缺失的配置）
        self._validate_config()
        
        ***REMOVED*** 线程安全锁
        self._lock = threading.RLock()
        
        ***REMOVED*** 操作历史记录（用于幂等性检查）
        self._operation_history: Dict[str, Dict[str, Any]] = {}
        self._history_lock = threading.Lock()
        
        ***REMOVED*** 限流：信号量控制并发操作数
        self._operation_semaphore = threading.Semaphore(max_concurrent_operations)
        
        ***REMOVED*** 操作超时配置（秒）
        self.operation_timeout = float(self.config.get("operation_timeout", 300.0))
        
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
        
        ***REMOVED*** 性能指标（使用数据类，线程安全）
        self.metrics = {
            "retain": OperationMetrics(),
            "recall": OperationMetrics(),
            "reflect": OperationMetrics(),
            "adapter_calls": {},  ***REMOVED*** 适配器调用统计
        }
        self._metrics_lock = threading.Lock()
        
        ***REMOVED*** 系统启动时间
        self._start_time = datetime.now()
        
        logger.info("UniMem initialized successfully")
    
    def _validate_config(self) -> None:
        """
        验证配置
        
        Raises:
            AdapterConfigurationError: 如果配置无效
        """
        ***REMOVED*** 验证必需配置（允许最小配置，即使后端不可用）
        ***REMOVED*** 如果缺少 graph 或 vector，使用最小配置
        if "graph" not in self.config:
            logger.warning("Missing 'graph' config, using minimal configuration (memory-only mode)")
            self.config["graph"] = {
                "backend": "memory",
                "workspace": "./unimem_workspace",
                "llm_model": "gpt-4o-mini",
                "embedding_model": "text-embedding-3-small",
            }
        
        if "vector" not in self.config:
            logger.warning("Missing 'vector' config, using minimal configuration (memory-only mode)")
            self.config["vector"] = {
                "backend": "memory"
            }
        
        ***REMOVED*** 验证后端配置
        valid_storage_backends = ["redis", "mongodb", "postgresql"]
        if self.storage_backend not in valid_storage_backends:
            logger.warning(f"Unknown storage backend: {self.storage_backend}")
        
        valid_graph_backends = ["neo4j", "networkx", "memory"]
        if self.graph_backend not in valid_graph_backends:
            logger.warning(f"Unknown graph backend: {self.graph_backend}, will use degraded mode")
        
        valid_vector_backends = ["qdrant", "faiss", "milvus", "memory"]
        if self.vector_backend not in valid_vector_backends:
            logger.warning(f"Unknown vector backend: {self.vector_backend}, will use degraded mode")
        
        ***REMOVED*** 验证超时配置
        if self.operation_timeout <= 0:
            raise AdapterConfigurationError(
                f"operation_timeout must be positive, got {self.operation_timeout}",
                adapter_name="UniMem"
            )
    
    def _init_adapters(self) -> None:
        """
        初始化功能适配器（带优雅降级）
        
        按照 UniMem 的功能需求初始化适配器，从各大架构吸收精华思路：
        - 操作接口：参考 HindSight
        - 分层存储：参考 CogMem
        - 记忆分类：参考 MemMachine
        - 图结构：参考 LightRAG
        - 网络链接：参考 A-Mem
        - 检索融合：参考各架构
        - 更新机制：参考 LightMem + A-Mem
        
        注意：适配器初始化失败不会导致整个系统失败，系统会以降级模式运行
        """
        adapters_config = [
            ("operation", OperationAdapter, self.config.get("operation", {}), True),  ***REMOVED*** 必需
            ("layered_storage", LayeredStorageAdapter, {
                **self.config.get("layered_storage", {}),
                **self.config.get("storage", {}),  ***REMOVED*** 合并 storage 配置
            }, True),  ***REMOVED*** 必需
            ("memory_type", MemoryTypeAdapter, self.config.get("memory_type", {}), False),  ***REMOVED*** 可选
            ("graph", GraphAdapter, {**self.config.get("graph", {}), "backend": self.graph_backend}, False),  ***REMOVED*** 可选
            ("network", AtomLinkAdapter, self.config.get("network", {}), False),  ***REMOVED*** 可选
            ("retrieval", RetrievalAdapter, self.config.get("retrieval", {}), False),  ***REMOVED*** 可选
            ("update", UpdateAdapter, self.config.get("update", {}), False),  ***REMOVED*** 可选
        ]
        
        failed_adapters = []
        
        for name, adapter_class, config, required in adapters_config:
            try:
                adapter = adapter_class(config=config)
                adapter.initialize()
                
                ***REMOVED*** 设置属性
                if name == "operation":
                    self.operation_adapter = adapter
                elif name == "layered_storage":
                    self.storage_adapter = adapter
                elif name == "memory_type":
                    self.memory_type_adapter = adapter
                elif name == "graph":
                    self.graph_adapter = adapter
                elif name == "network":
                    self.network_adapter = adapter
                elif name == "retrieval":
                    self.retrieval_adapter = adapter
                elif name == "update":
                    self.update_adapter = adapter
                
                if not adapter.is_available() and required:
                    logger.warning(f"Required adapter '{name}' is not available, system will be limited")
                    failed_adapters.append(name)
                elif not adapter.is_available():
                    logger.warning(f"Optional adapter '{name}' is not available, some features will be limited")
                    failed_adapters.append(name)
                    
            except AdapterConfigurationError as e:
                logger.error(f"Adapter '{name}' configuration error: {e}", exc_info=True)
                if required:
                    raise  ***REMOVED*** 必需适配器的配置错误需要重新抛出
                failed_adapters.append(name)
            except Exception as e:
                logger.error(f"Failed to initialize adapter '{name}': {e}", exc_info=True)
                if required:
                    raise  ***REMOVED*** 必需适配器的初始化失败需要重新抛出
                failed_adapters.append(name)
        
        ***REMOVED*** 记录适配器状态
        self._log_adapter_status()
        
        if failed_adapters:
            logger.warning(f"Some adapters failed to initialize: {', '.join(failed_adapters)}. System running in degraded mode.")
    
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
        """
        操作上下文管理器，用于性能监控和错误处理（线程安全）
        
        提供：
        - 限流控制（信号量）
        - 性能监控（耗时统计）
        - 错误统计
        - 超时控制（可选）
        """
        ***REMOVED*** 限流：获取信号量
        self._operation_semaphore.acquire()
        start_time = time.time()
        try:
            try:
                yield
                duration = time.time() - start_time
                ***REMOVED*** 记录成功指标
                with self._metrics_lock:
                    if operation_name in self.metrics and isinstance(self.metrics[operation_name], OperationMetrics):
                        self.metrics[operation_name].record(duration, success=True)
                    else:
                        ***REMOVED*** 向后兼容：如果指标不存在，初始化它
                        self.metrics[operation_name] = OperationMetrics()
                        self.metrics[operation_name].record(duration, success=True)
                logger.debug(f"{operation_name} completed in {duration:.3f}s")
            except Exception as e:
                duration = time.time() - start_time
                ***REMOVED*** 记录错误指标
                with self._metrics_lock:
                    if operation_name in self.metrics and isinstance(self.metrics[operation_name], OperationMetrics):
                        self.metrics[operation_name].record(duration, success=False)
                    else:
                        self.metrics[operation_name] = OperationMetrics()
                        self.metrics[operation_name].record(duration, success=False)
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
                ***REMOVED*** 合并context的metadata到memory的metadata
                memory_metadata = {}
                if hasattr(atomic_note, 'metadata') and atomic_note.metadata:
                    memory_metadata.update(atomic_note.metadata)
                if context.metadata:
                    memory_metadata.update(context.metadata)
                
                ***REMOVED*** 捕获决策痕迹和理由（Context Graph增强）
                ***REMOVED*** 优先使用metadata中已有的decision_trace
                decision_trace = context.metadata.get("decision_trace") if context.metadata else None
                reasoning = context.metadata.get("reasoning", "") if context.metadata else None
                
                ***REMOVED*** 调试日志：检查decision_trace的来源
                logger.debug(f"RETAIN: decision_trace from context.metadata: {decision_trace is not None}, type: {type(decision_trace)}")
                if decision_trace:
                    logger.debug(f"RETAIN: decision_trace keys: {list(decision_trace.keys()) if isinstance(decision_trace, dict) else 'N/A'}")
                
                ***REMOVED*** 如果没有decision_trace，则从metadata中构建
                if not decision_trace and context.metadata:
                    ***REMOVED*** 检查是否有构建decision_trace所需的字段
                    has_trace_fields = any([
                        context.metadata.get("inputs"),
                        context.metadata.get("rules"),
                        context.metadata.get("exceptions"),
                        context.metadata.get("approvals")
                    ])
                    
                    if has_trace_fields:
                        decision_trace = {
                            "inputs": context.metadata.get("inputs", []),
                            "rules_applied": context.metadata.get("rules", []),
                            "exceptions": context.metadata.get("exceptions", []),
                            "approvals": context.metadata.get("approvals", []),
                            "timestamp": experience.timestamp.isoformat(),
                            "operation_id": operation_id,
                        }
                    else:
                        ***REMOVED*** 即使没有明确字段，也创建一个基础trace（至少包含时间戳和操作ID）
                        decision_trace = {
                            "inputs": [experience.content[:200]] if experience.content else [],
                            "rules_applied": [],
                            "exceptions": [],
                            "approvals": [],
                            "timestamp": experience.timestamp.isoformat(),
                            "operation_id": operation_id,
                        }
                
                ***REMOVED*** 如果decision_trace存在，确保包含必要字段
                if decision_trace:
                    if "timestamp" not in decision_trace:
                        decision_trace["timestamp"] = experience.timestamp.isoformat()
                    if "operation_id" not in decision_trace:
                        decision_trace["operation_id"] = operation_id
                
                ***REMOVED*** 提取决策理由（如果没有，尝试从metadata中其他字段推断）
                if not reasoning and context.metadata:
                    ***REMOVED*** 尝试从其他metadata字段构建reasoning
                    if context.metadata.get("task_description"):
                        reasoning = f"基于任务：{context.metadata.get('task_description', '')}"
                    elif context.metadata.get("source"):
                        reasoning = f"来源：{context.metadata.get('source', '')}"
                    else:
                        reasoning = ""  ***REMOVED*** 设置为空字符串而不是None
                
                ***REMOVED*** 调试日志：在创建Memory对象之前检查decision_trace
                logger.debug(f"RETAIN: Before creating Memory - decision_trace: {decision_trace is not None}, reasoning: {reasoning is not None and len(reasoning) > 0}")
                if decision_trace:
                    logger.debug(f"RETAIN: decision_trace content: keys={list(decision_trace.keys()) if isinstance(decision_trace, dict) else 'N/A'}")
                
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
                    metadata=memory_metadata,  ***REMOVED*** 确保metadata被正确传递
                    reasoning=reasoning,  ***REMOVED*** 新增：决策理由
                    decision_trace=decision_trace,  ***REMOVED*** 新增：决策痕迹
                )
                
                ***REMOVED*** 调试日志：Memory对象创建后立即检查decision_trace
                logger.debug(f"RETAIN: After creating Memory {memory.id} - decision_trace: {memory.decision_trace is not None}, reasoning: {memory.reasoning is not None and len(memory.reasoning) > 0 if memory.reasoning else False}")
                if memory.decision_trace:
                    logger.debug(f"RETAIN: Memory.decision_trace keys: {list(memory.decision_trace.keys()) if isinstance(memory.decision_trace, dict) else 'N/A'}")
                
                ***REMOVED*** 去重检查：在存储前检查是否有相似记忆
                similar_memory = self._check_duplicate_memory(memory)
                skip_storage = False  ***REMOVED*** 标记是否跳过存储逻辑
                
                if similar_memory:
                    ***REMOVED*** 如果找到高度相似的记忆，更新已有记忆而不是创建新记忆
                    logger.info(f"Found similar memory {similar_memory.id}, updating instead of creating new")
                    ***REMOVED*** 更新已有记忆的内容和元数据
                    similar_memory.content = memory.content  ***REMOVED*** 使用新内容
                    similar_memory.timestamp = memory.timestamp  ***REMOVED*** 更新时间戳
                    ***REMOVED*** 合并metadata
                    if memory.metadata:
                        if not similar_memory.metadata:
                            similar_memory.metadata = {}
                        similar_memory.metadata.update(memory.metadata)
                    ***REMOVED*** 合并keywords和tags
                    similar_memory.keywords = list(set(similar_memory.keywords + memory.keywords))
                    similar_memory.tags = list(set(similar_memory.tags + memory.tags))
                    ***REMOVED*** 重要：更新decision_trace和reasoning（修复DecisionEvent创建问题）
                    if memory.decision_trace:
                        similar_memory.decision_trace = memory.decision_trace
                        logger.debug(f"Updated similar_memory {similar_memory.id} with decision_trace")
                    if memory.reasoning:
                        similar_memory.reasoning = memory.reasoning
                        logger.debug(f"Updated similar_memory {similar_memory.id} with reasoning")
                    ***REMOVED*** 更新记忆（相似记忆已经存在，直接更新即可）
                    self.storage.update_memory(similar_memory)
                    ***REMOVED*** 将similar_memory赋值给memory，以便后续的DecisionEvent创建逻辑使用
                    memory = similar_memory
                    skip_storage = True  ***REMOVED*** 标记跳过存储逻辑
                
                ***REMOVED*** 使用事务确保原子性（仅对新记忆执行）
                if not skip_storage:
                    with self._retain_transaction(memory.id) as rollback_actions:
                        ***REMOVED*** 5. 存储管理器：存储到相应层级（自动判断 FoA/DA/LTM）
                        self._record_adapter_call("LayeredStorageAdapter", "add_to_foa")
                        if not self.storage.add_memory(memory, context):
                            raise RetainError(
                                "Failed to add memory to storage",
                                adapter_name="UniMem"
                            )
                        
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
                else:
                    ***REMOVED*** 相似记忆也需要更新图结构（如果有新的实体和关系）
                    if entities:
                        self._record_adapter_call("GraphAdapter", "add_entities")
                        if not self.graph_adapter.add_entities(entities):
                            logger.warning("Failed to add some entities to graph")
                    
                    if relations:
                        self._record_adapter_call("GraphAdapter", "add_relations")
                        if not self.graph_adapter.add_relations(relations):
                            logger.warning("Failed to add some relations to graph")
                    
                ***REMOVED*** 7. 原子链接适配器：生成链接
                self._record_adapter_call("AtomLinkAdapter", "generate_links")
                links = self.network_adapter.generate_links(memory, top_k=10)
                memory.links = links
                
                ***REMOVED*** 更新向量存储中的链接信息
                if hasattr(self.network_adapter, 'update_memory_in_vector_store'):
                    self.network_adapter.update_memory_in_vector_store(memory)
                
                ***REMOVED*** 如果生成了links，更新Neo4j中的memory节点以建立RELATED_TO关系
                if links:
                    try:
                        self._record_adapter_call("LayeredStorageAdapter", "update_memory_links")
                        ***REMOVED*** 通过storage manager更新memory（会更新Neo4j中的关系）
                        if hasattr(self.storage, 'update_memory'):
                            self.storage.update_memory(memory)
                        logger.debug(f"Updated memory {memory.id} with {len(links)} links in Neo4j")
                    except Exception as e:
                        logger.warning(f"Failed to update memory links in Neo4j: {e}")
                    
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
                
                ***REMOVED*** 9. 创建决策事件节点（Context Graph增强）
                ***REMOVED*** 优化：降低创建阈值，增强fallback机制
                should_create_event = False
                decision_trace_for_event = None
                reasoning_for_event = memory.reasoning or ""
                
                ***REMOVED*** 调试日志：检查Memory对象在DecisionEvent创建前的状态
                logger.debug(f"RETAIN: Before DecisionEvent creation for memory {memory.id} - decision_trace: {memory.decision_trace is not None}, type: {type(memory.decision_trace)}")
                if memory.decision_trace:
                    logger.debug(f"RETAIN: Memory.decision_trace is dict: {isinstance(memory.decision_trace, dict)}, keys: {list(memory.decision_trace.keys()) if isinstance(memory.decision_trace, dict) else 'N/A'}")
                
                ***REMOVED*** 首先检查memory对象中的decision_trace
                if memory.decision_trace and isinstance(memory.decision_trace, dict):
                    decision_trace_for_event = memory.decision_trace
                    ***REMOVED*** 检查是否有有效内容（降低阈值：只要decision_trace存在且有结构就创建）
                    has_content = (
                        len(memory.decision_trace.get("inputs", [])) > 0 or
                        len(memory.decision_trace.get("rules_applied", [])) > 0 or
                        len(memory.decision_trace.get("exceptions", [])) > 0 or
                        len(memory.decision_trace.get("approvals", [])) > 0 or
                        memory.decision_trace.get("timestamp") or
                        memory.decision_trace.get("operation_id")
                    )
                    if has_content:
                        should_create_event = True
                
                ***REMOVED*** Fallback: 如果memory对象没有decision_trace，尝试从Neo4j读取
                if not decision_trace_for_event:
                    try:
                        from .neo4j import get_memory
                        ***REMOVED*** 从Neo4j读取完整的memory节点（使用已修复的读取逻辑）
                        neo4j_memory = get_memory(memory.id)
                        if neo4j_memory and neo4j_memory.decision_trace and isinstance(neo4j_memory.decision_trace, dict):
                            decision_trace_for_event = neo4j_memory.decision_trace
                            if not reasoning_for_event and neo4j_memory.reasoning:
                                reasoning_for_event = neo4j_memory.reasoning
                            ***REMOVED*** 检查是否有有效内容
                            has_content = (
                                len(decision_trace_for_event.get("inputs", [])) > 0 or
                                len(decision_trace_for_event.get("rules_applied", [])) > 0 or
                                len(decision_trace_for_event.get("exceptions", [])) > 0 or
                                len(decision_trace_for_event.get("approvals", [])) > 0 or
                                decision_trace_for_event.get("timestamp") or
                                decision_trace_for_event.get("operation_id")
                            )
                            if has_content:
                                should_create_event = True
                                logger.debug(f"Found decision_trace in Neo4j for memory {memory.id}, will create event")
                    except Exception as e:
                        logger.debug(f"Failed to read decision_trace from Neo4j for memory {memory.id}: {e}")
                
                ***REMOVED*** 如果有reasoning但还没有decision_trace，也尝试创建（至少记录推理过程）
                if not should_create_event and reasoning_for_event and len(reasoning_for_event.strip()) > 10:
                    ***REMOVED*** 创建一个基础的decision_trace
                    decision_trace_for_event = {
                        "inputs": [memory.content[:200]] if memory.content else [],
                        "rules_applied": [],
                        "exceptions": [],
                        "approvals": [],
                        "timestamp": memory.timestamp.isoformat(),
                        "operation_id": operation_id,
                        "reasoning": reasoning_for_event
                    }
                    should_create_event = True
                    logger.debug(f"Creating decision event based on reasoning for memory {memory.id}")
                
                ***REMOVED*** 调试日志：DecisionEvent创建条件检查
                logger.debug(f"RETAIN: DecisionEvent creation check for memory {memory.id} - should_create_event: {should_create_event}, decision_trace_for_event: {decision_trace_for_event is not None}")
                
                ***REMOVED*** 创建DecisionEvent节点
                if should_create_event and decision_trace_for_event:
                    try:
                        from .neo4j import create_decision_event
                        ***REMOVED*** 获取相关实体ID
                        related_entity_ids = memory.entities if memory.entities else []
                        ***REMOVED*** 调试日志：即将创建DecisionEvent
                        logger.debug(f"RETAIN: Creating DecisionEvent for memory {memory.id} with decision_trace keys: {list(decision_trace_for_event.keys()) if isinstance(decision_trace_for_event, dict) else 'N/A'}")
                        ***REMOVED*** 创建决策事件节点
                        if create_decision_event(
                            memory_id=memory.id,
                            decision_trace=decision_trace_for_event,
                            reasoning=reasoning_for_event,
                            related_entity_ids=related_entity_ids
                        ):
                            logger.info(f"Created decision event for memory {memory.id}")
                        else:
                            logger.warning(f"Failed to create decision event for memory {memory.id} (create_decision_event returned False)")
                    except Exception as e:
                        ***REMOVED*** 决策事件创建失败不影响主流程
                        logger.warning(f"Failed to create decision event for memory {memory.id}: {e}", exc_info=True)
                else:
                    logger.debug(f"Skipping decision event creation for memory {memory.id} - should_create_event: {should_create_event}, decision_trace_for_event: {decision_trace_for_event is not None}, reasoning_for_event: {len(reasoning_for_event) if reasoning_for_event else 0} chars")
                
                ***REMOVED*** 记录操作历史（用于幂等性检查）
                self._record_operation("retain", operation_id, memory)
                
                logger.info(f"RETAIN completed: Memory {memory.id} stored")
                return memory
                
            except (RetainError, AdapterError, AdapterNotAvailableError):
                ***REMOVED*** 重新抛出已知的适配器异常
                raise
            except Exception as e:
                logger.error(f"RETAIN failed: {e}", exc_info=True)
                raise RetainError(
                    f"Failed to retain memory: {e}",
                    adapter_name="UniMem",
                    cause=e
                ) from e
    
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
                
            except (RecallError, AdapterError, AdapterNotAvailableError):
                ***REMOVED*** 重新抛出已知的适配器异常
                raise
            except Exception as e:
                logger.error(f"RECALL failed: {e}", exc_info=True)
                raise RecallError(
                    f"Failed to recall memories: {e}",
                    adapter_name="UniMem",
                    cause=e
                ) from e
    
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
                new_experiences = reflect_result.get("new_experiences", [])
                
                logger.debug(f"REFLECT answer: {answer[:100]}...")
                if new_opinions:
                    logger.info(f"REFLECT: Generated {len(new_opinions)} new opinions")
                if new_experiences:
                    logger.info(f"REFLECT: Extracted {len(new_experiences)} new experiences")
                
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
                ***REMOVED*** 改进：使用retain方法存储，确保创建decision_trace
                for opinion in new_opinions:
                    ***REMOVED*** 构建决策痕迹（Context Graph增强）
                    experience = Experience(
                        content=opinion.content,
                        timestamp=opinion.timestamp
                    )
                    
                    ***REMOVED*** 构建包含decision_trace的context
                    reflect_context = Context(
                        metadata={
                            "source": opinion.metadata.get("source", "reflect"),
                            "task_description": current_task.description,
                            "task_id": current_task.id,
                            "inputs": [m.content[:200] for m in memories[:3]],  ***REMOVED*** 基于的记忆
                            "rules": [
                                "基于事实进行推理",
                                "形成可复用的观点",
                                "考虑Agent性格配置"
                            ],
                            "exceptions": [],
                            "approvals": [],
                            "reasoning": opinion.reasoning or "",
                            "decision_trace": {
                                "inputs": [m.content[:200] for m in memories[:3]],
                                "rules_applied": [
                                    "基于事实进行推理",
                                    "形成可复用的观点",
                                    "考虑Agent性格配置"
                                ],
                                "exceptions": [],
                                "approvals": [],
                                "timestamp": opinion.timestamp.isoformat(),
                                "operation_id": f"reflect_opinion_{current_task.id}",
                                "task_id": current_task.id,
                                "based_on_memories": [m.id for m in memories[:5]]
                            }
                        }
                    )
                    
                    ***REMOVED*** 使用retain存储，确保创建decision_trace和DecisionEvent
                    stored_opinion = self.retain(experience, reflect_context)
                    evolved_memories.append(stored_opinion)
                    logger.debug(f"Stored new opinion: {stored_opinion.id}")
                
                ***REMOVED*** 4. 存储新提取的经验（增强功能）
                ***REMOVED*** 改进：使用retain方法存储，确保创建decision_trace
                for experience_mem in new_experiences:
                    ***REMOVED*** 确保经验记忆有正确的source
                    source = experience_mem.metadata.get("source", "reflect_experience")
                    
                    ***REMOVED*** 构建决策痕迹（Context Graph增强）
                    experience = Experience(
                        content=experience_mem.content,
                        timestamp=experience_mem.timestamp
                    )
                    
                    ***REMOVED*** 构建包含decision_trace的context
                    reflect_context = Context(
                        metadata={
                            "source": source,
                            "task_description": current_task.description,
                            "task_id": current_task.id,
                            "inputs": [m.content[:200] for m in memories[:3]],  ***REMOVED*** 基于的记忆
                            "rules": [
                                "从多轮对话中提取经验模式",
                                "识别可复用的优化策略",
                                "总结通用最佳实践"
                            ],
                            "exceptions": [],
                            "approvals": [],
                            "reasoning": experience_mem.reasoning or "",
                            "decision_trace": {
                                "inputs": [m.content[:200] for m in memories[:3]],
                                "rules_applied": [
                                    "从多轮对话中提取经验模式",
                                    "识别可复用的优化策略",
                                    "总结通用最佳实践"
                                ],
                                "exceptions": [],
                                "approvals": [],
                                "timestamp": experience_mem.timestamp.isoformat(),
                                "operation_id": f"reflect_experience_{current_task.id}",
                                "task_id": current_task.id,
                                "based_on_memories": [m.id for m in memories[:5]],
                                "experience_type": source  ***REMOVED*** reflect_experience, reflect_implicit, reflect_pattern_summary
                            }
                        }
                    )
                    
                    ***REMOVED*** 使用retain存储，确保创建decision_trace和DecisionEvent
                    stored_experience = self.retain(experience, reflect_context)
                    evolved_memories.append(stored_experience)
                    logger.debug(f"Stored new experience: {stored_experience.id}")
                
                logger.info(f"REFLECT completed: {len(evolved_memories)} memories evolved "
                          f"(including {len(new_opinions)} new opinions, {len(new_experiences)} new experiences)")
                return evolved_memories
                
            except (ReflectError, AdapterError, AdapterNotAvailableError):
                ***REMOVED*** 重新抛出已知的适配器异常
                raise
            except Exception as e:
                logger.error(f"REFLECT failed: {e}", exc_info=True)
                raise ReflectError(
                    f"Failed to reflect memories: {e}",
                    adapter_name="UniMem",
                    cause=e
                ) from e
    
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
            raise AdapterError(
                f"memories_list and tasks must have the same length, "
                f"got {len(memories_list)} and {len(tasks)}",
                adapter_name="UniMem"
            )
        
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
        获取所有适配器的状态（线程安全）
        
        Returns:
            适配器状态字典，包含每个适配器的健康检查信息
        """
        adapters = {
            "operation": self.operation_adapter,
            "layered_storage": self.storage_adapter,
            "memory_type": self.memory_type_adapter,
            "graph": self.graph_adapter,
            "atom_link": self.network_adapter,
            "retrieval": self.retrieval_adapter,
            "update": self.update_adapter,
        }
        
        status = {}
        for name, adapter in adapters.items():
            try:
                health_status = adapter.health_check()
                ***REMOVED*** 如果返回的是数据类，转换为字典
                if hasattr(health_status, '__dict__') and not isinstance(health_status, dict):
                    status[name] = {
                        "adapter": health_status.adapter,
                        "initialized": health_status.initialized,
                        "available": health_status.available,
                        "capabilities": health_status.capabilities,
                        **({"details": health_status.details} if health_status.details else {})
                    }
                else:
                    status[name] = health_status if isinstance(health_status, dict) else adapter.get_health_dict() if hasattr(adapter, 'get_health_dict') else {}
            except Exception as e:
                logger.error(f"Error checking health of adapter {name}: {e}", exc_info=True)
                status[name] = {
                    "adapter": name,
                    "initialized": True,
                    "available": False,
                    "error": str(e)
                }
        
        return status
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        获取性能指标（线程安全）
        
        Returns:
            指标字典，包含操作统计和适配器调用统计
        """
        with self._metrics_lock:
            result = {
                "retain": self._metrics_to_dict(self.metrics.get("retain")),
                "recall": self._metrics_to_dict(self.metrics.get("recall")),
                "reflect": self._metrics_to_dict(self.metrics.get("reflect")),
                "adapter_calls": self.metrics.get("adapter_calls", {}).copy(),
            }
        
        return result
    
    def _metrics_to_dict(self, metrics: Optional[OperationMetrics]) -> Dict[str, Any]:
        """将 OperationMetrics 转换为字典"""
        if metrics is None:
            return {
                "count": 0,
                "errors": 0,
                "average_time": 0.0,
                "min_time": 0.0,
                "max_time": 0.0,
                "error_rate": 0.0,
            }
        return {
            "count": metrics.count,
            "errors": metrics.errors,
            "average_time": metrics.average_time,
            "min_time": metrics.min_time if metrics.min_time != float('inf') else 0.0,
            "max_time": metrics.max_time,
            "error_rate": metrics.error_rate,
        }
    
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
        系统健康检查（线程安全）
        
        检查所有组件的健康状态，包括：
        - 适配器可用性
        - 操作错误率
        - 系统运行时间
        - 性能指标
        
        Returns:
            健康状态字典，包含：
            - status: "healthy" | "degraded" | "unhealthy"
            - all_adapters_available: bool
            - critical_adapters_available: bool
            - error_rate: float
            - adapter_status: Dict
            - metrics: Dict
            - uptime_seconds: float
        """
        adapter_status = self.get_adapter_status()
        metrics = self.get_metrics()
        
        ***REMOVED*** 检查适配器可用性
        all_available = all(
            status.get("available", False)
            for status in adapter_status.values()
        )
        
        ***REMOVED*** 检查关键适配器可用性（操作、存储、检索）
        critical_adapters = ["operation", "layered_storage", "retrieval"]
        critical_available = all(
            adapter_status.get(name, {}).get("available", False)
            for name in critical_adapters
        )
        
        ***REMOVED*** 计算总体错误率
        total_operations = (
            metrics["retain"]["count"] + 
            metrics["recall"]["count"] + 
            metrics["reflect"]["count"]
        )
        total_errors = (
            metrics["retain"]["errors"] + 
            metrics["recall"]["errors"] + 
            metrics["reflect"]["errors"]
        )
        error_rate = total_errors / (total_operations + total_errors) if (total_operations + total_errors) > 0 else 0.0
        
        ***REMOVED*** 计算系统运行时间
        uptime_seconds = (datetime.now() - self._start_time).total_seconds()
        
        ***REMOVED*** 判断整体状态
        if not critical_available:
            status = "unhealthy"
        elif error_rate > 0.2 or not all_available:
            status = "degraded"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": uptime_seconds,
            "all_adapters_available": all_available,
            "critical_adapters_available": critical_available,
            "error_rate": error_rate,
            "adapter_status": adapter_status,
            "metrics": {
                "retain": metrics["retain"],
                "recall": metrics["recall"],
                "reflect": metrics["reflect"],
                "total_operations": total_operations,
                "total_errors": total_errors,
                "adapter_calls": metrics["adapter_calls"],
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
    
    def _check_duplicate_memory(self, memory: Memory, similarity_threshold: float = 0.9) -> Optional[Memory]:
        """
        检查是否有重复或高度相似的记忆
        
        使用向量相似度检索查找相似记忆，如果相似度超过阈值，返回已有记忆。
        
        Args:
            memory: 要检查的记忆
            similarity_threshold: 相似度阈值（0-1），默认0.9
            
        Returns:
            如果找到相似记忆，返回已有记忆；否则返回None
        """
        try:
            ***REMOVED*** 使用网络适配器（AtomLinkAdapter）搜索相似记忆
            if hasattr(self.network_adapter, '_search_similar_memories'):
                similar_memories = self.network_adapter._search_similar_memories(
                    memory.content, 
                    top_k=5
                )
                
                if similar_memories:
                    ***REMOVED*** 检查相似度（如果网络适配器提供了相似度分数）
                    for similar in similar_memories:
                        ***REMOVED*** 计算内容相似度（简单的文本相似度作为后备）
                        similarity = self._calculate_content_similarity(memory.content, similar.content)
                        
                        if similarity >= similarity_threshold:
                            logger.debug(f"Found duplicate memory: {similar.id} (similarity: {similarity:.2f})")
                            return similar
                    
                    ***REMOVED*** 如果相似度在0.7-0.9之间，记录日志但不合并（可能需要人工判断）
                    best_match = similar_memories[0]
                    best_similarity = self._calculate_content_similarity(memory.content, best_match.content)
                    if 0.7 <= best_similarity < similarity_threshold:
                        logger.debug(f"Found similar memory (not duplicate): {best_match.id} (similarity: {best_similarity:.2f})")
        except Exception as e:
            ***REMOVED*** 去重检查失败不应该阻止存储
            logger.debug(f"Duplicate check failed (non-blocking): {e}")
        
        return None
    
    def capture_cross_system_decision(
        self,
        system: str,
        action: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        reasoning: str,
        rules_applied: Optional[List[str]] = None,
        exceptions: Optional[List[str]] = None,
        approvals: Optional[List[str]] = None,
        related_entities: Optional[List[str]] = None
    ) -> Memory:
        """
        捕获跨系统的决策上下文（Context Graph增强）
        
        这个方法专门用于捕获来自不同系统的决策痕迹，形成跨系统的决策图谱。
        
        Args:
            system: 系统名称（如 "CRM", "ERP", "VideoScript"）
            action: 执行的动作（如 "生成脚本", "审批订单"）
            inputs: 输入数据字典
            outputs: 输出结果字典
            reasoning: 决策理由（"为什么"）
            rules_applied: 应用的规则列表
            exceptions: 异常处理列表
            approvals: 审批流程列表
            related_entities: 相关实体ID列表
            
        Returns:
            创建的记忆对象
        """
        from .memory_types import Experience, Context
        
        ***REMOVED*** 构建经验内容
        content = f"{system}: {action}"
        if outputs:
            output_summary = ", ".join([f"{k}: {str(v)[:50]}" for k, v in list(outputs.items())[:3]])
            content += f" -> {output_summary}"
        
        experience = Experience(
            content=content,
            timestamp=datetime.now()
        )
        
        ***REMOVED*** 构建决策痕迹
        decision_trace = {
            "system": system,
            "action": action,
            "inputs": list(inputs.values()) if isinstance(inputs, dict) else inputs,
            "outputs": list(outputs.values()) if isinstance(outputs, dict) else outputs,
            "rules_applied": rules_applied or [],
            "exceptions": exceptions or [],
            "approvals": approvals or [],
            "timestamp": datetime.now().isoformat(),
        }
        
        ***REMOVED*** 构建上下文
        context = Context(
            metadata={
                "source": f"{system.lower()}_decision",
                "system": system,
                "action": action,
                "cross_system": True,
                "inputs": inputs,
                "outputs": outputs,
                "rules": rules_applied or [],
                "exceptions": exceptions or [],
                "approvals": approvals or [],
                "reasoning": reasoning,
            }
        )
        
        ***REMOVED*** 使用RETAIN存储
        memory = self.retain(experience, context)
        
        logger.info(f"Captured cross-system decision: {system}/{action} -> memory {memory.id}")
        return memory
    
    def search_precedents(
        self,
        inputs: Optional[List[str]] = None,
        rules: Optional[List[str]] = None,
        exceptions: Optional[List[str]] = None,
        query_text: Optional[str] = None,
        top_k: int = 10,
        min_match_score: float = 0.6
    ) -> List[Memory]:
        """
        搜索相似先例（基于决策上下文）
        
        这是Context Graph的核心功能之一，用于找到历史上类似情况下是如何决策的。
        
        Args:
            inputs: 输入数据列表
            rules: 应用的规则列表
            exceptions: 异常处理列表
            query_text: 可选的文本查询（用于向量搜索）
            top_k: 返回结果数量
            min_match_score: 最小匹配分数（0-1），默认0.6
            
        Returns:
            匹配的先例记忆列表（按匹配度排序）
        """
        logger.info(f"Searching precedents: inputs={len(inputs) if inputs else 0}, rules={len(rules) if rules else 0}, exceptions={len(exceptions) if exceptions else 0}")
        
        precedents = []
        
        try:
            ***REMOVED*** 1. 构建查询文本（用于向量搜索）
            if not query_text:
                query_parts = []
                if inputs:
                    query_parts.extend(inputs[:3])  ***REMOVED*** 最多取前3个输入
                if rules:
                    query_parts.extend([f"规则: {r}" for r in rules[:3]])
                if exceptions:
                    query_parts.extend([f"异常: {e}" for e in exceptions[:2]])
                query_text = " ".join(query_parts) if query_parts else ""
            
            if not query_text:
                logger.warning("No query text available for precedent search")
                return []
            
            ***REMOVED*** 2. 使用向量搜索找到相似记忆
            if hasattr(self.network_adapter, '_search_similar_memories'):
                similar_memories = self.network_adapter._search_similar_memories(
                    query_text,
                    top_k=top_k * 2  ***REMOVED*** 搜索更多，然后过滤
                )
            else:
                ***REMOVED*** 如果没有向量搜索，使用RECALL
                recall_results = self.recall(query_text, context=Context(), top_k=top_k * 2)
                similar_memories = [r.memory for r in recall_results[:top_k * 2]]
            
            if not similar_memories:
                logger.debug("No similar memories found for precedent search")
                return []
            
            ***REMOVED*** 3. 基于decision_trace进行精确匹配和评分
            scored_precedents = []
            for mem in similar_memories:
                score = 0.0
                match_reasons = []
                
                ***REMOVED*** 检查是否有decision_trace
                if mem.decision_trace:
                    trace = mem.decision_trace
                    
                    ***REMOVED*** 匹配规则（权重：0.4）
                    if rules:
                        trace_rules = trace.get("rules_applied", [])
                        if isinstance(trace_rules, str):
                            import json
                            try:
                                trace_rules = json.loads(trace_rules)
                            except:
                                trace_rules = [trace_rules]
                        
                        matched_rules = set(rules).intersection(set(trace_rules))
                        if matched_rules:
                            rule_score = len(matched_rules) / max(len(rules), len(trace_rules))
                            score += 0.4 * rule_score
                            match_reasons.append(f"规则匹配: {len(matched_rules)}/{len(rules)}")
                    
                    ***REMOVED*** 匹配异常（权重：0.3）
                    if exceptions:
                        trace_exceptions = trace.get("exceptions", [])
                        if isinstance(trace_exceptions, str):
                            import json
                            try:
                                trace_exceptions = json.loads(trace_exceptions)
                            except:
                                trace_exceptions = [trace_exceptions]
                        
                        matched_exceptions = set(exceptions).intersection(set(trace_exceptions))
                        if matched_exceptions:
                            exception_score = len(matched_exceptions) / max(len(exceptions), len(trace_exceptions))
                            score += 0.3 * exception_score
                            match_reasons.append(f"异常匹配: {len(matched_exceptions)}/{len(exceptions)}")
                    
                    ***REMOVED*** 匹配输入（权重：0.3）- 基于相似度
                    if inputs:
                        trace_inputs = trace.get("inputs", [])
                        if isinstance(trace_inputs, str):
                            import json
                            try:
                                trace_inputs = json.loads(trace_inputs)
                            except:
                                trace_inputs = [trace_inputs]
                        
                        ***REMOVED*** 计算输入相似度
                        input_similarity = 0.0
                        if trace_inputs:
                            ***REMOVED*** 简单的集合重叠度
                            inputs_set = set([str(i).lower() for i in inputs])
                            trace_inputs_set = set([str(i).lower() for i in trace_inputs])
                            if inputs_set or trace_inputs_set:
                                overlap = len(inputs_set.intersection(trace_inputs_set))
                                union = len(inputs_set.union(trace_inputs_set))
                                input_similarity = overlap / union if union > 0 else 0.0
                        
                        score += 0.3 * input_similarity
                        if input_similarity > 0.3:
                            match_reasons.append(f"输入相似: {input_similarity:.2f}")
                
                ***REMOVED*** 如果没有decision_trace，使用内容相似度（降级）
                else:
                    ***REMOVED*** 基于内容的简单相似度
                    content_similarity = self._calculate_content_similarity(
                        query_text,
                        mem.content
                    )
                    score = content_similarity * 0.7  ***REMOVED*** 降级权重
                    if score > 0.5:
                        match_reasons.append(f"内容相似: {content_similarity:.2f}")
                
                ***REMOVED*** 如果有reasoning，增加分数（有理由的先例更有价值）
                if mem.reasoning:
                    score += 0.1
                    match_reasons.append("包含决策理由")
                
                ***REMOVED*** 只保留达到最小匹配分数的先例
                if score >= min_match_score:
                    precedents.append({
                        "memory": mem,
                        "score": score,
                        "match_reasons": match_reasons
                    })
                    logger.debug(f"Precedent match: {mem.id[:20]}... score={score:.2f}, reasons={match_reasons}")
            
            ***REMOVED*** 4. 按分数排序
            precedents.sort(key=lambda x: x["score"], reverse=True)
            
            ***REMOVED*** 5. 返回前top_k个
            result = [p["memory"] for p in precedents[:top_k]]
            
            logger.info(f"Found {len(result)} precedents (from {len(similar_memories)} similar memories)")
            return result
            
        except Exception as e:
            logger.error(f"Error searching precedents: {e}", exc_info=True)
            return []
    
    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """
        计算两个记忆内容的相似度
        
        使用简单的文本相似度计算（Jaccard相似度或关键词重叠）
        如果向量检索可用，应该使用向量相似度
        
        Args:
            content1: 内容1
            content2: 内容2
            
        Returns:
            相似度分数（0-1）
        """
        if not content1 or not content2:
            return 0.0
        
        ***REMOVED*** 简单的关键词重叠相似度
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return 0.0
        
        ***REMOVED*** Jaccard相似度
        jaccard = len(intersection) / len(union)
        
        ***REMOVED*** 如果内容长度相似，增加相似度
        length_ratio = min(len(content1), len(content2)) / max(len(content1), len(content2)) if max(len(content1), len(content2)) > 0 else 0
        
        ***REMOVED*** 综合相似度（Jaccard权重0.7，长度相似度权重0.3）
        similarity = 0.7 * jaccard + 0.3 * length_ratio
        
        return similarity
    
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
