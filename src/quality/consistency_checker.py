"""
一致性检查器

实现多维度的一致性检查，包括人物、设定、情节、风格等。
"""

import logging
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from ..unimem.types import Memory

logger = logging.getLogger(__name__)


@dataclass
class Issue:
    """一致性问题"""
    type: str  ***REMOVED*** character, setting, plot, style
    severity: str  ***REMOVED*** critical, major, minor
    description: str
    location: Optional[str] = None  ***REMOVED*** 问题位置（章节、段落等）
    suggestion: Optional[str] = None  ***REMOVED*** 修复建议


@dataclass
class ConsistencyReport:
    """一致性检查报告"""
    score: float  ***REMOVED*** 0-1, 1表示完全一致
    issues: List[Issue] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_consistent(self) -> bool:
        """是否一致（无严重问题）"""
        critical_issues = [i for i in self.issues if i.severity == "critical"]
        return len(critical_issues) == 0 and self.score >= 0.7


class ConsistencyChecker:
    """一致性检查器
    
    检查内容在以下维度的一致性：
    - 人物：人物设定、性格、行为的一致性
    - 设定：世界观、时间、地点的一致性
    - 情节：情节逻辑、时间线的一致性
    - 风格：写作风格、语言风格的一致性
    """
    
    def __init__(self, llm_func=None):
        """
        初始化一致性检查器
        
        Args:
            llm_func: LLM 调用函数（用于复杂检查）
        """
        self.llm_func = llm_func
        logger.info("ConsistencyChecker initialized")
    
    def check(
        self,
        content: str,
        memories: List[Memory],
        check_dimensions: Optional[List[str]] = None
    ) -> ConsistencyReport:
        """
        全面一致性检查
        
        Args:
            content: 要检查的内容
            memories: 相关记忆（用于对比）
            check_dimensions: 要检查的维度，如果为None则检查所有维度
            
        Returns:
            一致性检查报告
        """
        if not content:
            return ConsistencyReport(score=0.0, issues=[Issue(
                type="general",
                severity="critical",
                description="内容为空"
            )])
        
        check_dimensions = check_dimensions or ["character", "setting", "plot", "style"]
        
        all_issues = []
        dimension_scores = {}
        
        ***REMOVED*** 提取记忆中的关键信息
        memory_context = self._extract_memory_context(memories)
        
        ***REMOVED*** 检查各维度
        if "character" in check_dimensions:
            char_issues = self.check_character(content, memory_context)
            all_issues.extend(char_issues)
            dimension_scores["character"] = 1.0 - min(len(char_issues) * 0.2, 1.0)
        
        if "setting" in check_dimensions:
            setting_issues = self.check_setting(content, memory_context)
            all_issues.extend(setting_issues)
            dimension_scores["setting"] = 1.0 - min(len(setting_issues) * 0.2, 1.0)
        
        if "plot" in check_dimensions:
            plot_issues = self.check_plot(content, memory_context)
            all_issues.extend(plot_issues)
            dimension_scores["plot"] = 1.0 - min(len(plot_issues) * 0.2, 1.0)
        
        if "style" in check_dimensions:
            style_issues = self.check_style(content, memory_context)
            all_issues.extend(style_issues)
            dimension_scores["style"] = 1.0 - min(len(style_issues) * 0.15, 1.0)
        
        ***REMOVED*** 计算总体分数
        if dimension_scores:
            overall_score = sum(dimension_scores.values()) / len(dimension_scores)
        else:
            overall_score = 1.0
        
        return ConsistencyReport(
            score=overall_score,
            issues=all_issues,
            details={
                "dimension_scores": dimension_scores,
                "total_issues": len(all_issues),
                "critical_issues": len([i for i in all_issues if i.severity == "critical"]),
                "major_issues": len([i for i in all_issues if i.severity == "major"]),
                "minor_issues": len([i for i in all_issues if i.severity == "minor"])
            }
        )
    
    def check_character(self, content: str, memory_context: Dict[str, Any] = None) -> List[Issue]:
        """
        检查人物一致性
        
        Args:
            content: 要检查的内容
            memory_context: 记忆上下文（包含人物设定等）
            
        Returns:
            问题列表
        """
        issues = []
        memory_context = memory_context or {}
        
        ***REMOVED*** 提取内容中的人物信息
        characters_in_content = self._extract_characters(content)
        characters_in_memory = memory_context.get("characters", {})
        
        ***REMOVED*** 检查人物设定一致性
        for char_name, char_info in characters_in_content.items():
            if char_name in characters_in_memory:
                memory_char = characters_in_memory[char_name]
                
                ***REMOVED*** 检查性格一致性
                if "personality" in char_info and "personality" in memory_char:
                    if char_info["personality"] != memory_char["personality"]:
                        issues.append(Issue(
                            type="character",
                            severity="major",
                            description=f"人物 {char_name} 的性格描述不一致",
                            suggestion=f"请统一人物 {char_name} 的性格设定"
                        ))
                
                ***REMOVED*** 检查外貌一致性
                if "appearance" in char_info and "appearance" in memory_char:
                    if char_info["appearance"] != memory_char["appearance"]:
                        issues.append(Issue(
                            type="character",
                            severity="minor",
                            description=f"人物 {char_name} 的外貌描述不一致",
                            suggestion=f"请统一人物 {char_name} 的外貌设定"
                        ))
        
        ***REMOVED*** 使用 LLM 进行更深入的检查
        if self.llm_func and characters_in_memory:
            llm_issues = self._llm_check_character(content, characters_in_memory)
            issues.extend(llm_issues)
        
        return issues
    
    def check_setting(self, content: str, memory_context: Dict[str, Any] = None) -> List[Issue]:
        """
        检查设定一致性
        
        Args:
            content: 要检查的内容
            memory_context: 记忆上下文
            
        Returns:
            问题列表
        """
        issues = []
        memory_context = memory_context or {}
        
        ***REMOVED*** 提取设定信息
        settings_in_content = self._extract_settings(content)
        settings_in_memory = memory_context.get("settings", {})
        
        ***REMOVED*** 检查时间设定
        if "time" in settings_in_content and "time" in settings_in_memory:
            if settings_in_content["time"] != settings_in_memory["time"]:
                issues.append(Issue(
                    type="setting",
                    severity="critical",
                    description="时间设定不一致",
                    suggestion="请统一时间设定"
                ))
        
        ***REMOVED*** 检查地点设定
        if "location" in settings_in_content and "location" in settings_in_memory:
            if settings_in_content["location"] != settings_in_memory["location"]:
                issues.append(Issue(
                    type="setting",
                    severity="major",
                    description="地点设定不一致",
                    suggestion="请统一地点设定"
                ))
        
        return issues
    
    def check_plot(self, content: str, memory_context: Dict[str, Any] = None) -> List[Issue]:
        """
        检查情节一致性
        
        Args:
            content: 要检查的内容
            memory_context: 记忆上下文
            
        Returns:
            问题列表
        """
        issues = []
        
        ***REMOVED*** 简化检查：检查逻辑矛盾
        ***REMOVED*** 实际应该使用更复杂的逻辑推理
        
        ***REMOVED*** 检查时间线
        timeline_issues = self._check_timeline(content, memory_context)
        issues.extend(timeline_issues)
        
        return issues
    
    def check_style(self, content: str, memory_context: Dict[str, Any] = None) -> List[Issue]:
        """
        检查风格一致性
        
        Args:
            content: 要检查的内容
            memory_context: 记忆上下文
            
        Returns:
            问题列表
        """
        issues = []
        memory_context = memory_context or {}
        
        ***REMOVED*** 提取风格特征
        style_in_content = self._extract_style(content)
        style_in_memory = memory_context.get("style", {})
        
        ***REMOVED*** 检查语言风格
        if "tone" in style_in_content and "tone" in style_in_memory:
            if style_in_content["tone"] != style_in_memory["tone"]:
                issues.append(Issue(
                    type="style",
                    severity="minor",
                    description="语言风格不一致",
                    suggestion="请保持统一的语言风格"
                ))
        
        return issues
    
    def _extract_memory_context(self, memories: List[Memory]) -> Dict[str, Any]:
        """从记忆中提取上下文信息"""
        context = {
            "characters": {},
            "settings": {},
            "style": {}
        }
        
        for memory in memories:
            ***REMOVED*** 从记忆元数据中提取信息
            if memory.metadata:
                if "characters" in memory.metadata:
                    context["characters"].update(memory.metadata["characters"])
                if "settings" in memory.metadata:
                    context["settings"].update(memory.metadata["settings"])
                if "style" in memory.metadata:
                    context["style"].update(memory.metadata["style"])
        
        return context
    
    def _extract_characters(self, content: str) -> Dict[str, Dict[str, str]]:
        """从内容中提取人物信息（简化实现）"""
        characters = {}
        
        ***REMOVED*** 使用正则表达式提取人物提及
        ***REMOVED*** 简化实现，实际应该使用更复杂的 NLP 方法
        char_pattern = r"([A-Za-z\u4e00-\u9fa5]{2,4})(?:说|道|想|看|走|来|去)"
        matches = re.findall(char_pattern, content)
        
        for char_name in set(matches):
            characters[char_name] = {
                "name": char_name,
                "mentioned": True
            }
        
        return characters
    
    def _extract_settings(self, content: str) -> Dict[str, str]:
        """从内容中提取设定信息（简化实现）"""
        settings = {}
        
        ***REMOVED*** 提取时间
        time_pattern = r"(?:在|于|是)(\d{4}年|\d{1,2}月|\d{1,2}日|今天|昨天|明天|上午|下午|晚上)"
        time_match = re.search(time_pattern, content)
        if time_match:
            settings["time"] = time_match.group(1)
        
        ***REMOVED*** 提取地点
        location_pattern = r"(?:在|到|去)([A-Za-z\u4e00-\u9fa5]{2,10}(?:市|县|区|镇|村|家|公司|学校|医院))"
        location_match = re.search(location_pattern, content)
        if location_match:
            settings["location"] = location_match.group(1)
        
        return settings
    
    def _extract_style(self, content: str) -> Dict[str, str]:
        """从内容中提取风格特征（简化实现）"""
        style = {}
        
        ***REMOVED*** 判断语调（简化）
        if "！" in content or "!" in content:
            style["tone"] = "excited"
        elif "？" in content or "?" in content:
            style["tone"] = "questioning"
        else:
            style["tone"] = "neutral"
        
        return style
    
    def _check_timeline(self, content: str, memory_context: Dict[str, Any]) -> List[Issue]:
        """检查时间线一致性"""
        issues = []
        ***REMOVED*** 简化实现
        return issues
    
    def _llm_check_character(
        self,
        content: str,
        characters: Dict[str, Dict[str, Any]]
    ) -> List[Issue]:
        """使用 LLM 进行人物一致性检查"""
        if not self.llm_func:
            return []
        
        try:
            prompt = f"""请检查以下内容中的人物设定是否与已知人物设定一致：

已知人物设定：
{self._format_characters(characters)}

待检查内容：
{content}

请指出任何不一致的地方，包括：
1. 人物性格描述不一致
2. 人物行为不符合设定
3. 人物关系描述不一致

如果没有问题，请回复"无问题"。"""
            
            from ..unimem.chat import ark_deepseek_v3_2
            llm_func = self.llm_func or ark_deepseek_v3_2
            messages = [{"role": "user", "content": prompt}]
            _, response = llm_func(messages)
            
            ***REMOVED*** 解析响应
            if "无问题" not in response and "一致" in response.lower():
                return [Issue(
                    type="character",
                    severity="major",
                    description="LLM检测到人物设定不一致",
                    suggestion=response[:200]  ***REMOVED*** 截取前200字符作为建议
                )]
            
            return []
        except Exception as e:
            logger.warning(f"LLM character check failed: {e}")
            return []
    
    def _format_characters(self, characters: Dict[str, Dict[str, Any]]) -> str:
        """格式化人物设定"""
        lines = []
        for name, info in characters.items():
            lines.append(f"{name}: {info}")
        return "\n".join(lines)

