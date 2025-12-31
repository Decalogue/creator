"""
短剧剧本创作适配器

专门用于短剧剧本创作的适配器，基于 atom_link_adapter 的基础架构，
但针对短剧剧本的特殊需求进行定制化实现。

短剧剧本特点：
- 分镜设计：需要明确的分镜脚本
- 场景描述：更注重视觉化描述
- 对话为主：对话占主要篇幅
- 节奏控制：需要精确的时间控制（每集时长）
- 格式要求：标准的剧本格式（场景、人物、对话、动作）

创作流程：
大纲 -> 分集大纲 -> 分镜脚本 -> 完整剧本

主要功能：
1. 剧本结构化分析：提取分镜、场景、对话、节奏等维度
2. 分镜脚本生成：生成标准格式的分镜脚本
3. 剧本格式生成：生成标准剧本格式（场景、人物、对话、动作）
4. 节奏控制：控制每集的时长和节奏
5. 自动优化：根据执行结果优化 prompt 和上下文结构
"""

import json
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from .atom_link_adapter import AtomLinkAdapter
from ..types import Entity, Memory
from ..chat import ark_deepseek_v3_2

logger = logging.getLogger(__name__)


class ScriptAdapter(AtomLinkAdapter):
    """
    短剧剧本创作适配器
    
    继承 AtomLinkAdapter 的基础功能，但针对短剧剧本创作进行定制化。
    
    核心功能：
    1. 剧本结构化分析：提取分镜、场景、对话、节奏等维度
    2. 分镜脚本生成：生成标准格式的分镜脚本
    3. 剧本格式生成：生成标准剧本格式（场景、人物、对话、动作）
    4. 节奏控制：控制每集的时长和节奏
    """
    
    def _do_initialize(self) -> None:
        """
        初始化短剧剧本创作适配器
        
        调用父类初始化以复用基础架构（向量存储、嵌入模型等），
        然后进行剧本创作特定的初始化。
        """
        super()._do_initialize()
        logger.info("Script adapter initialized (specialized for script writing)")
    
    def _analyze_script_content(self, content: str, max_new_tokens: int = 1024) -> Dict[str, Any]:
        """
        分析短剧剧本内容，提取剧本特有的维度
        
        维度包括：
        - 剧本类型（悬疑、爱情、喜剧等）
        - 分镜设计
        - 场景设置
        - 人物对话风格
        - 节奏控制
        - 视觉元素
        
        Args:
            content: 剧本内容（如果过长会自动截取前2000字符）
            max_new_tokens: 最大生成 token 数，默认 1024
            
        Returns:
            包含剧本维度的分析结果字典，包含以下字段：
            - keywords: List[str] - 关键词列表
            - context: str - 一句话总结
            - tags: List[str] - 标签列表
            - script_dimensions: Dict[str, Any] - 剧本特有维度（可选）
            
        Note:
            如果解析失败，返回默认的空结构，不会抛出异常
        """
        if not content or not content.strip():
            logger.warning("Empty content provided for script analysis")
            return {"keywords": [], "context": "General", "tags": []}
        
        ***REMOVED*** 限制内容长度以提高分析效率
        content_preview = content[:2000] if len(content) > 2000 else content
        
        prompt = f"""请对以下短剧剧本内容进行结构化分析，提取剧本特有的维度信息。

短剧剧本的维度：
1. **剧本类型**：悬疑、爱情、喜剧、动作、古装等
2. **分镜设计**：镜头语言、画面构图、镜头运动
3. **场景设置**：场景描述、环境氛围、视觉元素
4. **人物对话风格**：对话特点、语言风格、情感表达
5. **节奏控制**：情节节奏、冲突密度、高潮设置
6. **视觉元素**：道具、服装、特效、音效等

请以 JSON 格式返回结果：
{{
    "keywords": [
        // 关键词（人物、场景、道具等）
    ],
    "context": 
        // 一句话总结：剧本类型、核心冲突、目标受众
    ,
    "tags": [
        // 标签（类型、风格等）
    ],
    "script_dimensions": {{
        // 剧本特有维度
        "script_type": "剧本类型",
        "scene_design": ["场景1描述", "场景2描述", ...],
        "dialogue_style": "对话风格",
        "rhythm_control": "节奏特点",
        "visual_elements": ["视觉元素1", "视觉元素2", ...],
        "shot_design": ["分镜1", "分镜2", ...]
    }}
}}

待分析的剧本内容：
{content_preview}"""
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的短剧剧本分析助手，擅长提取剧本的结构化信息和创作维度。请始终以有效的 JSON 格式返回结果。"
                },
                {"role": "user", "content": prompt}
            ]
            
            _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=max_new_tokens)
            
            ***REMOVED*** 解析 JSON（使用父类方法）
            result = self._parse_json_response(response_text)
            if result:
                base_result = {
                    "keywords": result.get("keywords", []),
                    "context": result.get("context", "General"),
                    "tags": result.get("tags", []),
                }
                ***REMOVED*** 添加剧本维度
                if "script_dimensions" in result:
                    base_result["script_dimensions"] = result.get("script_dimensions")
                logger.debug(f"Script analysis completed: {len(base_result.get('keywords', []))} keywords, "
                           f"{len(base_result.get('tags', []))} tags")
                return base_result
            else:
                logger.warning(f"Failed to parse script analysis response: {response_text[:200]}")
                return {"keywords": [], "context": "General", "tags": []}
        except Exception as e:
            logger.error(f"Error analyzing script content: {e}", exc_info=True)
            return {"keywords": [], "context": "General", "tags": []}
    
    def structure_script_hierarchy(self, episodes: List[str], level: str = "episode_outline") -> Dict[str, Any]:
        """
        短剧剧本的多层级结构化：分集->分集大纲->分镜脚本->完整剧本
        
        根据短剧剧本创作流程：
        - 流程：分集->分集大纲->分镜脚本->完整剧本
        - 维度：剧本类型、分镜设计、场景设置、对话风格、节奏控制、视觉元素
        
        Args:
            episodes: 分集内容列表（每集内容会被截取前500-600字符用于分析）
            level: 结构化层级，可选值：
                - "episode_outline": 分集大纲
                - "shot_script": 分镜脚本
                - "full_script": 完整剧本
            
        Returns:
            结构化结果字典：
            - 对于 "episode_outline" 和 "shot_script"：返回包含结构化数据的字典
            - 对于 "full_script"：返回 {"script": "完整剧本文本"}
            - 如果失败：返回空字典 {}
            
        Note:
            如果适配器不可用或发生错误，返回空字典，不会抛出异常
        """
        if not self.is_available():
            logger.warning("ScriptAdapter not available, cannot perform structure_script_hierarchy")
            return {}
        
        if not episodes:
            logger.warning("Empty episodes list provided for structure_script_hierarchy")
            return {}
        
        try:
            ***REMOVED*** 根据层级选择不同的 prompt
            if level == "episode_outline":
                ***REMOVED*** 分集 -> 分集大纲
                ***REMOVED*** 限制处理的集数以提高效率
                max_episodes = min(10, len(episodes))
                episodes_preview = [f"第{i+1}集: {ep[:500]}" for i, ep in enumerate(episodes[:max_episodes])]
                
                prompt = f"""请对以下短剧分集内容进行结构化分析，生成分集大纲。

要求：
1. 提取核心情节和冲突
2. 识别主要场景和分镜点
3. 分析节奏和高潮设置
4. 大纲长度控制在300-400字左右

分集内容：
{chr(10).join(episodes_preview)}

请以 JSON 格式返回结果：
{{
    "episode_outlines": ["大纲1", "大纲2", ...],
    "metadata": {{
        "total_episodes": {len(episodes)},
        "extracted_info": {{
            "scenes": ["场景1", "场景2", ...],
            "characters": ["角色1", "角色2", ...],
            "conflicts": ["冲突1", "冲突2", ...],
            "rhythm_points": ["节奏点1", "节奏点2", ...]
        }}
    }}
}}"""
            elif level == "shot_script":
                ***REMOVED*** 分集大纲 -> 分镜脚本
                max_episodes = min(5, len(episodes))
                episodes_preview = [f"大纲{i+1}: {ep[:400]}" for i, ep in enumerate(episodes[:max_episodes])]
                
                prompt = f"""请根据以下分集大纲生成分镜脚本。

要求：
1. 为每个主要情节设计分镜
2. 包含镜头语言、画面构图、镜头运动
3. 标注场景切换和视觉元素
4. 分镜脚本应该清晰、可执行

分集大纲：
{chr(10).join(episodes_preview)}

请以 JSON 格式返回结果：
{{
    "shot_scripts": [
        {{
            "scene_num": 1,
            "scene_name": "场景名称",
            "location": "拍摄地点",
            "time": "时间",
            "shots": [
                {{
                    "shot_num": 1,
                    "shot_type": "镜头类型（全景/中景/近景/特写）",
                    "camera_movement": "镜头运动（固定/推拉/摇移）",
                    "description": "画面描述",
                    "dialogue": "对话内容",
                    "action": "动作描述",
                    "duration": "时长（秒）"
                }},
                ...
            ]
        }},
        ...
    ]
}}"""
            elif level == "full_script":
                ***REMOVED*** 分镜脚本 -> 完整剧本
                max_episodes = min(3, len(episodes))
                episodes_preview = [ep[:600] for ep in episodes[:max_episodes]]
                
                prompt = f"""请根据以下分镜脚本生成完整的短剧剧本。

要求：
1. 使用标准剧本格式
2. 包含场景、人物、对话、动作
3. 标注镜头语言和视觉元素
4. 控制每集时长在3-5分钟

分镜脚本：
{chr(10).join(episodes_preview)}

请以标准剧本格式返回，包含：
- 场景标题（场景、地点、时间）
- 人物对话
- 动作描述
- 镜头提示"""
            else:
                logger.warning(f"Unknown level '{level}', defaulting to 'episode_outline'")
                level = "episode_outline"
                ***REMOVED*** 使用 episode_outline 的 prompt
                max_episodes = min(10, len(episodes))
                episodes_preview = [f"第{i+1}集: {ep[:500]}" for i, ep in enumerate(episodes[:max_episodes])]
                prompt = f"""请对以下短剧分集内容进行结构化分析，生成分集大纲。

要求：
1. 提取核心情节和冲突
2. 识别主要场景和分镜点
3. 分析节奏和高潮设置
4. 大纲长度控制在300-400字左右

分集内容：
{chr(10).join(episodes_preview)}

请以 JSON 格式返回结果：
{{
    "episode_outlines": ["大纲1", "大纲2", ...],
    "metadata": {{
        "total_episodes": {len(episodes)},
        "extracted_info": {{
            "scenes": ["场景1", "场景2", ...],
            "characters": ["角色1", "角色2", ...],
            "conflicts": ["冲突1", "冲突2", ...],
            "rhythm_points": ["节奏点1", "节奏点2", ...]
        }}
    }}
}}"""
            
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的短剧剧本创作助手，擅长进行多层级结构化分析。请始终以有效的 JSON 格式返回结果（除完整剧本外）。"
                },
                {"role": "user", "content": prompt}
            ]
            
            _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=2048)
            
            ***REMOVED*** 解析结果
            if level == "full_script":
                ***REMOVED*** 完整剧本直接返回文本
                script_text = response_text.strip()
                logger.debug(f"Generated full script with {len(script_text)} characters")
                return {"script": script_text}
            else:
                result = self._parse_json_response(response_text)
                if result:
                    logger.debug(f"Structured script hierarchy at level '{level}': "
                               f"{len(result)} keys in result")
                    return result
                else:
                    logger.warning(f"Failed to parse structure hierarchy response: {response_text[:200]}")
                    return {}
        except Exception as e:
            logger.error(f"Error structuring script hierarchy: {e}", exc_info=True)
            return {}
    
    def generate_script_from_outline(
        self,
        outline: str,
        target_level: str = "full_script",
        context_memories: Optional[List[Memory]] = None
    ) -> str:
        """
        短剧剧本生成流程：大纲->分集大纲->分镜脚本->完整剧本
        
        根据需求文档：
        - 流程：大纲->分集大纲->分镜脚本->完整剧本
        - 上下文：与当前生成目标相关的原子笔记
        
        Args:
            outline: 故事大纲或分集大纲（根据 target_level 决定）
            target_level: 目标层级，可选值：
                - "episode_outline": 生成分集大纲（返回 JSON 字符串）
                - "shot_script": 生成分镜脚本（返回 JSON 字符串）
                - "full_script": 生成完整剧本（返回文本）
            context_memories: 相关的原子笔记列表（用于提供上下文，最多使用前5个）
            
        Returns:
            生成的内容：
            - 对于 "episode_outline" 和 "shot_script"：返回 JSON 格式字符串
            - 对于 "full_script"：返回标准剧本格式文本
            - 如果失败：返回空字符串
            
        Note:
            如果适配器不可用或发生错误，返回空字符串，不会抛出异常
        """
        if not self.is_available():
            logger.warning("ScriptAdapter not available, cannot perform generate_script_from_outline")
            return ""
        
        if not outline or not outline.strip():
            logger.warning("Empty outline provided for script generation")
            return ""
        
        try:
            ***REMOVED*** 构建上下文信息
            context_text = ""
            if context_memories:
                context_text = "\n相关原子笔记：\n"
                ***REMOVED*** 限制使用的记忆数量以提高效率
                for mem in context_memories[:5]:
                    context_text += f"- {mem.content[:200]}\n"
                    if mem.metadata and mem.metadata.get("script_dimensions"):
                        dims = mem.metadata["script_dimensions"]
                        if dims.get("scenes"):
                            context_text += f"  场景: {', '.join(dims['scenes'][:3])}\n"
                        if dims.get("characters"):
                            context_text += f"  人物: {', '.join(dims['characters'][:3])}\n"
            
            ***REMOVED*** 根据目标层级选择不同的 prompt
            if target_level == "episode_outline":
                prompt = f"""请根据以下故事大纲生成分集大纲。

要求：
1. 将故事分解为多个分集
2. 每集包含完整的情节单元
3. 保持节奏紧凑，每集有高潮点
4. 分集大纲应该清晰、连贯

故事大纲：
{outline}

{context_text}

请以 JSON 格式返回结果：
{{
    "episode_outlines": [
        {{
            "episode_num": 1,
            "title": "分集标题",
            "summary": "分集摘要",
            "key_scenes": ["场景1", "场景2", ...],
            "conflict": "核心冲突",
            "climax": "高潮点"
        }},
        ...
    ]
}}"""
            elif target_level == "shot_script":
                prompt = f"""请根据以下分集大纲生成分镜脚本。

要求：
1. 为每个场景设计分镜
2. 包含镜头语言、画面构图、镜头运动
3. 标注场景切换和视觉元素
4. 分镜脚本应该清晰、可执行

分集大纲：
{outline}

{context_text}

请以 JSON 格式返回结果：
{{
    "shot_scripts": [
        {{
            "scene_num": 1,
            "scene_name": "场景名称",
            "location": "拍摄地点",
            "time": "时间",
            "shots": [
                {{
                    "shot_num": 1,
                    "shot_type": "镜头类型",
                    "camera_movement": "镜头运动",
                    "description": "画面描述",
                    "dialogue": "对话内容",
                    "action": "动作描述",
                    "duration": "时长（秒）"
                }},
                ...
            ]
        }},
        ...
    ]
}}"""
            elif target_level == "full_script":
                prompt = f"""请根据以下分镜脚本生成完整的短剧剧本。

要求：
1. 使用标准剧本格式
2. 包含场景、人物、对话、动作
3. 标注镜头语言和视觉元素
4. 控制每集时长在3-5分钟
5. 对话要自然、有张力
6. 场景描述要视觉化

分镜脚本：
{outline}

{context_text}

请以标准剧本格式返回，格式如下：

【场景1：地点 - 时间】
[镜头：全景/中景/近景/特写]
[画面描述]
[人物动作]

人物A: [对话内容]

人物B: [对话内容]

[动作描述]

【场景2：地点 - 时间】
..."""
            else:
                logger.warning(f"Unknown target_level '{target_level}', defaulting to 'full_script'")
                target_level = "full_script"
                prompt = f"""请根据以下分镜脚本生成完整的短剧剧本。

要求：
1. 使用标准剧本格式
2. 包含场景、人物、对话、动作
3. 标注镜头语言和视觉元素
4. 控制每集时长在3-5分钟
5. 对话要自然、有张力
6. 场景描述要视觉化

分镜脚本：
{outline}

{context_text}

请以标准剧本格式返回，格式如下：

【场景1：地点 - 时间】
[镜头：全景/中景/近景/特写]
[画面描述]
[人物动作]

人物A: [对话内容]

人物B: [对话内容]

[动作描述]

【场景2：地点 - 时间】
..."""
            
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的短剧剧本创作助手，擅长根据结构化内容生成短剧剧本。请保持风格一致性和节奏控制。"
                },
                {"role": "user", "content": prompt}
            ]
            
            _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=4096)
            
            ***REMOVED*** 清理响应文本
            if target_level in ["episode_outline", "shot_script"]:
                result = self._parse_json_response(response_text)
                if result:
                    if target_level == "episode_outline":
                        outlines = result.get("episode_outlines", [])
                        logger.debug(f"Generated {len(outlines)} episode outlines")
                        return json.dumps(outlines, ensure_ascii=False, indent=2)
                    else:
                        scripts = result.get("shot_scripts", [])
                        logger.debug(f"Generated {len(scripts)} shot scripts")
                        return json.dumps(scripts, ensure_ascii=False, indent=2)
                else:
                    logger.warning(f"Failed to parse JSON response for target_level '{target_level}'")
                    return ""
            
            ***REMOVED*** 对于完整剧本，直接返回文本
            script_text = response_text.strip()
            logger.debug(f"Generated full script with {len(script_text)} characters")
            return script_text
        except Exception as e:
            logger.error(f"Error generating script from outline: {e}", exc_info=True)
            return ""
    
    def construct_script_note(
        self,
        content: str,
        timestamp: datetime,
        entities: Optional[List[Entity]] = None,
        generate_summary: bool = True
    ) -> Memory:
        """
        构建短剧剧本原子笔记
        
        使用剧本特有的维度分析，创建包含剧本维度信息的 Memory 对象。
        
        Args:
            content: 原始剧本内容（如果过长会自动截取或生成摘要）
            timestamp: 时间戳，用于记录笔记创建时间
            entities: 实体列表（可选），用于关联相关实体
            generate_summary: 是否生成摘要性内容，默认 True
                - True: 使用 LLM 生成结构化摘要（150-250字）
                - False: 直接截取前1024字符作为原子内容
            
        Returns:
            Memory 对象，包含：
            - 原子内容（摘要或截取的内容）
            - 关键词、上下文、标签
            - 剧本维度信息（存储在 metadata 中）
            - 关联的实体 ID 列表
            
        Note:
            如果适配器不可用，仍会创建 Memory 对象，但不会生成摘要
        """
        if not content or not content.strip():
            logger.warning("Empty content provided for construct_script_note")
            ***REMOVED*** 返回一个默认的 Memory 对象
            memory_id = str(uuid.uuid4())
            return Memory(
                id=memory_id,
                content="",
                timestamp=timestamp,
                keywords=[],
                context="General",
                tags=[],
                entities=[e.id for e in entities] if entities else [],
            )
        
        ***REMOVED*** 使用剧本特有的分析
        analysis = self._analyze_script_content(content)
        
        ***REMOVED*** 如果启用摘要生成，使用 LLM 生成结构化的摘要
        if generate_summary and self.is_available():
            try:
                summary = self._generate_script_summary(content, analysis)
                atomic_content = summary
            except Exception as e:
                logger.warning(f"Failed to generate summary, using truncated content: {e}")
                atomic_content = content[:1024] if len(content) > 1024 else content
        else:
            atomic_content = content[:1024] if len(content) > 1024 else content
        
        ***REMOVED*** 构建 Memory 对象
        memory_id = str(uuid.uuid4())
        memory = Memory(
            id=memory_id,
            content=atomic_content,
            timestamp=timestamp,
            keywords=analysis.get("keywords", []),
            context=analysis.get("context", "General"),
            tags=analysis.get("tags", []),
            entities=[e.id for e in entities] if entities else [],
        )
        
        ***REMOVED*** 在 metadata 中保存剧本维度
        memory.metadata = memory.metadata or {}
        if "script_dimensions" in analysis:
            memory.metadata["script_dimensions"] = analysis["script_dimensions"]
            ***REMOVED*** 将剧本维度信息添加到 tags 中以便检索
            script_dims = analysis["script_dimensions"]
            if script_dims:
                if script_dims.get("script_type"):
                    memory.tags.append(f"类型:{script_dims['script_type']}")
                if script_dims.get("dialogue_style"):
                    memory.tags.append(f"对话风格:{script_dims['dialogue_style']}")
        
        ***REMOVED*** 存储到内存中
        self.memory_store[memory_id] = memory
        
        logger.debug(f"Constructed script note: {memory_id} with {len(memory.keywords)} keywords, "
                    f"{len(memory.tags)} tags, {len(memory.entities)} entities")
        return memory
    
    def _generate_script_summary(self, content: str, analysis: Dict[str, Any]) -> str:
        """
        使用 LLM 生成短剧剧本摘要
        
        生成一个结构化的摘要，包含：
        - 核心情节
        - 主要场景
        - 关键对话
        - 视觉元素
        
        Args:
            content: 原始剧本内容（如果过长会自动截取前1536字符）
            analysis: 已分析得到的元数据字典，包含 keywords 和 context
            
        Returns:
            摘要性内容字符串，长度限制在500字符以内
            
        Note:
            如果生成失败，返回截取的内容（前300字符）
        """
        if not content or not content.strip():
            logger.warning("Empty content provided for _generate_script_summary")
            return ""
        
        ***REMOVED*** 限制内容长度以提高效率
        content_preview = content[:1536] if len(content) > 1536 else content
        keywords_str = ', '.join(analysis.get('keywords', [])[:5]) if analysis.get('keywords') else '无'
        context_str = analysis.get('context', '') or '无'
        
        prompt = f"""请对以下短剧剧本片段进行结构化摘要，提取核心信息。

要求：
1. 提取核心情节和冲突（2-3句话）
2. 识别主要场景和分镜
3. 描述关键对话和动作
4. 保持信息的准确性和完整性
5. 使用简洁、清晰的语言
6. 摘要长度控制在150-250字左右

已提取的关键词：{keywords_str}
已提取的上下文：{context_str}

原始剧本：
{content_preview}

请直接返回摘要内容，不要包含其他格式："""
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的短剧剧本分析助手，擅长提取剧本的核心信息和关键情节。"
                },
                {"role": "user", "content": prompt}
            ]
            
            _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=256)
            
            ***REMOVED*** 清理响应文本
            summary = response_text.strip()
            ***REMOVED*** 移除可能的 markdown 代码块标记
            if summary.startswith("```"):
                lines = summary.split('\n')
                summary = '\n'.join([line for line in lines if not line.strip().startswith('```')])
            
            ***REMOVED*** 限制摘要长度
            summary = summary[:500]
            logger.debug(f"Generated script summary with {len(summary)} characters")
            return summary
        except Exception as e:
            logger.error(f"Error generating script summary: {e}", exc_info=True)
            ***REMOVED*** 返回截取的内容作为后备
            return content[:300] + "..." if len(content) > 300 else content
    
    def retrieve_script_with_reward(
        self,
        query: str,
        original_scripts: List[str],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        根据结构化结果检索原剧本，并计算奖励
        
        适用于短剧剧本的检索奖励机制。使用语义相似度检索相关记忆，
        然后匹配到原始剧本并计算奖励分数。
        
        Args:
            query: 查询文本（通常是结构化后的分集大纲/分镜脚本）
            original_scripts: 原始剧本列表，用于匹配和计算奖励
            top_k: 返回结果数量，默认 10
            
        Returns:
            检索结果列表，每个结果包含以下字段：
            - memory: Memory 对象
            - score: 相似度分数（0-1）
            - reward: 奖励分数（0-1），基于匹配位置计算
            - original_index: 匹配到的原始剧本索引（如果匹配成功）
            - retrieval_rank: 检索排名（1-based）
            
        Note:
            如果适配器不可用或发生错误，返回空列表，不会抛出异常
        """
        if not self.is_available():
            logger.warning("ScriptAdapter not available, cannot perform retrieve_script_with_reward")
            return []
        
        if not query or not query.strip():
            logger.warning("Empty query provided for retrieve_script_with_reward")
            return []
        
        if not original_scripts:
            logger.warning("Empty original_scripts list provided for retrieve_script_with_reward")
            return []
        
        try:
            ***REMOVED*** 1. 使用结构化查询检索相似记忆（检索更多以增加匹配机会）
            similar_memories = self._search_similar_memories(query, top_k=top_k * 2)
            
            if not similar_memories:
                logger.debug("No similar memories found for query")
                return []
            
            ***REMOVED*** 2. 匹配到原始剧本并计算奖励
            results = []
            N = len(original_scripts)
            
            for idx, memory in enumerate(similar_memories[:top_k]):
                ***REMOVED*** 尝试匹配到原始剧本（使用前100字符进行匹配）
                matched_index = None
                memory_preview = memory.content[:100] if memory.content else ""
                
                for orig_idx, orig_script in enumerate(original_scripts):
                    if not orig_script:
                        continue
                    orig_preview = orig_script[:100]
                    ***REMOVED*** 双向匹配检查
                    if memory_preview in orig_script or orig_preview in memory.content:
                        matched_index = orig_idx
                        break
                
                ***REMOVED*** 计算奖励：reward = 1 - index/N（越靠前奖励越高）
                if matched_index is not None:
                    reward = 1.0 - (matched_index / N) if N > 0 else 1.0
                else:
                    ***REMOVED*** 如果没有匹配到，基于检索排名计算奖励
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
            
            logger.debug(f"Retrieved {len(results)} script results with rewards")
            return results[:top_k]
        except Exception as e:
            logger.error(f"Error retrieving script with reward: {e}", exc_info=True)
            return []
    
    def optimize_script_prompt(
        self,
        input_text: str,
        execution_result: str,
        current_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        自动优化：根据输入和 Agent 执行结果来优化 prompt 或上下文结构
        
        专门针对短剧剧本创作的优化，分析执行结果并提供针对性的优化建议。
        
        Args:
            input_text: 输入文本（用于分析，会被截取前500字符）
            execution_result: Agent 执行结果（用于分析，会被截取前500字符）
            current_prompt: 当前的 prompt（可选），如果提供会被用于优化
            
        Returns:
            优化结果字典，包含以下字段：
            - optimized_prompt: str - 优化后的 prompt
            - optimized_context: Dict[str, Any] - 优化后的上下文结构建议
            - analysis: Dict[str, Any] - 分析结果，包含：
                - satisfaction: 满足程度（"满足"/"部分满足"/"不满足"）
                - issues: 问题列表
                - suggestions: 建议列表
            
        Note:
            如果适配器不可用或发生错误，返回默认结构，不会抛出异常
        """
        if not self.is_available():
            logger.warning("ScriptAdapter not available, cannot perform optimize_script_prompt")
            return {
                "optimized_prompt": current_prompt or "",
                "optimized_context": {},
                "analysis": {}
            }
        
        if not input_text or not input_text.strip():
            logger.warning("Empty input_text provided for optimize_script_prompt")
            return {
                "optimized_prompt": current_prompt or "",
                "optimized_context": {},
                "analysis": {}
            }
        
        if not execution_result or not execution_result.strip():
            logger.warning("Empty execution_result provided for optimize_script_prompt")
            return {
                "optimized_prompt": current_prompt or "",
                "optimized_context": {},
                "analysis": {}
            }
        
        try:
            ***REMOVED*** 限制文本长度以提高效率
            input_preview = input_text[:500] if len(input_text) > 500 else input_text
            result_preview = execution_result[:500] if len(execution_result) > 500 else execution_result
            prompt_preview = current_prompt[:500] if current_prompt and len(current_prompt) > 500 else (current_prompt or "无")
            
            prompt = f"""请分析以下短剧剧本创作的输入和执行结果，优化 prompt 和上下文结构。

输入：
{input_preview}

执行结果：
{result_preview}

当前 Prompt（如果提供）：
{prompt_preview}

请分析：
1. 执行结果是否满足短剧剧本创作的要求？
2. 如果未满足，prompt 或上下文结构需要如何优化？
3. 针对短剧剧本的特殊需求（分镜、场景、对话、节奏），提供优化建议

请以 JSON 格式返回结果：
{{
    "analysis": {{
        "satisfaction": "满足/部分满足/不满足",
        "issues": ["问题1", "问题2", ...],
        "suggestions": ["建议1", "建议2", ...]
    }},
    "optimized_prompt": "优化后的 prompt",
    "optimized_context": {{
        "structure": "上下文结构建议",
        "key_points": ["要点1", "要点2", ...],
        "script_specific": {{
            "shot_design": "分镜设计建议",
            "dialogue_style": "对话风格建议",
            "rhythm_control": "节奏控制建议"
        }}
    }}
}}"""
            
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的短剧剧本创作优化助手，擅长分析执行结果并优化 prompt 和上下文结构。请始终以有效的 JSON 格式返回结果。"
                },
                {"role": "user", "content": prompt}
            ]
            
            _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=2048)
            result = self._parse_json_response(response_text)
            
            if result:
                optimized_prompt = result.get("optimized_prompt", current_prompt or "")
                optimized_context = result.get("optimized_context", {})
                analysis = result.get("analysis", {})
                
                logger.debug(f"Optimized script prompt: satisfaction={analysis.get('satisfaction', 'unknown')}, "
                           f"issues={len(analysis.get('issues', []))}, "
                           f"suggestions={len(analysis.get('suggestions', []))}")
                
                return {
                    "optimized_prompt": optimized_prompt,
                    "optimized_context": optimized_context,
                    "analysis": analysis
                }
            else:
                logger.warning(f"Failed to parse optimization response: {response_text[:200]}")
                return {
                    "optimized_prompt": current_prompt or "",
                    "optimized_context": {},
                    "analysis": {}
                }
        except Exception as e:
            logger.error(f"Error optimizing script prompt: {e}", exc_info=True)
            return {
                "optimized_prompt": current_prompt or "",
                "optimized_context": {},
                "analysis": {}
            }

