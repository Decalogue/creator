"""
分层存储实现

实现创作内容的多层级存储，支持 work/outline/chapter/scene 层级结构。
"""

import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from ...types import Memory
from .level_index import ContentLevel, LevelIndexManager

logger = logging.getLogger(__name__)


@dataclass
class ConsistencyReport:
    """一致性检查报告"""
    level: str
    is_consistent: bool
    issues: List[str] = None
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []
        if self.details is None:
            self.details = {}


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
        """
        self.storage_manager = storage_manager
        self.index_manager = LevelIndexManager()
        
        ***REMOVED*** 层级记忆缓存（memory_id -> Memory）
        self._memory_cache: Dict[str, Memory] = {}
        
        logger.info("HierarchicalStorage initialized")
    
    def store(self, memory: Memory, level: ContentLevel) -> bool:
        """
        存储记忆到指定层级
        
        Args:
            memory: 记忆对象
            level: 内容层级
            
        Returns:
            是否成功存储
        """
        if not memory:
            logger.warning("Cannot store None memory")
            return False
        
        if not isinstance(level, ContentLevel):
            logger.warning(f"Invalid level type: {type(level)}")
            return False
        
        try:
            ***REMOVED*** 1. 存储到底层存储管理器
            if self.storage_manager:
                if not self.storage_manager.add_memory(memory):
                    logger.warning(f"Failed to store memory {memory.id} to storage_manager")
                    return False
            
            ***REMOVED*** 2. 添加到层级索引
            if not self.index_manager.add_memory(memory.id, level):
                logger.warning(f"Failed to add memory {memory.id} to {level.value} index")
                return False
            
            ***REMOVED*** 3. 更新缓存
            self._memory_cache[memory.id] = memory
            
            ***REMOVED*** 4. 更新记忆元数据，记录层级信息
            if not memory.metadata:
                memory.metadata = {}
            memory.metadata["content_level"] = level.value
            
            logger.debug(f"Stored memory {memory.id} to {level.value} level")
            return True
            
        except Exception as e:
            logger.error(f"Error storing memory {memory.id} to {level.value}: {e}", exc_info=True)
            return False
    
    def retrieve(self, query: str, level: ContentLevel, top_k: int = 10) -> List[Memory]:
        """
        从指定层级检索记忆
        
        Args:
            query: 查询文本
            level: 内容层级
            top_k: 返回前K个结果
            
        Returns:
            记忆列表
        """
        if not query:
            logger.warning("Empty query provided")
            return []
        
        if not isinstance(level, ContentLevel):
            logger.warning(f"Invalid level type: {type(level)}")
            return []
        
        try:
            ***REMOVED*** 1. 获取该层级的所有记忆ID
            memory_ids = self.index_manager.get_memories_at_level(level)
            
            if not memory_ids:
                logger.debug(f"No memories found at {level.value} level")
                return []
            
            ***REMOVED*** 2. 从缓存或存储管理器获取记忆对象
            memories = []
            for memory_id in memory_ids:
                if memory_id in self._memory_cache:
                    memories.append(self._memory_cache[memory_id])
                elif self.storage_manager:
                    ***REMOVED*** 从存储管理器获取（这里简化处理，实际应该通过检索接口）
                    ***REMOVED*** 暂时跳过，需要存储管理器提供检索接口
                    pass
            
            ***REMOVED*** 3. 简单的文本匹配（实际应该使用向量检索）
            ***REMOVED*** 这里简化实现，实际应该调用检索引擎
            matched_memories = []
            query_lower = query.lower()
            
            for memory in memories:
                if query_lower in memory.content.lower():
                    matched_memories.append(memory)
            
            ***REMOVED*** 4. 返回Top-K
            return matched_memories[:top_k]
            
        except Exception as e:
            logger.error(f"Error retrieving from {level.value} level: {e}", exc_info=True)
            return []
    
    def cross_level_retrieve(
        self, 
        query: str, 
        levels: List[ContentLevel]
    ) -> Dict[str, List[Memory]]:
        """
        跨层级检索
        
        从多个层级同时检索，返回各层级的结果。
        
        Args:
            query: 查询文本
            levels: 要检索的层级列表
            
        Returns:
            字典，key为层级名称，value为该层级的记忆列表
        """
        if not query:
            logger.warning("Empty query provided")
            return {}
        
        if not levels:
            logger.warning("Empty levels list provided")
            return {}
        
        results = {}
        
        for level in levels:
            memories = self.retrieve(query, level, top_k=10)
            results[level.value] = memories
        
        logger.debug(f"Cross-level retrieval: {len(results)} levels, {sum(len(v) for v in results.values())} total memories")
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
        """获取指定ID的记忆"""
        if memory_id in self._memory_cache:
            return self._memory_cache[memory_id]
        return None
    
    def remove_memory(self, memory_id: str, level: ContentLevel) -> bool:
        """从指定层级移除记忆"""
        try:
            ***REMOVED*** 从索引中移除
            if self.index_manager.remove_memory(memory_id, level):
                ***REMOVED*** 从缓存中移除
                if memory_id in self._memory_cache:
                    del self._memory_cache[memory_id]
                logger.debug(f"Removed memory {memory_id} from {level.value} level")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing memory {memory_id} from {level.value}: {e}", exc_info=True)
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取存储统计信息"""
        stats = self.index_manager.get_statistics()
        stats["cached_memories"] = len(self._memory_cache)
        return stats

