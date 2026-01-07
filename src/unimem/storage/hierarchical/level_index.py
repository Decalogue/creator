"""
层级索引

为不同层级的记忆建立索引，支持快速检索和跨层级查询。
"""

import logging
from typing import Dict, List, Set, Optional, Any
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

from ...types import Memory

logger = logging.getLogger(__name__)


class ContentLevel(Enum):
    """内容层级枚举
    
    用于小说和剧本创作的多层级结构：
    - WORK: 作品级别（整部小说/剧本）
    - OUTLINE: 大纲级别（章节大纲/集数大纲）
    - CHAPTER: 章节级别（具体章节/集数）
    - SCENE: 场景级别（具体场景/镜头）
    """
    WORK = "work"
    OUTLINE = "outline"
    CHAPTER = "chapter"
    SCENE = "scene"


@dataclass
class LevelIndex:
    """层级索引
    
    为每个层级建立索引，支持：
    - 快速检索同层级记忆
    - 跨层级关联查询
    - 层级一致性检查
    """
    
    level: ContentLevel
    memory_ids: Set[str] = field(default_factory=set)
    parent_level: Optional[ContentLevel] = None
    child_levels: List[ContentLevel] = field(default_factory=list)
    
    ***REMOVED*** 层级元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_updated: Optional[datetime] = None
    
    def __post_init__(self):
        """初始化层级关系"""
        if self.level == ContentLevel.WORK:
            self.parent_level = None
            self.child_levels = [ContentLevel.OUTLINE]
        elif self.level == ContentLevel.OUTLINE:
            self.parent_level = ContentLevel.WORK
            self.child_levels = [ContentLevel.CHAPTER]
        elif self.level == ContentLevel.CHAPTER:
            self.parent_level = ContentLevel.OUTLINE
            self.child_levels = [ContentLevel.SCENE]
        elif self.level == ContentLevel.SCENE:
            self.parent_level = ContentLevel.CHAPTER
            self.child_levels = []
    
    def add_memory(self, memory_id: str) -> bool:
        """添加记忆到索引"""
        if not memory_id:
            logger.warning("Cannot add empty memory_id to index")
            return False
        
        self.memory_ids.add(memory_id)
        self.last_updated = datetime.now()
        logger.debug(f"Added memory {memory_id} to {self.level.value} index")
        return True
    
    def remove_memory(self, memory_id: str) -> bool:
        """从索引中移除记忆"""
        if memory_id in self.memory_ids:
            self.memory_ids.remove(memory_id)
            self.last_updated = datetime.now()
            logger.debug(f"Removed memory {memory_id} from {self.level.value} index")
            return True
        return False
    
    def has_memory(self, memory_id: str) -> bool:
        """检查记忆是否在索引中"""
        return memory_id in self.memory_ids
    
    def get_memory_count(self) -> int:
        """获取索引中的记忆数量"""
        return len(self.memory_ids)
    
    def clear(self) -> None:
        """清空索引"""
        self.memory_ids.clear()
        self.last_updated = datetime.now()
        logger.debug(f"Cleared {self.level.value} index")


class LevelIndexManager:
    """层级索引管理器
    
    管理所有层级的索引，提供统一的索引操作接口。
    """
    
    def __init__(self):
        """初始化索引管理器"""
        self._indices: Dict[ContentLevel, LevelIndex] = {}
        
        ***REMOVED*** 初始化所有层级索引
        for level in ContentLevel:
            self._indices[level] = LevelIndex(level=level)
        
        logger.info("LevelIndexManager initialized")
    
    def get_index(self, level: ContentLevel) -> LevelIndex:
        """获取指定层级的索引"""
        return self._indices.get(level)
    
    def add_memory(self, memory_id: str, level: ContentLevel) -> bool:
        """添加记忆到指定层级索引"""
        index = self._indices.get(level)
        if not index:
            logger.error(f"Index for level {level.value} not found")
            return False
        return index.add_memory(memory_id)
    
    def remove_memory(self, memory_id: str, level: ContentLevel) -> bool:
        """从指定层级索引中移除记忆"""
        index = self._indices.get(level)
        if not index:
            return False
        return index.remove_memory(memory_id)
    
    def get_memories_at_level(self, level: ContentLevel) -> Set[str]:
        """获取指定层级的所有记忆ID"""
        index = self._indices.get(level)
        if not index:
            return set()
        return index.memory_ids.copy()
    
    def get_parent_level(self, level: ContentLevel) -> Optional[ContentLevel]:
        """获取父层级"""
        index = self._indices.get(level)
        if not index:
            return None
        return index.parent_level
    
    def get_child_levels(self, level: ContentLevel) -> List[ContentLevel]:
        """获取子层级列表"""
        index = self._indices.get(level)
        if not index:
            return []
        return index.child_levels.copy()
    
    def get_statistics(self) -> Dict[str, int]:
        """获取各层级的统计信息"""
        stats = {}
        for level, index in self._indices.items():
            stats[level.value] = index.get_memory_count()
        return stats

