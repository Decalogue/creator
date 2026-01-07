"""
记忆分类适配器

实现 UniMem 的记忆类型分类功能
参考架构：MemMachine（多类型记忆）+ Hindsight（四大逻辑网络）

核心功能：
- 智能分类记忆类型（Hindsight 四大类型：WORLD, EXPERIENCE, OPINION, OBSERVATION）
- 辅助维度识别（MemMachine 抽象层级：episodic, semantic, user_profile）
- 主分类 + 辅助维度设计，两个维度正交存在
"""

from typing import Optional
from .base import BaseAdapter
from ..types import Memory, MemoryType
from ..chat import ark_deepseek_v3_2
import logging

logger = logging.getLogger(__name__)


class MemoryTypeAdapter(BaseAdapter):
    """
    记忆分类适配器
    
    功能需求：对记忆进行类型分类
    参考架构：MemMachine（多类型记忆）+ Hindsight（四大逻辑网络）
    
    核心功能：
    - 主分类：Hindsight 的四大逻辑网络（WORLD, EXPERIENCE, OPINION, OBSERVATION）
    - 辅助维度：MemMachine 的抽象层级（episodic, semantic, user_profile）
    - 两个维度正交存在，互不冲突
    """
    
    def _do_initialize(self) -> None:
        """初始化记忆分类适配器"""
        logger.info("Memory type adapter initialized (using MemMachine + Hindsight principles)")
    
    def classify(self, memory: Memory, use_hindsight: bool = True) -> MemoryType:
        """
        智能分类记忆类型（推荐方案：主分类 + 辅助维度）
        
        **架构设计原则**：
        1. 主分类使用 Hindsight 的四大逻辑网络（核心认知属性）
        2. MemMachine 维度作为辅助信息存储在 metadata 中
        3. 特殊处理用户画像信息
        
        主分类（Hindsight）：
        - WORLD: 客观事实
        - EXPERIENCE: Agent 自己的经历和行为
        - OBSERVATION: 对人物、事件、事物的客观总结
        - OPINION: Agent 的主观观点和信念（带置信度）
        
        辅助维度（MemMachine，存储在 metadata）：
        - abstraction_level: "episodic" | "semantic" | "user_profile"
        - is_user_profile: bool
        
        如果 use_hindsight=False，则使用纯 MemMachine 分类（向后兼容）：
        - EPISODIC: 情景记忆
        - SEMANTIC: 语义记忆
        - USER_PROFILE: 用户画像记忆
        
        Args:
            memory: 要分类的记忆
            use_hindsight: 是否使用 Hindsight 分类（默认 True）
            
        Returns:
            MemoryType: 主分类类型
        """
        if use_hindsight:
            ***REMOVED*** 主分类：使用 Hindsight
            primary_type = self._classify_hindsight(memory)
            
            ***REMOVED*** 辅助维度：识别 MemMachine 的抽象层级
            abstraction_level = self._identify_abstraction_level(memory)
            if abstraction_level:
                if memory.metadata is None:
                    memory.metadata = {}
                memory.metadata["abstraction_level"] = abstraction_level
            
            ***REMOVED*** 特殊处理：用户画像
            if self._is_user_profile(memory):
                if memory.metadata is None:
                    memory.metadata = {}
                memory.metadata["is_user_profile"] = True
                ***REMOVED*** 如果明显是用户画像但分类为 WORLD，调整为 OPINION
                if primary_type == MemoryType.WORLD and "偏好" in memory.content or "喜欢" in memory.content:
                    primary_type = MemoryType.OPINION
                    logger.debug(f"Adjusted memory {memory.id[:8]}... from WORLD to OPINION (user profile)")
            
            return primary_type
        else:
            ***REMOVED*** 向后兼容：纯 MemMachine 分类
            return self._classify_memmachine(memory)
    
    def _classify_hindsight(self, memory: Memory) -> MemoryType:
        """
        使用 Hindsight 的四大逻辑网络分类
        
        参考 Hindsight 的分类思路：
        - WORLD: 客观事实（"The stove gets hot"）
        - EXPERIENCE: Agent 自己的经历（"I touched the stove and it really hurt"）
        - OPINION: 信念和观点（"I shouldn't touch the stove again" - 带置信度）
        - OBSERVATION: 复杂心理模型（"Curling irons, ovens, and fire are also hot"）
        """
        ***REMOVED*** 使用 LLM 进行智能分类
        prompt = f"""请分析以下记忆内容，判断它属于 Hindsight 的哪种记忆类型。

Hindsight 的四大记忆类型：
1. **WORLD (世界知识)**: 客观事实，关于外部世界的信息（如"炉子会变热"、"用户叫Alice"）
2. **EXPERIENCE (个人经历)**: Agent 自己的经历、行为、对话、任务执行记录（如"我触摸了炉子，很疼"、"用户昨天询问了Python问题"）
3. **OPINION (演变信念)**: Agent 的主观观点、信念、判断，通常包含情感色彩或价值判断（如"我不应该再触摸炉子"、"用户更喜欢Python"）
4. **OBSERVATION (实体观察)**: 通过对多个事实和经历的反思得出的复杂心理模型、模式识别、总结性观察（如"卷发棒、烤箱和火都很热，我也不应该触摸它们"）

记忆内容：
{memory.content}

关键词：{', '.join(memory.keywords[:5]) if memory.keywords else '无'}
上下文：{memory.context or '无'}

请只返回一个类型名称（WORLD、EXPERIENCE、OPINION 或 OBSERVATION），不要包含其他解释："""
        
        try:
            messages = [
                {"role": "system", "content": "你是一个专业的记忆分类助手，擅长根据内容特征将记忆分类到 Hindsight 的四大逻辑网络中。请只返回类型名称。"},
                {"role": "user", "content": prompt}
            ]
            
            _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=32)
            
            ***REMOVED*** 解析响应
            response_text = response_text.strip().upper()
            
            ***REMOVED*** 映射到 MemoryType
            type_mapping = {
                "WORLD": MemoryType.WORLD,
                "EXPERIENCE": MemoryType.EXPERIENCE,
                "OPINION": MemoryType.OPINION,
                "OBSERVATION": MemoryType.OBSERVATION,
            }
            
            for key, memory_type in type_mapping.items():
                if key in response_text:
                    logger.debug(f"Classified memory {memory.id[:8]}... as {memory_type.value}")
                    return memory_type
            
            ***REMOVED*** 如果无法识别，使用启发式规则作为回退
            logger.warning(f"LLM classification failed, using heuristic fallback for memory {memory.id[:8]}...")
            return self._classify_hindsight_heuristic(memory)
            
        except Exception as e:
            logger.error(f"Error classifying memory with LLM: {e}, using heuristic fallback")
            return self._classify_hindsight_heuristic(memory)
    
    def _classify_hindsight_heuristic(self, memory: Memory) -> MemoryType:
        """
        Hindsight 分类的启发式回退方法
        """
        content_lower = memory.content.lower()
        
        ***REMOVED*** OPINION: 包含主观判断、情感词汇
        opinion_keywords = ['应该', '不应该', '喜欢', '不喜欢', '认为', '相信', '觉得', '偏好', '建议']
        if any(keyword in content_lower for keyword in opinion_keywords):
            return MemoryType.OPINION
        
        ***REMOVED*** EXPERIENCE: 包含第一人称、动作、对话
        experience_keywords = ['我', '我们', '执行', '完成', '对话', '询问', '回答', '操作', '任务']
        if any(keyword in content_lower for keyword in experience_keywords):
            return MemoryType.EXPERIENCE
        
        ***REMOVED*** OBSERVATION: 包含总结、模式、多个实体
        observation_keywords = ['总结', '模式', '规律', '通常', '一般', '都', '也', '同样']
        if any(keyword in content_lower for keyword in observation_keywords):
            return MemoryType.OBSERVATION
        
        ***REMOVED*** 默认：WORLD（客观事实）
        return MemoryType.WORLD
    
    def _identify_abstraction_level(self, memory: Memory) -> Optional[str]:
        """
        识别 MemMachine 的抽象层级（辅助维度）
        
        返回 "episodic" | "semantic" | "user_profile" | None
        
        这个信息存储在 metadata 中，用于细粒度查询
        
        优先级：episodic > user_profile > semantic
        （更具体的特征优先）
        """
        content_lower = memory.content.lower()
        
        ***REMOVED*** 情景记忆：具体事件、交互细节（优先级最高，因为最具体）
        ***REMOVED*** 包含时间、动作、具体交互
        episodic_indicators = [
            '昨天', '今天', '刚才', '之前', '之后', '完成', '执行', '操作',
            '询问', '回答', '对话', '交互', '发生', '事件', '任务', '工作'
        ]
        episodic_score = sum(1 for indicator in episodic_indicators if indicator in content_lower)
        
        ***REMOVED*** 用户画像：用户偏好、行为模式（需要排除具体事件）
        ***REMOVED*** 如果同时包含时间词，更可能是 episodic 而不是 user_profile
        user_profile_indicators = ['偏好', '喜欢', '不喜欢', '习惯', '通常', '一般', '总是', '从不']
        user_profile_score = sum(1 for indicator in user_profile_indicators if indicator in content_lower)
        
        ***REMOVED*** 语义记忆：抽象概念、知识结构
        semantic_indicators = [
            '概念', '定义', '原理', '规则', '知识', '理论', '方法', '技术',
            '是', '属于', '支持', '具有', '特征', '特点', '类型'
        ]
        semantic_score = sum(1 for indicator in semantic_indicators if indicator in content_lower)
        
        ***REMOVED*** 决策逻辑：优先选择得分最高的，但考虑上下文
        ***REMOVED*** 如果包含时间词，优先 episodic
        has_time_words = any(word in content_lower for word in ['昨天', '今天', '刚才', '之前', '之后'])
        
        if has_time_words and episodic_score > 0:
            return "episodic"
        
        ***REMOVED*** 如果用户画像得分高且不是具体事件
        if user_profile_score >= 2 and episodic_score == 0:
            return "user_profile"
        
        ***REMOVED*** 如果情景记忆得分高
        if episodic_score >= 2:
            return "episodic"
        
        ***REMOVED*** 如果语义记忆得分高且不是具体事件
        if semantic_score >= 2 and episodic_score == 0:
            return "semantic"
        
        ***REMOVED*** 如果只有单一指标，按优先级返回
        if episodic_score > 0:
            return "episodic"
        if user_profile_score > 0:
            return "user_profile"
        if semantic_score > 0:
            return "semantic"
        
        ***REMOVED*** 如果无法确定，返回 None（不强制分类）
        return None
    
    def _is_user_profile(self, memory: Memory) -> bool:
        """
        判断记忆是否明显是用户画像信息
        
        用于特殊处理，确保用户画像信息被正确标记
        """
        content_lower = memory.content.lower()
        user_profile_indicators = [
            '用户', '偏好', '喜欢', '不喜欢', '习惯', '常用', '通常使用',
            'profile', 'prefer', 'user', 'behavior'
        ]
        return any(indicator in content_lower for indicator in user_profile_indicators)
    
    def _classify_memmachine(self, memory: Memory) -> MemoryType:
        """
        使用 MemMachine 的分类方法（向后兼容）
        
        当 use_hindsight=False 时使用此方法
        """
        content = memory.content.lower()
        
        ***REMOVED*** 参考 MemMachine 的分类逻辑
        if any(keyword in content for keyword in ['user', 'prefer', 'like', 'dislike', 'profile']):
            return MemoryType.USER_PROFILE
        elif any(keyword in content for keyword in ['event', 'happened', 'occurred', 'time']):
            return MemoryType.EPISODIC
        else:
            return MemoryType.SEMANTIC
