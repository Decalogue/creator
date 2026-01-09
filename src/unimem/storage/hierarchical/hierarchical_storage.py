"""
分层存储实现

实现创作内容的多层级存储，支持 work/outline/chapter/scene 层级结构。

工业级特性：
- 线程安全（使用 RLock 保护共享状态）
- 统一异常处理（使用适配器异常体系）
- 性能监控（操作耗时统计）
- 数据验证（输入验证和类型检查）
"""

import logging
import threading
import time
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field

from ...memory_types import Memory
from ...adapters.base import (
    AdapterError,
    AdapterNotAvailableError,
)
from .level_index import ContentLevel, LevelIndexManager

logger = logging.getLogger(__name__)


@dataclass
class ConsistencyReport:
    """一致性检查报告"""
    level: str
    is_consistent: bool
    issues: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """数据验证"""
        if not self.level or not isinstance(self.level, str):
            raise ValueError("level must be a non-empty string")
        if not isinstance(self.is_consistent, bool):
            raise TypeError("is_consistent must be a boolean")
        if not isinstance(self.issues, list):
            raise TypeError("issues must be a list")
        if not isinstance(self.details, dict):
            raise TypeError("details must be a dict")


class HierarchicalStorage:
    """分层存储
    
    实现创作内容的多层级存储和检索，支持：
    - work: 作品级别（整部小说/剧本）
    - outline: 大纲级别（章节大纲/集数大纲）
    - chapter: 章节级别（具体章节/集数）
    - scene: 场景级别（具体场景/镜头）
    
    设计特点：
    - 层级索引：快速定位各层级记忆
    - 跨层级关联：支持父子层级关联
    - 一致性检查：检查层级间的一致性
    """
    
    def __init__(self, storage_manager: Any = None):
        """
        初始化分层存储
        
        Args:
            storage_manager: 底层存储管理器（用于实际存储操作）
            
        Raises:
            AdapterError: 如果初始化失败
        """
        self.storage_manager = storage_manager
        self.index_manager = LevelIndexManager()
        
        ***REMOVED*** 线程安全锁
        self._lock = threading.RLock()
        self._cache_lock = threading.Lock()
        
        ***REMOVED*** 层级记忆缓存（memory_id -> Memory）- 线程安全
        self._memory_cache: Dict[str, Memory] = {}
        
        ***REMOVED*** 性能统计
        self._operation_stats: Dict[str, Dict[str, float]] = {
            "store": {"count": 0, "total_time": 0.0},
            "retrieve": {"count": 0, "total_time": 0.0},
            "cross_level_retrieve": {"count": 0, "total_time": 0.0},
        }
        self._stats_lock = threading.Lock()
        
        logger.info("HierarchicalStorage initialized")
    
    def store(self, memory: Memory, level: ContentLevel) -> bool:
        """
        存储记忆到指定层级（线程安全，性能监控）
        
        Args:
            memory: 记忆对象
            level: 内容层级
            
        Returns:
            是否成功存储
            
        Raises:
            AdapterError: 如果 memory 或 level 无效
        """
        if not memory:
            raise AdapterError(
                "memory cannot be None",
                adapter_name="HierarchicalStorage"
            )
        
        if not isinstance(level, ContentLevel):
            raise AdapterError(
                f"level must be ContentLevel, got {type(level)}",
                adapter_name="HierarchicalStorage"
            )
        
        start_time = time.time()
        
        with self._lock:
            try:
                ***REMOVED*** 1. 存储到底层存储管理器
                if self.storage_manager:
                    if not self.storage_manager.add_memory(memory):
                        raise AdapterError(
                            f"Failed to store memory {memory.id} to storage_manager",
                            adapter_name="HierarchicalStorage"
                        )
                
                ***REMOVED*** 2. 添加到层级索引
                if not self.index_manager.add_memory(memory.id, level):
                    raise AdapterError(
                        f"Failed to add memory {memory.id} to {level.value} index",
                        adapter_name="HierarchicalStorage"
                    )
                
                ***REMOVED*** 3. 更新缓存（线程安全）
                with self._cache_lock:
                    self._memory_cache[memory.id] = memory
                
                ***REMOVED*** 4. 更新记忆元数据，记录层级信息
                if not memory.metadata:
                    memory.metadata = {}
                memory.metadata["content_level"] = level.value
                
                duration = time.time() - start_time
                self._record_stats("store", duration)
                
                logger.debug(f"Stored memory {memory.id} to {level.value} level (time: {duration:.3f}s)")
                return True
                
            except (AdapterError, AdapterNotAvailableError):
                duration = time.time() - start_time
                self._record_stats("store", duration)
                raise
            except Exception as e:
                duration = time.time() - start_time
                self._record_stats("store", duration)
                logger.error(f"Error storing memory {memory.id} to {level.value}: {e}", exc_info=True)
                raise AdapterError(
                    f"Failed to store memory {memory.id} to {level.value}: {e}",
                    adapter_name="HierarchicalStorage",
                    cause=e
                ) from e
    
    def retrieve(self, query: str, level: ContentLevel, top_k: int = 10) -> List[Memory]:
        """
        从指定层级检索记忆（线程安全，性能监控）
        
        Args:
            query: 查询文本
            level: 内容层级
            top_k: 返回前K个结果
            
        Returns:
            记忆列表
        """
        if not query or not query.strip():
            logger.warning("Empty query provided")
            return []
        
        if not isinstance(level, ContentLevel):
            logger.warning(f"Invalid level type: {type(level)}")
            return []
        
        if top_k <= 0:
            logger.warning(f"Invalid top_k: {top_k}, using default 10")
            top_k = 10
        
        start_time = time.time()
        
        with self._lock:
            try:
                ***REMOVED*** 1. 获取该层级的所有记忆ID
                memory_ids = self.index_manager.get_memories_at_level(level)
                
                if not memory_ids:
                    logger.debug(f"No memories found at {level.value} level")
                    return []
                
                ***REMOVED*** 2. 从缓存获取记忆对象（线程安全）
                memories = []
                with self._cache_lock:
                    for memory_id in memory_ids:
                        if memory_id in self._memory_cache:
                            memories.append(self._memory_cache[memory_id])
                
                ***REMOVED*** TODO: 如果缓存未命中，应该从存储管理器检索（需要存储管理器提供检索接口）
                ***REMOVED*** 目前简化实现，只使用缓存
                
                ***REMOVED*** 3. 简单的文本匹配（实际应该使用向量检索）
                ***REMOVED*** 这里简化实现，实际应该调用检索引擎
                matched_memories = []
                query_lower = query.lower()
                
                for memory in memories:
                    if query_lower in memory.content.lower():
                        matched_memories.append(memory)
                
                ***REMOVED*** 4. 返回Top-K
                results = matched_memories[:top_k]
                
                duration = time.time() - start_time
                self._record_stats("retrieve", duration)
                
                logger.debug(f"Retrieved {len(results)} memories from {level.value} level (time: {duration:.3f}s)")
                return results
                
            except Exception as e:
                duration = time.time() - start_time
                self._record_stats("retrieve", duration)
                logger.error(f"Error retrieving from {level.value} level: {e}", exc_info=True)
                return []
    
    def cross_level_retrieve(
        self, 
        query: str, 
        levels: List[ContentLevel]
    ) -> Dict[str, List[Memory]]:
        """
        跨层级检索（线程安全，性能监控）
        
        从多个层级同时检索，返回各层级的结果。
        
        Args:
            query: 查询文本
            levels: 要检索的层级列表
            
        Returns:
            字典，key为层级名称，value为该层级的记忆列表
        """
        if not query or not query.strip():
            logger.warning("Empty query provided")
            return {}
        
        if not levels or not isinstance(levels, list):
            logger.warning("Invalid levels list provided")
            return {}
        
        start_time = time.time()
        
        results = {}
        
        for level in levels:
            if not isinstance(level, ContentLevel):
                logger.warning(f"Invalid level type: {type(level)}, skipping")
                continue
            memories = self.retrieve(query, level, top_k=10)
            results[level.value] = memories
        
        duration = time.time() - start_time
        self._record_stats("cross_level_retrieve", duration)
        
        total_memories = sum(len(v) for v in results.values())
        logger.debug(f"Cross-level retrieval: {len(results)} levels, {total_memories} total memories (time: {duration:.3f}s)")
        return results
    
    def check_consistency(self, level: ContentLevel) -> ConsistencyReport:
        """
        检查指定层级的一致性
        
        检查内容：
        - 层级内记忆的一致性
        - 与父层级的一致性
        - 与子层级的一致性
        
        Args:
            level: 要检查的层级
            
        Returns:
            一致性检查报告
        """
        issues = []
        details = {}
        
        try:
            ***REMOVED*** 1. 获取该层级的所有记忆
            memory_ids = self.index_manager.get_memories_at_level(level)
            details["memory_count"] = len(memory_ids)
            
            ***REMOVED*** 2. 检查父层级一致性
            parent_level = self.index_manager.get_parent_level(level)
            if parent_level:
                parent_memory_ids = self.index_manager.get_memories_at_level(parent_level)
                details["parent_level"] = parent_level.value
                details["parent_memory_count"] = len(parent_memory_ids)
                
                ***REMOVED*** 简化检查：如果子层级有记忆但父层级没有，可能存在问题
                if memory_ids and not parent_memory_ids:
                    issues.append(f"Level {level.value} has memories but parent level {parent_level.value} is empty")
            
            ***REMOVED*** 3. 检查子层级一致性
            child_levels = self.index_manager.get_child_levels(level)
            if child_levels:
                child_details = {}
                for child_level in child_levels:
                    child_memory_ids = self.index_manager.get_memories_at_level(child_level)
                    child_details[child_level.value] = len(child_memory_ids)
                details["child_levels"] = child_details
            
            ***REMOVED*** 4. 简化的一致性检查（实际应该更复杂）
            is_consistent = len(issues) == 0
            
            report = ConsistencyReport(
                level=level.value,
                is_consistent=is_consistent,
                issues=issues,
                details=details
            )
            
            logger.debug(f"Consistency check for {level.value}: {'PASS' if is_consistent else 'FAIL'}")
            return report
            
        except Exception as e:
            logger.error(f"Error checking consistency for {level.value}: {e}", exc_info=True)
            return ConsistencyReport(
                level=level.value,
                is_consistent=False,
                issues=[f"Error during consistency check: {str(e)}"],
                details={}
            )
    
    def get_memory(self, memory_id: str) -> Optional[Memory]:
        """获取指定ID的记忆（线程安全）"""
        with self._cache_lock:
            return self._memory_cache.get(memory_id)
    
    def remove_memory(self, memory_id: str, level: ContentLevel) -> bool:
        """从指定层级移除记忆（线程安全）"""
        if not memory_id or not isinstance(memory_id, str):
            logger.warning(f"Invalid memory_id: {memory_id}")
            return False
        
        if not isinstance(level, ContentLevel):
            logger.warning(f"Invalid level type: {type(level)}")
            return False
        
        with self._lock:
            try:
                ***REMOVED*** 从索引中移除
                if self.index_manager.remove_memory(memory_id, level):
                    ***REMOVED*** 从缓存中移除（线程安全）
                    with self._cache_lock:
                        if memory_id in self._memory_cache:
                            del self._memory_cache[memory_id]
                    logger.debug(f"Removed memory {memory_id} from {level.value} level")
                    return True
                return False
            except Exception as e:
                logger.error(f"Error removing memory {memory_id} from {level.value}: {e}", exc_info=True)
                return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取存储统计信息（线程安全）"""
        with self._lock:
            stats = self.index_manager.get_statistics()
            with self._cache_lock:
                stats["cached_memories"] = len(self._memory_cache)
            
            ***REMOVED*** 添加操作统计
            with self._stats_lock:
                stats["operations"] = {}
                for op, op_stats in self._operation_stats.items():
                    if op_stats["count"] > 0:
                        stats["operations"][op] = {
                            "count": op_stats["count"],
                            "average_time": op_stats["total_time"] / op_stats["count"],
                        }
            
            return stats
    
    def _record_stats(self, operation: str, duration: float) -> None:
        """记录操作统计（线程安全）"""
        with self._stats_lock:
            if operation in self._operation_stats:
                self._operation_stats[operation]["count"] += 1
                self._operation_stats[operation]["total_time"] += duration
    
    def clear_cache(self) -> None:
        """清除缓存（线程安全）"""
        with self._cache_lock:
            count = len(self._memory_cache)
            self._memory_cache.clear()
            logger.info(f"Cleared {count} cached memories")

