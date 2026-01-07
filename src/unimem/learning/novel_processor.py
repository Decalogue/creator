"""
小说数据处理器

从大量优质小说中提取模式并存储到记忆系统
"""

import os
import re
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class NovelProcessor:
    """小说数据处理器"""
    
    def __init__(self, unimem_instance=None):
        """
        初始化处理器
        
        Args:
            unimem_instance: UniMem 实例（可选，用于直接存储）
        """
        self.unimem = unimem_instance
        
        ***REMOVED*** 章节标题模式（更宽松的匹配）
        self.chapter_patterns = [
            r'第[一二三四五六七八九十百千万\d]+章[^\n]*',
            r'第[一二三四五六七八九十百千万\d]+[章节][^\n]*',
            r'Chapter\s+\d+[^\n]*',
            r'^\s*第?\s*\d+\s*[章节][^\n]*',
            r'^[上中下]?[卷部篇]\s*[一二三四五六七八九十\d]+[^\n]*',
            r'^\s*卷\s*[一二三四五六七八九十\d]+[^\n]*',  ***REMOVED*** 卷X格式
            r'^\s*[一二三四五六七八九十\d]+\s*[^\n]{0,50}$',  ***REMOVED*** 纯数字标题
            r'^[^\n]{0,30}章节字数[^\n]*$',  ***REMOVED*** 包含"章节字数"的行
        ]
        
        ***REMOVED*** 情节类型关键词
        self.plot_keywords = {
            "打脸": ["打脸", "反击", "碾压", "秒杀", "完虐", "吊打"],
            "装逼": ["装逼", "震撼", "惊艳", "惊叹", "不可思议", "逆天"],
            "反转": ["反转", "真相", "原来", "竟然", "没想到", "出乎意料"],
            "高潮": ["高潮", "大战", "决战", "巅峰", "激烈", "惊天"],
            "情感": ["心动", "喜欢", "爱", "心疼", "感动", "温馨"],
            "冲突": ["冲突", "矛盾", "对立", "仇敌", "敌对", "对抗"],
        }
    
    def extract_metadata(self, filepath: str) -> Dict[str, Any]:
        """
        从文件名提取元数据
        
        Args:
            filepath: 文件路径
            
        Returns:
            元数据字典
        """
        filename = os.path.basename(filepath)
        
        metadata = {
            "filename": filename,
            "filepath": filepath,
            "title": None,
            "category": None,
            "author": None,
        }
        
        ***REMOVED*** 尝试从文件名提取信息
        ***REMOVED*** 格式示例：电子书合集_10万+小说合集_12000本小说_TOP100-言情篇_No.11 仙侠奇缘之花千骨.txt
        parts = filename.replace(".txt", "").split("_")
        
        ***REMOVED*** 提取标题（通常在最末尾）
        if len(parts) > 0:
            metadata["title"] = parts[-1].strip()
        
        ***REMOVED*** 提取分类（通常在文件名中间部分）
        for part in parts:
            if "言情" in part or "仙侠" in part or "网游" in part or "玄幻" in part:
                metadata["category"] = part
                break
        
        return metadata
    
    def extract_structure(self, text: str) -> Dict[str, Any]:
        """
        提取小说结构
        
        Args:
            text: 小说文本
            
        Returns:
            结构信息字典
        """
        structure = {
            "chapters": [],
            "total_length": len(text),
            "chapter_count": 0,
        }
        
        lines = text.split('\n')
        current_chapter = None
        chapter_content = []
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            ***REMOVED*** 跳过空行
            if not line_stripped:
                if current_chapter is not None:
                    chapter_content.append("")
                continue
            
            ***REMOVED*** 检查是否是章节标题
            is_chapter = False
            for pattern in self.chapter_patterns:
                if re.match(pattern, line_stripped, re.IGNORECASE):
                    is_chapter = True
                    break
            
            ***REMOVED*** 额外检查：包含"章节字数"的行通常也是章节标题
            if "章节字数" in line_stripped and len(line_stripped) < 100:
                is_chapter = True
            
            if is_chapter:
                ***REMOVED*** 保存前一章
                if current_chapter is not None:
                    structure["chapters"].append({
                        "title": current_chapter,
                        "content": "\n".join(chapter_content),
                        "length": len("\n".join(chapter_content)),
                    })
                
                ***REMOVED*** 开始新章节
                current_chapter = line_stripped
                chapter_content = []
            else:
                if current_chapter is not None:
                    chapter_content.append(line)
        
        ***REMOVED*** 保存最后一章
        if current_chapter is not None:
            structure["chapters"].append({
                "title": current_chapter,
                "content": "\n".join(chapter_content),
                "length": len("\n".join(chapter_content)),
            })
        
        structure["chapter_count"] = len(structure["chapters"])
        
        return structure
    
    def extract_plot_points(self, text: str) -> List[Dict[str, Any]]:
        """
        提取情节节点
        
        Args:
            text: 小说文本
            
        Returns:
            情节节点列表
        """
        plot_points = []
        
        ***REMOVED*** 按段落分割
        paragraphs = re.split(r'\n\s*\n', text)
        
        for i, para in enumerate(paragraphs):
            if len(para.strip()) < 50:  ***REMOVED*** 跳过太短的段落
                continue
            
            ***REMOVED*** 检测情节类型
            plot_types = []
            for plot_type, keywords in self.plot_keywords.items():
                if any(keyword in para for keyword in keywords):
                    plot_types.append(plot_type)
            
            if plot_types:
                plot_points.append({
                    "index": i,
                    "paragraph": para[:500],  ***REMOVED*** 只保存前500字符
                    "types": plot_types,
                    "position": i / max(len(paragraphs), 1),  ***REMOVED*** 位置比例
                })
        
        return plot_points
    
    def extract_characters(self, text: str) -> List[Dict[str, Any]]:
        """
        提取人物信息（简化版，基于频率和上下文）
        
        Args:
            text: 小说文本
            
        Returns:
            人物列表
        """
        characters = []
        character_freq = {}
        
        ***REMOVED*** 过滤词（常见非人名的词）
        stop_words = {
            "什么", "怎么", "这样", "那个", "这个", "那个", "这样", "那样",
            "什么", "怎么", "如何", "因为", "所以", "但是", "然而", "然后",
            "一直", "总是", "经常", "从来", "还是", "还是", "不过", "可是",
            "不过", "只是", "只有", "只要", "只是", "只要", "只有", "只是",
            "小说", "章节", "内容", "更新", "时间", "字数", "作者", "作品",
            "关键字", "类别", "完结", "仙侠", "奇缘",
        }
        
        ***REMOVED*** 提取可能的姓名（2-4字的中文名字）
        ***REMOVED*** 分析前50000字以获取更准确的结果
        sample_text = text[:50000] if len(text) > 50000 else text
        
        ***REMOVED*** 方法1: 直接提取2-4字中文词
        name_candidates1 = re.findall(r'[一-龥]{2,4}', sample_text)
        
        ***REMOVED*** 方法2: 提取引号内的人名（对话中的人名）
        name_candidates2 = re.findall(r'["""]([一-龥]{2,4})["""]', sample_text)
        
        ***REMOVED*** 合并候选
        all_candidates = name_candidates1 + name_candidates2
        
        ***REMOVED*** 统计频率
        for name in all_candidates:
            ***REMOVED*** 过滤停止词和明显不是人名的词
            if (name not in stop_words and 
                len(name) >= 2 and 
                not re.match(r'^\d+$', name)):  ***REMOVED*** 不是纯数字
                character_freq[name] = character_freq.get(name, 0) + 1
        
        ***REMOVED*** 取频率最高的前15个作为候选
        sorted_chars = sorted(character_freq.items(), key=lambda x: x[1], reverse=True)[:15]
        
        ***REMOVED*** 进一步筛选：出现频率足够高，且在文本中分布较广
        for name, freq in sorted_chars:
            if freq >= 3:  ***REMOVED*** 降低阈值，至少出现3次
                ***REMOVED*** 检查是否在不同位置出现（避免重复的短文本片段）
                positions = [m.start() for m in re.finditer(name, sample_text)]
                if len(positions) >= 3:
                    characters.append({
                        "name": name,
                        "frequency": freq,
                    })
        
        return characters[:10]  ***REMOVED*** 返回前10个
    
    def extract_rhythm(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        提取节奏特征
        
        Args:
            structure: 结构信息
            
        Returns:
            节奏特征
        """
        if not structure.get("chapters"):
            return {}
        
        chapter_lengths = [ch["length"] for ch in structure["chapters"]]
        
        rhythm = {
            "avg_chapter_length": sum(chapter_lengths) / len(chapter_lengths) if chapter_lengths else 0,
            "min_chapter_length": min(chapter_lengths) if chapter_lengths else 0,
            "max_chapter_length": max(chapter_lengths) if chapter_lengths else 0,
            "chapter_count": len(chapter_lengths),
            "total_length": structure["total_length"],
        }
        
        return rhythm
    
    def process_novel(self, filepath: str) -> Dict[str, Any]:
        """
        处理单本小说
        
        Args:
            filepath: 小说文件路径
            
        Returns:
            处理结果
        """
        try:
            logger.info(f"处理小说: {filepath}")
            
            ***REMOVED*** 读取文件
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            
            if len(text) < 1000:  ***REMOVED*** 跳过太短的文件
                logger.warning(f"文件过短，跳过: {filepath}")
                return None
            
            ***REMOVED*** 提取元数据
            metadata = self.extract_metadata(filepath)
            
            ***REMOVED*** 提取结构
            structure = self.extract_structure(text)
            
            ***REMOVED*** 提取情节节点
            plot_points = self.extract_plot_points(text)
            
            ***REMOVED*** 提取人物（简化版）
            characters = self.extract_characters(text)
            
            ***REMOVED*** 提取节奏
            rhythm = self.extract_rhythm(structure)
            
            ***REMOVED*** 构建处理结果
            result = {
                "metadata": metadata,
                "structure": structure,
                "plot_points": plot_points[:50],  ***REMOVED*** 只保存前50个情节节点
                "characters": characters,
                "rhythm": rhythm,
                "processed_at": datetime.now().isoformat(),
            }
            
            logger.info(f"处理完成: {metadata.get('title')}, 章节数: {structure.get('chapter_count')}")
            
            return result
            
        except Exception as e:
            logger.error(f"处理小说失败 {filepath}: {e}", exc_info=True)
            return None
    
    def store_patterns_to_memory(self, processed_novel: Dict[str, Any]):
        """
        将提取的模式存储到记忆系统
        
        Args:
            processed_novel: 处理过的小说数据
        """
        if not self.unimem:
            logger.warning("UniMem 实例未提供，无法存储模式")
            return
        
        from ..types import Experience, Context, MemoryType, MemoryLayer
        
        metadata = processed_novel.get("metadata", {})
        title = metadata.get("title", "未知")
        
        ***REMOVED*** 存储情节模式
        plot_points = processed_novel.get("plot_points", [])
        for plot_point in plot_points[:10]:  ***REMOVED*** 只存储前10个关键情节节点
            plot_types = ", ".join(plot_point.get("types", []))
            content = f"【情节模式】{title}\n类型: {plot_types}\n位置: {plot_point.get('position', 0):.2f}\n内容: {plot_point.get('paragraph', '')[:200]}"
            
            self.unimem.retain(
                experience=Experience(
                    content=content,
                    timestamp=datetime.now(),
                    metadata={
                        "novel_title": title,
                        "pattern_type": "plot",
                        "plot_types": plot_point.get("types", []),
                        "position": plot_point.get("position", 0),
                    }
                ),
                context=Context(
                    session_id="novel_learning",
                    user_id="system",
                    metadata={"source": "novel_dataset"}
                ),
                memory_type=MemoryType.SEMANTIC,
                layer=MemoryLayer.LTM,
            )
        
        ***REMOVED*** 存储节奏模式
        rhythm = processed_novel.get("rhythm", {})
        if rhythm:
            rhythm_content = f"【节奏模式】{title}\n平均章节长度: {rhythm.get('avg_chapter_length', 0):.0f}字\n章节数: {rhythm.get('chapter_count', 0)}\n总长度: {rhythm.get('total_length', 0):.0f}字"
            
            self.unimem.retain(
                experience=Experience(
                    content=rhythm_content,
                    timestamp=datetime.now(),
                    metadata={
                        "novel_title": title,
                        "pattern_type": "rhythm",
                        "avg_chapter_length": rhythm.get("avg_chapter_length", 0),
                        "chapter_count": rhythm.get("chapter_count", 0),
                    }
                ),
                context=Context(
                    session_id="novel_learning",
                    user_id="system",
                    metadata={"source": "novel_dataset"}
                ),
                memory_type=MemoryType.SEMANTIC,
                layer=MemoryLayer.LTM,
            )
        
        ***REMOVED*** 存储人物模式
        characters = processed_novel.get("characters", [])
        if characters:
            char_names = ", ".join([ch["name"] for ch in characters[:5]])
            char_content = f"【人物模式】{title}\n主要人物: {char_names}\n人物数量: {len(characters)}"
            
            self.unimem.retain(
                experience=Experience(
                    content=char_content,
                    timestamp=datetime.now(),
                    metadata={
                        "novel_title": title,
                        "pattern_type": "character",
                        "character_count": len(characters),
                    }
                ),
                context=Context(
                    session_id="novel_learning",
                    user_id="system",
                    metadata={"source": "novel_dataset"}
                ),
                memory_type=MemoryType.SEMANTIC,
                layer=MemoryLayer.LTM,
            )
        
        logger.info(f"已存储 {title} 的模式到记忆系统")
    
    def batch_process(self, novel_dir: str, limit: Optional[int] = None, 
                     store_to_memory: bool = True) -> List[Dict[str, Any]]:
        """
        批量处理小说
        
        Args:
            novel_dir: 小说目录
            limit: 处理数量限制（None表示全部）
            store_to_memory: 是否存储到记忆系统
            
        Returns:
            处理结果列表
        """
        results = []
        
        ***REMOVED*** 查找所有txt文件
        novel_files = []
        for root, dirs, files in os.walk(novel_dir):
            for file in files:
                if file.endswith('.txt'):
                    novel_files.append(os.path.join(root, file))
        
        if limit:
            novel_files = novel_files[:limit]
        
        logger.info(f"找到 {len(novel_files)} 本小说，开始批量处理...")
        
        for i, filepath in enumerate(novel_files, 1):
            logger.info(f"处理进度: {i}/{len(novel_files)}")
            
            processed = self.process_novel(filepath)
            
            if processed:
                results.append(processed)
                
                ***REMOVED*** 存储到记忆系统
                if store_to_memory and self.unimem:
                    try:
                        self.store_patterns_to_memory(processed)
                    except Exception as e:
                        logger.error(f"存储模式失败: {e}", exc_info=True)
            
            ***REMOVED*** 每处理10本保存一次中间结果
            if i % 10 == 0:
                logger.info(f"已处理 {i} 本，成功 {len(results)} 本")
        
        logger.info(f"批量处理完成，共处理 {len(results)} 本小说")
        
        return results

