"""
语义网格记忆（Semantic Mesh Memory）
仿照代码的 LSP，为创作内容建立"实体-关系图谱"

核心思想：
- 每一个章节、角色、设定、伏笔都是一个"符号（Symbol）"
- 当 Agent 修改内容时，自动识别实体并触发关联记忆
- 动态推送到相关 Agent 的上下文窗口
"""
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class EntityType(Enum):
    """实体类型"""
    CHAPTER = "chapter"  ***REMOVED*** 章节
    CHARACTER = "character"  ***REMOVED*** 角色
    SETTING = "setting"  ***REMOVED*** 设定
    PLOT_POINT = "plot_point"  ***REMOVED*** 情节节点
    FORESHADOWING = "foreshadowing"  ***REMOVED*** 伏笔
    DIALOGUE = "dialogue"  ***REMOVED*** 对话
    DESCRIPTION = "description"  ***REMOVED*** 描写
    THEME = "theme"  ***REMOVED*** 主题
    SYMBOL = "symbol"  ***REMOVED*** 符号（如"神秘吊坠"）


class RelationType(Enum):
    """关系类型"""
    MENTIONS = "mentions"  ***REMOVED*** 提及
    REFERENCES = "references"  ***REMOVED*** 引用
    CONTRADICTS = "contradicts"  ***REMOVED*** 矛盾
    DEVELOPS = "develops"  ***REMOVED*** 发展
    FORESHADOWS = "foreshadows"  ***REMOVED*** 伏笔
    BELONGS_TO = "belongs_to"  ***REMOVED*** 属于
    APPEARS_IN = "appears_in"  ***REMOVED*** 出现在
    CONFLICTS_WITH = "conflicts_with"  ***REMOVED*** 冲突


@dataclass
class Entity:
    """实体"""
    id: str
    type: EntityType
    name: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "content": self.content,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class Relation:
    """关系"""
    source_id: str
    target_id: str
    relation_type: RelationType
    strength: float = 1.0  ***REMOVED*** 关系强度（0-1）
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type.value,
            "strength": self.strength,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }


class SemanticMeshMemory:
    """
    语义网格记忆系统
    
    维护实体-关系图谱，支持动态触发关联记忆
    """
    
    def __init__(self):
        """初始化语义网格记忆"""
        self.entities: Dict[str, Entity] = {}
        self.relations: List[Relation] = []
        self.entity_index: Dict[EntityType, Set[str]] = {et: set() for et in EntityType}
    
    def add_entity(self, entity: Entity) -> None:
        """添加实体"""
        self.entities[entity.id] = entity
        self.entity_index[entity.type].add(entity.id)
        logger.debug(f"Added entity: {entity.id} ({entity.type.value})")
    
    def add_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: RelationType,
        strength: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """添加关系"""
        if source_id not in self.entities or target_id not in self.entities:
            logger.warning(f"Relation skipped: entity not found")
            return
        
        relation = Relation(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            strength=strength,
            metadata=metadata or {}
        )
        self.relations.append(relation)
        logger.debug(f"Added relation: {source_id} --{relation_type.value}--> {target_id}")
    
    def find_related_entities(
        self,
        entity_id: str,
        relation_types: Optional[List[RelationType]] = None,
        min_strength: float = 0.5
    ) -> List[Tuple[Entity, Relation]]:
        """
        查找相关实体
        
        Args:
            entity_id: 实体 ID
            relation_types: 关系类型过滤（可选）
            min_strength: 最小关系强度
        
        Returns:
            相关实体和关系的列表
        """
        if entity_id not in self.entities:
            return []
        
        related = []
        for relation in self.relations:
            if relation.strength < min_strength:
                continue
            
            if relation_types and relation.relation_type not in relation_types:
                continue
            
            target_id = None
            if relation.source_id == entity_id:
                target_id = relation.target_id
            elif relation.target_id == entity_id:
                target_id = relation.source_id
            
            if target_id and target_id in self.entities:
                related.append((self.entities[target_id], relation))
        
        ***REMOVED*** 按关系强度排序
        related.sort(key=lambda x: x[1].strength, reverse=True)
        
        return related
    
    def extract_entities_from_text(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Entity]:
        """
        从文本中提取实体（简化实现，实际应使用 NER 或 LLM）
        
        Args:
            text: 文本内容
            context: 上下文信息（如章节号、位置等）
        
        Returns:
            提取的实体列表
        """
        ***REMOVED*** 这里是一个简化实现
        ***REMOVED*** 实际应该使用 NER 模型或 LLM 来提取实体
        
        entities = []
        
        ***REMOVED*** 简单的关键词匹配（示例）
        ***REMOVED*** 实际应该使用更智能的方法
        
        return entities
    
    def trigger_related_memories(
        self,
        entity_id: str,
        max_results: int = 5
    ) -> List[Entity]:
        """
        触发关联记忆
        
        当某个实体被修改时，自动查找并返回相关实体
        
        Args:
            entity_id: 被修改的实体 ID
            max_results: 最多返回的结果数
        
        Returns:
            相关实体列表
        """
        related = self.find_related_entities(
            entity_id,
            relation_types=[
                RelationType.MENTIONS,
                RelationType.REFERENCES,
                RelationType.FORESHADOWS,
                RelationType.DEVELOPS
            ],
            min_strength=0.3
        )
        
        return [entity for entity, _ in related[:max_results]]
    
    def get_context_for_agent(
        self,
        focus_entity_id: str,
        agent_type: str = "general"
    ) -> Dict[str, Any]:
        """
        为特定 Agent 生成上下文
        
        Args:
            focus_entity_id: 焦点实体 ID
            agent_type: Agent 类型（如 "consistency_checker", "style_editor"）
        
        Returns:
            上下文字典
        """
        ***REMOVED*** 获取相关实体
        related_entities = self.trigger_related_memories(focus_entity_id)
        
        ***REMOVED*** 根据 Agent 类型过滤和格式化
        context = {
            "focus_entity": self.entities.get(focus_entity_id),
            "related_entities": related_entities,
            "agent_type": agent_type,
            "timestamp": datetime.now().isoformat()
        }
        
        return context
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于序列化）"""
        return {
            "entities": {eid: e.to_dict() for eid, e in self.entities.items()},
            "relations": [r.to_dict() for r in self.relations]
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """从字典加载（用于反序列化）"""
        ***REMOVED*** 加载实体
        for eid, edata in data.get("entities", {}).items():
            entity = Entity(
                id=edata["id"],
                type=EntityType(edata["type"]),
                name=edata["name"],
                content=edata["content"],
                metadata=edata.get("metadata", {}),
                created_at=edata.get("created_at", datetime.now().isoformat()),
                updated_at=edata.get("updated_at", datetime.now().isoformat())
            )
            self.add_entity(entity)
        
        ***REMOVED*** 加载关系
        for rdata in data.get("relations", []):
            self.add_relation(
                source_id=rdata["source_id"],
                target_id=rdata["target_id"],
                relation_type=RelationType(rdata["relation_type"]),
                strength=rdata.get("strength", 1.0),
                metadata=rdata.get("metadata", {})
            )
