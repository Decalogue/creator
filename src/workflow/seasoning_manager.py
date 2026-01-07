"""
调味管理器

基于"换壳理论"的"调味七件套"系统。
为故事添加调味元素，增强故事吸引力。
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class SeasoningType(Enum):
    """调味类型枚举（"调味七件套"）"""
    LOVE = "love"              ***REMOVED*** 爱情
    GRUDGE = "grudge"          ***REMOVED*** 恩仇
    MONEY = "money"            ***REMOVED*** 金钱
    POWER = "power"            ***REMOVED*** 权势
    STRONG_ENEMY = "strong_enemy"  ***REMOVED*** 强敌
    BETRAYAL = "betrayal"      ***REMOVED*** 背叛
    OPPORTUNITY = "opportunity"    ***REMOVED*** 机缘


@dataclass
class Seasoning:
    """调味元素"""
    seasoning_type: SeasoningType
    description: str
    intensity: float = 1.0  ***REMOVED*** 强度（0.0-1.0）
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SeasonedStory:
    """添加调味后的故事"""
    original_story: Any  ***REMOVED*** 原始故事
    seasonings: List[Seasoning] = field(default_factory=list)
    enhanced_content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class SeasoningManager:
    """调味管理器
    
    管理"调味七件套"：
    - 爱情（Love）
    - 恩仇（Grudges/Revenge）
    - 金钱（Money）
    - 权势（Power/Influence）
    - 强敌（Strong Enemies）
    - 背叛（Betrayal）
    - 机缘（Opportunities）
    """
    
    ***REMOVED*** 默认调味七件套
    DEFAULT_SEASONINGS = [
        SeasoningType.LOVE,
        SeasoningType.GRUDGE,
        SeasoningType.MONEY,
        SeasoningType.POWER,
        SeasoningType.STRONG_ENEMY,
        SeasoningType.BETRAYAL,
        SeasoningType.OPPORTUNITY
    ]
    
    ***REMOVED*** 调味描述模板
    SEASONING_TEMPLATES = {
        SeasoningType.LOVE: {
            "urban": "都市中的情感纠葛，职场恋、三角恋、暗恋等",
            "fantasy": "仙侠中的情缘，师徒恋、仙凡恋、前世今生等",
            "sci-fi": "科幻中的情感，人机恋、星际恋、时空恋等"
        },
        SeasoningType.GRUDGE: {
            "urban": "都市中的恩怨情仇，商业竞争、家族仇恨等",
            "fantasy": "仙侠中的血海深仇，门派恩怨、杀父之仇等",
            "sci-fi": "科幻中的星际恩怨，种族仇恨、资源争夺等"
        },
        SeasoningType.MONEY: {
            "urban": "都市中的金钱诱惑，商业帝国、财富争夺等",
            "fantasy": "仙侠中的资源争夺，灵石、法宝、天材地宝等",
            "sci-fi": "科幻中的资源争夺，能源、技术、星球资源等"
        },
        SeasoningType.POWER: {
            "urban": "都市中的权力游戏，政治斗争、商业竞争等",
            "fantasy": "仙侠中的势力争夺，门派、宗门、王朝等",
            "sci-fi": "科幻中的权力结构，星际联盟、科技公司等"
        },
        SeasoningType.STRONG_ENEMY: {
            "urban": "都市中的强敌，商业对手、黑帮、政敌等",
            "fantasy": "仙侠中的强敌，魔道、妖兽、天劫等",
            "sci-fi": "科幻中的强敌，外星文明、AI、星际海盗等"
        },
        SeasoningType.BETRAYAL: {
            "urban": "都市中的背叛，商业背叛、情感背叛等",
            "fantasy": "仙侠中的背叛，师门背叛、兄弟背叛等",
            "sci-fi": "科幻中的背叛，AI背叛、盟友背叛等"
        },
        SeasoningType.OPPORTUNITY: {
            "urban": "都市中的机遇，商业机会、人生转折等",
            "fantasy": "仙侠中的机缘，奇遇、传承、突破等",
            "sci-fi": "科幻中的机遇，科技突破、星际发现等"
        }
    }
    
    def __init__(self, llm_func: Optional[Any] = None):
        """
        初始化调味管理器
        
        Args:
            llm_func: LLM 调用函数（可选，用于生成调味内容）
        """
        self.llm_func = llm_func
        logger.info("SeasoningManager initialized")
    
    def add_seasonings(
        self,
        story: Any,
        seasonings: Optional[List[SeasoningType]] = None,
        shell_type: Optional[str] = None,
        intensity: float = 1.0
    ) -> SeasonedStory:
        """
        为故事添加"调味七件套"
        
        Args:
            story: 故事对象（可以是 ShelledStory 或其他格式）
            seasonings: 调味类型列表（可选，默认使用全部七件套）
            shell_type: 外壳类型（可选，用于选择模板）
            intensity: 调味强度（0.0-1.0）
            
        Returns:
            添加调味后的故事
        """
        if seasonings is None:
            seasonings = self.DEFAULT_SEASONINGS
        
        ***REMOVED*** 创建调味列表
        seasoning_list = []
        for seasoning_type in seasonings:
            description = self._get_seasoning_description(seasoning_type, shell_type)
            seasoning = Seasoning(
                seasoning_type=seasoning_type,
                description=description,
                intensity=intensity,
                metadata={"shell_type": shell_type}
            )
            seasoning_list.append(seasoning)
        
        ***REMOVED*** 生成增强后的内容
        enhanced_content = self._enhance_story_with_seasonings(story, seasoning_list)
        
        ***REMOVED*** 创建调味后的故事
        seasoned_story = SeasonedStory(
            original_story=story,
            seasonings=seasoning_list,
            enhanced_content=enhanced_content,
            metadata={
                "seasonings_count": len(seasoning_list),
                "intensity": intensity,
                "shell_type": shell_type
            }
        )
        
        logger.debug(f"Added {len(seasoning_list)} seasonings to story")
        return seasoned_story
    
    def _get_seasoning_description(
        self,
        seasoning_type: SeasoningType,
        shell_type: Optional[str] = None
    ) -> str:
        """
        获取调味描述
        
        Args:
            seasoning_type: 调味类型
            shell_type: 外壳类型（可选）
            
        Returns:
            调味描述
        """
        templates = self.SEASONING_TEMPLATES.get(seasoning_type, {})
        
        if shell_type and shell_type in templates:
            return templates[shell_type]
        elif templates:
            ***REMOVED*** 返回第一个可用的模板
            return list(templates.values())[0]
        else:
            ***REMOVED*** 默认描述
            return f"{seasoning_type.value}相关元素"
    
    def _enhance_story_with_seasonings(
        self,
        story: Any,
        seasonings: List[Seasoning]
    ) -> str:
        """
        使用调味元素增强故事内容
        
        Args:
            story: 故事对象
            seasonings: 调味列表
            
        Returns:
            增强后的内容
        """
        ***REMOVED*** 获取原始内容
        if hasattr(story, "content"):
            original_content = story.content
        elif isinstance(story, dict):
            original_content = story.get("content", "")
        else:
            original_content = str(story)
        
        ***REMOVED*** 构建调味部分
        seasoning_parts = ["【调味元素】"]
        for seasoning in seasonings:
            seasoning_parts.append(
                f"- {seasoning.seasoning_type.value}：{seasoning.description}"
            )
        
        seasoning_section = "\n".join(seasoning_parts)
        
        ***REMOVED*** 合并内容
        enhanced_content = f"{original_content}\n\n{seasoning_section}"
        
        return enhanced_content
    
    def apply_seasoning_to_growth_arc(
        self,
        growth_arc: Any,
        seasoning_type: SeasoningType,
        shell_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        将调味应用到人物成长线
        
        Args:
            growth_arc: 成长线对象
            seasoning_type: 调味类型
            shell_type: 外壳类型（可选）
            
        Returns:
            应用调味后的成长线信息
        """
        description = self._get_seasoning_description(seasoning_type, shell_type)
        
        ***REMOVED*** 构建提示词
        prompt = f"""请将以下调味元素融入到人物成长线中：

人物成长线：
- 前期状态：{growth_arc.early_state if hasattr(growth_arc, 'early_state') else ''}
- 中期冲突：{growth_arc.mid_conflict if hasattr(growth_arc, 'mid_conflict') else ''}
- 后期结果：{growth_arc.late_outcome if hasattr(growth_arc, 'late_outcome') else ''}

调味元素：{seasoning_type.value} - {description}

请生成融合后的成长线描述。"""
        
        ***REMOVED*** 如果提供了 LLM 函数，使用 LLM 生成
        if self.llm_func:
            try:
                messages = [{"role": "user", "content": prompt}]
                response = self.llm_func(messages)
                content = response.get("content", "") if isinstance(response, dict) else str(response)
                return {
                    "success": True,
                    "enhanced_growth_arc": content,
                    "seasoning_type": seasoning_type.value
                }
            except Exception as e:
                logger.warning(f"Failed to use LLM for seasoning: {e}")
        
        ***REMOVED*** 否则返回简单融合
        return {
            "success": True,
            "enhanced_growth_arc": f"{description}融入成长线",
            "seasoning_type": seasoning_type.value
        }
    
    def get_seasoning_statistics(self) -> Dict[str, Any]:
        """获取调味统计信息"""
        return {
            "total_seasoning_types": len(SeasoningType),
            "default_seasonings": [st.value for st in self.DEFAULT_SEASONINGS],
            "available_templates": {
                st.value: list(self.SEASONING_TEMPLATES.get(st, {}).keys())
                for st in SeasoningType
            }
        }

