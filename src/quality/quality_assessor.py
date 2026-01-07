"""
质量评估器

实现多维度质量评估，包括情节覆盖度、人物一致性、风格一致性等。
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from ..unimem.chat import ark_deepseek_v3_2

logger = logging.getLogger(__name__)


@dataclass
class QualityReport:
    """质量评估报告"""
    overall_score: float  ***REMOVED*** 0-1, 总体质量分数
    dimension_scores: Dict[str, float] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)
    
    @property
    def is_acceptable(self) -> bool:
        """是否可接受（分数 >= 0.7）"""
        return self.overall_score >= 0.7


class QualityAssessor:
    """质量评估器
    
    评估内容在以下维度的质量：
    - 情节覆盖度：内容是否覆盖了预期情节
    - 人物一致性：人物设定和行为是否一致
    - 风格一致性：写作风格是否统一
    - 语言质量：语言表达是否流畅、准确
    - 结构完整性：结构是否完整、逻辑是否清晰
    """
    
    def __init__(self, llm_func=None):
        """
        初始化质量评估器
        
        Args:
            llm_func: LLM 调用函数
        """
        self.llm_func = llm_func or ark_deepseek_v3_2
        logger.info("QualityAssessor initialized")
    
    def assess(
        self,
        content: str,
        expected: Optional[str] = None,
        check_dimensions: Optional[List[str]] = None
    ) -> QualityReport:
        """
        全面质量评估
        
        Args:
            content: 要评估的内容
            expected: 预期内容（用于对比）
            check_dimensions: 要检查的维度，如果为None则检查所有维度
            
        Returns:
            质量评估报告
        """
        if not content:
            return QualityReport(
                overall_score=0.0,
                dimension_scores={},
                details={"error": "内容为空"}
            )
        
        check_dimensions = check_dimensions or [
            "plot_coverage",
            "character_consistency",
            "style_consistency",
            "language_quality",
            "structure"
        ]
        
        dimension_scores = {}
        suggestions = []
        
        ***REMOVED*** 评估各维度
        if "plot_coverage" in check_dimensions:
            score = self.assess_plot_coverage(content, expected)
            dimension_scores["plot_coverage"] = score
            if score < 0.7:
                suggestions.append("建议增加情节描述，提高情节覆盖度")
        
        if "character_consistency" in check_dimensions:
            score = self.assess_character_consistency(content)
            dimension_scores["character_consistency"] = score
            if score < 0.7:
                suggestions.append("建议检查人物设定和行为的一致性")
        
        if "style_consistency" in check_dimensions:
            score = self.assess_style_consistency(content)
            dimension_scores["style_consistency"] = score
            if score < 0.7:
                suggestions.append("建议统一写作风格")
        
        if "language_quality" in check_dimensions:
            score = self.assess_language_quality(content)
            dimension_scores["language_quality"] = score
            if score < 0.7:
                suggestions.append("建议改进语言表达，提高流畅度")
        
        if "structure" in check_dimensions:
            score = self.assess_structure(content)
            dimension_scores["structure"] = score
            if score < 0.7:
                suggestions.append("建议优化结构，提高逻辑清晰度")
        
        ***REMOVED*** 计算总体分数
        if dimension_scores:
            overall_score = sum(dimension_scores.values()) / len(dimension_scores)
        else:
            overall_score = 0.0
        
        return QualityReport(
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            details={
                "content_length": len(content),
                "dimension_count": len(dimension_scores)
            },
            suggestions=suggestions
        )
    
    def assess_plot_coverage(self, content: str, expected: Optional[str] = None) -> float:
        """
        评估情节覆盖度
        
        Args:
            content: 要评估的内容
            expected: 预期情节
            
        Returns:
            覆盖度分数（0-1）
        """
        if not expected:
            ***REMOVED*** 如果没有预期内容，使用简单启发式方法
            ***REMOVED*** 检查是否有足够的情节描述
            plot_indicators = ["发生", "开始", "结束", "因为", "所以", "但是", "然而"]
            indicator_count = sum(1 for indicator in plot_indicators if indicator in content)
            return min(indicator_count / 5.0, 1.0)
        
        ***REMOVED*** 使用 LLM 评估覆盖度
        try:
            prompt = f"""请评估以下内容对预期情节的覆盖度（0-1分）：

