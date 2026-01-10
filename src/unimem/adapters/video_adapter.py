"""
短视频文案适配器

专门用于自媒体和电商短视频文案创作的适配器，基于 atom_link_adapter 的基础架构，
针对短视频混剪创作的特殊需求进行定制化实现。

短视频创作特点：
- 剪辑流程：素材导入 -> 文案撰写 -> 镜头匹配 -> 节奏控制 -> 最终成片
- 个性化定制：基于用户记忆和偏好
- 商品营销：结合商品信息进行推广
- 素材利用：最大化利用拍摄镜头素材

主要功能：
1. Word 文档解析：解析用户记忆、商品信息、镜头素材
2. 个性化文案生成：基于用户偏好生成文案
3. 镜头素材匹配：根据文案匹配最佳镜头
4. 剪辑脚本生成：生成完整的剪辑脚本
5. 节奏控制：控制视频节奏和时长

工业级特性：
- 参数验证和输入检查
- 统一异常处理
- Word 文档解析支持
- 错误处理和降级
"""

import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    Document = None

from .atom_link_adapter import AtomLinkAdapter
from .base import AdapterError, AdapterNotAvailableError
from ..memory_types import Memory, Experience, Context, MemoryType
from ..chat import ark_deepseek_v3_2

logger = logging.getLogger(__name__)


class VideoAdapter(AtomLinkAdapter):
    """
    短视频文案适配器
    
    继承 AtomLinkAdapter 的基础功能，但针对短视频混剪创作进行定制化。
    
    核心功能：
    1. Word 文档解析：解析用户记忆、商品信息、镜头素材
    2. 个性化文案生成：基于用户偏好生成文案
    3. 镜头素材匹配：根据文案匹配最佳镜头
    4. 剪辑脚本生成：生成完整的剪辑脚本
    
    UniMem 优势利用：
    1. 语义检索：从 UniMem 中检索相关的历史创作和用户偏好
    2. 记忆存储：将生成的脚本存储到 UniMem，建立关联网络
    3. 跨任务学习：利用通用记忆和任务记忆，实现风格一致性
    4. 记忆演化：通过 REFLECT 操作优化和总结创作经验
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, unimem_instance=None):
        """
        初始化短视频文案适配器
        
        Args:
            config: 适配器配置
            unimem_instance: UniMem 实例（可选），用于深度集成 UniMem 功能
        """
        super().__init__(config)
        self.unimem = unimem_instance
        if self.unimem:
            logger.info("Video adapter initialized with UniMem integration")
        else:
            logger.info("Video adapter initialized (standalone mode)")
    
    def _do_initialize(self) -> None:
        """
        初始化短视频文案适配器
        
        调用父类初始化以复用基础架构（向量存储、嵌入模型等），
        然后进行短视频创作特定的初始化。
        """
        super()._do_initialize()
        logger.info("Video adapter initialized (specialized for short video script writing)")
    
    def enrich_memories_from_unimem(
        self,
        task_memories: List[str],
        video_type: str,
        top_k: int = 10
    ) -> Dict[str, List[str]]:
        """
        从 UniMem 中丰富记忆信息
        
        利用 UniMem 的语义检索能力，从历史记忆中检索：
        1. 相关的历史创作（相似题材、风格、主题）
        2. 用户的创作偏好和习惯
        3. 成功的创作模式和经验
        4. 相关的实体和关系
        
        Args:
            task_memories: 当前任务记忆列表
            video_type: 视频类型
            top_k: 每个检索维度返回的结果数量
            
        Returns:
            丰富的记忆字典：
            - historical_scripts: 历史相关脚本
            - successful_patterns: 成功的创作模式
            - related_entities: 相关的实体和关系
            - user_style_preferences: 用户的风格偏好
        """
        if not self.unimem:
            logger.debug("UniMem not available, skipping memory enrichment")
            return {
                "historical_scripts": [],
                "successful_patterns": [],
                "related_entities": [],
                "user_style_preferences": []
            }
        
        enriched = {
            "historical_scripts": [],
            "successful_patterns": [],
            "related_entities": [],
            "user_style_preferences": []
        }
        
        try:
            # 1. 从任务记忆构建查询，检索相关的历史创作
            task_query = " ".join(task_memories[:3])  # 使用前3个任务记忆作为查询
            if task_query:
                # 使用 UniMem 的语义检索
                # 检查是否是 HTTP 服务客户端（不需要 context 参数）
                if hasattr(self.unimem, 'base_url'):
                    recall_results = self.unimem.recall(
                        query=f"{video_type} {task_query}",
                        top_k=top_k
                    )
                else:
                    recall_results = self.unimem.recall(
                        query=f"{video_type} {task_query}",
                        context=Context(),
                        top_k=top_k
                    )
                
                for result in recall_results:
                    if result.memory:
                        # 筛选视频相关的记忆
                        content = result.memory.content
                        if any(keyword in content.lower() for keyword in 
                               ["视频", "脚本", "文案", "镜头", "剪辑", "video", "script"]):
                            enriched["historical_scripts"].append({
                                "content": content[:200],  # 截取前200字符
                                "score": result.score,
                                "metadata": result.memory.metadata
                            })
            
            # 2. 检索成功的创作模式（通过标签或元数据）
            if video_type:
                if hasattr(self.unimem, 'base_url'):
                    pattern_results = self.unimem.recall(
                        query=f"成功 {video_type} 模式 经验",
                        top_k=top_k
                    )
                else:
                    pattern_results = self.unimem.recall(
                        query=f"成功 {video_type} 模式 经验",
                        context=Context(),
                        top_k=top_k
                    )
                for result in pattern_results[:5]:  # 只取前5个
                    if result.memory:
                        enriched["successful_patterns"].append({
                            "pattern": result.memory.content[:150],
                            "score": result.score
                        })
            
            # 3. 检索用户风格偏好（通过通用记忆）
            if hasattr(self.unimem, 'base_url'):
                style_results = self.unimem.recall(
                    query="用户 风格 偏好 语气 表达方式",
                    top_k=top_k
                )
            else:
                style_results = self.unimem.recall(
                    query="用户 风格 偏好 语气 表达方式",
                    context=Context(),
                    top_k=top_k
                )
            for result in style_results[:5]:
                if result.memory:
                    enriched["user_style_preferences"].append({
                        "preference": result.memory.content[:150],
                        "score": result.score
                    })
            
            logger.info(f"Enriched memories from UniMem: {len(enriched['historical_scripts'])} scripts, "
                       f"{len(enriched['successful_patterns'])} patterns, "
                       f"{len(enriched['user_style_preferences'])} preferences")
        except Exception as e:
            logger.warning(f"Error enriching memories from UniMem: {e}", exc_info=True)
        
        return enriched
    
    def store_script_to_unimem(
        self,
        script_data: Dict[str, Any],
        task_memories: List[str],
        video_type: str,
        platform: str
    ) -> Optional[str]:
        """
        将生成的脚本存储到 UniMem
        
        使用 UniMem 的 RETAIN 操作，将脚本内容存储为记忆，
        并建立与其他记忆的关联，便于后续检索和学习。
        
        Args:
            script_data: 生成的脚本数据
            task_memories: 任务记忆列表
            video_type: 视频类型
            platform: 平台类型
            
        Returns:
            存储的记忆 ID，如果存储失败返回 None
        """
        if not self.unimem:
            logger.debug("UniMem not available, skipping script storage")
            return None
        
        try:
            # 构建记忆内容
            script_summary = script_data.get("summary", {})
            script_content = script_data.get("script", "")
            
            # 创建 Experience 对象
            experience_content = f"""
