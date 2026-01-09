"""
更新管理器

管理涟漪效应和睡眠更新

设计特点：
- 涟漪效应更新：新记忆触发的连锁更新机制（参考 LightMem + A-Mem）
- 睡眠更新：批量处理非关键记忆的优化（参考 LightMem）
- 统一接口：提供统一的更新接口，简化调用
- 错误处理：完善的错误处理和降级策略

工业级特性：
- 统一异常处理（使用适配器异常体系）
- 参数验证和输入检查
"""

import logging
from typing import List, Set, Optional

from ..memory_types import Memory, Entity, Relation
from ..adapters import GraphAdapter, AtomLinkAdapter, UpdateAdapter
from ..adapters.base import AdapterError, AdapterNotAvailableError
from .ripple_effect import RippleEffectUpdater

logger = logging.getLogger(__name__)


class UpdateManager:
    """
    更新管理器：管理涟漪效应和睡眠更新
    
    提供统一的更新接口，管理两种更新机制：
    - 涟漪效应更新：新记忆触发的连锁更新（实时）
    - 睡眠更新：批量处理非关键记忆的优化（异步）
    
    设计参考：
    - LightMem: 涟漪效应更新机制
    - A-Mem: 记忆演化机制
    """
    
    def __init__(
        self,
        graph_adapter: Optional[GraphAdapter] = None,
        atom_link_adapter: Optional[AtomLinkAdapter] = None,
        update_adapter: Optional[UpdateAdapter] = None,
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
    ) -> bool:
        """
        触发涟漪效应更新
        
        当新记忆添加时，触发涟漪效应更新，更新相关的记忆和实体。
        
        Args:
            center: 中心记忆（新记忆）
            entities: 关联的实体列表
            relations: 关联的关系列表
            links: 链接的记忆ID集合
            
        Returns:
            是否成功触发
            
        Raises:
            ValueError: 如果 center 为 None
        """
        if not center:
            raise AdapterError("center cannot be None", adapter_name="UpdateManager")
        
        try:
            self.ripple_updater.trigger_ripple(
                center=center,
                entities=entities or [],
                relations=relations or [],
                links=links or set(),
            )
            logger.debug(f"Ripple effect triggered for memory {center.id}")
            return True
        except Exception as e:
            logger.error(f"Error triggering ripple effect for memory {center.id}: {e}", exc_info=True)
            return False
    
    def add_to_sleep_queue(self, memories: List[Memory]) -> bool:
        """
        添加到睡眠更新队列
        
        将非关键记忆添加到睡眠更新队列，等待批量处理。
        
        Args:
            memories: 要添加的记忆列表
            
        Returns:
            是否成功添加
            
        Raises:
            ValueError: 如果 memories 为 None
        """
        if not memories:
            logger.warning("Empty memories list for sleep queue")
            return False
        
        if not self.update_adapter or not self.update_adapter.is_available():
            logger.warning("Update adapter not available, cannot add to sleep queue")
            return False
        
        try:
            self.update_adapter.add_to_sleep_queue(memories)
            logger.debug(f"Added {len(memories)} memories to sleep queue")
            return True
        except Exception as e:
            logger.error(f"Error adding memories to sleep queue: {e}", exc_info=True)
            return False
    
    def run_sleep_update(self) -> int:
        """
        执行睡眠更新
        
        批量处理睡眠更新队列中的记忆。
        
        Returns:
            处理的记忆数量
        """
        if not self.update_adapter:
            logger.warning("Update adapter not available, cannot run sleep update")
            return 0
        
        try:
            count = self.update_adapter.run_sleep_update()
            logger.info(f"Sleep update completed: {count} memories processed")
            return count
        except Exception as e:
            logger.error(f"Error running sleep update: {e}", exc_info=True)
            return 0
    
    def get_sleep_queue_size(self) -> int:
        """
        获取睡眠更新队列大小
        
        Returns:
            队列中的记忆数量
        """
        if not self.update_adapter:
            return 0
        
        try:
            if hasattr(self.update_adapter, 'get_sleep_queue_size'):
                return self.update_adapter.get_sleep_queue_size()
            return 0
        except Exception as e:
            logger.warning(f"Error getting sleep queue size: {e}")
            return 0

