"""
跨层级检索

实现跨层级的智能检索，支持从多个层级同时检索并融合结果。
"""

import logging
from typing import List, Dict, Optional
from collections import defaultdict

from ...memory_types import Memory
from .level_index import ContentLevel
from .hierarchical_storage import HierarchicalStorage

logger = logging.getLogger(__name__)


class CrossLevelRetrieval:
    """跨层级检索器
    
    支持从多个层级同时检索，并提供智能融合策略：
    - 层级权重：不同层级可以设置不同权重
    - 相关性排序：根据查询相关性排序
    - 去重：去除重复的记忆
    """
    
    def __init__(self, hierarchical_storage: HierarchicalStorage):
        """
        初始化跨层级检索器
        
        Args:
            hierarchical_storage: 分层存储实例
        """
        self.storage = hierarchical_storage
        
        # 默认层级权重（可以根据需求调整）
        self.level_weights = {
            ContentLevel.WORK: 1.0,
            ContentLevel.OUTLINE: 0.8,
            ContentLevel.CHAPTER: 0.6,
            ContentLevel.SCENE: 0.4,
        }
        
        logger.info("CrossLevelRetrieval initialized")
    
    def retrieve(
        self,
        query: str,
        levels: Optional[List[ContentLevel]] = None,
        top_k: int = 10,
        level_weights: Optional[Dict[ContentLevel, float]] = None
    ) -> List[Memory]:
        """
        跨层级检索并融合结果
        
        Args:
            query: 查询文本
            levels: 要检索的层级列表，如果为None则检索所有层级
            top_k: 返回前K个结果
            level_weights: 层级权重字典，如果为None则使用默认权重
            
        Returns:
            融合后的记忆列表，按相关性排序
        """
        if not query:
            logger.warning("Empty query provided")
            return []
        
        # 使用默认层级或指定层级
        if levels is None:
            levels = list(ContentLevel)
        
        # 使用默认权重或指定权重
        weights = level_weights if level_weights else self.level_weights
        
        try:
            # 1. 从各层级检索
            all_results = []
            for level in levels:
                memories = self.storage.retrieve(query, level, top_k=top_k * 2)
                weight = weights.get(level, 0.5)
                
                # 为每个记忆添加层级权重
                for memory in memories:
                    # 在元数据中记录权重
                    if not memory.metadata:
                        memory.metadata = {}
                    memory.metadata["_retrieval_weight"] = weight
                    memory.metadata["_retrieval_level"] = level.value
                    all_results.append((memory, weight))
            
            # 2. 去重（基于记忆ID）
            seen_ids = set()
            unique_results = []
            for memory, weight in all_results:
                if memory.id not in seen_ids:
                    seen_ids.add(memory.id)
                    unique_results.append((memory, weight))
            
            # 3. 按权重和相关性排序（简化：仅按权重）
            # 实际应该结合向量相似度等
            unique_results.sort(key=lambda x: x[1], reverse=True)
            
            # 4. 返回Top-K
            result_memories = [mem for mem, _ in unique_results[:top_k]]
            
            logger.debug(f"Cross-level retrieval: {len(result_memories)} memories from {len(levels)} levels")
            return result_memories
            
        except Exception as e:
            logger.error(f"Error in cross-level retrieval: {e}", exc_info=True)
            return []
    
    def retrieve_by_hierarchy(
        self,
        query: str,
        start_level: ContentLevel,
        include_children: bool = True,
        include_parent: bool = True,
        top_k: int = 10
    ) -> Dict[str, List[Memory]]:
        """
        按层级关系检索
        
        从指定层级开始，检索其父层级和/或子层级。
        
        Args:
            query: 查询文本
            start_level: 起始层级
            include_children: 是否包含子层级
            include_parent: 是否包含父层级
            top_k: 每个层级返回的前K个结果
            
        Returns:
            字典，key为层级名称，value为该层级的记忆列表
        """
        levels_to_search = [start_level]
        
        # 添加父层级
        if include_parent:
            parent_level = self.storage.index_manager.get_parent_level(start_level)
            if parent_level:
                levels_to_search.append(parent_level)
        
        # 添加子层级
        if include_children:
            child_levels = self.storage.index_manager.get_child_levels(start_level)
            levels_to_search.extend(child_levels)
        
        # 执行跨层级检索
        results = {}
        for level in levels_to_search:
            memories = self.storage.retrieve(query, level, top_k=top_k)
            results[level.value] = memories
        
        logger.debug(f"Hierarchy retrieval from {start_level.value}: {len(results)} levels")
        return results
    
    def set_level_weights(self, weights: Dict[ContentLevel, float]) -> None:
        """设置层级权重"""
        self.level_weights.update(weights)
        logger.debug(f"Updated level weights: {weights}")

