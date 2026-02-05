"""
ReMe 启发的增强提取器

实现多面蒸馏：从成功、失败、比较中提取结构化经验
借鉴 ReMe 的设计思想，解决"提取过于简单"的问题
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import Counter

logger = logging.getLogger(__name__)


@dataclass
class StructuredExperience:
    """结构化经验（借鉴 ReMe 的 Experience E）"""
    # 适用场景（applicable scenario）ω
    scenario: str  # 例如："角色首次出场"、"矛盾冲突升级"
    scenario_description: str  # 详细的场景描述
    
    # 核心内容（core content）e
    content: str  # 经验的核心内容
    pattern_type: str  # 情节类型：打脸/装逼/反转/高潮等
    
    # 关键词（keywords）κ
    keywords: List[str] = field(default_factory=list)
    
    # 置信度（confidence）c
    confidence: float = 0.8  # 0-1，基于验证次数和效果
    
    # 使用的工具（tools used）τ
    tools: List[str] = field(default_factory=list)  # 需要的 Agent 或工具
    
    # 扩展字段（ReMe 没有，但我们需要的）
    success_score: float = 0.0  # 成功案例的评分（如果有）
    failure_count: int = 0  # 失败次数
    usage_count: int = 0  # 使用次数
    utility_score: float = 0.0  # 效用评分（usage_count > 0 时的平均效果）
    
    # 来源信息
    source_novel: str = ""  # 来源小说
    extraction_method: str = ""  # 提取方法：success/failure/comparison
    
    # 时间戳
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "scenario": self.scenario,
            "scenario_description": self.scenario_description,
            "content": self.content,
            "pattern_type": self.pattern_type,
            "keywords": self.keywords,
            "confidence": self.confidence,
            "tools": self.tools,
            "success_score": self.success_score,
            "failure_count": self.failure_count,
            "usage_count": self.usage_count,
            "utility_score": self.utility_score,
            "source_novel": self.source_novel,
            "extraction_method": self.extraction_method,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class RemeInspiredExtractor:
    """ReMe 启发的多面蒸馏提取器"""
    
    def __init__(self, llm_func=None):
        """
        初始化提取器
        
        Args:
            llm_func: LLM 调用函数（用于复杂分析）
        """
        self.llm_func = llm_func
        
        # 情节类型关键词（继承自 novel_processor）
        self.plot_keywords = {
            "打脸": ["打脸", "反击", "碾压", "秒杀", "完虐", "吊打"],
            "装逼": ["装逼", "震撼", "惊艳", "惊叹", "不可思议", "逆天"],
            "反转": ["反转", "真相", "原来", "竟然", "没想到", "出乎意料"],
            "高潮": ["高潮", "大战", "决战", "巅峰", "激烈", "惊天"],
            "情感": ["心动", "喜欢", "爱", "心疼", "感动", "温馨"],
            "冲突": ["冲突", "矛盾", "对立", "仇敌", "敌对", "对抗"],
        }
        
        logger.info("RemeInspiredExtractor initialized")
    
    def extract_from_success(
        self,
        chapters: List[Dict[str, Any]],
        success_indicators: Optional[Dict[str, float]] = None
    ) -> List[StructuredExperience]:
        """
        从成功模式中提取经验（借鉴 ReMe SuccessExtractionOp）
        
        Args:
            chapters: 章节列表
            success_indicators: 成功指标（如评分、读者反馈等）
            
        Returns:
            成功模式的经验列表
        """
        experiences = []
        
        # 如果没有成功指标，使用简单的启发式规则
        if success_indicators is None:
            success_indicators = self._estimate_success_indicators(chapters)
        
        # 识别高成功章节
        high_success_chapters = [
            (ch, score) for ch, score in zip(chapters, 
                [success_indicators.get(str(ch.get("chapter_number", "")), 0.5) 
                 for ch in chapters])
            if score > 0.7  # 阈值
        ]
        
        logger.info(f"识别到 {len(high_success_chapters)} 个高成功章节")
        
        for chapter, score in high_success_chapters:
            # 提取成功模式
            patterns = self._extract_success_patterns(chapter, score)
            experiences.extend(patterns)
        
        return experiences
    
    def extract_from_failure(
        self,
        chapters: List[Dict[str, Any]],
        failure_indicators: Optional[Dict[str, float]] = None
    ) -> List[StructuredExperience]:
        """
        从失败模式中提取经验（借鉴 ReMe FailureExtractionOp）
        
        Args:
            chapters: 章节列表
            failure_indicators: 失败指标（如低评分、被跳过等）
            
        Returns:
            失败模式的经验列表（用于避免重复错误）
        """
        experiences = []
        
        # 如果没有失败指标，使用简单的启发式规则
        if failure_indicators is None:
            failure_indicators = self._estimate_failure_indicators(chapters)
        
        # 识别高失败章节
        high_failure_chapters = [
            (ch, score) for ch, score in zip(chapters,
                [failure_indicators.get(str(ch.get("chapter_number", "")), 0.3)
                 for ch in chapters])
            if score > 0.6  # 失败分数高
        ]
        
        logger.info(f"识别到 {len(high_failure_chapters)} 个高失败章节")
        
        for chapter, score in high_failure_chapters:
            # 提取失败模式
            patterns = self._extract_failure_patterns(chapter, score)
            experiences.extend(patterns)
        
        return experiences
    
    def extract_from_comparison(
        self,
        chapters: List[Dict[str, Any]],
        success_indicators: Optional[Dict[str, float]] = None,
        failure_indicators: Optional[Dict[str, float]] = None
    ) -> List[StructuredExperience]:
        """
        从比较性洞察中提取经验（ReMe 的比较性分析）
        
        找到相似场景的不同处理方式，提取改进点
        
        Args:
            chapters: 章节列表
            success_indicators: 成功指标
            failure_indicators: 失败指标
            
        Returns:
            比较性洞察的经验列表
        """
        experiences = []
        
        if success_indicators is None:
            success_indicators = self._estimate_success_indicators(chapters)
        if failure_indicators is None:
            failure_indicators = self._estimate_failure_indicators(chapters)
        
        # 1. 找到相似场景的不同处理
        similar_scenarios = self._find_similar_scenarios(chapters)
        
        logger.info(f"找到 {len(similar_scenarios)} 组相似场景")
        
        # 2. 对比每组的成功和失败案例
        for scenario_group in similar_scenarios:
            if len(scenario_group) < 2:
                continue
            
            # 分离成功和失败案例
            success_cases = [
                ch for ch in scenario_group
                if success_indicators.get(str(ch.get("chapter_number", "")), 0.5) > 0.7
            ]
            failure_cases = [
                ch for ch in scenario_group
                if failure_indicators.get(str(ch.get("chapter_number", "")), 0.3) > 0.6
            ]
            
            if success_cases and failure_cases:
                # 提取比较性洞察
                insights = self._analyze_comparison(success_cases[0], failure_cases[0])
                experiences.extend(insights)
        
        return experiences
    
    def _extract_success_patterns(
        self,
        chapter: Dict[str, Any],
        success_score: float
    ) -> List[StructuredExperience]:
        """提取成功模式"""
        experiences = []
        
        content = chapter.get("content", "")
        title = chapter.get("chapter_title", "")
        
        # 识别情节类型
        pattern_type = self._identify_plot_type(content)
        
        # 提取场景
        scenario = self._extract_scenario(chapter)
        
        # 提取关键事件
        key_events = self._extract_key_events(content)
        
        # 构建经验
        experience = StructuredExperience(
            scenario=scenario,
            scenario_description=f"章节《{title}》中的{scenario}场景",
            content=f"成功模式：{key_events[:2]}",  # 前2个关键事件
            pattern_type=pattern_type,
            keywords=self._extract_keywords(content),
            confidence=0.8 + success_score * 0.2,  # 基于成功分数
            tools=["planning", "reasoning"],  # 默认工具
            success_score=success_score,
            source_novel=chapter.get("source_novel", ""),
            extraction_method="success",
        )
        
        experiences.append(experience)
        return experiences
    
    def _extract_failure_patterns(
        self,
        chapter: Dict[str, Any],
        failure_score: float
    ) -> List[StructuredExperience]:
        """提取失败模式（用于避免重复错误）"""
        experiences = []
        
        content = chapter.get("content", "")
        title = chapter.get("chapter_title", "")
        
        # 识别问题点
        problems = self._identify_problems(content)
        
        if not problems:
            return experiences
        
        # 提取场景
        scenario = self._extract_scenario(chapter)
        
        # 构建经验（用于预防）
        experience = StructuredExperience(
            scenario=scenario,
            scenario_description=f"章节《{title}》中的失败场景",
            content=f"失败模式：应避免{problems[0]}",  # 主要问题
            pattern_type="failure_prevention",
            keywords=self._extract_keywords(content),
            confidence=0.7,  # 失败模式置信度稍低
            tools=["planning", "reasoning"],
            failure_count=1,
            source_novel=chapter.get("source_novel", ""),
            extraction_method="failure",
        )
        
        experiences.append(experience)
        return experiences
    
    def _analyze_comparison(
        self,
        success_chapter: Dict[str, Any],
        failure_chapter: Dict[str, Any]
    ) -> List[StructuredExperience]:
        """分析比较性洞察"""
        experiences = []
        
        success_content = success_chapter.get("content", "")
        failure_content = failure_chapter.get("content", "")
        
        # 提取关键差异（简化版，实际应该用 LLM）
        differences = self._extract_differences(success_content, failure_content)
        
        if not differences:
            return experiences
        
        # 构建比较性洞察
        scenario = self._extract_scenario(success_chapter)
        
        experience = StructuredExperience(
            scenario=scenario,
            scenario_description=f"相似场景的成功与失败对比",
            content=f"改进建议：{differences[0]}",  # 主要差异
            pattern_type="comparison_insight",
            keywords=list(set(
                self._extract_keywords(success_content) +
                self._extract_keywords(failure_content)
            )),
            confidence=0.85,  # 比较性洞察置信度较高
            tools=["planning", "reasoning"],
            source_novel=success_chapter.get("source_novel", ""),
            extraction_method="comparison",
        )
        
        experiences.append(experience)
        return experiences
    
    def _estimate_success_indicators(
        self,
        chapters: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """估计成功指标（启发式规则）"""
        indicators = {}
        
        for chapter in chapters:
            ch_num = str(chapter.get("chapter_number", ""))
            content = chapter.get("content", "")
            
            # 简单的成功指标
            score = 0.5  # 基础分
            
            # 长度适中（3000-6000字）加分
            word_count = len(content)
            if 3000 <= word_count <= 6000:
                score += 0.1
            
            # 包含高潮情节加分
            if any(kw in content for kw in self.plot_keywords.get("高潮", [])):
                score += 0.1
            
            # 包含反转情节加分
            if any(kw in content for kw in self.plot_keywords.get("反转", [])):
                score += 0.1
            
            indicators[ch_num] = min(score, 1.0)
        
        return indicators
    
    def _estimate_failure_indicators(
        self,
        chapters: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """估计失败指标（启发式规则）"""
        indicators = {}
        
        for chapter in chapters:
            ch_num = str(chapter.get("chapter_number", ""))
            content = chapter.get("content", "")
            
            # 简单的失败指标
            score = 0.0
            
            # 内容过短（<1000字）扣分
            word_count = len(content)
            if word_count < 1000:
                score += 0.5
            
            # 内容过长（>8000字）可能也是问题
            if word_count > 8000:
                score += 0.2
            
            # 缺少关键情节元素
            has_plot = any(
                any(kw in content for kw in keywords)
                for keywords in self.plot_keywords.values()
            )
            if not has_plot:
                score += 0.3
            
            indicators[ch_num] = min(score, 1.0)
        
        return indicators
    
    def _find_similar_scenarios(
        self,
        chapters: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """找到相似场景的章节分组（简化版）"""
        # 按场景类型分组
        scenario_groups: Dict[str, List[Dict[str, Any]]] = {}
        
        for chapter in chapters:
            scenario = self._extract_scenario(chapter)
            if scenario not in scenario_groups:
                scenario_groups[scenario] = []
            scenario_groups[scenario].append(chapter)
        
        # 返回包含多个章节的组
        return [group for group in scenario_groups.values() if len(group) >= 2]
    
    def _extract_scenario(self, chapter: Dict[str, Any]) -> str:
        """提取场景类型"""
        title = chapter.get("chapter_title", "")
        content = chapter.get("content", "")[:500]  # 前500字
        
        # 简单的场景识别
        if any(kw in title or kw in content for kw in ["出场", "遇见", "相遇", "初遇"]):
            return "角色首次出场"
        elif any(kw in title or kw in content for kw in ["冲突", "矛盾", "对抗", "战斗"]):
            return "矛盾冲突升级"
        elif any(kw in title or kw in content for kw in ["转折", "变化", "改变"]):
            return "情节转折点"
        elif any(kw in title or kw in content for kw in ["高潮", "决战", "最终"]):
            return "高潮阶段"
        else:
            return "常规叙事"
    
    def _identify_plot_type(self, content: str) -> str:
        """识别情节类型"""
        scores = {}
        for plot_type, keywords in self.plot_keywords.items():
            score = sum(1 for kw in keywords if kw in content)
            if score > 0:
                scores[plot_type] = score
        
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        return "综合"
    
    def _extract_key_events(self, content: str) -> List[str]:
        """提取关键事件"""
        event_patterns = [
            r'[^。！？]{0,20}(发现|得知|决定|前往|遇到|见到|开始|结束)[^。！？]{0,20}[。！？]',
        ]
        
        events = []
        for pattern in event_patterns:
            matches = re.findall(pattern, content[:5000])  # 前5000字
            events.extend(matches[:3])  # 最多3个
        
        return events
    
    def _extract_keywords(self, content: str) -> List[str]:
        """提取关键词"""
        # 提取3-6字的中文短语
        phrases = re.findall(r'[一-龥]{3,6}', content[:10000])
        common = Counter(phrases).most_common(5)
        return [phrase for phrase, count in common if count > 2]
    
    def _identify_problems(self, content: str) -> List[str]:
        """识别问题点（简化版）"""
        problems = []
        
        # 内容过短
        if len(content) < 1000:
            problems.append("内容过短，缺乏细节")
        
        # 缺少对话
        if content.count('"') < 5 and content.count('"') < 5:
            problems.append("缺少对话，缺乏互动")
        
        # 缺少动作
        action_words = ["走", "跑", "跳", "打", "看", "说", "想"]
        if not any(word in content for word in action_words):
            problems.append("缺少动作描写，缺乏画面感")
        
        return problems
    
    def _extract_differences(
        self,
        success_content: str,
        failure_content: str
    ) -> List[str]:
        """提取成功与失败的差异（简化版）"""
        differences = []
        
        # 长度差异
        if len(success_content) > len(failure_content) * 1.5:
            differences.append("成功案例更注重细节描写")
        elif len(failure_content) > len(success_content) * 1.5:
            differences.append("失败案例过于冗长，应精简")
        
        # 对话比例
        success_dialog_ratio = (success_content.count('"') + success_content.count('"')) / max(len(success_content), 1)
        failure_dialog_ratio = (failure_content.count('"') + failure_content.count('"')) / max(len(failure_content), 1)
        
        if success_dialog_ratio > failure_dialog_ratio * 1.5:
            differences.append("成功案例更注重对话，增强互动性")
        
        return differences
    
    def extract_all(
        self,
        chapters: List[Dict[str, Any]],
        success_indicators: Optional[Dict[str, float]] = None,
        failure_indicators: Optional[Dict[str, float]] = None
    ) -> Dict[str, List[StructuredExperience]]:
        """
        完整的多面蒸馏提取
        
        Returns:
            {
                "success": [...],
                "failure": [...],
                "comparison": [...]
            }
        """
        logger.info("开始多面蒸馏提取...")
        
        # 1. 成功模式
        success_experiences = self.extract_from_success(chapters, success_indicators)
        logger.info(f"提取了 {len(success_experiences)} 个成功模式")
        
        # 2. 失败模式
        failure_experiences = self.extract_from_failure(chapters, failure_indicators)
        logger.info(f"提取了 {len(failure_experiences)} 个失败模式")
        
        # 3. 比较性洞察
        comparison_experiences = self.extract_from_comparison(
            chapters, success_indicators, failure_indicators
        )
        logger.info(f"提取了 {len(comparison_experiences)} 个比较性洞察")
        
        return {
            "success": success_experiences,
            "failure": failure_experiences,
            "comparison": comparison_experiences,
        }