视频类型：{video_type}
平台：{platform}
脚本摘要：{json.dumps(script_summary, ensure_ascii=False)}
脚本预览：{script_content[:500]}
任务需求：{' | '.join(task_memories[:3])}
            """.strip()
            
            experience = Experience(
                content=experience_content,
                timestamp=datetime.now()
            )
            
            # 创建 Context 对象
            # 构建决策上下文（Context Graph增强）
            context = Context(
                metadata={
                    "source": "video_script",  # 明确标识来源
                    "task_description": f"生成{video_type}类型短视频脚本",
                    "video_type": video_type,
                    "platform": platform,
                    "segments_count": len(script_data.get("segments", [])),
                    "duration": script_data.get("editing_script", {}).get("total_duration", 0),
                    # 决策痕迹（Context Graph增强）
                    "inputs": task_memories[:5] if task_memories else [],  # 使用的任务记忆
                    "rules": [
                        f"{platform}平台规则",
                        f"{video_type}类型脚本规范",
                        "3秒原则（前3秒抓住注意力）",
                        "转化率优化要求"
                    ],
                    "exceptions": [],  # 可以在这里添加异常情况
                    "approvals": [],  # 可以在这里添加审批流程
                    "reasoning": f"基于{len(task_memories) if task_memories else 0}条任务记忆，生成{video_type}类型脚本，适配{platform}平台特点",
                    # 确保decision_trace字段被正确设置
                    "decision_trace": {
                        "inputs": task_memories[:5] if task_memories else [],
                        "rules_applied": [
                            f"{platform}平台规则",
                            f"{video_type}类型脚本规范",
                            "3秒原则（前3秒抓住注意力）",
                            "转化率优化要求"
                        ],
                        "exceptions": [],
                        "approvals": [],
                        "timestamp": datetime.now().isoformat(),
                    }
                }
            )
            
            # 使用 UniMem 的 RETAIN 操作存储
            memory = self.unimem.retain(experience, context)
            
            logger.info(f"Stored script to UniMem: memory_id={memory.id}")
            return memory.id
        except Exception as e:
            logger.warning(f"Error storing script to UniMem: {e}", exc_info=True)
            return None
    
    def create_word_template(
        self, 
        output_path: str = "video_script_template.docx",
        auto_fill_from_memory: bool = True
    ) -> str:
        """
        创建 Word 模板文档，用户可以下载填写后上传
        
        模板包含所有必要的字段，用户只需填写相应内容即可。
        
        增强功能：
        1. 智能提示：根据视频类型提供不同的填写建议
        2. 自动填充：从UniMem历史记忆中自动填充通用偏好和镜头素材建议
        3. 格式容错：支持更多灵活的填写格式
        
        Args:
            output_path: 模板文件保存路径（默认为 "video_script_template.docx"）
            auto_fill_from_memory: 是否从历史记忆中自动填充部分内容（默认True）
            
        Returns:
            创建的模板文件路径
            
        Raises:
            AdapterNotAvailableError: 如果 python-docx 不可用
            AdapterError: 如果路径无效
        """
        if not DOCX_AVAILABLE:
            raise AdapterNotAvailableError(
                "python-docx library not available. Install with: pip install python-docx",
                adapter_name="VideoAdapter"
            )
        
        if not output_path or not isinstance(output_path, str):
            raise AdapterError("output_path must be a non-empty string", adapter_name="VideoAdapter")
        
        try:
            from docx.shared import Pt, RGBColor
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            
            doc = Document()
            
            # 标题
            title = doc.add_heading('短视频创作需求模板', 0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # 说明
            doc.add_paragraph('请根据以下说明填写相应内容，所有内容都是可选的，根据需要填写即可。')
            
            # 智能提示说明
            if auto_fill_from_memory and self.unimem:
                doc.add_paragraph('💡 提示：系统已根据您的历史偏好自动填充了部分建议内容，您可以直接使用或修改。')
            else:
                doc.add_paragraph('💡 提示：建议填写尽可能详细的信息，以便生成更符合您需求的视频剧本。')
            doc.add_paragraph()
            
            # 1. 视频基本信息
            doc.add_heading('一、视频基本信息', level=1)
            doc.add_paragraph('视频类型（必填，从以下选项选择其一）：')
            doc.add_paragraph('  - ecommerce（电商推广）', style='List Bullet')
            doc.add_paragraph('  - ip_building（个人IP打造）', style='List Bullet')
            doc.add_paragraph('  - knowledge（知识分享）', style='List Bullet')
            doc.add_paragraph('  - vlog（生活Vlog）', style='List Bullet')
            doc.add_paragraph('  - media（自媒体内容）', style='List Bullet')
            doc.add_paragraph('视频类型: [请填写，例如：ecommerce]')
            doc.add_paragraph()
            
            doc.add_paragraph('目标平台（必填，从以下选项选择其一）：')
            doc.add_paragraph('  - douyin（抖音）', style='List Bullet')
            doc.add_paragraph('  - xiaohongshu（小红书）', style='List Bullet')
            doc.add_paragraph('  - tiktok（TikTok国际）', style='List Bullet')
            doc.add_paragraph('  - youtube（YouTube）', style='List Bullet')
            doc.add_paragraph('目标平台: [请填写，例如：douyin]')
            doc.add_paragraph()
            
            doc.add_paragraph('目标时长（秒，可选，默认60秒）: [请填写数字，例如：60]')
            doc.add_paragraph()
            
            # 2. 当前任务需求
            doc.add_heading('二、当前任务需求', level=1)
            doc.add_paragraph('请详细描述本次视频创作的具体需求，每行一条：')
            doc.add_paragraph('[例如：推广新品手机]')
            doc.add_paragraph('[例如：突出性价比和拍照功能]')
            doc.add_paragraph('[例如：目标受众：年轻人]')
            doc.add_paragraph()
            
            # 3. 修改需求（可选）
            doc.add_heading('三、修改需求（可选）', level=1)
            doc.add_paragraph('如果在已有脚本基础上进行修改，请填写修改要求：')
            doc.add_paragraph('[例如：增加情感共鸣]')
            doc.add_paragraph('[例如：调整语气更轻松]')
            doc.add_paragraph()
            
            # 4. 通用记忆总结（可选）
            doc.add_heading('四、通用记忆总结（可选）', level=1)
            doc.add_paragraph('跨任务的用户偏好和通用风格偏好，这些会应用到所有视频创作：')
            
            # 尝试从历史记忆中自动填充通用偏好
            auto_filled_general_memories = []
            if auto_fill_from_memory and self.unimem:
                try:
                    auto_filled_general_memories = self._get_auto_fill_general_memories()
                    if auto_filled_general_memories:
                        doc.add_paragraph('【系统建议（基于历史记录）】', style='Strong')
                        for mem in auto_filled_general_memories[:5]:
                            doc.add_paragraph(f'✓ {mem}', style='List Bullet')
                        doc.add_paragraph('【您也可以填写或修改】', style='Strong')
                except Exception as e:
                    logger.debug(f"Failed to auto-fill general memories: {e}")
            
            if not auto_filled_general_memories:
                doc.add_paragraph('[例如：喜欢用生活化语言]')
                doc.add_paragraph('[例如：避免使用"姐妹们"等称呼]')
                doc.add_paragraph('[例如：偏好真实体验分享]')
            doc.add_paragraph()
            
            # 5. 用户偏好设置
            doc.add_heading('五、用户偏好设置（可选）', level=1)
            doc.add_paragraph('请使用"键: 值"的格式填写，例如：')
            
            # 尝试从历史记忆中自动填充用户偏好
            auto_filled_preferences = {}
            if auto_fill_from_memory and self.unimem:
                try:
                    auto_filled_preferences = self._get_auto_fill_preferences()
                    if auto_filled_preferences:
                        doc.add_paragraph('【系统建议（基于历史记录）】', style='Strong')
                        for key, value in list(auto_filled_preferences.items())[:5]:
                            doc.add_paragraph(f'✓ {key}: {value}', style='List Bullet')
                        doc.add_paragraph('【您也可以填写或修改】', style='Strong')
                except Exception as e:
                    logger.debug(f"Failed to auto-fill preferences: {e}")
            
            if not auto_filled_preferences:
                doc.add_paragraph('风格偏好: 真诚自然')
                doc.add_paragraph('平台偏好: 抖音')
                doc.add_paragraph('语气偏好: 像朋友分享')
            doc.add_paragraph('[请在此填写您的偏好设置]')
            doc.add_paragraph()
            
            # 6. 商品信息（仅电商题材需要）
            doc.add_heading('六、商品信息（仅电商题材需要）', level=1)
            doc.add_paragraph('请使用"键: 值"的格式填写，例如：')
            doc.add_paragraph('产品名称: 新品手机')
            doc.add_paragraph('核心卖点: 性价比、拍照')
            doc.add_paragraph('目标价格: 2000-3000元')
            doc.add_paragraph('[请在此填写商品信息]')
            doc.add_paragraph()
            
            # 7. 镜头素材
            doc.add_heading('七、镜头素材', level=1)
            doc.add_paragraph('请描述可用的镜头素材，每行一个镜头，使用"键: 值"格式或直接描述：')
            doc.add_paragraph('💡 提示：镜头素材越详细，生成的剧本越精准。建议包括：产品展示、使用场景、细节特写、对比效果等。')
            
            # 尝试从历史记忆中自动填充镜头素材建议
            auto_filled_shots = []
            if auto_fill_from_memory and self.unimem:
                try:
                    auto_filled_shots = self._get_auto_fill_shot_suggestions()
                    if auto_filled_shots:
                        doc.add_paragraph('【系统建议（基于历史记录）】', style='Strong')
                        for i, shot in enumerate(auto_filled_shots[:8], 1):
                            doc.add_paragraph(f'✓ 镜头{i}: {shot}', style='List Bullet')
                        doc.add_paragraph('【您也可以填写或修改】', style='Strong')
                except Exception as e:
                    logger.debug(f"Failed to auto-fill shot suggestions: {e}")
            
            if not auto_filled_shots:
                doc.add_paragraph('镜头1: 产品特写，展示手机外观')
                doc.add_paragraph('镜头2: 使用场景，年轻人拍照')
                doc.add_paragraph('[请在此填写镜头素材]')
            doc.add_paragraph()
            
            # 保存文档
            doc.save(output_path)
            logger.info(f"Word template created: {output_path} (auto_fill: {auto_fill_from_memory})")
            return output_path
        except Exception as e:
            raise AdapterError(
                f"Failed to create Word template: {e}",
                adapter_name="VideoAdapter",
                cause=e
            ) from e
    
    def _get_auto_fill_general_memories(self) -> List[str]:
        """
        从UniMem历史记忆中获取通用记忆建议
        
        Returns:
            通用记忆列表
        """
        if not self.unimem:
            return []
        
        try:
            # 检索通用记忆和风格偏好
            results = self.unimem.recall(
                query="用户风格偏好 通用记忆 创作偏好",
                memory_type=MemoryType.OPINION,  # 偏好通常是OPINION类型
                top_k=5
            )
            
            memories = []
            for result in results:
                if result.memory and result.memory.content:
                    content = result.memory.content
                    # 提取关键偏好信息（过滤掉太长的内容）
                    if len(content) < 200:
                        memories.append(content)
            
            return memories[:5]
        except Exception as e:
            logger.debug(f"Failed to get auto-fill general memories: {e}")
            return []
    
    def _get_auto_fill_preferences(self) -> Dict[str, str]:
        """
        从UniMem历史记忆中获取用户偏好建议
        
        Returns:
            偏好字典
        """
        if not self.unimem:
            return {}
        
        try:
            # 检索用户偏好记忆
            results = self.unimem.recall(
                query="用户偏好设置 风格偏好 语气偏好 平台偏好",
                top_k=10
            )
            
            preferences = {}
            for result in results:
                if result.memory and result.memory.metadata:
                    metadata = result.memory.metadata
                    # 从metadata中提取偏好信息
                    for key in ["style_preference", "tone_preference", "platform_preference", "风格偏好", "语气偏好", "平台偏好"]:
                        if key in metadata and metadata[key]:
                            pref_key = key.replace("_preference", "").replace("偏好", "")
                            if pref_key not in preferences:
                                preferences[pref_key] = metadata[key]
            
            return preferences
        except Exception as e:
            logger.debug(f"Failed to get auto-fill preferences: {e}")
            return {}
    
    def _get_auto_fill_shot_suggestions(self) -> List[str]:
        """
        从UniMem历史记忆中获取镜头素材建议
        
        Returns:
            镜头素材描述列表
        """
        if not self.unimem:
            return []
        
        try:
            # 检索历史脚本中的镜头信息
            results = self.unimem.recall(
                query="镜头素材 画面描述 视频脚本 镜头",
                top_k=5
            )
            
            shots = []
            for result in results:
                if result.memory:
                    # 从metadata中提取镜头信息
                    metadata = result.memory.get("metadata", {}) if isinstance(result.memory, dict) else getattr(result.memory, "metadata", {})
                    if isinstance(metadata, dict):
                        script_segments = metadata.get("script_segments", [])
                        if script_segments:
                            for segment in script_segments[:3]:  # 每个脚本取前3个镜头
                                if isinstance(segment, dict):
                                    shot_desc = segment.get("画面", segment.get("shot_description", ""))
                                    if shot_desc and shot_desc not in shots:
                                        shots.append(shot_desc)
            
            # 如果没有找到，返回通用的镜头建议
            if not shots:
                shots = [
                    "产品整体展示（全景，展示产品全貌）",
                    "产品特写（细节展示，突出卖点）",
                    "使用场景展示（实际应用场景）",
                    "对比效果（使用前后对比）",
                    "用户反应镜头（惊喜/满意表情）",
                    "产品细节特写（材质/做工细节）"
                ]
            
            return shots[:8]
        except Exception as e:
            logger.debug(f"Failed to get auto-fill shot suggestions: {e}")
            return []
    
    def parse_word_document(self, doc_path: str) -> Dict[str, Any]:
        """
        解析 Word 文档，提取用户记忆、商品信息、镜头素材
        
        使用 LLM API 从 Word 文档中提取短视频剧本 prompt 中需要的参数。
        
        支持三种类型的记忆提取：
        1. 当前任务记忆（需求）：当前视频创作任务的具体需求
        2. 修改需求记忆：对话中提取的新的修改需求
        3. 通用记忆总结：跨任务的用户偏好和通用风格偏好
        
        Args:
            doc_path: Word 文档路径（.docx 格式）
            
        Returns:
            解析结果字典，包含：
            - task_memories: List[str] - 当前任务记忆（需求）
            - modification_memories: List[str] - 修改需求记忆
            - general_memories: List[str] - 跨任务通用记忆总结
            - user_preferences: Dict[str, Any] - 用户偏好（风格、语气、平台偏好等）
            - product_info: Dict[str, Any] - 商品信息
            - shot_materials: List[Dict[str, Any]] - 镜头素材信息
            - video_type: str - 视频类型
            - platform: str - 目标平台
            - duration_seconds: int - 目标时长（秒）
            
        Raises:
            AdapterNotAvailableError: 如果 python-docx 不可用
            AdapterError: 如果文档路径无效或解析失败
        """
        if not DOCX_AVAILABLE:
            raise AdapterNotAvailableError(
                "python-docx library not available. Install with: pip install python-docx",
                adapter_name="VideoAdapter"
            )
        
        if not doc_path or not isinstance(doc_path, str):
            raise AdapterError("doc_path must be a non-empty string", adapter_name="VideoAdapter")
        
        doc_file = Path(doc_path)
        if not doc_file.exists():
            raise AdapterError(f"Document file not found: {doc_path}", adapter_name="VideoAdapter")
        
        if not doc_file.suffix.lower() == ".docx":
            raise AdapterError(
                f"Unsupported file format: {doc_file.suffix}. Only .docx files are supported",
                adapter_name="VideoAdapter"
            )
        
        try:
            doc = Document(doc_path)
            
            # 解析文档内容
            full_text = []
            for paragraph in doc.paragraphs:
                text = paragraph.text.strip()
                if text:
                    full_text.append(text)
            
            # 将文档内容合并为文本
            document_text = "\n".join(full_text)
            
            # 如果文档为空，返回默认值
            if not document_text.strip():
                logger.warning("Document is empty, returning default values")
                return {
                "task_memories": [],
                "modification_memories": [],
                "general_memories": [],
                "user_preferences": {},
                "product_info": {},
                "shot_materials": [],
                    "video_type": "ecommerce",
                    "platform": "douyin",
                    "duration_seconds": 60
            }
            
            # 使用 LLM API 提取参数
            try:
                prompt = f"""请从以下 Word 文档内容中提取短视频剧本生成所需的所有参数。

