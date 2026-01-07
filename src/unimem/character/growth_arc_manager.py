"""
人物成长线管理器

基于"换壳理论"：人物成长线是故事的"骨头"，是所有题材的引擎。
管理人物成长线的创建、检索、更新和跨题材适配。
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from ..types import Memory, MemoryType

logger = logging.getLogger(__name__)


class GrowthArcStage(Enum):
    """成长线阶段"""
    EARLY = "early"      ***REMOVED*** 前期状态
    MID = "mid"          ***REMOVED*** 中期冲突
    LATE = "late"        ***REMOVED*** 后期结果


@dataclass
class GrowthArc:
    """人物成长线（三句话骨架）
    
    基于"换壳理论"的核心结构：
    - 前期状态：人物的初始状态
    - 中期冲突：人物遇到的冲突和挑战
    - 后期结果：人物的最终状态
    """
    character_id: str
    character_name: str
    
    ***REMOVED*** 三句话骨架
    early_state: str      ***REMOVED*** 前期状态
    mid_conflict: str     ***REMOVED*** 中期冲突
    late_outcome: str     ***REMOVED*** 后期结果
    
    ***REMOVED*** 元数据
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_three_sentences(self) -> str:
        """转换为三句话描述"""
        return f"{self.early_state}\n{self.mid_conflict}\n{self.late_outcome}"
    
    def to_memory(self) -> Memory:
        """转换为 Memory 对象（核心记忆）"""
        content = f"人物成长线：{self.character_name}\n{self.to_three_sentences()}"
        
        return Memory(
            id=f"growth_arc_{self.character_id}",
            content=content,
            timestamp=self.created_at,
            memory_type=MemoryType.EXPERIENCE,  ***REMOVED*** 人物经历
            keywords=["成长线", "人物", self.character_name],
            tags=["growth_arc", "core"],
            context=f"人物成长线：{self.character_name}",
            metadata={
                "character_id": self.character_id,
                "character_name": self.character_name,
                "early_state": self.early_state,
                "mid_conflict": self.mid_conflict,
                "late_outcome": self.late_outcome,
                "is_core": True,  ***REMOVED*** 标记为核心记忆
                **self.metadata
            }
        )


class CharacterGrowthArcManager:
    """人物成长线管理器
    
    基于"换壳理论"：
    - 人物成长线是故事的"骨头"，是所有题材的引擎
    - 支持成长线的创建、检索、更新
    - 支持成长线的跨题材适配
    """
    
    def __init__(self, storage_manager: Any = None):
        """
        初始化成长线管理器
        
        Args:
            storage_manager: 存储管理器（用于持久化）
        """
        self.storage_manager = storage_manager
        
        ***REMOVED*** 成长线缓存（character_id -> GrowthArc）
        self._growth_arcs: Dict[str, GrowthArc] = {}
        
        logger.info("CharacterGrowthArcManager initialized")
    
    def create_growth_arc(
        self,
        character_id: str,
        character_name: str,
        early_state: str,
        mid_conflict: str,
        late_outcome: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> GrowthArc:
        """
        创建人物成长线（三句话骨架）
        
        基于"换壳理论"的核心方法：
        - 前期状态：人物的初始状态
        - 中期冲突：人物遇到的冲突和挑战
        - 后期结果：人物的最终状态
        
        Args:
            character_id: 人物ID
            character_name: 人物名称
            early_state: 前期状态
            mid_conflict: 中期冲突
            late_outcome: 后期结果
            metadata: 扩展元数据
            
        Returns:
            成长线对象
        """
        if not character_id or not character_name:
            raise ValueError("character_id and character_name cannot be empty")
        
        if not early_state or not mid_conflict or not late_outcome:
            raise ValueError("early_state, mid_conflict, and late_outcome cannot be empty")
        
        growth_arc = GrowthArc(
            character_id=character_id,
            character_name=character_name,
            early_state=early_state,
            mid_conflict=mid_conflict,
            late_outcome=late_outcome,
            metadata=metadata or {}
        )
        
        ***REMOVED*** 缓存
        self._growth_arcs[character_id] = growth_arc
        
        ***REMOVED*** 存储到存储管理器（作为核心记忆）
        if self.storage_manager:
            try:
                memory = growth_arc.to_memory()
                ***REMOVED*** 标记为核心记忆，存储到 LTM
                if hasattr(self.storage_manager, 'storage_adapter'):
                    ***REMOVED*** 使用分层存储存储核心记忆
                    if hasattr(self.storage_manager, 'hierarchical_storage'):
                        from ..storage.hierarchical.hierarchical_storage import ContentLevel
                        self.storage_manager.hierarchical_storage.store_core(
                            memory, 
                            ContentLevel.WORK
                        )
                    else:
                        self.storage_manager.add_memory(memory)
                else:
                    self.storage_manager.add_memory(memory)
            except Exception as e:
                logger.warning(f"Failed to store growth arc to storage: {e}")
        
        logger.info(f"Created growth arc for character {character_name} ({character_id})")
        return growth_arc
    
    def get_growth_arc(self, character_id: str) -> Optional[GrowthArc]:
        """
        获取人物成长线
        
        Args:
            character_id: 人物ID
            
        Returns:
            成长线对象，如果不存在则返回 None
        """
        ***REMOVED*** 先从缓存获取
        if character_id in self._growth_arcs:
            return self._growth_arcs[character_id]
        
        ***REMOVED*** 从存储管理器检索
        if self.storage_manager:
            try:
                memory_id = f"growth_arc_{character_id}"
                ***REMOVED*** 这里简化处理，实际应该通过检索接口获取
                ***REMOVED*** 暂时返回 None，需要存储管理器提供检索接口
                pass
            except Exception as e:
                logger.warning(f"Failed to retrieve growth arc from storage: {e}")
        
        return None
    
    def update_growth_arc(
        self,
        character_id: str,
        early_state: Optional[str] = None,
        mid_conflict: Optional[str] = None,
        late_outcome: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        更新人物成长线
        
        Args:
            character_id: 人物ID
            early_state: 前期状态（可选）
            mid_conflict: 中期冲突（可选）
            late_outcome: 后期结果（可选）
            metadata: 扩展元数据（可选）
            
        Returns:
            是否成功更新
        """
        growth_arc = self.get_growth_arc(character_id)
        if not growth_arc:
            logger.warning(f"Growth arc not found for character {character_id}")
            return False
        
        ***REMOVED*** 更新字段
        if early_state:
            growth_arc.early_state = early_state
        if mid_conflict:
            growth_arc.mid_conflict = mid_conflict
        if late_outcome:
            growth_arc.late_outcome = late_outcome
        if metadata:
            growth_arc.metadata.update(metadata)
        
        growth_arc.updated_at = datetime.now()
        
        ***REMOVED*** 更新存储
        if self.storage_manager:
            try:
                memory = growth_arc.to_memory()
                if hasattr(self.storage_manager, 'update_memory'):
                    self.storage_manager.update_memory(memory)
            except Exception as e:
                logger.warning(f"Failed to update growth arc in storage: {e}")
        
        logger.debug(f"Updated growth arc for character {character_id}")
        return True
    
    def adapt_to_shell(
        self,
        character_id: str,
        shell_type: str
    ) -> Optional[GrowthArc]:
        """
        将成长线适配到不同题材外壳
        
        基于"换壳理论"：同一个成长线可以适配到不同题材。
        
        Args:
            character_id: 人物ID
            shell_type: 外壳类型（如 "urban", "fantasy", "sci-fi"）
            
        Returns:
            适配后的成长线（新实例，不修改原成长线）
        """
        growth_arc = self.get_growth_arc(character_id)
        if not growth_arc:
            logger.warning(f"Growth arc not found for character {character_id}")
            return None
        
        ***REMOVED*** 创建适配后的成长线（保持核心不变，只调整外壳相关的描述）
        adapted_arc = GrowthArc(
            character_id=growth_arc.character_id,
            character_name=growth_arc.character_name,
            early_state=growth_arc.early_state,  ***REMOVED*** 核心不变
            mid_conflict=growth_arc.mid_conflict,  ***REMOVED*** 核心不变
            late_outcome=growth_arc.late_outcome,  ***REMOVED*** 核心不变
            metadata={
                **growth_arc.metadata,
                "adapted_shell": shell_type,
                "original_character_id": character_id
            }
        )
        
        logger.debug(f"Adapted growth arc for character {character_id} to shell {shell_type}")
        return adapted_arc
    
    def list_growth_arcs(self) -> List[GrowthArc]:
        """列出所有成长线"""
        return list(self._growth_arcs.values())
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_growth_arcs": len(self._growth_arcs),
            "characters": [
                {
                    "character_id": arc.character_id,
                    "character_name": arc.character_name,
                    "created_at": arc.created_at.isoformat(),
                    "updated_at": arc.updated_at.isoformat()
                }
                for arc in self._growth_arcs.values()
            ]
        }

