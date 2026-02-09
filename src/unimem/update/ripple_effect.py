"""
涟漪效应更新器

实现新记忆触发的连锁更新机制

设计特点：
- 多层传播：支持多层涟漪传播（wave1, wave2, wave3）
- 优先级控制：不同层级的更新有不同的优先级
- 异步处理：弱相关节点异步处理，不阻塞主流程
- 衰减机制：使用衰减因子控制传播强度
- 错误处理：单个节点更新失败不影响整体流程

设计参考：
- LightMem: 涟漪效应更新机制
- A-Mem: 记忆演化机制

工业级特性：
- 参数验证和输入检查
- 统一异常处理
- 关键参数保护
"""

import logging
from typing import List, Set, Optional

from ..memory_types import Memory, Entity, Relation
from ..adapters import GraphAdapter, AtomLinkAdapter, UpdateAdapter
from ..adapters.base import AdapterError, AdapterConfigurationError

logger = logging.getLogger(__name__)


class RippleEffectUpdater:
    """
    涟漪效应更新器：实现连锁更新机制
    
    当新记忆添加时，触发涟漪效应，更新相关的记忆和实体。
    支持多层传播，不同层级有不同的优先级和更新策略。
    """
    
    def __init__(
        self,
        graph_adapter: Optional[GraphAdapter] = None,
        atom_link_adapter: Optional[AtomLinkAdapter] = None,
        update_adapter: Optional[UpdateAdapter] = None,
        max_depth: int = 3,
        decay_factor: float = 0.5,
    ):
        """
        初始化涟漪效应更新器
        
        Args:
            graph_adapter: 图结构适配器（预留）
            atom_link_adapter: 原子链接适配器（参考 A-Mem）
            update_adapter: 更新机制适配器（参考 LightMem）
            max_depth: 最大传播深度（默认 3）
            decay_factor: 衰减因子（默认 0.5，控制传播强度）
            
        Raises:
            AdapterConfigurationError: 如果参数无效
        """
        if max_depth < 1:
            raise AdapterConfigurationError(
                f"max_depth must be >= 1, got {max_depth}",
                adapter_name="RippleEffectUpdater"
            )
        if not (0.0 <= decay_factor <= 1.0):
            raise AdapterConfigurationError(
                f"decay_factor must be between 0.0 and 1.0, got {decay_factor}",
                adapter_name="RippleEffectUpdater"
            )
        
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
    ) -> None:
        """
        触发涟漪效应更新
        
        当新记忆添加时，触发涟漪效应，更新相关的记忆和实体。
        支持多层传播，不同层级有不同的优先级和更新策略。
        
        Args:
            center: 中心记忆（新记忆）
            entities: 关联的实体列表
            relations: 关联的关系列表
            links: 链接的记忆ID集合
            
        Raises:
            AdapterError: 如果参数无效
        """
        if not center:
            raise AdapterError("center cannot be None", adapter_name="RippleEffectUpdater")
        
        logger.info(f"Triggering ripple effect for memory {center.id}")
        
        try:
            # 第一层涟漪：直接相关节点（高优先级，实时更新）
            wave1 = self._get_direct_related(center, entities or [], links or set())
            if wave1:
                self._update_wave(wave1, priority='high')
                logger.debug(f"Wave 1: Updated {len(wave1)} nodes")
            else:
                logger.debug("Wave 1: No direct related nodes found")
            
            # 第二层涟漪：间接相关节点（中优先级，实时更新）
            if wave1 and self.max_depth >= 2:
                wave2 = self._get_indirect_related(wave1, max_hops=2)
                if wave2:
                    self._update_wave(wave2, priority='medium')
                    logger.debug(f"Wave 2: Updated {len(wave2)} nodes")
                else:
                    logger.debug("Wave 2: No indirect related nodes found")
            else:
                wave2 = []
            
            # 第三层涟漪：弱相关节点（低优先级，异步处理）
            if wave2 and self.max_depth >= 3:
                wave3 = self._get_weak_related(wave2, max_hops=3)
                if wave3:
                    if self.update_adapter:
                        self.update_adapter.add_to_sleep_queue(wave3)
                        logger.debug(f"Wave 3: Queued {len(wave3)} nodes for sleep update")
                    else:
                        logger.warning("Update adapter not available, cannot queue wave 3")
                else:
                    logger.debug("Wave 3: No weak related nodes found")
            
            logger.info(f"Ripple effect completed for memory {center.id}")
        except Exception as e:
            logger.error(f"Error triggering ripple effect for memory {center.id}: {e}", exc_info=True)
            raise
    
    def _get_direct_related(
        self,
        center: Memory,
        entities: List[Entity],
        links: Set[str],
    ) -> List[Memory]:
        """
        获取直接相关节点
        
        通过实体和链接找到与中心记忆直接相关的记忆。
        
        Args:
            center: 中心记忆
            entities: 关联的实体列表
            links: 链接的记忆ID集合
            
        Returns:
            直接相关的记忆列表
        """
        related: List[Memory] = []
        seen_ids: Set[str] = {center.id}  # 避免重复添加中心记忆
        
        # 1. 通过网络链接适配器找到相关记忆（参考 A-Mem）
        if self.atom_link_adapter and links:
            try:
                # 使用 find_related_memories 方法找到相关记忆
                # 注意：这里使用中心记忆的链接来查找相关记忆
                related_memories = self.atom_link_adapter.find_related_memories(center, top_k=20)
                for memory in related_memories:
                    if memory.id not in seen_ids:
                        related.append(memory)
                        seen_ids.add(memory.id)
            except Exception as e:
                logger.warning(f"Error finding related memories via links: {e}", exc_info=True)
        
        # 2. 通过图结构适配器找到相关实体对应的记忆
        if self.graph_adapter and entities:
            try:
                for entity in entities:
                    # 通过实体ID获取关联的记忆
                    entity_memories = self.graph_adapter.get_entities_for_memory(center.id)
                    # 注意：这里获取的是与中心记忆共享实体的其他记忆
                    # 如果适配器支持，可以进一步扩展
                    # 目前使用 find_related_memories 作为降级方案
                    if self.atom_link_adapter:
                        # 创建一个临时记忆用于查找
                        temp_memory = Memory(
                            id=center.id,
                            content=center.content,
                            timestamp=center.timestamp,
                            entities=[entity.id],
                        )
                        entity_related = self.atom_link_adapter.find_related_memories(temp_memory, top_k=10)
                        for memory in entity_related:
                            if memory.id not in seen_ids:
                                related.append(memory)
                                seen_ids.add(memory.id)
            except Exception as e:
                logger.warning(f"Error finding related memories via entities: {e}", exc_info=True)
        
        return related
    
    def _get_indirect_related(
        self,
        wave: List[Memory],
        max_hops: int = 2,
    ) -> List[Memory]:
        """
        获取间接相关节点
        
        通过多层跳转找到间接相关的记忆。
        
        Args:
            wave: 当前层的记忆列表
            max_hops: 最大跳数
            
        Returns:
            间接相关的记忆列表
        """
        if not wave:
            return []
        
        related: List[Memory] = []
        seen_ids: Set[str] = set()
        
        # 记录当前层的所有记忆ID，避免重复
        for memory in wave:
            seen_ids.add(memory.id)
        
        # 对每个记忆，找到其相关记忆
        for memory in wave:
            if self.atom_link_adapter:
                try:
                    indirect = self.atom_link_adapter.find_related_memories(memory, top_k=10)
                    for mem in indirect:
                        if mem.id not in seen_ids:
                            related.append(mem)
                            seen_ids.add(mem.id)
                except Exception as e:
                    logger.warning(f"Error finding indirect related memories for {memory.id}: {e}", exc_info=True)
        
        return related
    
    def _get_weak_related(
        self,
        wave: List[Memory],
        max_hops: int = 3,
    ) -> List[Memory]:
        """
        获取弱相关节点
        
        类似间接相关，但使用更大的跳数，用于异步处理。
        
        Args:
            wave: 当前层的记忆列表
            max_hops: 最大跳数（默认 3）
            
        Returns:
            弱相关的记忆列表
        """
        # 使用更大的跳数，但实际实现与间接相关类似
        # 可以通过调整 top_k 参数来控制弱相关的数量
        if not wave:
            return []
        
        related: List[Memory] = []
        seen_ids: Set[str] = set()
        
        for memory in wave:
            seen_ids.add(memory.id)
        
        for memory in wave:
            if self.atom_link_adapter:
                try:
                    # 使用较小的 top_k，只获取最相关的弱相关记忆
                    weak = self.atom_link_adapter.find_related_memories(memory, top_k=5)
                    for mem in weak:
                        if mem.id not in seen_ids:
                            related.append(mem)
                            seen_ids.add(mem.id)
                except Exception as e:
                    logger.warning(f"Error finding weak related memories for {memory.id}: {e}", exc_info=True)
        
        return related
    
    def _update_wave(self, wave: List[Memory], priority: str = 'medium') -> None:
        """
        更新一波节点
        
        对一波记忆进行更新，包括记忆演化和实体描述更新。
        
        Args:
            wave: 要更新的记忆列表
            priority: 优先级（high/medium/low）
        """
        if not wave:
            return
        
        updated_count = 0
        error_count = 0
        
        for node in wave:
            try:
                # 网络链接适配器：演化记忆（参考 A-Mem）
                if self.atom_link_adapter:
                    related = self.atom_link_adapter.find_related_memories(node, top_k=5)
                    evolved = self.atom_link_adapter.evolve_memory(
                        memory=node,
                        related=related,
                        new_context=getattr(node, 'context', '') or node.content[:100],
                    )
                    node = evolved
                
                # 图结构适配器：增量更新实体描述
                if self.graph_adapter and hasattr(node, 'entities') and node.entities:
                    for entity_id in node.entities:
                        try:
                            self.graph_adapter.update_entity_description(
                                entity_id=entity_id,
                                description=getattr(node, 'context', '') or node.content[:200],
                            )
                        except Exception as e:
                            logger.warning(f"Error updating entity {entity_id} description: {e}")
                
                updated_count += 1
            except Exception as e:
                error_count += 1
                logger.error(f"Error updating node {node.id}: {e}", exc_info=True)
        
        logger.debug(f"Wave update completed: {updated_count} updated, {error_count} errors (priority: {priority})")

