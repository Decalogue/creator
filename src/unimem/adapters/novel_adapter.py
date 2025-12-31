"""
小说创作适配器

专门用于小说创作的适配器，基于 atom_link_adapter 的基础架构，
但针对小说创作的特殊需求进行定制化实现。

小说创作特点：
- 多层级结构化：章节->摘要->大纲->简介
- 创作维度：文章/小说类型，写作风格，故事线，场景，人物，事件，线索等
- 生成流程：简介->大纲->摘要->章节

主要功能：
1. 多层级结构化：章节->摘要->大纲->简介
2. 带奖励的检索：根据结构化结果检索原内容并计算奖励
3. 层级生成：简介->大纲->摘要->章节
"""

import json
import logging
from typing import Dict, Any, Optional, List

from .atom_link_adapter import AtomLinkAdapter
from ..types import Memory
from ..chat import ark_deepseek_v3_2

logger = logging.getLogger(__name__)


class NovelAdapter(AtomLinkAdapter):
    """
    小说创作适配器
    
    继承 AtomLinkAdapter 的基础功能，但针对小说创作进行定制化。
    
    核心功能：
    1. 多层级结构化：章节->摘要->大纲->简介
    2. 带奖励的检索：根据结构化结果检索原内容并计算奖励
    3. 层级生成：简介->大纲->摘要->章节
    """
    
    def _do_initialize(self) -> None:
        """
        初始化小说创作适配器
        
        调用父类初始化以复用基础架构（向量存储、嵌入模型等），
        然后进行小说创作特定的初始化。
        """
        super()._do_initialize()
        logger.info("Novel adapter initialized (specialized for novel writing)")
    
    def structure_content_hierarchy(self, chapters: List[str], level: str = "summary") -> Dict[str, Any]:
        """
        多层级结构化：章节->摘要->大纲->简介
        
        根据需求文档：
        - 流程：章节->摘要->大纲->简介
        - 维度：文章/小说类型，写作风格，故事线，场景，人物，事件，线索等
        
        Args:
            chapters: 章节内容列表（每章内容会被截取前300-500字符用于分析）
            level: 结构化层级，可选值：
                - "summary": 章节摘要
                - "outline": 故事大纲
                - "synopsis": 作品简介
            
        Returns:
            结构化结果字典：
            - 对于 "summary"：返回 {"summaries": [...], "metadata": {...}}
            - 对于 "outline"：返回 {"outline": {...}, "metadata": {...}}
            - 对于 "synopsis"：返回 {"synopsis": "...", "metadata": {...}}
            - 如果失败：返回空字典 {}
            
        Note:
            如果适配器不可用或发生错误，返回空字典，不会抛出异常
        """
        if not self.is_available():
            logger.warning("NovelAdapter not available, cannot perform structure_content_hierarchy")
            return {}
        
        if not chapters:
            logger.warning("Empty chapters list provided for structure_content_hierarchy")
            return {}
        
        try:
            ***REMOVED*** 根据层级选择不同的 prompt
            if level == "summary":
                ***REMOVED*** 章节 -> 摘要
                max_chapters = min(10, len(chapters))
                chapters_preview = [f"章节{i+1}: {ch[:500]}" for i, ch in enumerate(chapters[:max_chapters])]
                
                prompt = f"""请对以下章节内容进行结构化摘要，提取关键信息。

要求：
1. 提取核心事件、情节和关键信息
2. 识别主要角色、场景和重要关系
3. 保持信息的准确性和完整性
4. 摘要长度控制在200-300字左右

章节内容：
{chr(10).join(chapters_preview)}

请以 JSON 格式返回结果：
{{
    "summaries": ["摘要1", "摘要2", ...],
    "metadata": {{
        "total_chapters": {len(chapters)},
        "extracted_info": {{
            "characters": ["角色1", "角色2", ...],
            "scenes": ["场景1", "场景2", ...],
            "events": ["事件1", "事件2", ...]
        }}
    }}
}}"""
            elif level == "outline":
                ***REMOVED*** 摘要 -> 大纲
                max_chapters = min(20, len(chapters))
                chapters_preview = [f"摘要{i+1}: {ch[:300]}" for i, ch in enumerate(chapters[:max_chapters])]
                
                prompt = f"""请根据以下摘要内容生成故事大纲。

要求：
1. 提取主要故事线和情节结构
2. 识别关键转折点和冲突
3. 整理时间线和因果关系
4. 大纲应该清晰、层次分明

摘要内容：
{chr(10).join(chapters_preview)}

请以 JSON 格式返回结果：
{{
    "outline": {{
        "main_storyline": "主要故事线",
        "plot_points": ["情节点1", "情节点2", ...],
        "conflicts": ["冲突1", "冲突2", ...],
        "turning_points": ["转折点1", "转折点2", ...]
    }},
    "metadata": {{
        "structure_type": "故事结构类型",
        "themes": ["主题1", "主题2", ...]
    }}
}}"""
            elif level == "synopsis":
                ***REMOVED*** 大纲 -> 简介
                max_chapters = min(5, len(chapters))
                chapters_preview = [ch[:400] for ch in chapters[:max_chapters]]
                
                prompt = f"""请根据以下大纲内容生成作品简介。

要求：
1. 概括整个作品的核心内容
2. 突出主要角色和关键冲突
3. 吸引读者兴趣
4. 简介长度控制在150-200字左右

大纲内容：
{chr(10).join(chapters_preview)}

请以 JSON 格式返回结果：
{{
    "synopsis": "作品简介内容",
    "metadata": {{
        "genre": "作品类型",
        "writing_style": "写作风格",
        "target_audience": "目标受众"
    }}
}}"""
            else:
                logger.warning(f"Unknown level '{level}', defaulting to 'summary'")
                level = "summary"
                ***REMOVED*** 使用 summary 的 prompt
                max_chapters = min(10, len(chapters))
                chapters_preview = [f"章节{i+1}: {ch[:500]}" for i, ch in enumerate(chapters[:max_chapters])]
                prompt = f"""请对以下章节内容进行结构化摘要，提取关键信息。

要求：
1. 提取核心事件、情节和关键信息
2. 识别主要角色、场景和重要关系
3. 保持信息的准确性和完整性
4. 摘要长度控制在200-300字左右

章节内容：
{chr(10).join(chapters_preview)}

请以 JSON 格式返回结果：
{{
    "summaries": ["摘要1", "摘要2", ...],
    "metadata": {{
        "total_chapters": {len(chapters)},
        "extracted_info": {{
            "characters": ["角色1", "角色2", ...],
            "scenes": ["场景1", "场景2", ...],
            "events": ["事件1", "事件2", ...]
        }}
    }}
}}"""
            
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的创作助手，擅长对内容进行多层级结构化分析。请始终以有效的 JSON 格式返回结果。"
                },
                {"role": "user", "content": prompt}
            ]
            
            _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=2048)
            result = self._parse_json_response(response_text)
            
            if result:
                logger.debug(f"Structured content hierarchy at level '{level}': "
                           f"{len(result)} keys in result")
                return result
            else:
                logger.warning(f"Failed to parse structure hierarchy response: {response_text[:200]}")
                return {}
        except Exception as e:
            logger.error(f"Error structuring content hierarchy: {e}", exc_info=True)
            return {}
    
    def retrieve_with_reward(
        self,
        query: str,
        original_contents: List[str],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        根据结构化结果检索原内容，并计算奖励
        
        根据需求文档：
        - 奖励 = 1 - index/N，其中 index 为索引，N 为原内容列表
        - 例如对于原章节结构化的摘要，使用摘要在所有章节(N)中检索原章节，索引越靠前奖励越高
        
        Args:
            query: 查询文本（通常是结构化后的摘要/大纲/简介）
            original_contents: 原始内容列表（如原章节列表）
            top_k: 返回结果数量，默认 10
            
        Returns:
            检索结果列表，每个结果包含以下字段：
            - memory: Memory 对象
            - score: 相似度分数（0-1）
            - reward: 奖励分数（0-1），基于匹配位置计算
            - original_index: 匹配到的原始内容索引（如果匹配成功）
            - retrieval_rank: 检索排名（1-based）
            
        Note:
            如果适配器不可用或发生错误，返回空列表，不会抛出异常
        """
        if not self.is_available():
            logger.warning("NovelAdapter not available, cannot perform retrieve_with_reward")
            return []
        
        if not query or not query.strip():
            logger.warning("Empty query provided for retrieve_with_reward")
            return []
        
        if not original_contents:
            logger.warning("Empty original_contents list provided for retrieve_with_reward")
            return []
        
        try:
            ***REMOVED*** 1. 使用结构化查询检索相似记忆（检索更多以增加匹配机会）
            similar_memories = self._search_similar_memories(query, top_k=top_k * 2)
            
            if not similar_memories:
                logger.debug("No similar memories found for query")
                return []
            
            ***REMOVED*** 2. 匹配到原始内容并计算奖励
            results = []
            N = len(original_contents)
            
            for idx, memory in enumerate(similar_memories[:top_k]):
                ***REMOVED*** 尝试匹配到原始内容（使用前100字符进行匹配）
                matched_index = None
                memory_preview = memory.content[:100] if memory.content else ""
                
                for orig_idx, orig_content in enumerate(original_contents):
                    if not orig_content:
                        continue
                    orig_preview = orig_content[:100]
                    ***REMOVED*** 双向匹配检查
                    if memory_preview in orig_content or orig_preview in memory.content:
                        matched_index = orig_idx
                        break
                
                ***REMOVED*** 计算奖励：reward = 1 - index/N（越靠前奖励越高）
                if matched_index is not None:
                    reward = 1.0 - (matched_index / N) if N > 0 else 1.0
                else:
                    ***REMOVED*** 如果无法匹配，使用检索排名计算奖励
                    reward = 1.0 - (idx / top_k) if top_k > 0 else 1.0
                
                ***REMOVED*** 获取相似度分数（如果存在）
                similarity_score = memory.metadata.get("similarity_score", 1.0 - idx / top_k) if memory.metadata else 1.0 - idx / top_k
                
                results.append({
                    "memory": memory,
                    "score": similarity_score,
                    "reward": reward,
                    "original_index": matched_index,
                    "retrieval_rank": idx + 1
                })
            
            ***REMOVED*** 按奖励排序（奖励高的在前）
            results.sort(key=lambda x: x["reward"], reverse=True)
            
            logger.debug(f"Retrieved {len(results)} results with rewards")
            return results[:top_k]
        except Exception as e:
            logger.error(f"Error retrieving with reward: {e}", exc_info=True)
            return []
    
    def generate_from_hierarchy(
        self,
        synopsis: str,
        target_level: str = "chapter",
        context_memories: Optional[List[Memory]] = None
    ) -> str:
        """
        生成流程：简介->大纲->摘要->章节
        
        根据需求文档：
        - 流程：简介->大纲->摘要->章节
        - 上下文：与当前生成目标相关的原子笔记
        
        Args:
            synopsis: 简介内容或大纲/摘要内容（根据 target_level 决定）
            target_level: 目标层级，可选值：
                - "outline": 生成故事大纲（返回 JSON 字符串）
                - "summary": 生成章节摘要（返回文本，每行一个摘要）
                - "chapter": 生成章节内容（返回文本）
            context_memories: 相关的原子笔记列表（用于提供上下文，最多使用前5个）
            
        Returns:
            生成的内容：
            - 对于 "outline"：返回 JSON 格式字符串
            - 对于 "summary"：返回文本，每行一个摘要
            - 对于 "chapter"：返回章节文本
            - 如果失败：返回空字符串
            
        Note:
            如果适配器不可用或发生错误，返回空字符串，不会抛出异常
        """
        if not self.is_available():
            logger.warning("NovelAdapter not available, cannot perform generate_from_hierarchy")
            return ""
        
        if not synopsis or not synopsis.strip():
            logger.warning("Empty synopsis provided for generate_from_hierarchy")
            return ""
        
        try:
            ***REMOVED*** 构建上下文信息
            context_text = ""
            if context_memories:
                context_text = "\n相关原子笔记：\n"
                ***REMOVED*** 限制使用的记忆数量以提高效率
                for mem in context_memories[:5]:
                    context_text += f"- {mem.content[:200]}\n"
                    if mem.metadata and mem.metadata.get("creative_dimensions"):
                        dims = mem.metadata["creative_dimensions"]
                        if dims.get("characters"):
                            context_text += f"  人物: {', '.join(dims['characters'][:3])}\n"
                        if dims.get("scenes"):
                            context_text += f"  场景: {', '.join(dims['scenes'][:3])}\n"
            
            ***REMOVED*** 根据目标层级选择不同的 prompt
            if target_level == "outline":
                prompt = f"""请根据以下作品简介生成详细的故事大纲。

要求：
1. 扩展主要故事线和情节结构
2. 设计关键转折点和冲突
3. 规划时间线和因果关系
4. 大纲应该详细、层次分明

作品简介：
{synopsis}

{context_text}

请以 JSON 格式返回结果：
{{
    "outline": {{
        "main_storyline": "主要故事线",
        "plot_points": ["情节点1", "情节点2", ...],
        "conflicts": ["冲突1", "冲突2", ...],
        "turning_points": ["转折点1", "转折点2", ...]
    }}
}}"""
            elif target_level == "summary":
                prompt = f"""请根据以下故事大纲生成章节摘要。

要求：
1. 为每个主要情节点生成摘要
2. 保持与大纲的一致性
3. 摘要应该清晰、连贯

故事大纲：
{synopsis}

{context_text}

请以 JSON 格式返回结果：
{{
    "summaries": ["摘要1", "摘要2", ...]
}}"""
            elif target_level == "chapter":
                prompt = f"""请根据以下内容生成具体的章节内容。

要求：
1. 扩展摘要为完整的章节内容
2. 包含对话、场景描写和情节推进
3. 保持风格一致性和连贯性
4. 章节长度控制在1000-2000字左右

内容：
{synopsis}

{context_text}

请直接返回章节内容，不要包含其他格式："""
            else:
                logger.warning(f"Unknown target_level '{target_level}', defaulting to 'chapter'")
                target_level = "chapter"
                prompt = f"""请根据以下内容生成具体的章节内容。

要求：
1. 扩展摘要为完整的章节内容
2. 包含对话、场景描写和情节推进
3. 保持风格一致性和连贯性
4. 章节长度控制在1000-2000字左右

内容：
{synopsis}

{context_text}

请直接返回章节内容，不要包含其他格式："""
            
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的创作助手，擅长根据结构化内容生成创作内容。请保持风格一致性和连贯性。"
                },
                {"role": "user", "content": prompt}
            ]
            
            _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=4096)
            
            ***REMOVED*** 清理响应文本
            if target_level in ["outline", "summary"]:
                result = self._parse_json_response(response_text)
                if result:
                    if target_level == "outline":
                        outline = result.get("outline", {})
                        logger.debug(f"Generated outline with {len(outline)} keys")
                        return json.dumps(outline, ensure_ascii=False, indent=2)
                    else:
                        summaries = result.get("summaries", [])
                        logger.debug(f"Generated {len(summaries)} summaries")
                        return "\n".join(summaries)
                else:
                    logger.warning(f"Failed to parse JSON response for target_level '{target_level}'")
                    return ""
            
            ***REMOVED*** 对于章节，直接返回文本
            chapter_text = response_text.strip()
            logger.debug(f"Generated chapter with {len(chapter_text)} characters")
            return chapter_text
        except Exception as e:
            logger.error(f"Error generating from hierarchy: {e}", exc_info=True)
            return ""

