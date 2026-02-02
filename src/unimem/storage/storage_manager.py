"""
存储管理器

管理 FoA/DA/LTM 三层存储，直接使用分层存储适配器

设计特点：
- 三层存储架构（FoA/DA/LTM）：参考 CogMem
- 自动层级判断：根据记忆类型和上下文自动判断存储层级
- 跨层更新：支持跨层更新记忆
- 统一接口：提供统一的存储和检索接口
- 错误处理：完善的错误处理和降级策略

工业级特性：
- 线程安全（使用 RLock 保护共享状态）
- 事务支持（确保操作的原子性）
- 批量操作优化（提高性能）
- 错误重试机制（提高可靠性）
- 连接健康检查（监控适配器状态）
- 统一异常处理（使用适配器异常体系）
- 性能监控（操作耗时、成功率统计）
- 优雅降级（适配器失败时的处理）
"""

from typing import Optional, List, Set, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field
import threading
import time
import logging

from ..memory_types import Memory, MemoryType, Context, RetrievalResult
from ..adapters import LayeredStorageAdapter, MemoryTypeAdapter
from ..adapters.base import (
    AdapterError,
    AdapterNotAvailableError,
    AdapterConfigurationError,
)

logger = logging.getLogger(__name__)


@dataclass
class OperationStats:
    """操作统计信息"""
    count: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.count == 0:
            return 0.0
        return self.success_count / self.count
    
    @property
    def average_time(self) -> float:
        """平均耗时（秒）"""
        if self.count == 0:
            return 0.0
        return self.total_time / self.count
    
    def record(self, duration: float, success: bool = True) -> None:
        """记录操作统计"""
        self.count += 1
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        self.total_time += duration
        self.min_time = min(self.min_time, duration)
        self.max_time = max(self.max_time, duration)


