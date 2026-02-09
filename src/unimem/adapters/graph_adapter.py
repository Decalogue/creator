"""
图结构适配器

实现 UniMem 的实体-关系建模和图结构管理接口。
当前为占位实现，所有操作返回空/False，后续在 unimem 内自实现图结构。
"""

import logging
from typing import List, Tuple

from .base import BaseAdapter
from ..memory_types import Entity, Relation, Memory

logger = logging.getLogger(__name__)


class GraphAdapter(BaseAdapter):
    """
    图结构适配器（占位实现）

    提供实体-关系建模和图结构管理接口。
    当前未接入外部服务，所有方法返回空/False，供 unimem 内部架构预留。
    """

    def _do_initialize(self) -> None:
        """初始化：占位实现，不连接任何外部服务。"""
        logger.info(
            "GraphAdapter: placeholder implementation (no graph backend). "
            "Entity/relation extraction and retrieval return empty."
        )
        self._available = False

    def extract_entities_relations(self, text: str) -> Tuple[List[Entity], List[Relation]]:
        """从文本中提取实体和关系。占位：返回空元组。"""
        return [], []

    def add_entities(self, entities: List[Entity]) -> bool:
        """添加实体到图结构。占位：返回 False。"""
        return not entities  # 空列表视为成功

    def add_relations(self, relations: List[Relation]) -> bool:
        """添加关系到图结构。占位：返回 False。"""
        return not relations

    def entity_retrieval(self, query: str, top_k: int = 10) -> List[Memory]:
        """实体级检索。占位：返回空列表。"""
        return []

    def abstract_retrieval(self, query: str, top_k: int = 10) -> List[Memory]:
        """抽象概念检索。占位：返回空列表。"""
        return []

    def get_entities_for_memory(self, memory_id: str) -> List[Entity]:
        """获取记忆关联的实体。占位：返回空列表。"""
        return []

    def update_entity_description(self, entity_id: str, description: str) -> bool:
        """更新实体描述。占位：返回 False。"""
        return False
