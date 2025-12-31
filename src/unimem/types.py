"""
UniMem 核心数据类型定义

统一的数据类型，确保各模块之间的数据一致性
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Set, Optional, Any
from enum import Enum


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


@dataclass
class Context:
    """
    上下文信息
    
    用于操作时的上下文，包含会话和用户信息
    """
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


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
