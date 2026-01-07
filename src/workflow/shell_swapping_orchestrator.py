"""
换壳编排器

基于"换壳理论"实现故事核心与外壳的分离和适配。
实现"换壳"工作流：提取核心 → 选择外壳 → 融合调整 → 添加调味
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from unimem.character import CharacterGrowthArcManager, GrowthArc
from unimem.storage.hierarchical.hierarchical_storage import HierarchicalStorage, ContentLevel

logger = logging.getLogger(__name__)


@dataclass
class StoryCore:
    """故事核心（"骨头"）
    
    包含跨题材复用的核心元素：
    - 人物成长线
    - 核心冲突
    - 关系网络
    - 情绪推进
    """
    growth_arcs: List[GrowthArc] = field(default_factory=list)
    core_conflicts: List[str] = field(default_factory=list)
    relationship_network: Dict[str, Any] = field(default_factory=dict)
    emotional_progression: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StoryShell:
    """故事外壳（"衣服"）
    
    包含题材特定的元素：
    - 题材背景
    - 世界观设定
    - 题材细节
    - 题材规则
    """
    shell_type: str  ***REMOVED*** "urban", "fantasy", "sci-fi", etc.
    background: str = ""
    world_setting: Dict[str, Any] = field(default_factory=dict)
    genre_details: List[str] = field(default_factory=list)
    genre_rules: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ShelledStory:
    """换壳后的故事
    
    核心 + 外壳融合后的完整故事
    """
    core: StoryCore
    shell: StoryShell
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class ShellSwappingOrchestrator:
    """换壳编排器
    
    实现"换壳"工作流：
    1. 提取核心（"骨头"）：人物成长线、核心冲突、关系网络
    2. 选择外壳（"衣服"）：目标题材的背景、设定、细节
    3. 融合调整：根据题材调整细节
    4. 添加调味：加入"调味七件套"
    """
    
    def __init__(
        self,
        growth_arc_manager: Optional[CharacterGrowthArcManager] = None,
        hierarchical_storage: Optional[HierarchicalStorage] = None,
        unimem: Optional[Any] = None
    ):
        """
        初始化换壳编排器
        
        Args:
            growth_arc_manager: 成长线管理器
            hierarchical_storage: 分层存储
            unimem: UniMem 实例（用于检索记忆）
        """
        self.growth_arc_manager = growth_arc_manager
        self.hierarchical_storage = hierarchical_storage
        self.unimem = unimem
        
        logger.info("ShellSwappingOrchestrator initialized")
    
    def swap_shell(
        self,
        source_story: Dict[str, Any],
        target_shell: str,
        character_ids: Optional[List[str]] = None
    ) -> ShelledStory:
        """
        换壳工作流
        
        完整流程：
        1. 提取核心（"骨头"）
        2. 选择外壳（"衣服"）
        3. 融合调整
        4. 添加调味
        
        Args:
            source_story: 源故事（字典格式）
            target_shell: 目标外壳类型（如 "urban", "fantasy", "sci-fi"）
            character_ids: 人物ID列表（可选，用于提取成长线）
            
        Returns:
            换壳后的故事
        """
        try:
            logger.info(f"Starting shell swapping: {target_shell}")
            
            ***REMOVED*** 步骤1：提取核心（"骨头"）
            core = self._extract_core(source_story, character_ids)
            logger.debug(f"Extracted core: {len(core.growth_arcs)} growth arcs, {len(core.core_conflicts)} conflicts")
            
            ***REMOVED*** 步骤2：选择外壳（"衣服"）
            shell = self._select_shell(target_shell)
            logger.debug(f"Selected shell: {shell.shell_type}")
            
            ***REMOVED*** 步骤3：融合调整
            shelled_story = self._merge_core_and_shell(core, shell)
            logger.debug("Merged core and shell")
            
            ***REMOVED*** 步骤4：添加调味（由 SeasoningManager 处理）
            ***REMOVED*** 注意：需要在外部调用 SeasoningManager 添加调味
            
            logger.info(f"Shell swapping completed: {target_shell}")
            return shelled_story
            
        except Exception as e:
            logger.error(f"Error in shell swapping: {e}", exc_info=True)
            raise
    
    def _extract_core(
        self,
        source_story: Dict[str, Any],
        character_ids: Optional[List[str]] = None
    ) -> StoryCore:
        """
        提取核心（"骨头"）
        
        从源故事中提取跨题材复用的核心元素：
        - 人物成长线
        - 核心冲突
        - 关系网络
        - 情绪推进
        
        Args:
            source_story: 源故事
            character_ids: 人物ID列表（可选）
            
        Returns:
            故事核心
        """
        core = StoryCore()
        
        ***REMOVED*** 1. 提取人物成长线
        if self.growth_arc_manager and character_ids:
            for character_id in character_ids:
                growth_arc = self.growth_arc_manager.get_growth_arc(character_id)
                if growth_arc:
                    core.growth_arcs.append(growth_arc)
        
        ***REMOVED*** 2. 从源故事中提取核心冲突
        if "conflicts" in source_story:
            core.core_conflicts = source_story["conflicts"]
        elif "core_conflicts" in source_story:
            core.core_conflicts = source_story["core_conflicts"]
        
        ***REMOVED*** 3. 从源故事中提取关系网络
        if "relationships" in source_story:
            core.relationship_network = source_story["relationships"]
        elif "relationship_network" in source_story:
            core.relationship_network = source_story["relationship_network"]
        
        ***REMOVED*** 4. 从源故事中提取情绪推进
        if "emotional_progression" in source_story:
            core.emotional_progression = source_story["emotional_progression"]
        
        ***REMOVED*** 5. 保存元数据
        core.metadata = {
            "source_story_id": source_story.get("id", ""),
            "extracted_at": source_story.get("timestamp", ""),
            **source_story.get("metadata", {})
        }
        
        logger.debug(f"Extracted core: {len(core.growth_arcs)} growth arcs")
        return core
    
    def _select_shell(self, shell_type: str) -> StoryShell:
        """
        选择外壳（"衣服"）
        
        根据目标题材选择对应的外壳记忆。
        
        Args:
            shell_type: 外壳类型（如 "urban", "fantasy", "sci-fi"）
            
        Returns:
            故事外壳
        """
        shell = StoryShell(shell_type=shell_type)
        
        ***REMOVED*** 从分层存储中检索外壳记忆
        if self.hierarchical_storage:
            try:
                ***REMOVED*** 检索外壳记忆（使用通用检索方法）
                shell_memories = self.hierarchical_storage.retrieve(
                    query=f"题材背景 {shell_type}",
                    level=ContentLevel.WORK,
                    top_k=10
                )
                
                ***REMOVED*** 过滤出匹配的外壳类型
                filtered_memories = []
                for memory in shell_memories:
                    if memory.metadata and memory.metadata.get("shell_type") == shell_type:
                        filtered_memories.append(memory)
                shell_memories = filtered_memories
                
                ***REMOVED*** 解析外壳记忆
                for memory in shell_memories:
                    if "background" in memory.content.lower() or "背景" in memory.content:
                        shell.background = memory.content
                    if memory.metadata:
                        if "world_setting" in memory.metadata:
                            shell.world_setting.update(memory.metadata["world_setting"])
                        if "genre_details" in memory.metadata:
                            shell.genre_details.extend(memory.metadata["genre_details"])
                        if "genre_rules" in memory.metadata:
                            shell.genre_rules.update(memory.metadata["genre_rules"])
                
            except Exception as e:
                logger.warning(f"Failed to retrieve shell memories: {e}")
        
        ***REMOVED*** 如果未找到外壳记忆，使用默认外壳
        if not shell.background:
            shell.background = self._get_default_shell_background(shell_type)
        
        shell.metadata = {
            "shell_type": shell_type,
            "selected_at": ""
        }
        
        logger.debug(f"Selected shell: {shell_type}")
        return shell
    
    def _get_default_shell_background(self, shell_type: str) -> str:
        """获取默认外壳背景"""
        defaults = {
            "urban": "现代都市背景，强调现实生活、职场竞争、都市情感",
            "fantasy": "玄幻世界背景，强调修炼体系、仙侠江湖、异界冒险",
            "sci-fi": "科幻未来背景，强调科技发展、星际探索、未来社会",
            "historical": "历史背景，强调历史事件、古代社会、历史人物",
            "mystery": "悬疑推理背景，强调谜题、推理、真相揭露"
        }
        return defaults.get(shell_type, f"{shell_type}题材背景")
    
    def _merge_core_and_shell(
        self,
        core: StoryCore,
        shell: StoryShell
    ) -> ShelledStory:
        """
        融合核心与外壳
        
        将核心（"骨头"）与外壳（"衣服"）融合，生成完整故事。
        
        Args:
            core: 故事核心
            shell: 故事外壳
            
        Returns:
            换壳后的故事
        """
        ***REMOVED*** 1. 适配人物成长线到新外壳
        adapted_growth_arcs = []
        if self.growth_arc_manager:
            for growth_arc in core.growth_arcs:
                adapted_arc = self.growth_arc_manager.adapt_to_shell(
                    growth_arc.character_id,
                    shell.shell_type
                )
                if adapted_arc:
                    adapted_growth_arcs.append(adapted_arc)
        
        ***REMOVED*** 2. 生成融合后的内容
        content_parts = []
        
        ***REMOVED*** 外壳背景
        content_parts.append(f"【题材背景】{shell.background}")
        
        ***REMOVED*** 世界观设定
        if shell.world_setting:
            content_parts.append(f"【世界观设定】{shell.world_setting}")
        
        ***REMOVED*** 人物成长线（适配后）
        if adapted_growth_arcs:
            content_parts.append("【人物成长线】")
            for arc in adapted_growth_arcs:
                content_parts.append(f"- {arc.character_name}: {arc.to_three_sentences()}")
        
        ***REMOVED*** 核心冲突
        if core.core_conflicts:
            content_parts.append("【核心冲突】")
            for conflict in core.core_conflicts:
                content_parts.append(f"- {conflict}")
        
        ***REMOVED*** 关系网络
        if core.relationship_network:
            content_parts.append(f"【关系网络】{core.relationship_network}")
        
        ***REMOVED*** 情绪推进
        if core.emotional_progression:
            content_parts.append("【情绪推进】")
            for emotion in core.emotional_progression:
                content_parts.append(f"- {emotion}")
        
        content = "\n\n".join(content_parts)
        
        ***REMOVED*** 3. 创建换壳后的故事
        shelled_story = ShelledStory(
            core=core,
            shell=shell,
            content=content,
            metadata={
                "merged_at": "",
                "shell_type": shell.shell_type,
                "growth_arcs_count": len(adapted_growth_arcs),
                "conflicts_count": len(core.core_conflicts)
            }
        )
        
        logger.debug("Merged core and shell")
        return shelled_story
    
    def _add_seasonings(self, story: ShelledStory) -> ShelledStory:
        """
        添加调味（"调味七件套"）
        
        注意：此方法由 SeasoningManager 实现，这里仅作为接口。
        
        Args:
            story: 换壳后的故事
            
        Returns:
            添加调味后的故事
        """
        ***REMOVED*** 由 SeasoningManager 处理
        ***REMOVED*** 这里暂时跳过，等待 SeasoningManager 实现
        return story
    
    def extract_core_from_memory(
        self,
        work_id: str
    ) -> Optional[StoryCore]:
        """
        从记忆系统中提取核心
        
        从 UniMem 中检索并提取故事核心。
        
        Args:
            work_id: 作品ID
            
        Returns:
            故事核心，如果不存在则返回 None
        """
        if not self.unimem or not self.hierarchical_storage:
            logger.warning("UniMem or HierarchicalStorage not available")
            return None
        
        try:
            ***REMOVED*** 从分层存储中检索核心记忆
            core_memories = self.hierarchical_storage.retrieve(
                query=work_id,
                level=ContentLevel.WORK,
                top_k=50
            )
            
            ***REMOVED*** 过滤出核心记忆（通过 metadata 中的 is_core 标记）
            filtered_memories = []
            for memory in core_memories:
                if memory.metadata and memory.metadata.get("is_core"):
                    filtered_memories.append(memory)
            core_memories = filtered_memories
            
            ***REMOVED*** 构建故事核心
            core = StoryCore()
            
            ***REMOVED*** 从核心记忆中提取成长线
            for memory in core_memories:
                if memory.metadata and memory.metadata.get("is_core"):
                    if "character_id" in memory.metadata:
                        character_id = memory.metadata["character_id"]
                        if self.growth_arc_manager:
                            growth_arc = self.growth_arc_manager.get_growth_arc(character_id)
                            if growth_arc:
                                core.growth_arcs.append(growth_arc)
            
            logger.debug(f"Extracted core from memory: {len(core.growth_arcs)} growth arcs")
            return core
            
        except Exception as e:
            logger.error(f"Error extracting core from memory: {e}", exc_info=True)
            return None

