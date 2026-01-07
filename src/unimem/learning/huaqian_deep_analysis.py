"""
《花千骨》深度分析模块

基于章节结构、时序信息和目录，深度挖掘动态编排和记忆系统的潜力
"""

import re
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class HuaqianDeepAnalyzer:
    """《花千骨》深度分析器"""
    
    def __init__(self, filepath: str):
        """
        初始化分析器
        
        Args:
            filepath: 小说文件路径
        """
        self.filepath = filepath
        self.raw_text = ""
        self.volumes = []  ***REMOVED*** 卷结构
        self.chapters = []  ***REMOVED*** 章节列表
        self.timeline = []  ***REMOVED*** 时序信息
        
    def load_and_parse(self):
        """加载并解析小说"""
        logger.info(f"加载小说: {self.filepath}")
        
        with open(self.filepath, 'r', encoding='utf-8', errors='ignore') as f:
            self.raw_text = f.read()
        
        logger.info(f"文本长度: {len(self.raw_text):,} 字符")
        
        ***REMOVED*** 解析结构
        self._parse_structure()
        self._parse_timeline()
        self._analyze_narrative_progression()
    
    def _parse_structure(self):
        """解析章节结构"""
        lines = self.raw_text.split('\n')
        
        current_volume = None
        current_chapter = None
        chapter_content = []
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            ***REMOVED*** 匹配卷标题：卷一、卷二等（更宽松的匹配）
            volume_match = re.search(r'卷([一二三四五六七八九十]+)[：:・]\s*(.+)', line_stripped)
            if volume_match and "仙侠奇缘之花千骨" in line_stripped:
                ***REMOVED*** 保存前一卷
                if current_volume:
                    self.volumes.append(current_volume)
                
                volume_num = self._chinese_to_number(volume_match.group(1))
                volume_title = volume_match.group(2).strip()
                
                current_volume = {
                    "volume_number": volume_num,
                    "volume_title": volume_title,
                    "chapters": [],
                    "start_line": i,
                }
                continue
            
            ***REMOVED*** 匹配章节元数据行：包含"章节字数"和"更新时间"
            chapter_meta_match = re.match(r'章节字数[：:]\s*(\d+)\s+更新时间[：:]\s*(\d{2}-\d{2}-\d{2}\s+\d{2}:\d{2})', line_stripped)
            if chapter_meta_match:
                word_count = int(chapter_meta_match.group(1))
                update_time = chapter_meta_match.group(2)
                
                ***REMOVED*** 下一行通常是章节标题
                if i + 1 < len(lines):
                    chapter_title = lines[i + 1].strip()
                    
                    ***REMOVED*** 保存前一章
                    if current_chapter:
                        current_chapter["content"] = "\n".join(chapter_content)
                        current_chapter["word_count"] = len(current_chapter["content"])
                        if current_volume:
                            current_volume["chapters"].append(current_chapter)
                    
                    ***REMOVED*** 创建新章节
                    current_chapter = {
                        "chapter_number": len([c for c in self.chapters if c.get("volume_number") == (current_volume["volume_number"] if current_volume else 0)]) + 1,
                        "volume_number": current_volume["volume_number"] if current_volume else 0,
                        "chapter_title": chapter_title,
                        "meta_word_count": word_count,
                        "update_time": update_time,
                        "content": "",
                        "start_line": i + 1,
                    }
                    self.chapters.append(current_chapter)
                    chapter_content = []
                continue
            
            ***REMOVED*** 收集章节内容
            if current_chapter:
                chapter_content.append(line)
        
        ***REMOVED*** 保存最后一章和最后一卷
        if current_chapter:
            current_chapter["content"] = "\n".join(chapter_content)
            current_chapter["word_count"] = len(current_chapter["content"])
            if current_volume:
                current_volume["chapters"].append(current_chapter)
        
        if current_volume:
            self.volumes.append(current_volume)
        
        logger.info(f"解析完成: {len(self.volumes)} 卷, {len(self.chapters)} 章")
    
    def _chinese_to_number(self, chinese: str) -> int:
        """中文数字转阿拉伯数字（支持更多格式）"""
        mapping = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
            '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20,
        }
        ***REMOVED*** 支持"十一"、"十二"等
        if chinese in mapping:
            return mapping[chinese]
        ***REMOVED*** 尝试提取数字
        import re
        num_match = re.search(r'\d+', chinese)
        if num_match:
            return int(num_match.group())
        return 0
    
    def _parse_timeline(self):
        """解析时序信息"""
        for chapter in self.chapters:
            update_time = chapter.get("update_time")
            if update_time:
                try:
                    ***REMOVED*** 解析时间：09-07-12 14:30
                    time_str = f"20{update_time}"  ***REMOVED*** 假设是2009年
                    dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
                    
                    self.timeline.append({
                        "chapter_number": chapter["chapter_number"],
                        "volume_number": chapter["volume_number"],
                        "update_time": dt,
                        "word_count": chapter.get("meta_word_count", 0),
                        "chapter_title": chapter["chapter_title"],
                    })
                except Exception as e:
                    logger.warning(f"解析时间失败 {update_time}: {e}")
        
        ***REMOVED*** 按时间排序
        self.timeline.sort(key=lambda x: x["update_time"])
        
        logger.info(f"解析时序: {len(self.timeline)} 条记录")
    
    def _analyze_narrative_progression(self):
        """分析叙事推进模式"""
        ***REMOVED*** 分析每章的推进强度
        for chapter in self.chapters:
            content = chapter.get("content", "")
            
            ***REMOVED*** 推进指标
            chapter["progression_indicators"] = {
                "plot_advancement": self._detect_plot_advancement(content),
                "character_development": self._detect_character_development(content),
                "conflict_intensity": self._detect_conflict_intensity(content),
                "emotional_intensity": self._detect_emotional_intensity(content),
            }
    
    def _detect_plot_advancement(self, content: str) -> float:
        """检测情节推进强度（0-1）"""
        advancement_keywords = [
            "发现", "得知", "明白", "决定", "前往", "来到", "开始",
            "终于", "突然", "意外", "原来", "竟然", "不料",
        ]
        
        count = sum(1 for keyword in advancement_keywords if keyword in content)
        return min(count / 20.0, 1.0)  ***REMOVED*** 归一化
    
    def _detect_character_development(self, content: str) -> float:
        """检测角色发展强度"""
        development_keywords = [
            "成长", "变化", "学会", "明白", "理解", "感悟",
            "醒悟", "改变", "进步", "提升", "突破",
        ]
        
        count = sum(1 for keyword in development_keywords if keyword in content)
        return min(count / 15.0, 1.0)
    
    def _detect_conflict_intensity(self, content: str) -> float:
        """检测冲突强度"""
        conflict_keywords = [
            "战斗", "对抗", "冲突", "矛盾", "争执", "打斗",
            "攻击", "防御", "危险", "危机", "威胁", "敌人",
        ]
        
        count = sum(1 for keyword in conflict_keywords if keyword in content)
        return min(count / 25.0, 1.0)
    
    def _detect_emotional_intensity(self, content: str) -> float:
        """检测情感强度"""
        emotional_keywords = [
            "心痛", "感动", "悲伤", "愤怒", "恐惧", "惊喜",
            "喜欢", "爱", "恨", "痛苦", "绝望", "希望",
        ]
        
        count = sum(1 for keyword in emotional_keywords if keyword in content)
        return min(count / 20.0, 1.0)
    
    def analyze_dynamic_orchestration_patterns(self) -> Dict[str, Any]:
        """分析动态编排模式"""
        patterns = {
            "volume_transitions": [],  ***REMOVED*** 卷之间的转换模式
            "chapter_sequences": [],   ***REMOVED*** 章节序列模式
            "progression_patterns": [], ***REMOVED*** 推进模式
            "pacing_patterns": [],      ***REMOVED*** 节奏模式
        }
        
        ***REMOVED*** 1. 分析卷之间的转换
        for i in range(len(self.volumes) - 1):
            vol1 = self.volumes[i]
            vol2 = self.volumes[i + 1]
            
            transition = {
                "from_volume": vol1["volume_number"],
                "to_volume": vol2["volume_number"],
                "chapter_count_change": len(vol2["chapters"]) - len(vol1["chapters"]),
                "narrative_shift": self._analyze_narrative_shift(
                    vol1["chapters"][-1] if vol1["chapters"] else None,
                    vol2["chapters"][0] if vol2["chapters"] else None
                ),
            }
            patterns["volume_transitions"].append(transition)
        
        ***REMOVED*** 2. 分析章节序列模式
        chapter_sequences = []
        for vol in self.volumes:
            vol_sequence = []
            for ch in vol["chapters"]:
                indicators = ch.get("progression_indicators", {})
                vol_sequence.append({
                    "chapter": ch["chapter_title"],
                    "plot": indicators.get("plot_advancement", 0),
                    "character": indicators.get("character_development", 0),
                    "conflict": indicators.get("conflict_intensity", 0),
                    "emotion": indicators.get("emotional_intensity", 0),
                })
            chapter_sequences.append({
                "volume": vol["volume_number"],
                "sequence": vol_sequence
            })
        patterns["chapter_sequences"] = chapter_sequences
        
        ***REMOVED*** 3. 分析推进模式（根据时间序列）
        progression_curve = []
        for timeline_item in self.timeline:
            ch_num = timeline_item["chapter_number"]
            chapter = next((c for c in self.chapters if c["chapter_number"] == ch_num), None)
            if chapter:
                indicators = chapter.get("progression_indicators", {})
                progression_curve.append({
                    "time": timeline_item["update_time"].isoformat(),
                    "total_intensity": sum(indicators.values()),
                    "indicators": indicators,
                })
        patterns["progression_patterns"] = progression_curve
        
        ***REMOVED*** 4. 分析节奏模式（更新频率、章节长度变化）
        pacing = []
        for i in range(len(self.timeline) - 1):
            time_diff = (self.timeline[i + 1]["update_time"] - self.timeline[i]["update_time"]).total_seconds() / 3600  ***REMOVED*** 小时
            word_diff = self.timeline[i + 1]["word_count"] - self.timeline[i]["word_count"]
            
            pacing.append({
                "interval_hours": time_diff,
                "word_count": self.timeline[i + 1]["word_count"],
                "productivity": self.timeline[i + 1]["word_count"] / max(time_diff, 1),  ***REMOVED*** 字/小时
            })
        patterns["pacing_patterns"] = pacing
        
        return patterns
    
    def _analyze_narrative_shift(self, ch1: Optional[Dict], ch2: Optional[Dict]) -> str:
        """分析叙事转换类型"""
        if not ch1 or not ch2:
            return "unknown"
        
        ind1 = ch1.get("progression_indicators", {})
        ind2 = ch2.get("progression_indicators", {})
        
        ***REMOVED*** 计算变化
        plot_change = ind2.get("plot_advancement", 0) - ind1.get("plot_advancement", 0)
        conflict_change = ind2.get("conflict_intensity", 0) - ind1.get("conflict_intensity", 0)
        
        if conflict_change > 0.3:
            return "conflict_escalation"
        elif plot_change > 0.3:
            return "plot_acceleration"
        elif conflict_change < -0.2:
            return "conflict_resolution"
        else:
            return "gradual_progression"
    
    def extract_memory_patterns(self) -> List[Dict[str, Any]]:
        """提取记忆模式"""
        memory_patterns = []
        
        ***REMOVED*** 1. 卷级别的模式
        for vol in self.volumes:
            pattern = {
                "type": "volume_pattern",
                "volume_number": vol["volume_number"],
                "title": vol["volume_title"],
                "chapter_count": len(vol["chapters"]),
                "key_elements": self._extract_key_elements(vol),
                "narrative_theme": self._infer_theme(vol),
            }
            memory_patterns.append(pattern)
        
        ***REMOVED*** 2. 章节级别的模式
        for chapter in self.chapters[:20]:  ***REMOVED*** 先分析前20章
            pattern = {
                "type": "chapter_pattern",
                "chapter_number": chapter["chapter_number"],
                "title": chapter["chapter_title"],
                "progression_indicators": chapter.get("progression_indicators", {}),
                "key_events": self._extract_key_events(chapter),
                "character_focus": self._extract_character_focus(chapter),
            }
            memory_patterns.append(pattern)
        
        ***REMOVED*** 3. 时序模式
        for i in range(len(self.timeline) - 1):
            interval = self.timeline[i + 1]["update_time"] - self.timeline[i]["update_time"]
            pattern = {
                "type": "temporal_pattern",
                "interval_hours": interval.total_seconds() / 3600,
                "word_count": self.timeline[i + 1]["word_count"],
                "productivity": self.timeline[i + 1]["word_count"] / max(interval.total_seconds() / 3600, 1),
            }
            memory_patterns.append(pattern)
        
        return memory_patterns
    
    def extract_with_reme_inspiration(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        使用 ReMe 启发的多面蒸馏提取经验
        
        Returns:
            {
                "success": [...],
                "failure": [...],
                "comparison": [...]
            }
        """
        from .reme_inspired_extractor import RemeInspiredExtractor
        
        extractor = RemeInspiredExtractor()
        
        ***REMOVED*** 将 chapters 转换为提取器需要的格式
        chapters_data = []
        for ch in self.chapters:
            chapters_data.append({
                "chapter_number": ch.get("chapter_number"),
                "chapter_title": ch.get("chapter_title"),
                "content": ch.get("content", ""),
                "source_novel": "花千骨",  ***REMOVED*** 可以从配置获取
            })
        
        ***REMOVED*** 执行多面蒸馏
        experiences = extractor.extract_all(chapters_data)
        
        ***REMOVED*** 转换为字典格式（用于 JSON 序列化）
        result = {
            "success": [exp.to_dict() for exp in experiences["success"]],
            "failure": [exp.to_dict() for exp in experiences["failure"]],
            "comparison": [exp.to_dict() for exp in experiences["comparison"]],
        }
        
        return result
    
    def _extract_key_elements(self, volume: Dict) -> List[str]:
        """提取卷的关键元素"""
        all_text = " ".join([ch.get("content", "") for ch in volume.get("chapters", [])])
        
        ***REMOVED*** 提取关键名词短语（简化版）
        key_phrases = re.findall(r'[一-龥]{3,6}', all_text[:10000])  ***REMOVED*** 前10000字
        from collections import Counter
        common = Counter(key_phrases).most_common(5)
        
        return [phrase for phrase, count in common if count > 3]
    
    def _infer_theme(self, volume: Dict) -> str:
        """推断叙事主题"""
        title = volume.get("volume_title", "")
        
        theme_keywords = {
            "成长": ["成长", "历练", "修炼", "进步"],
            "冲突": ["战斗", "对抗", "危机", "危险"],
            "情感": ["情", "爱", "恋", "心"],
            "探索": ["寻找", "发现", "探索", "冒险"],
        }
        
        for theme, keywords in theme_keywords.items():
            if any(kw in title for kw in keywords):
                return theme
        
        return "综合"
    
    def _extract_key_events(self, chapter: Dict) -> List[str]:
        """提取章节关键事件"""
        content = chapter.get("content", "")
        
        ***REMOVED*** 查找动作性句子
        event_patterns = [
            r'[^。！？]{0,20}(发现|得知|决定|前往|遇到|见到|开始|结束)[^。！？]{0,20}[。！？]',
        ]
        
        events = []
        for pattern in event_patterns:
            matches = re.findall(pattern, content[:5000])  ***REMOVED*** 前5000字
            events.extend(matches[:3])  ***REMOVED*** 最多3个
        
        return events
    
    def _extract_character_focus(self, chapter: Dict) -> List[str]:
        """提取章节关注的角色"""
        content = chapter.get("content", "")
        
        ***REMOVED*** 常见角色名（从作品关键字提取）
        known_characters = ["花千骨", "白子画", "杀阡陌", "轩辕朗"]
        
        character_mentions = []
        for char in known_characters:
            count = content.count(char)
            if count > 5:
                character_mentions.append((char, count))
        
        return [char for char, count in sorted(character_mentions, key=lambda x: x[1], reverse=True)[:3]]
    
    def generate_orchestration_insights(self) -> Dict[str, Any]:
        """生成编排洞察"""
        insights = {
            "agent_selection_patterns": [],
            "tool_usage_patterns": [],
            "memory_retrieval_patterns": [],
            "decision_points": [],
        }
        
        ***REMOVED*** 1. 根据章节类型推断需要的Agent
        for chapter in self.chapters:
            indicators = chapter.get("progression_indicators", {})
            
            ***REMOVED*** 高情节推进 -> 需要 planning agent
            if indicators.get("plot_advancement", 0) > 0.5:
                insights["agent_selection_patterns"].append({
                    "chapter": chapter["chapter_title"],
                    "recommended_agents": ["planning", "reasoning"],
                    "reason": "high_plot_advancement"
                })
            
            ***REMOVED*** 高角色发展 -> 需要 reasoning agent
            if indicators.get("character_development", 0) > 0.5:
                insights["agent_selection_patterns"].append({
                    "chapter": chapter["chapter_title"],
                    "recommended_agents": ["reasoning", "reflect"],
                    "reason": "high_character_development"
                })
            
            ***REMOVED*** 高冲突强度 -> 需要 action-focused agents
            if indicators.get("conflict_intensity", 0) > 0.5:
                insights["agent_selection_patterns"].append({
                    "chapter": chapter["chapter_title"],
                    "recommended_agents": ["planning", "reasoning", "action"],
                    "reason": "high_conflict"
                })
        
        ***REMOVED*** 2. 根据时序推断创作节奏
        if self.timeline:
            avg_interval = sum(
                (self.timeline[i+1]["update_time"] - self.timeline[i]["update_time"]).total_seconds() / 3600
                for i in range(len(self.timeline) - 1)
            ) / max(len(self.timeline) - 1, 1)
            
            insights["tool_usage_patterns"].append({
                "pattern": "temporal_rhythm",
                "avg_update_interval_hours": avg_interval,
                "recommendation": "batch_processing" if avg_interval < 24 else "incremental_processing"
            })
        
        return insights
    
    def export_for_memory_system(self) -> List[Dict[str, Any]]:
        """导出用于记忆系统的模式"""
        memory_items = []
        
        ***REMOVED*** 导出卷模式
        for vol in self.volumes:
            memory_items.append({
                "content": f"【卷模式】{vol['volume_title']}\n卷数: {vol['volume_number']}\n章节数: {len(vol['chapters'])}\n主题: {self._infer_theme(vol)}",
                "metadata": {
                    "pattern_type": "volume_structure",
                    "volume_number": vol["volume_number"],
                    "chapter_count": len(vol["chapters"]),
                },
                "keywords": [vol["volume_title"]] + self._extract_key_elements(vol),
            })
        
        ***REMOVED*** 导出章节模式
        for chapter in self.chapters[:30]:  ***REMOVED*** 前30章
            indicators = chapter.get("progression_indicators", {})
            memory_items.append({
                "content": f"【章节模式】{chapter['chapter_title']}\n情节推进: {indicators.get('plot_advancement', 0):.2f}\n角色发展: {indicators.get('character_development', 0):.2f}\n冲突强度: {indicators.get('conflict_intensity', 0):.2f}",
                "metadata": {
                    "pattern_type": "chapter_structure",
                    "chapter_number": chapter["chapter_number"],
                    "progression_indicators": indicators,
                },
                "keywords": [chapter["chapter_title"]] + self._extract_character_focus(chapter),
            })
        
        return memory_items