文档内容：
{document_text}

请提取以下信息并以 JSON 格式返回：

1. **视频基本信息**（必填）：
   - video_type: 视频类型，从以下选项选择：ecommerce（电商推广）、ip_building（个人IP打造）、knowledge（知识分享）、vlog（生活Vlog）、media（自媒体内容）。如果未找到，默认为 "ecommerce"
   - platform: 目标平台，从以下选项选择：douyin（抖音）、xiaohongshu（小红书）、tiktok（TikTok国际）、youtube（YouTube）。如果未找到，默认为 "douyin"
   - duration_seconds: 目标时长（秒），数字。如果未找到，默认为 60

2. **当前任务需求**（二、当前任务需求）：
   - task_memories: 字符串数组，每行一条需求

3. **修改需求**（三、修改需求，可选）：
   - modification_memories: 字符串数组，每行一条修改需求

4. **通用记忆总结**（四、通用记忆总结，可选）：
   - general_memories: 字符串数组，每行一条通用记忆

5. **用户偏好设置**（五、用户偏好设置，可选）：
   - user_preferences: 对象，键值对格式（如：风格偏好: 真诚自然）

6. **商品信息**（六、商品信息，仅电商题材需要，可选）：
   - product_info: 对象，键值对格式（如：产品名称: 新品手机）

