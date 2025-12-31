"""
更新管理器

管理涟漪效应和睡眠更新
"""

from typing import List, Set
from ..types import Memory, Entity, Relation
from .ripple_effect import RippleEffectUpdater

import logging
logger = logging.getLogger(__name__)


class UpdateManager:
    """更新管理器：管理涟漪效应和睡眠更新"""
    
    def __init__(
        self,
        graph_adapter=None,
        atom_link_adapter=None,
        update_adapter=None,
    ):
        """
        初始化更新管理器
        
        Args:
            graph_adapter: 图结构适配器（参考 LightRAG）
            atom_link_adapter: 原子链接适配器（参考 A-Mem）
            update_adapter: 更新机制适配器（参考 LightMem + A-Mem）
        """
        self.graph_adapter = graph_adapter
        self.atom_link_adapter = atom_link_adapter
        self.update_adapter = update_adapter
        
        self.ripple_updater = RippleEffectUpdater(
            graph_adapter=graph_adapter,
            atom_link_adapter=atom_link_adapter,
            update_adapter=update_adapter,
        )
        
        logger.info("UpdateManager initialized")
    
    def trigger_ripple(
        self,
        center: Memory,
        entities: List[Entity],
        relations: List[Relation],
        links: Set[str],
    ):
        """触发涟漪效应更新"""
        self.ripple_updater.trigger_ripple(
            center=center,
            entities=entities,
            relations=relations,
            links=links,
        )
    
    def add_to_sleep_queue(self, memory: Memory):
        """添加到睡眠更新队列"""
        if self.update_adapter:
            self.update_adapter.add_to_sleep_queue([memory])

