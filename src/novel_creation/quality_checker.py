"""
质量检查系统
用于检查小说创作的一致性、连贯性、风格等
"""
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class IssueType(Enum):
    """问题类型"""
    CHARACTER_INCONSISTENCY = "character_inconsistency"  ***REMOVED*** 角色不一致
    WORLDVIEW_INCONSISTENCY = "worldview_inconsistency"  ***REMOVED*** 世界观不一致
    TIMELINE_INCONSISTENCY = "timeline_inconsistency"  ***REMOVED*** 时间线不一致
    PLOT_INCONSISTENCY = "plot_inconsistency"  ***REMOVED*** 情节不一致
    COHERENCE_ISSUE = "coherence_issue"  ***REMOVED*** 连贯性问题
    STYLE_ISSUE = "style_issue"  ***REMOVED*** 风格问题


class IssueSeverity(Enum):
    """问题严重程度"""
    LOW = "low"  ***REMOVED*** 轻微问题
    MEDIUM = "medium"  ***REMOVED*** 中等问题
    HIGH = "high"  ***REMOVED*** 严重问题


@dataclass
class QualityIssue:
    """质量问题"""
    issue_type: IssueType
    severity: IssueSeverity
    description: str
    location: str  ***REMOVED*** 问题位置（如章节号、行号）
    suggestion: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class QualityChecker:
    """
    质量检查器
    
    检查小说创作的一致性、连贯性、风格等
    """
    
    def __init__(self, llm_client=None):
        """
        初始化质量检查器
        
        Args:
            llm_client: LLM 客户端（可选，用于高级检查）
        """
        self.llm_client = llm_client
    
    def check_chapter(
        self,
        chapter_content: str,
        chapter_number: int,
        previous_chapters: List[Dict[str, Any]],
        novel_plan: Optional[Dict[str, Any]] = None,
        semantic_mesh_entities: Optional[Dict[str, Any]] = None
    ) -> List[QualityIssue]:
        """
        检查章节质量
        
        Args:
            chapter_content: 章节内容
            chapter_number: 章节编号
            previous_chapters: 前面章节列表 [{"number": int, "content": str, "summary": str}, ...]
            novel_plan: 小说大纲（可选）
        
        Returns:
            质量问题列表
        """
        issues = []
        
        ***REMOVED*** 1. 角色一致性检查（使用语义网格实体进行深度检查）
        character_issues = self.check_character_consistency(
            chapter_content, chapter_number, previous_chapters, semantic_mesh_entities
        )
        issues.extend(character_issues)
        
        ***REMOVED*** 2. 世界观一致性检查
        worldview_issues = self.check_worldview_consistency(
            chapter_content, chapter_number, previous_chapters
        )
        issues.extend(worldview_issues)
        
        ***REMOVED*** 3. 时间线一致性检查
        timeline_issues = self.check_timeline_consistency(
            chapter_content, chapter_number, previous_chapters
        )
        issues.extend(timeline_issues)
        
        ***REMOVED*** 4. 情节逻辑检查
        plot_issues = self.check_plot_consistency(
            chapter_content, chapter_number, previous_chapters, novel_plan
        )
        issues.extend(plot_issues)
        
        ***REMOVED*** 5. 连贯性检查
        coherence_issues = self.check_coherence(
            chapter_content, chapter_number, previous_chapters
        )
        issues.extend(coherence_issues)
        
        ***REMOVED*** 6. 基础风格检查
        style_issues = self.check_style_basic(chapter_content, chapter_number)
        issues.extend(style_issues)
        
        return issues
    
    def check_character_consistency(
        self,
        chapter_content: str,
        chapter_number: int,
        previous_chapters: List[Dict[str, Any]],
        semantic_mesh_entities: Optional[Dict[str, Any]] = None
    ) -> List[QualityIssue]:
        """
        检查角色一致性
        
        Args:
            chapter_content: 章节内容
            chapter_number: 章节编号
            previous_chapters: 前面章节列表
            semantic_mesh_entities: 语义网格中的实体（可选，用于深度检查）
        
        Returns:
            角色一致性问题列表
        """
        issues = []
        
        ***REMOVED*** 提取本章角色
        chapter_characters = self._extract_characters(chapter_content)
        
        ***REMOVED*** 如果提供了语义网格实体，使用更深入的检查
        if semantic_mesh_entities:
            ***REMOVED*** 从语义网格中获取前面章节的角色实体
            previous_character_entities = {}
            for entity_id, entity in semantic_mesh_entities.items():
                if entity.get('type') == 'character':
                    entity_chapter = entity.get('metadata', {}).get('chapter', 0)
                    if entity_chapter > 0 and entity_chapter < chapter_number:
                        char_name = entity.get('name', '')
                        if char_name:
                            if char_name not in previous_character_entities:
                                previous_character_entities[char_name] = entity
            
            ***REMOVED*** 检查本章角色与语义网格中的角色一致性
            for char in chapter_characters:
                if char in previous_character_entities:
                    ***REMOVED*** 角色在语义网格中存在，可以进行更深入的检查
                    prev_entity = previous_character_entities[char]
                    prev_content = prev_entity.get('content', '')
                    
                    ***REMOVED*** 可以检查角色描述的一致性（简单检查）
                    ***REMOVED*** 这里可以扩展为更复杂的检查逻辑
                    pass
                else:
                    ***REMOVED*** 检查是否有相似的名称（可能是拼写错误）
                    for prev_char, prev_entity in previous_character_entities.items():
                        if char != prev_char and self._is_similar_name(char, prev_char):
                            issues.append(QualityIssue(
                                issue_type=IssueType.CHARACTER_INCONSISTENCY,
                                severity=IssueSeverity.MEDIUM,
                                description=f"角色名称可能不一致：'{char}' 和 '{prev_char}' 相似",
                                location=f"第{chapter_number}章",
                                suggestion=f"请确认是否为同一角色，建议统一使用 '{prev_char}'",
                                metadata={
                                    "character1": char,
                                    "character2": prev_char,
                                    "prev_chapter": prev_entity.get('metadata', {}).get('chapter', 0)
                                }
                            ))
        else:
            ***REMOVED*** 使用基础检查（文本匹配）
            if previous_chapters:
                previous_characters = {}
                for prev_chapter in previous_chapters:
                    prev_chars = self._extract_characters(prev_chapter.get('content', ''))
                    for char in prev_chars:
                        if char not in previous_characters:
                            previous_characters[char] = prev_chapter.get('number', 0)
                
                ***REMOVED*** 检查角色名称一致性（简单检查）
                for char in chapter_characters:
                    ***REMOVED*** 检查是否有相似的名称（可能是拼写错误）
                    for prev_char in previous_characters:
                        if char != prev_char and self._is_similar_name(char, prev_char):
                            issues.append(QualityIssue(
                                issue_type=IssueType.CHARACTER_INCONSISTENCY,
                                severity=IssueSeverity.MEDIUM,
                                description=f"角色名称可能不一致：'{char}' 和 '{prev_char}' 相似",
                                location=f"第{chapter_number}章",
                                suggestion=f"请确认是否为同一角色，建议统一使用 '{prev_char}'",
                                metadata={
                                    "character1": char,
                                    "character2": prev_char,
                                    "prev_chapter": previous_characters[prev_char]
                                }
                            ))
        
        return issues
    
    def check_worldview_consistency(
        self,
        chapter_content: str,
        chapter_number: int,
        previous_chapters: List[Dict[str, Any]]
    ) -> List[QualityIssue]:
        """
        检查世界观一致性
        
        Args:
            chapter_content: 章节内容
            chapter_number: 章节编号
            previous_chapters: 前面章节列表
        
        Returns:
            世界观一致性问题列表
        """
        issues = []
        
        ***REMOVED*** 提取世界观关键词
        worldview_keywords = {
            "时间": ["时间", "时空", "时间线", "时间旅行"],
            "地点": ["世界", "星球", "大陆", "国家", "城市"],
            "科技": ["科技", "技术", "设备", "机器", "系统"],
            "魔法": ["魔法", "法术", "魔力", "咒语"],
            "生物": ["人类", "种族", "生物", "怪物"],
        }
        
        ***REMOVED*** 检查本章的世界观设定
        chapter_worldview = {}
        for category, keywords in worldview_keywords.items():
            for keyword in keywords:
                if keyword in chapter_content:
                    chapter_worldview[category] = chapter_worldview.get(category, 0) + 1
        
        ***REMOVED*** 与前面章节对比（简单检查）
        if previous_chapters:
            for prev_chapter in previous_chapters:
                prev_content = prev_chapter.get('content', '')
                
                ***REMOVED*** 检查冲突的世界观设定
                ***REMOVED*** 例如：前面章节没有魔法，但本章提到魔法
                has_magic_in_prev = any(kw in prev_content for kw in worldview_keywords["魔法"])
                has_magic_in_current = any(kw in chapter_content for kw in worldview_keywords["魔法"])
                
                if not has_magic_in_prev and has_magic_in_current and chapter_worldview.get("魔法", 0) > 2:
                    issues.append(QualityIssue(
                        issue_type=IssueType.WORLDVIEW_INCONSISTENCY,
                        severity=IssueSeverity.HIGH,
                        description="世界观不一致：前面章节未提及魔法，但本章多次出现魔法相关设定",
                        location=f"第{chapter_number}章",
                        suggestion="如果这是新的世界观设定，建议在前面章节中铺垫",
                        metadata={
                            "category": "魔法",
                            "prev_chapter": prev_chapter.get('number', 0)
                        }
                    ))
        
        return issues
    
    def check_timeline_consistency(
        self,
        chapter_content: str,
        chapter_number: int,
        previous_chapters: List[Dict[str, Any]]
    ) -> List[QualityIssue]:
        """
        检查时间线一致性
        
        Args:
            chapter_content: 章节内容
            chapter_number: 章节编号
            previous_chapters: 前面章节列表
        
        Returns:
            时间线一致性问题列表
        """
        issues = []
        
        ***REMOVED*** 提取时间信息
        time_patterns = [
            r'(\d{4})年',  ***REMOVED*** 2023年
            r'(\d+)天前',  ***REMOVED*** 3天前
            r'(\d+)小时后',  ***REMOVED*** 2小时后
            r'第二天', r'第三天',
            r'次日', r'当晚', r'第二天早上',
        ]
        
        chapter_times = []
        for pattern in time_patterns:
            matches = re.findall(pattern, chapter_content)
            chapter_times.extend(matches)
        
        ***REMOVED*** 简单检查：如果章节编号递增，但时间描述倒退了，可能有问题
        if len(chapter_times) > 0 and chapter_number > 1:
            ***REMOVED*** 这里可以添加更复杂的时间线检查逻辑
            pass
        
        return issues
    
    def check_plot_consistency(
        self,
        chapter_content: str,
        chapter_number: int,
        previous_chapters: List[Dict[str, Any]],
        novel_plan: Optional[Dict[str, Any]] = None
    ) -> List[QualityIssue]:
        """
        检查情节逻辑一致性
        
        Args:
            chapter_content: 章节内容
            chapter_number: 章节编号
            previous_chapters: 前面章节列表
            novel_plan: 小说大纲
        
        Returns:
            情节一致性问题列表
        """
        issues = []
        
        ***REMOVED*** 如果有大纲，检查章节是否符合大纲
        if novel_plan:
            chapter_outline = novel_plan.get('chapter_outline', [])
            if chapter_number <= len(chapter_outline):
                expected_summary = chapter_outline[chapter_number - 1].get('summary', '')
                if expected_summary:
                    ***REMOVED*** 简单检查：章节内容是否包含大纲中的关键词
                    keywords = self._extract_keywords(expected_summary)
                    found_keywords = sum(1 for kw in keywords if kw in chapter_content)
                    
                    if found_keywords < len(keywords) * 0.3:  ***REMOVED*** 如果少于30%关键词出现
                        issues.append(QualityIssue(
                            issue_type=IssueType.PLOT_INCONSISTENCY,
                            severity=IssueSeverity.MEDIUM,
                            description=f"章节内容可能偏离大纲：预期关键词大部分未出现",
                            location=f"第{chapter_number}章",
                            suggestion="请检查章节是否按照大纲展开情节",
                            metadata={
                                "expected_keywords": keywords[:5],
                                "found_ratio": found_keywords / len(keywords) if keywords else 0
                            }
                        ))
        
        return issues
    
    def check_coherence(
        self,
        chapter_content: str,
        chapter_number: int,
        previous_chapters: List[Dict[str, Any]]
    ) -> List[QualityIssue]:
        """
        检查连贯性
        
        Args:
            chapter_content: 章节内容
            chapter_number: 章节编号
            previous_chapters: 前面章节列表
        
        Returns:
            连贯性问题列表
        """
        issues = []
        
        if not previous_chapters:
            return issues
        
        ***REMOVED*** 检查是否与前章有衔接
        last_chapter = previous_chapters[-1]
        last_content = last_chapter.get('content', '')
        
        ***REMOVED*** 提取前章的结尾关键词
        last_sentences = last_content.split('。')[-3:]  ***REMOVED*** 最后3句话
        last_keywords = []
        for sent in last_sentences:
            last_keywords.extend(self._extract_keywords(sent))
        
        ***REMOVED*** 检查本章开头是否与前章有衔接
        first_sentences = chapter_content.split('。')[:3]  ***REMOVED*** 前3句话
        first_content = '。'.join(first_sentences)
        
        ***REMOVED*** 如果前章和本章完全没有共同关键词，可能缺乏衔接
        common_keywords = [kw for kw in last_keywords if kw in first_content]
        if len(last_keywords) > 0 and len(common_keywords) == 0:
            issues.append(QualityIssue(
                issue_type=IssueType.COHERENCE_ISSUE,
                severity=IssueSeverity.LOW,
                description="章节间可能缺乏衔接：前章结尾与本章开头没有共同关键词",
                location=f"第{chapter_number}章开头",
                suggestion="考虑在前章结尾或本章开头添加过渡性的描述",
                metadata={
                    "last_keywords": last_keywords[:5],
                    "first_sentences": first_sentences
                }
            ))
        
        return issues
    
    def check_style_basic(
        self,
        chapter_content: str,
        chapter_number: int
    ) -> List[QualityIssue]:
        """
        基础风格检查
        
        Args:
            chapter_content: 章节内容
            chapter_number: 章节编号
        
        Returns:
            风格问题列表
        """
        issues = []
        
        ***REMOVED*** 检查过长段落
        paragraphs = chapter_content.split('\n\n')
        for i, para in enumerate(paragraphs):
            if len(para) > 1000:  ***REMOVED*** 段落超过1000字
                issues.append(QualityIssue(
                    issue_type=IssueType.STYLE_ISSUE,
                    severity=IssueSeverity.LOW,
                    description=f"段落过长：第{i+1}段超过1000字",
                    location=f"第{chapter_number}章，第{i+1}段",
                    suggestion="考虑将长段落拆分为多个段落",
                    metadata={"paragraph_length": len(para)}
                ))
        
        ***REMOVED*** 检查过多重复词汇
        words = re.findall(r'[\u4e00-\u9fa5]+', chapter_content)
        word_freq = {}
        for word in words:
            if len(word) >= 2:  ***REMOVED*** 至少2个字符
                word_freq[word] = word_freq.get(word, 0) + 1
        
        ***REMOVED*** 找出重复次数过多的词
        for word, count in word_freq.items():
            if count > 20:  ***REMOVED*** 出现超过20次
                issues.append(QualityIssue(
                    issue_type=IssueType.STYLE_ISSUE,
                    severity=IssueSeverity.LOW,
                    description=f"词汇重复过多：'{word}' 在本章出现 {count} 次",
                    location=f"第{chapter_number}章",
                    suggestion="考虑使用同义词替换部分出现",
                    metadata={"word": word, "count": count}
                ))
        
        return issues
    
    ***REMOVED*** 辅助方法
    
    def _extract_characters(self, text: str) -> List[str]:
        """提取角色名称"""
        ***REMOVED*** 简单提取：引号内的内容可能是对话，提取说话者
        ***REMOVED*** 或者使用角色名称模式
        
        ***REMOVED*** 提取引号内的对话（说话者通常在前面）
        dialogue_pattern = r'["""]([^"""]{2,50})["""]'
        dialogues = re.findall(dialogue_pattern, text)
        
        ***REMOVED*** 提取 "XXX说道" 模式
        speaker_pattern = r'([A-Za-z\u4e00-\u9fa5]{2,10})\s*[说道说]'
        speakers = re.findall(speaker_pattern, text)
        
        ***REMOVED*** 合并并去重
        characters = list(set(speakers + [d[:10] for d in dialogues if len(d) < 10]))
        
        ***REMOVED*** 过滤明显不是角色的词
        exclude_words = ["这个", "那个", "什么", "怎么", "为什么", "是否"]
        characters = [c for c in characters if c not in exclude_words]
        
        return characters[:20]  ***REMOVED*** 最多返回20个
    
    def _is_similar_name(self, name1: str, name2: str) -> bool:
        """检查两个名称是否相似（可能是拼写错误）"""
        ***REMOVED*** 简单检查：如果名称长度相同且只有一个字符不同
        if len(name1) != len(name2):
            return False
        
        if len(name1) < 2:
            return False
        
        diff_count = sum(1 for c1, c2 in zip(name1, name2) if c1 != c2)
        return diff_count == 1  ***REMOVED*** 只有一个字符不同
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        ***REMOVED*** 简单提取：2-5个字符的连续中文字符
        keywords = re.findall(r'[\u4e00-\u9fa5]{2,5}', text)
        
        ***REMOVED*** 过滤停用词
        stop_words = ["的", "了", "在", "是", "和", "与", "或", "但", "而", "为", "从", "到"]
        keywords = [kw for kw in keywords if kw not in stop_words]
        
        return list(set(keywords))[:10]  ***REMOVED*** 最多返回10个不重复的关键词


def check_chapter_quality(
    chapter_content: str,
    chapter_number: int,
    previous_chapters: List[Dict[str, Any]],
    novel_plan: Optional[Dict[str, Any]] = None,
    llm_client=None
) -> Dict[str, Any]:
    """
    检查章节质量的便捷函数
    
    Args:
        chapter_content: 章节内容
        chapter_number: 章节编号
        previous_chapters: 前面章节列表
        novel_plan: 小说大纲
        llm_client: LLM 客户端（可选）
    
    Returns:
        检查结果字典
    """
    checker = QualityChecker(llm_client=llm_client)
    issues = checker.check_chapter(
        chapter_content, chapter_number, previous_chapters, novel_plan
    )
    
    ***REMOVED*** 统计问题
    by_type = {}
    by_severity = {}
    
    for issue in issues:
        issue_type = issue.issue_type.value
        severity = issue.severity.value
        
        by_type[issue_type] = by_type.get(issue_type, 0) + 1
        by_severity[severity] = by_severity.get(severity, 0) + 1
    
    return {
        "total_issues": len(issues),
        "issues": [issue.__dict__ for issue in issues],
        "by_type": by_type,
        "by_severity": by_severity,
        "has_high_severity": IssueSeverity.HIGH.value in by_severity
    }