7. **镜头素材**（七、镜头素材，可选）：
   - shot_materials: 对象数组，每个对象包含 label（可选）和 description

请严格按照以下 JSON 格式返回：
{{
    "video_type": "ecommerce",
    "platform": "douyin",
    "duration_seconds": 60,
    "task_memories": ["需求1", "需求2"],
    "modification_memories": ["修改需求1"],
    "general_memories": ["通用记忆1"],
    "user_preferences": {{
        "风格偏好": "真诚自然",
        "语气偏好": "像朋友分享"
    }},
    "product_info": {{
        "产品名称": "新品手机",
        "核心卖点": "性价比、拍照"
    }},
    "shot_materials": [
        {{"label": "镜头1", "description": "产品特写，展示手机外观"}},
        {{"description": "使用场景，年轻人拍照"}}
    ]
}}

注意：
- 如果某个字段在文档中不存在，请使用空数组 [] 或空对象 {{}} 或默认值
- 过滤掉模板提示内容（如 "[请填写]"、"[例如]"、"例如："、"【系统建议】"、"【您也可以填写或修改】"、"✓" 等标记）
- 键值对格式支持多种格式：
  * 中文冒号（：）和英文冒号（:）
  * 等号（=）分隔
  * 空格分隔的键值对
- 镜头素材支持多种格式：
  * "镜头1: 描述"
  * "镜头1：描述"
  * "镜头1=描述"
  * "镜头1 描述"
  * 直接描述（没有编号）
- 任务记忆和通用记忆支持：
  * 每行一条
  * 列表格式（用 - 或 * 开头）
  * 编号格式（1. 2. 3.）
- 对于格式不规范的填写，尽量智能提取有用信息
- 确保所有字段都存在，即使值为空"""
                
                messages = [
                    {
                        "role": "system",
                        "content": """你是一个专业的文档解析助手，擅长从 Word 文档中提取结构化信息。请始终以有效的 JSON 格式返回结果。

