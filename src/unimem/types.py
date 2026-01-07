"""
UniMem 核心数据类型定义

统一的数据类型，确保各模块之间的数据一致性

工业级特性：
- 数据验证（字段验证、类型检查）
- 序列化/反序列化支持
- 默认值处理
- 类型约束
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Set, Optional, Any, Union
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """记忆类型枚举
    
    整合了 MemMachine 和 Hindsight 的记忆类型：
    - MemMachine 类型：EPISODIC, SEMANTIC, USER_PROFILE
    - Hindsight 类型：WORLD, EXPERIENCE, OBSERVATION, OPINION
    """
    ***REMOVED*** MemMachine 类型
    EPISODIC = "episodic"  ***REMOVED*** 情景记忆（事件级）
    SEMANTIC = "semantic"  ***REMOVED*** 语义记忆（概念级）
    USER_PROFILE = "user_profile"  ***REMOVED*** 用户画像记忆
    
    ***REMOVED*** Hindsight 类型（四大逻辑网络）
    WORLD = "world"  ***REMOVED*** 世界知识：客观事实（World Facts）
    EXPERIENCE = "experience"  ***REMOVED*** 个人经历：Agent 自己的经历和行为（Agent Experiences）
    OBSERVATION = "observation"  ***REMOVED*** 实体观察：对人物、事件、事物的客观总结（Synthesized Entity Summaries）
    OPINION = "opinion"  ***REMOVED*** 演变信念：Agent 的主观观点和信念，包含置信度（Evolving Beliefs）


class MemoryLayer(Enum):
    """记忆层级枚举"""
    FOA = "foa"  ***REMOVED*** Focus of Attention（工作记忆）
    DA = "da"  ***REMOVED*** Direct Access（快速访问）
    LTM = "ltm"  ***REMOVED*** Long-Term Memory（长期存储）


@dataclass
class Experience:
    """
    经验/体验数据
    
    用户输入或系统接收的原始经验信息
    """
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    context: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """数据验证"""
        if not self.content or not isinstance(self.content, str) or not self.content.strip():
            raise ValueError("Experience content cannot be empty")
        if not isinstance(self.timestamp, datetime):
            raise TypeError(f"timestamp must be datetime, got {type(self.timestamp)}")
        if self.context is not None and not isinstance(self.context, str):
            raise TypeError(f"context must be str or None, got {type(self.context)}")
        if not isinstance(self.metadata, dict):
            raise TypeError(f"metadata must be dict, got {type(self.metadata)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于序列化）"""
        return {
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Experience":
        """从字典创建（用于反序列化）"""
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif timestamp is None:
            timestamp = datetime.now()
        
        return cls(
            content=data["content"],
            timestamp=timestamp,
            context=data.get("context"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class Memory:
    """
    记忆单元
    
    统一的记忆表示，包含所有必要的元数据和链接信息
    """
    id: str
    content: str
    timestamp: datetime
    memory_type: Optional[MemoryType] = None
    layer: MemoryLayer = MemoryLayer.LTM
    
    ***REMOVED*** 语义元数据
    keywords: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    context: Optional[str] = None
    
    ***REMOVED*** 链接和关系
    links: Set[str] = field(default_factory=set)  ***REMOVED*** 链接的记忆ID
    entities: List[str] = field(default_factory=list)  ***REMOVED*** 关联的实体ID
    
    ***REMOVED*** 统计信息
    retrieval_count: int = 0
    last_accessed: Optional[datetime] = None
    
    ***REMOVED*** 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """数据验证"""
        if not self.id or not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("Memory id cannot be empty")
        if not self.content or not isinstance(self.content, str) or not self.content.strip():
            raise ValueError("Memory content cannot be empty")
        if not isinstance(self.timestamp, datetime):
            raise TypeError(f"timestamp must be datetime, got {type(self.timestamp)}")
        if self.memory_type is not None and not isinstance(self.memory_type, MemoryType):
            raise TypeError(f"memory_type must be MemoryType or None, got {type(self.memory_type)}")
        if not isinstance(self.layer, MemoryLayer):
            raise TypeError(f"layer must be MemoryLayer, got {type(self.layer)}")
        if not isinstance(self.keywords, list):
            raise TypeError(f"keywords must be list, got {type(self.keywords)}")
        if not isinstance(self.tags, list):
            raise TypeError(f"tags must be list, got {type(self.tags)}")
        if not isinstance(self.links, (set, list)):
            raise TypeError(f"links must be set, got {type(self.links)}")
        ***REMOVED*** 转换 links 为 set（如果传入的是 list）
        if isinstance(self.links, list):
            self.links = set(self.links)
        if not isinstance(self.entities, list):
            raise TypeError(f"entities must be list, got {type(self.entities)}")
        if not isinstance(self.retrieval_count, int) or self.retrieval_count < 0:
            raise ValueError(f"retrieval_count must be non-negative int, got {self.retrieval_count}")
        if not isinstance(self.metadata, dict):
            raise TypeError(f"metadata must be dict, got {type(self.metadata)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于序列化）"""
        return {
            "id": self.id,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "memory_type": self.memory_type.value if self.memory_type else None,
            "layer": self.layer.value,
            "keywords": self.keywords,
            "tags": self.tags,
            "context": self.context,
            "links": list(self.links),
            "entities": self.entities,
            "retrieval_count": self.retrieval_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Memory":
        """从字典创建（用于反序列化）"""
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        
        last_accessed = data.get("last_accessed")
        if isinstance(last_accessed, str):
            last_accessed = datetime.fromisoformat(last_accessed)
        
        memory_type = None
        if data.get("memory_type"):
            try:
                memory_type = MemoryType(data["memory_type"])
            except ValueError:
                pass
        
        layer = MemoryLayer.LTM
        if data.get("layer"):
            try:
                layer = MemoryLayer(data["layer"])
            except ValueError:
                pass
        
        return cls(
            id=data["id"],
            content=data["content"],
            timestamp=timestamp,
            memory_type=memory_type,
            layer=layer,
            keywords=data.get("keywords", []),
            tags=data.get("tags", []),
            context=data.get("context"),
            links=set(data.get("links", [])),
            entities=data.get("entities", []),
            retrieval_count=data.get("retrieval_count", 0),
            last_accessed=last_accessed,
            metadata=data.get("metadata", {}),
        )


@dataclass
class Task:
    """
    任务上下文
    
    用于 REFLECT 操作的任务信息
    """
    id: str
    description: str
    context: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """数据验证"""
        if not self.id or not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("Task id cannot be empty")
        if not self.description or not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("Task description cannot be empty")
        if not isinstance(self.context, str):
            raise TypeError(f"context must be str, got {type(self.context)}")
        if not isinstance(self.metadata, dict):
            raise TypeError(f"metadata must be dict, got {type(self.metadata)}")


@dataclass
class Context:
    """
    上下文信息
    
    用于操作时的上下文，包含会话和用户信息
    """
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """数据验证"""
        if self.session_id is not None and not isinstance(self.session_id, str):
            raise TypeError(f"session_id must be str or None, got {type(self.session_id)}")
        if self.user_id is not None and not isinstance(self.user_id, str):
            raise TypeError(f"user_id must be str or None, got {type(self.user_id)}")
        if not isinstance(self.metadata, dict):
            raise TypeError(f"metadata must be dict, got {type(self.metadata)}")


@dataclass
class RetrievalResult:
    """
    检索结果
    
    包含记忆、分数和检索方法信息
    """
    memory: Memory
    score: float
    retrieval_method: str  ***REMOVED*** 检索方法标识
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """数据验证"""
        if not isinstance(self.memory, Memory):
            raise TypeError(f"memory must be Memory, got {type(self.memory)}")
        if not isinstance(self.score, (int, float)):
            raise TypeError(f"score must be numeric, got {type(self.score)}")
        if not (0.0 <= self.score <= 1.0):
            logger.warning(f"RetrievalResult score should be between 0.0 and 1.0, got {self.score}")
        if not isinstance(self.retrieval_method, str) or not self.retrieval_method.strip():
            raise ValueError("retrieval_method cannot be empty")
        if not isinstance(self.metadata, dict):
            raise TypeError(f"metadata must be dict, got {type(self.metadata)}")


@dataclass
class Entity:
    """
    实体表示
    
    用于图结构中的实体节点（参考 LightRAG）
    """
    id: str
    name: str
    entity_type: str
    description: str
    retrieval_key: str = ""
    retrieval_value: str = ""
    neighbors: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """数据验证"""
        if not self.id or not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("Entity id cannot be empty")
        if not self.name or not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Entity name cannot be empty")
        if not isinstance(self.entity_type, str):
            raise TypeError(f"entity_type must be str, got {type(self.entity_type)}")
        if not isinstance(self.description, str):
            raise TypeError(f"description must be str, got {type(self.description)}")
        if not isinstance(self.neighbors, list):
            raise TypeError(f"neighbors must be list, got {type(self.neighbors)}")


@dataclass
class Relation:
    """
    关系表示
    
    用于图结构中的关系边（参考 LightRAG）
    """
    source: str  ***REMOVED*** 源实体ID
    target: str  ***REMOVED*** 目标实体ID
    keywords: List[str] = field(default_factory=list)
    description: str = ""
    retrieval_key: str = ""
    retrieval_value: str = ""
    
    def __post_init__(self):
        """数据验证"""
        if not self.source or not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("Relation source cannot be empty")
        if not self.target or not isinstance(self.target, str) or not self.target.strip():
            raise ValueError("Relation target cannot be empty")
        if self.source == self.target:
            logger.warning(f"Relation source and target are the same: {self.source}")
        if not isinstance(self.keywords, list):
            raise TypeError(f"keywords must be list, got {type(self.keywords)}")
        if not isinstance(self.description, str):
            raise TypeError(f"description must be str, got {type(self.description)}")