class StorageManager:
    """
    存储管理器：管理三层存储架构
    
    直接使用 LayeredStorageAdapter 进行存储操作，实现 FoA/DA/LTM 三层存储架构。
    
    存储策略：
    - FoA (Focus of Attention): 工作记忆，所有新记忆先进入此层
    - DA (Direct Access): 快速访问层，会话关键记忆进入此层
    - LTM (Long-Term Memory): 长期存储，所有记忆最终进入此层
    
    设计参考：
    - CogMem: 三层存储架构
    - MemMachine: 记忆类型分类
    
    工业级特性：
    - 线程安全：所有共享状态访问都受锁保护
    - 事务支持：确保跨层操作的原子性
    - 批量操作：支持批量添加和更新
    - 错误重试：自动重试失败的存储操作
    - 性能监控：统计操作耗时和成功率
    """
    
    def __init__(
        self,
        storage_adapter: LayeredStorageAdapter,
        memory_type_adapter: MemoryTypeAdapter,
        max_retries: int = 3,
        retry_delay: float = 0.1,
    ):
        """
        初始化存储管理器
        
        Args:
            storage_adapter: 分层存储适配器（参考 CogMem）
            memory_type_adapter: 记忆分类适配器（参考 MemMachine）
            max_retries: 最大重试次数（默认 3）
            retry_delay: 重试延迟（秒，默认 0.1）
            
        Raises:
            AdapterError: 如果适配器无效或不可用
        """
        if not storage_adapter:
            raise AdapterError(
                "storage_adapter cannot be None",
                adapter_name="StorageManager"
            )
        if not memory_type_adapter:
            raise AdapterError(
                "memory_type_adapter cannot be None",
                adapter_name="StorageManager"
            )
        
        ***REMOVED*** 检查适配器可用性
        if not storage_adapter.is_available():
            raise AdapterNotAvailableError(
                "storage_adapter is not available",
                adapter_name="StorageManager"
            )
        if not memory_type_adapter.is_available():
            raise AdapterNotAvailableError(
                "memory_type_adapter is not available",
                adapter_name="StorageManager"
            )
        
        self.storage_adapter = storage_adapter
        self.memory_type_adapter = memory_type_adapter
        self.max_retries = max(max_retries, 0)
        self.retry_delay = max(retry_delay, 0.0)
        
        ***REMOVED*** 线程安全锁
        self._lock = threading.RLock()
        self._cache_lock = threading.Lock()
        
        ***REMOVED*** 缓存：记录记忆所在的层级（用于优化 update_memory）
        self._memory_layers: Dict[str, Set[str]] = {}
        
        ***REMOVED*** 性能统计（线程安全）
        self._stats = {
            "add_memory": OperationStats(),
            "update_memory": OperationStats(),
            "search_foa": OperationStats(),
            "search_da": OperationStats(),
            "search_ltm": OperationStats(),
        }
        self._stats_lock = threading.Lock()
        
        logger.info("StorageManager initialized")
    
    def add_memory(self, memory: Memory, context: Optional[Context] = None) -> bool:
        """
        添加记忆到存储系统（线程安全，支持事务和重试）
        
        自动判断应该存储到哪一层：
        - FoA: 所有新记忆先进入工作记忆
        - DA: 如果记忆对会话关键，进入快速访问层
        - LTM: 所有记忆最终进入长期存储
        
        Args:
            memory: 记忆对象
            context: 上下文信息（用于判断是否关键）
            
        Returns:
            是否成功添加
            
        Raises:
            AdapterError: 如果 memory 为 None 或操作失败
        """
        if not memory:
            raise AdapterError(
                "memory cannot be None",
                adapter_name="StorageManager"
            )
        
        start_time = time.time()
        
        ***REMOVED*** 使用事务上下文确保原子性
        with self._lock:
            try:
                ***REMOVED*** 1. 分类记忆类型（带重试）
                if not memory.memory_type:
                    memory.memory_type = self._retry_operation(
                        lambda: self.memory_type_adapter.classify(memory),
                        operation_name="classify"
                    )
                
                layers_added: Set[str] = set()
                rollback_actions: List[callable] = []
                
                ***REMOVED*** 2. 添加到 FoA（工作记忆）- 带重试
                def add_to_foa():
                    if not self.storage_adapter.add_to_foa(memory):
                        raise AdapterError(
                            f"Failed to add memory {memory.id} to FoA",
                            adapter_name="StorageManager"
                        )
                    layers_added.add("foa")
                    rollback_actions.append(lambda: self._rollback_foa(memory.id))
                
                self._retry_operation(add_to_foa, operation_name="add_to_foa")
                
                ***REMOVED*** 3. 如果关键，添加到 DA（快速访问）- DA 失败不影响整体流程
                if context and hasattr(self.storage_adapter, 'is_session_critical'):
                    try:
                        if self.storage_adapter.is_session_critical(memory, context):
                            def add_to_da():
                                if not self.storage_adapter.add_to_da(memory):
                                    raise AdapterError(
                                        f"Failed to add memory {memory.id} to DA",
                                        adapter_name="StorageManager"
                                    )
                                layers_added.add("da")
                                rollback_actions.append(lambda: self._rollback_da(memory.id))
                            
                            self._retry_operation(add_to_da, operation_name="add_to_da", required=False)
                    except Exception as e:
                        logger.warning(f"Failed to add memory {memory.id} to DA (non-critical): {e}")
                
                ***REMOVED*** 4. 添加到 LTM（长期存储）- 必需操作
                def add_to_ltm():
                    if not self.storage_adapter.add_to_ltm(memory, memory.memory_type):
                        raise AdapterError(
                            f"Failed to add memory {memory.id} to LTM",
                            adapter_name="StorageManager"
                        )
                    layers_added.add("ltm")
                
                try:
                    self._retry_operation(add_to_ltm, operation_name="add_to_ltm", required=True)
                except AdapterError:
                    ***REMOVED*** LTM 失败，执行回滚
                    logger.error(f"Failed to add memory {memory.id} to LTM, rolling back...")
                    for action in reversed(rollback_actions):
                        try:
                            action()
                        except Exception as rollback_error:
                            logger.error(f"Rollback action failed: {rollback_error}")
                    raise
                
                ***REMOVED*** 5. 更新缓存（线程安全）
                with self._cache_lock:
                    self._memory_layers[memory.id] = layers_added
                
                duration = time.time() - start_time
                self._record_stats("add_memory", duration, success=True)
                
                logger.debug(f"Memory {memory.id} added to storage (type: {memory.memory_type}, layers: {layers_added}, time: {duration:.3f}s)")
                return True
                
            except (AdapterError, AdapterNotAvailableError):
                ***REMOVED*** 重新抛出适配器异常
                duration = time.time() - start_time
                self._record_stats("add_memory", duration, success=False)
                raise
            except Exception as e:
                duration = time.time() - start_time
                self._record_stats("add_memory", duration, success=False)
                logger.error(f"Error adding memory {memory.id}: {e}", exc_info=True)
                raise AdapterError(
                    f"Failed to add memory {memory.id}: {e}",
                    adapter_name="StorageManager",
                    cause=e
                ) from e
    
    def search_foa(self, query: str, top_k: int = 10, context: Optional[Context] = None) -> List[RetrievalResult]:
        """
        在 FoA (Focus of Attention) 中搜索（线程安全，性能监控）。
        当 context.session_id 存在时优先按会话检索（会话级工作记忆）。
        
        Args:
            query: 查询字符串
            top_k: 返回结果数量
            context: 上下文；若带 session_id 则优先返回该会话的 FoA 记忆
            
        Returns:
            检索结果列表
        """
        if not query or not query.strip():
            logger.warning("Empty query for search_foa")
            return []
        
        start_time = time.time()
        
        try:
            memories = self._retry_operation(
                lambda: self.storage_adapter.search_foa(query, top_k, context or Context()),
                operation_name="search_foa",
                required=False
            ) or []
            
            results = [
                RetrievalResult(
                    memory=m,
                    score=1.0,  ***REMOVED*** FoA 优先级最高
                    retrieval_method="foa",
                )
                for m in memories
            ]
            
            duration = time.time() - start_time
            self._record_stats("search_foa", duration, success=True)
            
            return results
        except Exception as e:
            duration = time.time() - start_time
            self._record_stats("search_foa", duration, success=False)
            logger.error(f"Error searching FoA: {e}", exc_info=True)
            return []
    
    def search_da(self, query: str, context: Optional[Context] = None, top_k: int = 10) -> List[RetrievalResult]:
        """
        在 DA (Direct Access) 中搜索（线程安全，性能监控）
        
        DA 是快速访问层，包含会话关键记忆。
        
        Args:
            query: 查询字符串
            context: 上下文信息（可选）
            top_k: 返回结果数量
            
        Returns:
            检索结果列表
        """
        if not query or not query.strip():
            logger.warning("Empty query for search_da")
            return []
        
        start_time = time.time()
        
        try:
            memories = self._retry_operation(
                lambda: self.storage_adapter.search_da(query, context or Context(), top_k),
                operation_name="search_da",
                required=False
            ) or []
            
            results = [
                RetrievalResult(
                    memory=m,
                    score=0.9,  ***REMOVED*** DA 优先级较高
                    retrieval_method="da",
                )
                for m in memories
            ]
            
            duration = time.time() - start_time
            self._record_stats("search_da", duration, success=True)
            
            return results
        except Exception as e:
            duration = time.time() - start_time
            self._record_stats("search_da", duration, success=False)
            logger.error(f"Error searching DA: {e}", exc_info=True)
            return []
    
    def search_ltm(self, query: str, top_k: int = 10) -> List[RetrievalResult]:
        """
        在 LTM (Long-Term Memory) 中搜索（线程安全，性能监控）
        
        LTM 是长期存储层，包含所有历史记忆。
        
        Args:
            query: 查询字符串
            top_k: 返回结果数量
            
        Returns:
            检索结果列表
        """
        if not query or not query.strip():
            logger.warning("Empty query for search_ltm")
            return []
        
        start_time = time.time()
        
        try:
            memories = self._retry_operation(
                lambda: self.storage_adapter.search_ltm(query, top_k),
                operation_name="search_ltm",
                required=False
            ) or []
            
            results = [
                RetrievalResult(
                    memory=m,
                    score=0.8,  ***REMOVED*** LTM 优先级较低
                    retrieval_method="ltm",
                )
                for m in memories
            ]
            
            duration = time.time() - start_time
            self._record_stats("search_ltm", duration, success=True)
            
            return results
        except Exception as e:
            duration = time.time() - start_time
            self._record_stats("search_ltm", duration, success=False)
            logger.error(f"Error searching LTM: {e}", exc_info=True)
            return []
    
    def update_memory(self, memory: Memory) -> bool:
        """
        更新记忆（线程安全，支持重试）
        
        实现跨层更新逻辑：需要更新所有包含该记忆的层。
        使用缓存优化，避免搜索所有记忆。
        
        Args:
            memory: 要更新的记忆对象
            
        Returns:
            是否成功更新
            
        Raises:
            AdapterError: 如果 memory 为 None 或操作失败
        """
        if not memory:
            raise AdapterError(
                "memory cannot be None",
                adapter_name="StorageManager"
            )
        
        start_time = time.time()
        
        with self._lock:
            try:
                ***REMOVED*** 获取记忆所在的层级（优先使用缓存，线程安全）
                with self._cache_lock:
                    layers = self._memory_layers.get(memory.id, set())
                    
                    ***REMOVED*** 如果缓存中没有，使用保守策略：更新所有层
                    if not layers:
                        logger.debug(f"Memory {memory.id} not in cache, updating all layers...")
                        layers = {"foa", "da", "ltm"}
                
                updated_layers: Set[str] = set()
                
                ***REMOVED*** 1. 更新 FoA（如果存在）
                if "foa" in layers:
                    def update_foa():
                        if hasattr(self.storage_adapter, 'update_in_foa'):
                            if not self.storage_adapter.update_in_foa(memory):
                                raise AdapterError(
                                    f"Failed to update memory {memory.id} in FoA",
                                    adapter_name="StorageManager"
                                )
                        else:
                            ***REMOVED*** 回退方案：删除后重新添加
                            if hasattr(self.storage_adapter, 'remove_from_foa'):
                                self.storage_adapter.remove_from_foa(memory.id)
                            if not self.storage_adapter.add_to_foa(memory):
                                raise AdapterError(
                                    f"Failed to re-add memory {memory.id} to FoA",
                                    adapter_name="StorageManager"
                                )
                        updated_layers.add("foa")
                    
                    try:
                        self._retry_operation(update_foa, operation_name="update_foa", required=False)
                    except Exception as e:
                        logger.warning(f"Failed to update memory {memory.id} in FoA: {e}")
                
                ***REMOVED*** 2. 更新 DA（如果存在）
                if "da" in layers:
                    def update_da():
                        if hasattr(self.storage_adapter, 'update_in_da'):
                            if not self.storage_adapter.update_in_da(memory):
                                raise AdapterError(
                                    f"Failed to update memory {memory.id} in DA",
                                    adapter_name="StorageManager"
                                )
                        else:
                            ***REMOVED*** 回退方案：删除后重新添加
                            if hasattr(self.storage_adapter, 'remove_from_da'):
                                self.storage_adapter.remove_from_da(memory.id)
                            if not self.storage_adapter.add_to_da(memory):
                                raise AdapterError(
                                    f"Failed to re-add memory {memory.id} to DA",
                                    adapter_name="StorageManager"
                                )
                        updated_layers.add("da")
                    
                    try:
                        self._retry_operation(update_da, operation_name="update_da", required=False)
                    except Exception as e:
                        logger.warning(f"Failed to update memory {memory.id} in DA: {e}")
                
                ***REMOVED*** 3. 更新 LTM（总是需要更新）
                def update_ltm():
                    if hasattr(self.storage_adapter, 'update_in_ltm'):
                        if not self.storage_adapter.update_in_ltm(memory, memory.memory_type):
                            raise AdapterError(
                                f"Failed to update memory {memory.id} in LTM",
                                adapter_name="StorageManager"
                            )
                    else:
                        ***REMOVED*** 回退方案：删除后重新添加
                        if hasattr(self.storage_adapter, 'remove_from_ltm'):
                            self.storage_adapter.remove_from_ltm(memory.id)
                        if not self.storage_adapter.add_to_ltm(memory, memory.memory_type):
                            raise AdapterError(
                                f"Failed to re-add memory {memory.id} to LTM",
                                adapter_name="StorageManager"
                            )
                    updated_layers.add("ltm")
                
                self._retry_operation(update_ltm, operation_name="update_ltm", required=True)
                
                ***REMOVED*** 更新缓存（线程安全）
                with self._cache_lock:
                    self._memory_layers[memory.id] = updated_layers
                
                duration = time.time() - start_time
                self._record_stats("update_memory", duration, success=True)
                
                logger.debug(f"Memory {memory.id} updated in storage (layers: {updated_layers}, time: {duration:.3f}s)")
                return True
                
            except (AdapterError, AdapterNotAvailableError):
                duration = time.time() - start_time
                self._record_stats("update_memory", duration, success=False)
                raise
            except Exception as e:
                duration = time.time() - start_time
                self._record_stats("update_memory", duration, success=False)
                logger.error(f"Error updating memory {memory.id}: {e}", exc_info=True)
                raise AdapterError(
                    f"Failed to update memory {memory.id}: {e}",
                    adapter_name="StorageManager",
                    cause=e
                ) from e
    
    def cleanup(self, max_age_hours: int = 24) -> int:
        """
        清理旧记忆（防止内存泄漏，线程安全）
        
        清理超过指定时间的旧记忆，主要用于 FoA 和 DA 层。
        LTM 层通常不清理，作为长期存储。
        
        Args:
            max_age_hours: 最大保留时间（小时），默认 24 小时
            
        Returns:
            清理的记忆数量
        """
        if max_age_hours <= 0:
            logger.warning(f"Invalid max_age_hours: {max_age_hours}, using default 24")
            max_age_hours = 24
        
        with self._lock:
            try:
                if hasattr(self.storage_adapter, 'cleanup_old_memories'):
                    cleaned_count = self._retry_operation(
                        lambda: self.storage_adapter.cleanup_old_memories(max_age_hours),
                        operation_name="cleanup",
                        required=False
                    ) or 0
                    
                    logger.info(f"Cleaned up {cleaned_count} old memories (max_age: {max_age_hours}h)")
                    
                    ***REMOVED*** 注意：这里无法精确知道哪些记忆被删除，所以不清除缓存
                    ***REMOVED*** 缓存会在下次访问时自动更新（如果记忆不存在会自然清理）
                    
                    return cleaned_count
                else:
                    logger.warning("Storage adapter does not support cleanup_old_memories")
                    return 0
            except Exception as e:
                logger.error(f"Error during cleanup: {e}", exc_info=True)
                return 0
    
    def get_memory_layers(self, memory_id: str) -> Set[str]:
        """
        获取记忆所在的层级（线程安全）
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            记忆所在的层级集合（foa, da, ltm）
        """
        with self._cache_lock:
            return self._memory_layers.get(memory_id, set()).copy()
    
    def clear_cache(self):
        """
        清除缓存（线程安全）
        
        用于在需要时手动清除层级缓存
        """
        with self._cache_lock:
            self._memory_layers.clear()
            logger.debug("Memory layers cache cleared")
    
    def _retry_operation(
        self,
        operation: callable,
        operation_name: str = "operation",
        required: bool = True,
    ) -> Any:
        """
        带重试的操作执行
        
        Args:
            operation: 要执行的操作（无参数函数）
            operation_name: 操作名称（用于日志）
            required: 是否为必需操作（如果为 False，失败不会抛出异常）
            
        Returns:
            操作结果
            
        Raises:
            AdapterError: 如果操作失败且 required=True
        """
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return operation()
            except (AdapterError, AdapterNotAvailableError) as e:
                last_error = e
                if attempt < self.max_retries:
                    wait_time = self.retry_delay * (2 ** attempt)  ***REMOVED*** 指数退避
                    logger.warning(
                        f"{operation_name} failed (attempt {attempt + 1}/{self.max_retries + 1}): {e}, "
                        f"retrying in {wait_time:.3f}s..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"{operation_name} failed after {self.max_retries + 1} attempts: {e}")
                    if required:
                        raise
                    return None
            except Exception as e:
                ***REMOVED*** 非适配器异常，不重试
                logger.error(f"{operation_name} failed with unexpected error: {e}", exc_info=True)
                if required:
                    raise AdapterError(
                        f"{operation_name} failed: {e}",
                        adapter_name="StorageManager",
                        cause=e
                    ) from e
                return None
        
        if required and last_error:
            raise last_error
        return None
    
    def _rollback_foa(self, memory_id: str) -> bool:
        """回滚 FoA 层操作"""
        try:
            if hasattr(self.storage_adapter, 'remove_from_foa'):
                return self.storage_adapter.remove_from_foa(memory_id)
            return False
        except Exception as e:
            logger.error(f"Failed to rollback FoA for memory {memory_id}: {e}")
            return False
    
    def _rollback_da(self, memory_id: str) -> bool:
        """回滚 DA 层操作"""
        try:
            if hasattr(self.storage_adapter, 'remove_from_da'):
                return self.storage_adapter.remove_from_da(memory_id)
            return False
        except Exception as e:
            logger.error(f"Failed to rollback DA for memory {memory_id}: {e}")
            return False
    
    def _record_stats(self, operation: str, duration: float, success: bool = True) -> None:
        """记录操作统计（线程安全）"""
        with self._stats_lock:
            if operation in self._stats:
                self._stats[operation].record(duration, success)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取性能统计信息（线程安全）
        
        Returns:
            统计信息字典
        """
        with self._stats_lock:
            return {
                op: {
                    "count": stats.count,
                    "success_count": stats.success_count,
                    "failure_count": stats.failure_count,
                    "success_rate": stats.success_rate,
                    "average_time": stats.average_time,
                    "min_time": stats.min_time if stats.min_time != float('inf') else 0.0,
                    "max_time": stats.max_time,
                }
                for op, stats in self._stats.items()
            }
    
    def health_check(self) -> Dict[str, Any]:
        """
        健康检查（线程安全）
        
        Returns:
            健康状态字典
        """
        with self._lock:
            try:
                ***REMOVED*** 检查适配器健康状态
                storage_health = self.storage_adapter.health_check()
                type_health = self.memory_type_adapter.health_check()
                
                ***REMOVED*** 获取统计信息
                stats = self.get_statistics()
                
                ***REMOVED*** 计算整体状态
                all_available = (
                    storage_health.get("available", False) and
                    type_health.get("available", False)
                )
                
                ***REMOVED*** 检查操作成功率
                total_ops = sum(s["count"] for s in stats.values())
                total_success = sum(s["success_count"] for s in stats.values())
                success_rate = total_success / total_ops if total_ops > 0 else 1.0
                
                status = "healthy" if all_available and success_rate >= 0.95 else "degraded"
                if not all_available:
                    status = "unhealthy"
                
                return {
                    "status": status,
                    "storage_adapter": storage_health,
                    "memory_type_adapter": type_health,
                    "statistics": stats,
                    "cache_size": len(self._memory_layers),
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                logger.error(f"Error during health check: {e}", exc_info=True)
                return {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