重要能力：
1. 容错性强：对于格式不规范的填写，能够智能提取有用信息
2. 灵活解析：支持多种键值对格式（冒号、等号、空格等）
3. 过滤噪音：自动过滤模板提示内容、示例内容、系统建议标记等
4. 智能推断：对于不完整的信息，能够根据上下文合理推断
5. 保证完整性：确保返回的JSON包含所有必需字段"""
                    },
                    {"role": "user", "content": prompt}
                ]
                
                _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=2048)
                result = self._parse_json_response(response_text)
                
                if result:
                    # 验证和规范化结果
                    parsed_result = {
                        "task_memories": result.get("task_memories", []),
                        "modification_memories": result.get("modification_memories", []),
                        "general_memories": result.get("general_memories", []),
                        "user_preferences": result.get("user_preferences", {}),
                        "product_info": result.get("product_info", {}),
                        "shot_materials": result.get("shot_materials", []),
                        "video_type": result.get("video_type", "ecommerce"),
                        "platform": result.get("platform", "douyin"),
                        "duration_seconds": result.get("duration_seconds", 60)
                    }
                    
                    # 验证 video_type
                    valid_video_types = ["ecommerce", "ip_building", "knowledge", "vlog", "media"]
                    if parsed_result["video_type"] not in valid_video_types:
                        logger.warning(f"Invalid video_type '{parsed_result['video_type']}', using default 'ecommerce'")
                        parsed_result["video_type"] = "ecommerce"
                    
                    # 验证 platform
                    valid_platforms = ["douyin", "xiaohongshu", "tiktok", "youtube"]
                    if parsed_result["platform"] not in valid_platforms:
                        logger.warning(f"Invalid platform '{parsed_result['platform']}', using default 'douyin'")
                        parsed_result["platform"] = "douyin"
                    
                    # 验证 duration_seconds
                    try:
                        parsed_result["duration_seconds"] = int(parsed_result["duration_seconds"])
                        if parsed_result["duration_seconds"] <= 0:
                            parsed_result["duration_seconds"] = 60
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid duration_seconds '{parsed_result['duration_seconds']}', using default 60")
                        parsed_result["duration_seconds"] = 60
                    
                    # 确保列表类型
                    for key in ["task_memories", "modification_memories", "general_memories", "shot_materials"]:
                        if not isinstance(parsed_result[key], list):
                            parsed_result[key] = []
                    
                    # 确保字典类型
                    for key in ["user_preferences", "product_info"]:
                        if not isinstance(parsed_result[key], dict):
                            parsed_result[key] = {}
                    
                    logger.info(f"Parsed Word document using LLM: {len(parsed_result['task_memories'])} task memories, "
                               f"{len(parsed_result['modification_memories'])} modification memories, "
                               f"{len(parsed_result['general_memories'])} general memories, "
                               f"{len(parsed_result['user_preferences'])} preference fields, "
                               f"{len(parsed_result['product_info'])} product fields, "
                               f"{len(parsed_result['shot_materials'])} shots, "
                               f"video_type={parsed_result['video_type']}, platform={parsed_result['platform']}, "
                               f"duration={parsed_result['duration_seconds']}s")
                    
                    return parsed_result
                else:
                    logger.warning("LLM failed to parse document, falling back to default values")
                    raise ValueError("LLM parsing failed")
                    
            except Exception as llm_error:
                logger.warning(f"LLM parsing failed: {llm_error}, using default values")
                # 如果 LLM 解析失败，返回默认值
                return {
                    "task_memories": [],
                    "modification_memories": [],
                    "general_memories": [],
                    "user_preferences": {},
                    "product_info": {},
                    "shot_materials": [],
                    "video_type": "ecommerce",
                    "platform": "douyin",
                    "duration_seconds": 60
                }
                
        except Exception as e:
            raise AdapterError(
                f"Failed to parse Word document: {e}",
                adapter_name="VideoAdapter",
                cause=e
            ) from e
    
    def generate_video_script(
        self,
        task_memories: Optional[List[str]] = None,
        modification_memories: Optional[List[str]] = None,
        general_memories: Optional[List[str]] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
        product_info: Optional[Dict[str, Any]] = None,
        shot_materials: Optional[List[Dict[str, Any]]] = None,
        video_type: str = "ecommerce",
        duration_seconds: int = 60,
        platform: str = "douyin",
        script_len: Optional[int] = None,
        use_unimem_retrieval: bool = True,
        store_to_unimem: bool = True
    ) -> Dict[str, Any]:
        """
        生成短视频文案和剪辑脚本
        
        支持多种题材：电商推广、个人IP打造、知识分享、生活 Vlog 等
        题材特定需求（如电商卖点、IP人设、知识结构等）应放在用户记忆的 Word 文档中
        
        通用功能（保留在 prompt 中）：
        1. 文案撰写：生成吸引人的文案（5-20字/句，开场吸引、中间递进、结尾转化）
        2. 镜头匹配：为每个文案段落匹配最佳镜头（不重复使用）
        3. 节奏控制：控制时长和节奏
        4. 剪辑脚本：生成完整的剪辑指导
        
        深度结合用户记忆和偏好：
        - 任务记忆：当前任务的具体需求（包含题材特定要求）
        - 修改记忆：对话中提取的修改需求
        - 通用记忆：跨任务的用户风格偏好
        
        Args:
            task_memories: 当前任务记忆（需求）列表，应包含题材特定需求（如电商卖点、IP人设等）
            modification_memories: 修改需求记忆列表
            general_memories: 跨任务通用记忆总结列表
            user_preferences: 用户偏好字典（风格、语气、平台偏好等）
            product_info: 商品信息字典（仅电商题材需要，其他题材可传空）
            shot_materials: 镜头素材信息列表（候选镜头）
            video_type: 视频类型，"ecommerce"（电商）、"ip_building"（个人IP）、"knowledge"（知识分享）、"vlog"（生活Vlog）等
            duration_seconds: 目标视频时长（秒），默认 60 秒
            platform: 平台类型，"douyin"（抖音）、"xiaohongshu"（小红书）、"tiktok"（TikTok国际）、"youtube"（YouTube）
            script_len: 脚本段数（序号上限），如果不提供则根据时长自动计算
            
        Returns:
            生成的脚本字典（JSON 格式），包含：
            - script: str - 完整文案
            - segments: List[Dict[str, Any]] - 分段详情（包含序号、分类、景别、文案、画面）
            - editing_script: Dict[str, Any] - 剪辑脚本（包含时间轴、转场等）
            - total_duration: float - 预计总时长（秒）
            
        Raises:
            AdapterError: 如果参数无效
        """
        if not self.is_available():
            logger.warning("VideoAdapter not available, cannot perform generate_video_script")
            return {}
        
        # 支持多种视频类型
        valid_video_types = ["ecommerce", "ip_building", "knowledge", "vlog", "media"]
        if video_type not in valid_video_types:
            raise AdapterError(
                f"Invalid video_type '{video_type}', must be one of: {', '.join(valid_video_types)}",
                adapter_name="VideoAdapter"
            )
        
        if duration_seconds <= 0:
            raise AdapterError(
                f"duration_seconds must be positive, got {duration_seconds}",
                adapter_name="VideoAdapter"
            )
        
        if platform not in ["douyin", "xiaohongshu", "tiktok", "youtube"]:
            raise AdapterError(
                f"Invalid platform '{platform}', must be one of: douyin, xiaohongshu, tiktok, youtube",
                adapter_name="VideoAdapter"
            )
        
        # 根据时长自动计算 script_len（如果未提供）
        if script_len is None:
            # 平均每段 8-12 秒
            script_len = max(5, min(30, duration_seconds // 8))
        
        if script_len <= 0:
            raise AdapterError(
                f"script_len must be positive, got {script_len}",
                adapter_name="VideoAdapter"
            )
        
        try:
            # ========== UniMem 优势利用 ==========
            # 1. 从 UniMem 中检索相关历史记忆（如果启用）
            enriched_memories = {}
            if use_unimem_retrieval and self.unimem and task_memories:
                enriched_memories = self.enrich_memories_from_unimem(
                    task_memories=task_memories,
                    video_type=video_type,
                    top_k=10
                )
            
            # 构建上下文信息（深度融合用户记忆和 UniMem 检索结果）
            context_parts = []
            
            # 1. 当前任务记忆（最高优先级）
            if task_memories:
                context_parts.append("【当前任务需求】")
                for mem in task_memories[:15]:
                    context_parts.append(f"- {mem}")
            
            # 2. 修改需求记忆（重要，需要优先应用）
            if modification_memories:
                context_parts.append("\n【最新修改需求】（必须严格执行）")
                for mem in modification_memories[:10]:
                    context_parts.append(f"- {mem}")
            
            # 3. 通用记忆总结（风格和偏好基础）
            if general_memories:
                context_parts.append("\n【用户通用偏好和风格】")
                for mem in general_memories[:15]:
                    context_parts.append(f"- {mem}")
            
            # 4. UniMem 检索的历史相关创作（如果有）
            if enriched_memories.get("historical_scripts"):
                context_parts.append("\n【历史相关创作】（来自 UniMem 检索）")
                for script in enriched_memories["historical_scripts"][:5]:
                    context_parts.append(f"- [相似度: {script['score']:.2f}] {script['content']}")
            
            # 5. UniMem 检索的成功模式（如果有）
            if enriched_memories.get("successful_patterns"):
                context_parts.append("\n【成功创作模式】（来自 UniMem 经验）")
                for pattern in enriched_memories["successful_patterns"][:3]:
                    context_parts.append(f"- {pattern['pattern']}")
            
            # 6. UniMem 检索的用户风格偏好（如果有）
            if enriched_memories.get("user_style_preferences"):
                context_parts.append("\n【用户风格偏好】（来自 UniMem 历史记忆）")
                for pref in enriched_memories["user_style_preferences"][:3]:
                    context_parts.append(f"- {pref['preference']}")
            
            # 7. 用户偏好（结构化偏好信息）
            if user_preferences:
                context_parts.append("\n【用户偏好设置】")
                for key, value in list(user_preferences.items())[:10]:
                    if isinstance(value, list):
                        context_parts.append(f"- {key}: {', '.join(str(v) for v in value[:5])}")
                    else:
                        context_parts.append(f"- {key}: {value}")
            
            # 8. 商品信息
            if product_info:
                context_parts.append("\n商品信息：")
                for key, value in list(product_info.items())[:10]:  # 限制数量
                    if isinstance(value, list):
                        context_parts.append(f"- {key}: {', '.join(value[:3])}")
                    else:
                        context_parts.append(f"- {key}: {value}")
            
            if shot_materials:
                context_parts.append("\n可用镜头素材：")
                for i, shot in enumerate(shot_materials[:15], 1):  # 限制数量
                    shot_desc = shot.get("description", shot.get("label", f"镜头{i}"))
                    context_parts.append(f"- 镜头{i}: {shot_desc}")
            
            context_text = "\n".join(context_parts)
            
            # 根据平台选择风格要求
            platform_styles = {
                "douyin": "节奏快、梗多、互动性强",
                "xiaohongshu": "精致感强、生活化、分享感强",
                "tiktok": "国际化表达、简洁有力",
                "youtube": "专业性强、详细讲解"
            }
            
            platform_visuals = {
                "douyin": "快节奏、转场流畅、特效丰富",
                "xiaohongshu": "画面精致、色调统一、构图讲究",
                "tiktok": "国际化审美、简洁大方",
                "youtube": "画面稳定、专业感强"
            }
            
            platform_style = platform_styles.get(platform, platform_styles["douyin"])
            platform_visual = platform_visuals.get(platform, platform_visuals["douyin"])
            
            # 通用 prompt 模板（题材特定需求从用户记忆获取）
            # 根据视频类型添加基础说明
            video_type_descriptions = {
                "ecommerce": "电商推广视频（卖点、转化等需求请在任务记忆中提供）",
                "ip_building": "个人IP打造视频（人设、风格等需求请在任务记忆中提供）",
                "knowledge": "知识分享视频（知识结构、讲解方式等需求请在任务记忆中提供）",
                "vlog": "生活 Vlog 视频（主题、情感表达等需求请在任务记忆中提供）",
                "media": "自媒体内容视频（内容方向等需求请在任务记忆中提供）"
            }
            
            video_type_desc = video_type_descriptions.get(video_type, "短视频内容")
            
            # 统一的 prompt（通用需求，题材特定需求从用户记忆获取）
            prompt = f"""请根据以下信息生成一个优质的短视频文案和剪辑脚本。