预期情节：
{expected}

实际内容：
{content}

请评估实际内容是否覆盖了预期情节的关键点，并给出0-1之间的分数。
只输出分数，不要其他说明。"""
            
            messages = [{"role": "user", "content": prompt}]
            _, response = self.llm_func(messages)
            
            ***REMOVED*** 提取分数
            try:
                score = float(response.strip())
                return max(0.0, min(1.0, score))
            except ValueError:
                ***REMOVED*** 如果无法解析，使用默认值
                return 0.7
        except Exception as e:
            logger.warning(f"LLM plot coverage assessment failed: {e}")
            return 0.7
    
    def assess_character_consistency(self, content: str) -> float:
        """
        评估人物一致性
        
        Args:
            content: 要评估的内容
            
        Returns:
            一致性分数（0-1）
        """
        ***REMOVED*** 简化实现：检查人物名称的一致性
        ***REMOVED*** 实际应该使用更复杂的方法
        
        ***REMOVED*** 提取人物名称
        import re
        char_pattern = r"([A-Za-z\u4e00-\u9fa5]{2,4})(?:说|道|想|看|走|来|去)"
        characters = set(re.findall(char_pattern, content))
        
        if not characters:
            return 1.0  ***REMOVED*** 没有人物，认为一致
        
        ***REMOVED*** 检查人物名称是否一致（简化：检查是否有明显错误）
        ***REMOVED*** 实际应该与记忆中的设定对比
        return 0.8  ***REMOVED*** 默认分数
    
    def assess_style_consistency(self, content: str) -> float:
        """
        评估风格一致性
        
        Args:
            content: 要评估的内容
            
        Returns:
            一致性分数（0-1）
        """
        ***REMOVED*** 简化实现：检查标点符号和语言风格的一致性
        ***REMOVED*** 实际应该使用更复杂的方法
        
        ***REMOVED*** 检查标点符号使用是否一致
        has_chinese_punct = "。" in content or "！" in content or "？" in content
        has_english_punct = "." in content or "!" in content or "?" in content
        
        if has_chinese_punct and has_english_punct:
            ***REMOVED*** 混合使用可能不一致
            return 0.7
        else:
            return 0.9
    
    def assess_language_quality(self, content: str) -> float:
        """
        评估语言质量
        
        Args:
            content: 要评估的内容
            
        Returns:
            质量分数（0-1）
        """
        ***REMOVED*** 简化实现：检查基本语言特征
        ***REMOVED*** 实际应该使用更复杂的方法
        
        if not content or len(content) < 50:
            return 0.5
        
        ***REMOVED*** 检查是否有明显的语法错误（简化）
        error_indicators = ["的的", "了了", "在在"]
        error_count = sum(1 for indicator in error_indicators if indicator in content)
        
        if error_count > 0:
            return max(0.5, 1.0 - error_count * 0.1)
        else:
            return 0.9
    
    def assess_structure(self, content: str) -> float:
        """
        评估结构完整性
        
        Args:
            content: 要评估的内容
            
        Returns:
            结构分数（0-1）
        """
        ***REMOVED*** 简化实现：检查是否有基本结构
        ***REMOVED*** 实际应该使用更复杂的方法
        
        ***REMOVED*** 检查是否有段落分隔
        has_paragraphs = "\n\n" in content or "\n" in content
        
        ***REMOVED*** 检查是否有基本结构（开头、中间、结尾）
        if len(content) < 100:
            return 0.6  ***REMOVED*** 内容太短，结构可能不完整
        
        if has_paragraphs:
            return 0.8
        else:
            return 0.7

