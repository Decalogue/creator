"""
网络管理器

管理图结构和原子笔记网络，直接使用适配器
"""

from typing import List, Set, Optional
from ..types import Entity, Relation, Memory
from ..adapters import GraphAdapter, NetworkLinkAdapter

import logging
logger = logging.getLogger(__name__)


class NetworkManager:
    """
    网络管理器：管理图结构和原子笔记网络
    
    直接使用 GraphAdapter 和 NetworkLinkAdapter 进行操作
    """
    
    def __init__(
        self,
        graph_adapter: GraphAdapter,
        network_link_adapter: NetworkLinkAdapter,
    ):
        """
        初始化网络管理器
        
        Args:
            graph_adapter: 图结构适配器（参考 LightRAG）
            network_link_adapter: 网络链接适配器（参考 A-Mem）
        """
        self.graph_adapter = graph_adapter
        self.network_link_adapter = network_link_adapter
        
        logger.info("NetworkManager initialized")
    
    def extract_entities_relations(self, text: str) -> tuple[List[Entity], List[Relation]]:
        """
        从文本中提取实体和关系
        
        使用图结构适配器进行提取
        """
        return self.graph_adapter.extract_entities_relations(text)
    
    def add_entities(self, entities: List[Entity]) -> bool:
        """添加实体到图结构"""
        return self.graph_adapter.add_entities(entities)
    
    def add_relations(self, relations: List[Relation]) -> bool:
        """添加关系到图结构"""
        return self.graph_adapter.add_relations(relations)
    
    def construct_atomic_note(
        self,
        content: str,
        timestamp,
        entities: List[Entity],
    ) -> Memory:
        """
        构建原子笔记
        
        使用网络链接适配器构建
        """
        memory = self.network_link_adapter.construct_atomic_note(
            content=content,
            timestamp=timestamp,
            entities=entities,
        )
        
        ***REMOVED*** 将记忆添加到向量存储
        if hasattr(self.network_link_adapter, 'add_memory_to_vector_store'):
            self.network_link_adapter.add_memory_to_vector_store(memory)
        
        return memory
    
    def generate_links(self, memory: Memory, top_k: int = 10) -> Set[str]:
        """
        生成记忆链接
        
        使用网络链接适配器生成动态链接
        """
        return self.network_link_adapter.generate_links(memory, top_k=top_k)
    
    def find_related_memories(self, memory: Memory, top_k: int = 10) -> List[Memory]:
        """
        查找相关记忆
        
        使用网络链接适配器通过链接网络查找
        """
        return self.network_link_adapter.find_related_memories(memory, top_k=top_k)
    
    def evolve_memory(
        self,
        memory: Memory,
        related: List[Memory],
        new_context: str,
    ) -> Memory:
        """
        演化记忆
        
        使用网络链接适配器进行记忆演化
        """
        return self.network_link_adapter.evolve_memory(
            memory=memory,
            related=related,
            new_context=new_context,
        )
    
    def update_graph_from_memory(self, memory: Memory) -> bool:
        """
        根据记忆更新图结构
        
        例如：更新实体描述等
        """
        entities = self.graph_adapter.get_entities_for_memory(memory.id)
        for entity in entities:
            self.graph_adapter.update_entity_description(
                entity_id=entity.id,
                description=memory.context or "",
            )
        return True