**重要说明**：
- 题材类型：{video_type_desc}
- 题材特定的需求（如电商卖点、IP人设、知识结构等）应从任务记忆中获取
- 严格遵循通用短视频创作要求
- 以 JSON 格式返回（JSON 格式质量更好）

目标：
- 视频类型：{video_type_desc}
- 目标时长：{duration_seconds} 秒
- 平台：{platform}（{platform_style}）
- 脚本段数：不超过 {script_len} 段
- 核心目标：根据任务记忆中的具体要求确定（如吸引用户、突出卖点、建立人设、分享知识、记录生活等）

{context_text}

**通用要求**（适用于所有题材）：

1. **文案要求**（严格遵循用户记忆和偏好）：
   - **长度**：每句5-20字，重点突出
   - **开场（黄金3秒）**：必须吸引人，用悬念或共鸣点抓住观众
     - 结合用户通用偏好，使用用户喜欢的表达方式
     - 根据任务记忆中的题材特定要求调整
   - **中间**：层层递进，突出核心内容
     - 根据任务记忆中的具体要求（如电商卖点、IP人设、知识要点、Vlog主题等）展开
     - 结合用户偏好，突出用户关心的内容
     - 根据修改需求记忆，确保满足最新要求
   - **结尾**：根据题材类型确定（如转化、互动、总结等，具体见任务记忆）
   - **语气和风格**（重点结合用户记忆）：
     - 根据通用记忆和用户偏好，使用用户喜欢的语气
     - 根据任务记忆中的题材要求调整（如电商的生活化分享、IP的专业感、知识的易懂性、Vlog的真实感等）
     - 避免生硬的表达，用生活化、口语化的表达
     - 适当使用流行语和网络热词，但不要过度
     - 可以加入个人感受和真实体验（参考通用记忆中的体验）
   - **禁止内容**：
     - 避免"姐妹们"、"小姐姐"等称呼（除非用户偏好中有明确要求）
     - 避免负面内容和动物性制品(肉蛋奶等)和五辛
   - **平台风格**（{platform}）：
     - {platform_style}

