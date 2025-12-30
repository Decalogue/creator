"""
涟漪效应更新器

实现新记忆触发的连锁更新机制
"""

from typing import List, Set
from ..types import Memory, Entity, Relation

import logging
logger = logging.getLogger(__name__)


class RippleEffectUpdater:
    """涟漪效应更新器：实现连锁更新机制"""
    
    def __init__(
        self,
        graph_adapter=None,
        atom_link_adapter=None,
        update_adapter=None,
        max_depth: int = 3,
        decay_factor: float = 0.5,
    ):
        """
        初始化涟漪效应更新器
        
        Args:
            graph_adapter: 图结构适配器（参考 LightRAG）
            atom_link_adapter: 原子链接适配器（参考 A-Mem）
            update_adapter: 更新机制适配器（参考 LightMem）
            max_depth: 最大传播深度
            decay_factor: 衰减因子
        """
        self.graph_adapter = graph_adapter
        self.atom_link_adapter = atom_link_adapter
        self.update_adapter = update_adapter
        self.max_depth = max_depth
        self.decay_factor = decay_factor
        
        logger.info(f"RippleEffectUpdater initialized (max_depth={max_depth}, decay_factor={decay_factor})")
    
    def trigger_ripple(
        self,
        center: Memory,
        entities: List[Entity],
        relations: List[Relation],
        links: Set[str],
    ):
        """
        触发涟漪效应更新
        
        Args:
            center: 中心记忆（新记忆）
            entities: 关联的实体
            relations: 关联的关系
            links: 链接的记忆ID
        """
        logger.info(f"Triggering ripple effect for memory {center.id}")
        
        ***REMOVED*** 第一层涟漪：直接相关节点
        wave1 = self._get_direct_related(center, entities, links)
        self._update_wave(wave1, priority='high')
        logger.debug(f"Wave 1: Updated {len(wave1)} nodes")
        
        ***REMOVED*** 第二层涟漪：间接相关节点
        wave2 = self._get_indirect_related(wave1, max_hops=2)
        self._update_wave(wave2, priority='medium')
        logger.debug(f"Wave 2: Updated {len(wave2)} nodes")
        
        ***REMOVED*** 第三层涟漪：弱相关节点（异步处理）
        wave3 = self._get_weak_related(wave2, max_hops=3)
        if self.update_adapter:
            self.update_adapter.add_to_sleep_queue(wave3)
        logger.debug(f"Wave 3: Queued {len(wave3)} nodes for sleep update")
    
    def _get_direct_related(
        self,
        center: Memory,
        entities: List[Entity],
        links: Set[str],
    ) -> List[Memory]:
        """获取直接相关节点"""
        related = []
        
        ***REMOVED*** 通过图结构适配器找到相关实体
        if self.graph_adapter:
            for entity in entities:
                ***REMOVED*** TODO: 实现获取实体邻居的方法
                ***REMOVED*** 目前通过 get_entities_for_memory 间接获取
                ***REMOVED*** neighbors = self.graph_adapter.get_neighbors(entity.id)
                pass
        
        ***REMOVED*** 通过网络链接适配器找到相关记忆（参考 A-Mem）
        if self.atom_link_adapter:
            for link_id in links:
                ***REMOVED*** TODO: 实现从链接ID获取记忆的方法
                ***REMOVED*** linked_memory = self.atom_link_adapter.get_memory(link_id)
                pass
        
        return list(set(related))
    
    def _get_indirect_related(
        self,
        wave: List[Memory],
        max_hops: int = 2,
    ) -> List[Memory]:
        """获取间接相关节点"""
        related = []
        
        for memory in wave:
            ***REMOVED*** 通过网络链接适配器找到间接相关节点（参考 A-Mem）
            if self.atom_link_adapter:
                indirect = self.atom_link_adapter.find_related_memories(memory)
                related.extend(indirect)
        
        return list(set(related))
    
    def _get_weak_related(
        self,
        wave: List[Memory],
        max_hops: int = 3,
    ) -> List[Memory]:
        """获取弱相关节点"""
        ***REMOVED*** 类似间接相关，但使用更大的跳数
        return self._get_indirect_related(wave, max_hops=max_hops)
    
    def _update_wave(self, wave: List[Memory], priority: str = 'medium'):
        """更新一波节点"""
        for node in wave:
            try:
                ***REMOVED*** 网络链接适配器：演化记忆（参考 A-Mem）
                if self.atom_link_adapter:
                    related = self.atom_link_adapter.find_related_memories(node)
                    evolved = self.atom_link_adapter.evolve_memory(
                        memory=node,
                        related=related,
                        new_context=getattr(node, 'context', ''),
                    )
                    node = evolved
                
                ***REMOVED*** 图结构适配器：增量更新实体描述（参考 LightRAG）
                if self.graph_adapter and hasattr(node, 'entities'):
                    for entity_id in node.entities:
                        self.graph_adapter.update_entity_description(
                            entity_id=entity_id,
                            description=getattr(node, 'context', ''),
                        )
            except Exception as e:
                logger.error(f"Error updating node {node.id}: {e}")