2. **画面要求**（通用匹配规则）：
   - **画面描述**：不要重复使用，要和候选镜头画面描述一致
   - **精准匹配**：画面和文案要精准匹配
   - **景别选项**：远景、全景、中景、近景、特写、俯拍、仰拍、跟踪镜头
   - **景别匹配**：景别要和画面内容相符
   - **镜头切换**：要流畅自然
   - **重点画面**：重点画面要给特写
   - **平台风格**（{platform}）：
     - {platform_visual}

3. **镜头使用**：
   - 候选镜头不要重复使用
   - 序号不超过 {script_len}

请以 JSON 格式返回结果：
{{
    "script": "完整文案（包含分段）",
    "segments": [
        {{
            "序号": 1,
            "分类": "分类选项（根据实际情况和题材类型）",
            "景别": "景别选项（远景/全景/中景/近景/特写/俯拍/仰拍/跟踪镜头）",
            "文案": "文案内容（5-20字/句，根据任务记忆中的题材要求）",
            "画面": "画面描述（与候选镜头一致，不重复）",
            "duration_seconds": 8,
            "matched_shots": ["镜头1", "镜头2"],
            "shot_reason": "为什么选择这些镜头",
            "visual_elements": ["特效建议", "字幕时机"],
            "music_cue": "音乐节奏建议"
        }},
        ...
    ],
    "editing_script": {{
        "total_duration": {duration_seconds},
        "transitions": [
            {{"from_segment": 1, "to_segment": 2, "type": "转场方式"}},
            ...
        ],
        "music_suggestions": {{
            "style": "音乐风格建议",
            "key_moments": ["关键时刻1", "关键时刻2"]
        }},
        "special_effects": [
            {{"segment": 1, "effect": "特效建议", "timing": "时机"}},
            ...
        ]
    }},
    "summary": {{
        "hook": "开头亮点总结",
        "core_content": "核心内容总结（根据题材类型：卖点/IP人设/知识点/生活主题等）",
        "ending_type": "结尾类型（转化/互动/总结等，根据任务记忆）",
        "target_audience": "目标受众",
        "style_applied": "应用的风格特点（基于用户记忆）"
    }}
}}"""
            
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的短视频文案和剪辑指导专家，擅长生成吸引人的文案和精准的剪辑脚本。请始终以有效的 JSON 格式返回结果。"
                },
                {"role": "user", "content": prompt}
            ]
            
            _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=4096)
            result = self._parse_json_response(response_text)
            
            if result:
                logger.info(f"Generated video script: {len(result.get('segments', []))} segments, "
                           f"target duration: {duration_seconds}s")
                
                # ========== UniMem 优势利用：存储生成的脚本 ==========
                if store_to_unimem and self.unimem:
                    memory_id = self.store_script_to_unimem(
                        script_data=result,
                        task_memories=task_memories or [],
                        video_type=video_type,
                        platform=platform
                    )
                    if memory_id:
                        result["unimem_memory_id"] = memory_id
                        logger.info(f"Script stored to UniMem with memory_id: {memory_id}")
                
                return result
            else:
                logger.warning(f"Failed to parse video script response: {response_text[:200]}")
                return {}
        except Exception as e:
            logger.error(f"Error generating video script: {e}", exc_info=True)
            return {}
    
    def match_shots_to_script(
        self,
        script_segments: List[Dict[str, Any]],
        available_shots: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        为文案段落匹配最佳镜头素材
        
        使用语义相似度匹配文案和镜头，为每个段落推荐最合适的镜头。
        
        Args:
            script_segments: 文案段落列表，每个段落包含 script_text
            available_shots: 可用镜头列表，每个镜头包含 description 或 label
            
        Returns:
            匹配结果列表，每个结果包含：
            - segment: 原段落信息
            - recommended_shots: 推荐的镜头列表（按匹配度排序）
            - match_scores: 匹配分数列表
            
        Raises:
            AdapterError: 如果参数无效
        """
        if not self.is_available():
            logger.warning("VideoAdapter not available, cannot perform match_shots_to_script")
            return []
        
        if not script_segments or not isinstance(script_segments, list):
            raise AdapterError("script_segments must be a non-empty list", adapter_name="VideoAdapter")
        
        if not available_shots or not isinstance(available_shots, list):
            raise AdapterError("available_shots must be a non-empty list", adapter_name="VideoAdapter")
        
        try:
            results = []
            
            for segment in script_segments:
                script_text = segment.get("script_text", "")
                if not script_text:
                    continue
                
                # 使用语义检索匹配镜头
                # 将镜头描述转换为查询列表
                shot_descriptions = []
                for shot in available_shots:
                    desc = shot.get("description", shot.get("label", ""))
                    if desc:
                        shot_descriptions.append(desc)
                
                if not shot_descriptions:
                    results.append({
                        "segment": segment,
                        "recommended_shots": [],
                        "match_scores": []
                    })
                    continue
                
                # 使用语义检索找到最相关的镜头
                # 简化实现：使用关键词匹配和相似度计算
                recommended_shots = []
                match_scores = []
                
                for shot in available_shots:
                    shot_desc = shot.get("description", shot.get("label", ""))
                    if not shot_desc:
                        continue
                    
                    # 简单的相似度计算（可以后续优化为向量相似度）
                    score = self._calculate_text_similarity(script_text, shot_desc)
                    recommended_shots.append(shot)
                    match_scores.append(score)
                
                # 按分数排序
                sorted_pairs = sorted(
                    zip(recommended_shots, match_scores),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                recommended_shots = [shot for shot, _ in sorted_pairs[:5]]  # 取前5个
                match_scores = [score for _, score in sorted_pairs[:5]]
                
                results.append({
                    "segment": segment,
                    "recommended_shots": recommended_shots,
                    "match_scores": match_scores
                })
            
            logger.debug(f"Matched shots for {len(results)} script segments")
            return results
        except Exception as e:
            logger.error(f"Error matching shots to script: {e}", exc_info=True)
            return []
    
    def extract_modification_memories_from_conversation(
        self,
        conversation_text: str,
        existing_modifications: Optional[List[str]] = None
    ) -> List[str]:
        """
        从对话中提取新的修改需求记忆
        
        分析对话内容，识别用户提出的修改要求、调整意见等，
        并提取为结构化的修改需求记忆。
        
        支持多次对话累积修改需求：如果提供了已有的修改需求，会避免重复提取。
        
        Args:
            conversation_text: 对话文本
            existing_modifications: 已有的修改需求列表（可选），用于避免重复提取
            
        Returns:
            修改需求记忆列表，每个元素是一个具体的修改需求（只包含新增的，不包含已有的）
            
        Raises:
            AdapterError: 如果参数无效
        """
        if not conversation_text or not isinstance(conversation_text, str) or not conversation_text.strip():
            raise AdapterError("conversation_text cannot be empty", adapter_name="VideoAdapter")
        
        if not self.is_available():
            logger.warning("VideoAdapter not available, cannot extract modification memories")
            return []
        
        try:
            # 构建已有修改需求的上下文（如果有）
            existing_context = ""
            if existing_modifications:
                existing_context = f"""

已有修改需求（请避免重复提取）：
{chr(10).join(f"- {mod}" for mod in existing_modifications[:10])}
{f"... 还有 {len(existing_modifications) - 10} 条修改需求" if len(existing_modifications) > 10 else ""}

请只提取本次对话中新增的、与已有修改需求不同的修改需求。如果用户只是重复或强调已有需求，请不要重复提取。"""
            
            prompt = f"""请从以下对话中提取用户提出的**新的**修改需求、调整意见和要求。

对话内容：
{conversation_text[:2000]}{existing_context}

请识别并提取：
1. 文案相关的修改要求（语气、风格、长度、内容等）
2. 画面相关的修改要求（景别、镜头、视觉效果等）
3. 节奏和时长相关的调整
4. 商品信息相关的修改
5. 其他明确的修改指令

重要提示：
- 只提取本次对话中**新增的**修改需求
- 如果用户只是重复或强调已有需求，请不要重复提取
- 如果用户修改或更新了已有需求，请提取更新后的需求（可以覆盖原有需求）

请以 JSON 格式返回结果：
{{
    "modification_memories": [
        "修改需求1（具体、明确）",
        "修改需求2（具体、明确）",
        ...
    ],
    "priority": "high/medium/low",  // 修改的紧急程度
    "is_update": false  // 是否是更新已有需求
}}"""
            
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的需求分析助手，擅长从对话中提取明确的修改需求和调整意见。请始终以有效的 JSON 格式返回结果，并避免重复提取已有需求。"
                },
                {"role": "user", "content": prompt}
            ]
            
            _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=1024)
            result = self._parse_json_response(response_text)
            
            if result and "modification_memories" in result:
                memories = result["modification_memories"]
                priority = result.get("priority", "medium")
                is_update = result.get("is_update", False)
                logger.info(f"Extracted {len(memories)} new modification memories "
                           f"(priority: {priority}, is_update: {is_update})")
                return memories
            else:
                logger.warning("Failed to extract modification memories from conversation")
                return []
        except Exception as e:
            logger.error(f"Error extracting modification memories: {e}", exc_info=True)
            return []
    
    def link_general_memories(
        self,
        task_memories: List[str],
        existing_general_memories: Optional[List[str]] = None
    ) -> List[str]:
        """
        联系跨任务的通用记忆总结
        
        根据当前任务记忆，从已有的通用记忆中筛选出相关的通用偏好和风格总结，
        建立任务记忆与通用记忆之间的联系。
        
        Args:
            task_memories: 当前任务记忆列表
            existing_general_memories: 已有的通用记忆列表（可选）
            
        Returns:
            与当前任务相关的通用记忆列表
            
        Raises:
            AdapterError: 如果参数无效
        """
        if not task_memories or not isinstance(task_memories, list):
            raise AdapterError("task_memories must be a non-empty list", adapter_name="VideoAdapter")
        
        if not existing_general_memories:
            return []
        
        if not self.is_available():
            logger.warning("VideoAdapter not available, cannot link general memories")
            return existing_general_memories[:10]  # 返回前10个作为默认
        
        try:
            # 使用语义相似度筛选相关的通用记忆
            task_text = " ".join(task_memories[:5])  # 使用前5个任务记忆作为查询
            
            relevant_memories = []
            for gen_mem in existing_general_memories:
                # 简单的关键词匹配（可以后续优化为向量相似度）
                similarity = self._calculate_text_similarity(task_text, gen_mem)
                if similarity > 0.1:  # 阈值可以调整
                    relevant_memories.append((gen_mem, similarity))
            
            # 按相似度排序，取前15个
            relevant_memories.sort(key=lambda x: x[1], reverse=True)
            result = [mem for mem, _ in relevant_memories[:15]]
            
            logger.debug(f"Linked {len(result)} relevant general memories from {len(existing_general_memories)} total")
            return result
        except Exception as e:
            logger.error(f"Error linking general memories: {e}", exc_info=True)
            return existing_general_memories[:10]  # 降级返回
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的相似度（简化实现）
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            相似度分数（0-1）
        """
        if not text1 or not text2:
            return 0.0
        
        # 简单的关键词匹配相似度
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    def optimize_script_for_editing(
        self,
        script_data: Dict[str, Any],
        feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        优化脚本以更好地适配剪辑流程
        
        根据剪辑反馈或最佳实践，优化文案和镜头匹配。
        
        Args:
            script_data: 原始脚本数据
            feedback: 剪辑反馈（可选）
            
        Returns:
            优化后的脚本数据，结构与原始数据相同
        """
        if not self.is_available():
            logger.warning("VideoAdapter not available, cannot perform optimize_script_for_editing")
            return script_data
        
        if not script_data or not isinstance(script_data, dict):
            raise AdapterError("script_data must be a non-empty dict", adapter_name="VideoAdapter")
        
        try:
            # 使用 LLM 优化脚本
            prompt = f"""请优化以下短视频脚本，使其更符合剪辑流程和最佳实践。

原始脚本：
{json.dumps(script_data, ensure_ascii=False, indent=2)}

{f"剪辑反馈：{feedback}" if feedback else ""}

优化要求：
1. 确保每段文案时长合理（5-15秒）
2. 优化镜头匹配，确保视觉与文案高度契合
3. 调整节奏，确保整体流畅
4. 优化转场和特效建议
5. 确保黄金3秒开头足够吸引人

请返回优化后的完整脚本（JSON 格式），保持原有结构："""
            
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的短视频剪辑优化专家，擅长优化脚本以提升剪辑效果。"
                },
                {"role": "user", "content": prompt}
            ]
            
            _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=4096)
            optimized_result = self._parse_json_response(response_text)
            
            if optimized_result:
                logger.info("Optimized script for editing")
                return optimized_result
            else:
                logger.warning("Failed to parse optimized script, returning original")
                return script_data
        except Exception as e:
            logger.error(f"Error optimizing script: {e}", exc_info=True)
            return script_data

