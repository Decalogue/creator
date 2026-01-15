"""
基于 ReAct 的中长篇小说创作系统

利用 Cursor 和 Manus 思路的 ReAct 系统进行小说创作：
- 工具动态发现（Index Layer + Discovery Layer）
- 上下文缩减（Context Offloading、Compaction、Summarization）
- 分层行动空间（L1/L2/L3）
- 多 Agent 协作（可选）
- 语义网格记忆（Semantic Mesh Memory）
- 动态上下文路由（Context Router）
- 订阅式记忆总线（Pub/Sub Memory Bus）

设计思路：
1. 分章节创作：将长篇小说分解为多个章节
2. 上下文管理：每章完成后进行 Compaction，保留关键信息
3. 章节连贯性：使用上下文摘要确保前后章节连贯
4. 渐进式创作：支持边写边改，迭代优化
5. 语义网格：自动提取实体和关系，维护创作一致性
6. 动态路由：根据用户行为预测并预加载上下文
7. 订阅通知：Agent 间实时通信，自动检测冲突
"""
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import logging

from react import ReActAgent
from agent.context_manager import get_context_manager
from agent.layered_action_space import get_layered_action_space

***REMOVED*** 集成创作上下文系统
try:
    from creative_context import (
        SemanticMeshMemory,
        Entity,
        EntityType,
        RelationType,
        ContextRouter,
        UserBehavior,
        PubSubMemoryBus,
        Topic
    )
    CREATIVE_CONTEXT_AVAILABLE = True
except ImportError:
    CREATIVE_CONTEXT_AVAILABLE = False
    logger.warning("Creative context system not available, running in basic mode")

logger = logging.getLogger(__name__)


class NovelChapter:
    """小说章节"""
    
    def __init__(
        self,
        chapter_number: int,
        title: str,
        content: str = "",
        summary: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.chapter_number = chapter_number
        self.title = title
        self.content = content
        self.summary = summary
        self.metadata = metadata or {}
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "chapter_number": self.chapter_number,
            "title": self.title,
            "content": self.content,
            "summary": self.summary,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "word_count": len(self.content),
        }
    
    def update_content(self, new_content: str):
        """更新内容"""
        self.content = new_content
        self.updated_at = datetime.now().isoformat()


class ReactNovelCreator:
    """
    基于 ReAct 的小说创作器
    
    利用改进后的 ReAct 系统进行中长篇小说创作
    """
    
    def __init__(
        self,
        novel_title: str,
        output_dir: Optional[Path] = None,
        enable_context_offloading: bool = True,
        enable_creative_context: bool = True,
        enable_enhanced_extraction: bool = True,
        enable_unimem: bool = False,
        enable_quality_check: bool = True
    ):
        """
        初始化小说创作器
        
        Args:
            novel_title: 小说标题
            output_dir: 输出目录，默认为 novel_creation/outputs/{novel_title}/
            enable_context_offloading: 是否启用上下文卸载
            enable_creative_context: 是否启用创作上下文系统（语义网格、动态路由、Pub/Sub）
            enable_enhanced_extraction: 是否启用增强实体提取（使用 LLM 辅助）
            enable_unimem: 是否启用 UniMem 集成（长期记忆）
            enable_quality_check: 是否启用质量检查
        """
        self.novel_title = novel_title
        
        if output_dir is None:
            current_dir = Path(__file__).parent
            output_dir = current_dir / "outputs" / novel_title
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        ***REMOVED*** 创建子目录
        (self.output_dir / "chapters").mkdir(exist_ok=True)
        (self.output_dir / "summaries").mkdir(exist_ok=True)
        (self.output_dir / "drafts").mkdir(exist_ok=True)
        (self.output_dir / "semantic_mesh").mkdir(exist_ok=True)
        
        ***REMOVED*** 创建 ReActAgent
        self.agent = ReActAgent(
            max_iterations=20,  ***REMOVED*** 小说创作可能需要更多迭代
            enable_context_offloading=enable_context_offloading
        )
        
        ***REMOVED*** 上下文管理器
        self.context_manager = get_context_manager() if enable_context_offloading else None
        
        ***REMOVED*** 分层行动空间
        self.layered_action_space = get_layered_action_space()
        
        ***REMOVED*** 章节列表
        self.chapters: List[NovelChapter] = []
        
        ***REMOVED*** 小说元数据
        self.metadata = {
            "title": novel_title,
            "created_at": datetime.now().isoformat(),
            "total_chapters": 0,
            "total_words": 0,
        }
        
        ***REMOVED*** 增强实体提取器（支持多模型投票）
        self.entity_extractor = None
        self.enable_enhanced_extraction = enable_enhanced_extraction
        if enable_enhanced_extraction:
            try:
                ***REMOVED*** 尝试使用多模型投票提取器（更准确）
                try:
                    from novel_creation.multi_model_entity_extractor import MultiModelEntityExtractor
                    from llm.gemini import gemini_3_flash
                    from llm.chat import deepseek_v3_2
                    
                    ***REMOVED*** 使用 Gemini 和 DeepSeek 进行投票
                    llm_clients = [gemini_3_flash, deepseek_v3_2]
                    self.entity_extractor = MultiModelEntityExtractor(
                        llm_clients=llm_clients,
                        vote_threshold=2,  ***REMOVED*** 至少2个模型都提取到才保留
                        use_ner=False
                    )
                    logger.info(f"多模型投票实体提取器已启用（{len(llm_clients)} 个模型）")
                except (ImportError, Exception) as e:
                    logger.debug(f"多模型提取器初始化失败，回退到单模型: {e}")
                    ***REMOVED*** 回退到单模型提取器
                    from novel_creation.enhanced_entity_extractor import EnhancedEntityExtractor
                    try:
                        from llm.gemini import gemini_3_flash
                        llm_client = gemini_3_flash
                        logger.info("增强实体提取器已启用（使用 Gemini 模型）")
                    except ImportError:
                        from llm.chat import deepseek_v3_2
                        llm_client = deepseek_v3_2
                        logger.info("增强实体提取器已启用（使用 DeepSeek 模型）")
                    
                    self.entity_extractor = EnhancedEntityExtractor(
                        llm_client=llm_client,
                        use_ner=False
                    )
            except Exception as e:
                logger.warning(f"增强实体提取器初始化失败，将使用基础提取: {e}")
                self.entity_extractor = None
                self.enable_enhanced_extraction = False
        
        ***REMOVED*** UniMem 集成
        self.unimem = None
        self.enable_unimem = enable_unimem
        if enable_unimem:
            try:
                from unimem import UniMem
                self.unimem = UniMem()
                logger.info("UniMem 已集成（长期记忆）")
            except Exception as e:
                logger.warning(f"UniMem 初始化失败: {e}")
                self.unimem = None
                self.enable_unimem = False
        
        ***REMOVED*** 质量检查器
        self.enable_quality_check = enable_quality_check
        self.quality_checker = None
        if enable_quality_check:
            try:
                from novel_creation.quality_checker import QualityChecker
                from llm.chat import deepseek_v3_2
                self.quality_checker = QualityChecker(llm_client=deepseek_v3_2)
                logger.info("质量检查器已启用")
            except Exception as e:
                logger.warning(f"质量检查器初始化失败: {e}")
                self.quality_checker = None
                self.enable_quality_check = False
        
        ***REMOVED*** 创作上下文系统（如果可用）
        self.enable_creative_context = enable_creative_context and CREATIVE_CONTEXT_AVAILABLE
        if self.enable_creative_context:
            ***REMOVED*** 语义网格记忆
            self.semantic_mesh = SemanticMeshMemory()
            
            ***REMOVED*** 动态上下文路由器
            self.context_router = ContextRouter(self.semantic_mesh)
            
            ***REMOVED*** 订阅式记忆总线
            self.memory_bus = PubSubMemoryBus()
            
            ***REMOVED*** 注册世界观检测 Agent（示例）
            self._register_worldview_agent()
            
            logger.info("创作上下文系统已启用：语义网格、动态路由、Pub/Sub")
        else:
            self.semantic_mesh = None
            self.context_router = None
            self.memory_bus = None
            if enable_creative_context:
                logger.warning("创作上下文系统不可用，运行在基础模式")
    
    def _register_worldview_agent(self):
        """注册世界观检测 Agent（示例）"""
        def on_worldview_change(topic: str, data: dict):
            """世界观变化时的回调"""
            content = data.get("content", "")
            entity_id = data.get("entity_id", "")
            
            ***REMOVED*** 简化的冲突检测（实际应使用更智能的方法）
            ***REMOVED*** 这里只是示例，实际应该检查已有的世界观设定
            logger.info(f"[世界观检测] 检测到世界观描述: {content[:50]}...")
            
            ***REMOVED*** 可以在这里添加实际的冲突检测逻辑
            ***REMOVED*** 例如：检查是否与已有设定冲突
        
        self.memory_bus.subscribe(
            "worldview_agent",
            [Topic.WORLDVIEW, Topic.SETTING_DESCRIPTION],
            on_worldview_change
        )
    
    def create_novel_plan(
        self,
        genre: str,
        theme: str,
        target_chapters: int = 20,
        words_per_chapter: int = 3000
    ) -> Dict[str, Any]:
        """
        创建小说大纲
        
        Args:
            genre: 小说类型（如：科幻、玄幻、都市等）
            theme: 主题
            target_chapters: 目标章节数
            words_per_chapter: 每章目标字数
        
        Returns:
            小说大纲
        """
        prompt = f"""请为小说《{self.novel_title}》创建详细的大纲。

小说信息：
- 类型：{genre}
- 主题：{theme}
- 目标章节数：{target_chapters}
- 每章目标字数：{words_per_chapter}

请提供：
1. 故事背景设定
2. 主要角色介绍
3. 章节大纲（每章标题和简要内容）
4. 故事主线
5. 关键情节节点

请以 JSON 格式返回，包含以下字段：
- background: 背景设定
- characters: 主要角色列表
- chapter_outline: 章节大纲列表（每项包含 chapter_number, title, summary）
- main_plot: 故事主线
- key_plot_points: 关键情节节点列表

重要提示：这是一个创作任务，请直接生成内容，不需要搜索工具或调用任何函数。直接返回 JSON 格式的结果。
"""
        
        ***REMOVED*** 使用 ReActAgent 生成大纲（限制迭代次数，避免工具搜索循环）
        original_max_iterations = self.agent.max_iterations
        self.agent.max_iterations = 5  ***REMOVED*** 限制迭代次数，强制直接生成
        try:
            result = self.agent.run(query=prompt, verbose=False)  ***REMOVED*** 关闭详细输出以加快速度
        finally:
            self.agent.max_iterations = original_max_iterations  ***REMOVED*** 恢复原始值
        
        ***REMOVED*** 尝试解析 JSON
        try:
            ***REMOVED*** 提取 JSON 部分
            if "```json" in result:
                json_start = result.find("```json") + 7
                json_end = result.find("```", json_start)
                json_str = result[json_start:json_end].strip()
            elif "{" in result:
                json_start = result.find("{")
                json_end = result.rfind("}") + 1
                json_str = result[json_start:json_end]
            else:
                json_str = result
            
            plan = json.loads(json_str)
        except Exception as e:
            logger.warning(f"解析大纲 JSON 失败: {e}")
            ***REMOVED*** 如果解析失败，创建基本结构
            plan = {
                "background": "待完善",
                "characters": [],
                "chapter_outline": [
                    {"chapter_number": i+1, "title": f"第{i+1}章", "summary": "待创作"}
                    for i in range(target_chapters)
                ],
                "main_plot": "待完善",
                "key_plot_points": []
            }
        
        ***REMOVED*** 保存大纲
        try:
            plan_file = self.output_dir / "novel_plan.json"
            plan_file.write_text(
                json.dumps(plan, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            logger.debug(f"大纲文件已保存: {plan_file}")
        except (IOError, OSError) as e:
            logger.error(f"保存大纲文件失败: {e}", exc_info=True)
            ***REMOVED*** 不抛出异常，允许继续执行
        
        ***REMOVED*** 更新元数据
        self.metadata.update({
            "genre": genre,
            "theme": theme,
            "target_chapters": target_chapters,
            "words_per_chapter": words_per_chapter,
            "plan": plan
        })
        
        return plan
    
    def create_chapter(
        self,
        chapter_number: int,
        chapter_title: str,
        chapter_summary: str,
        previous_chapters_summary: Optional[str] = None,
        target_words: int = 3000
    ) -> NovelChapter:
        """
        创作单个章节
        
        Args:
            chapter_number: 章节编号
            chapter_title: 章节标题
            chapter_summary: 章节摘要（来自大纲）
            previous_chapters_summary: 前面章节的摘要（用于保持连贯性）
            target_words: 目标字数
        
        Returns:
            NovelChapter 对象
        """
        ***REMOVED*** 从 UniMem 检索相关记忆（如果启用）
        unimem_context = ""
        if self.enable_unimem and self.unimem:
            try:
                ***REMOVED*** 检索相关章节、角色、情节线索
                precedents = self._retrieve_unimem_memories(chapter_number, chapter_summary)
                if precedents:
                    unimem_context = f"""
相关记忆（从长期记忆检索）：
{precedents}

请参考这些记忆，保持创作的一致性。
"""
                    memory_lines = precedents.split('\n')
                    logger.info(f"从 UniMem 检索到 {len([l for l in memory_lines if l.strip()])} 条相关记忆")
            except Exception as e:
                logger.warning(f"UniMem 检索失败: {e}")
        
        ***REMOVED*** 从语义网格检索前面章节的实体（如果启用创作上下文）
        semantic_entities_context = ""
        if self.enable_creative_context and self.semantic_mesh and chapter_number > 1:
            try:
                ***REMOVED*** 检索前面章节中的关键实体（角色、地点、物品等）
                previous_entities = self._get_previous_chapters_entities(chapter_number)
                if previous_entities:
                    semantic_entities_context = f"""
前面章节中的关键实体信息：
{previous_entities}

请确保新章节中出现的实体与前面章节保持一致，特别是：
- 角色名称、性格、外貌特征
- 地点名称和描述
- 重要物品和设定
"""
                    newline_count = len(previous_entities.split('\n'))
                logger.info(f"从语义网格检索到 {newline_count} 条实体信息")
            except Exception as e:
                logger.warning(f"语义网格实体检索失败: {e}")
        
        ***REMOVED*** 构建创作提示词
        context_info = ""
        if previous_chapters_summary:
            context_info = f"""
前面章节摘要：
{previous_chapters_summary}

请确保新章节与前面章节保持连贯性。
"""
        
        ***REMOVED*** 计算字数范围（允许 ±10% 浮动）
        word_tolerance = int(target_words * 0.1)
        min_words = target_words - word_tolerance
        max_words = target_words + word_tolerance
        
        prompt = f"""请创作小说《{self.novel_title}》的第{chapter_number}章。
{unimem_context}
{semantic_entities_context}

章节信息：
- 标题：{chapter_title}
- 摘要：{chapter_summary}
- 目标字数：{target_words}字（允许范围：{min_words}-{max_words}字）
{context_info}

创作要求：
1. 严格按照章节摘要展开情节
2. 保持与前面章节的连贯性
3. **字数控制（重要）**：请严格控制字数在 {min_words}-{max_words} 字范围内，目标 {target_words} 字。如果内容过多，请精简描述，保留核心情节；如果内容不足，请适当展开细节描写。
4. 注意人物性格的一致性（参考前面章节的实体信息）
5. 保持文笔流畅，情节紧凑
6. 确保实体（角色、地点、物品）与前面章节保持一致

字数控制提示：
- 目标字数：{target_words} 字
- 允许范围：{min_words}-{max_words} 字（±10%）
- 请在创作时注意控制篇幅，避免过度展开或过于简略
- 如果发现内容过长，优先精简环境描写和重复性描述
- 如果发现内容过短，可以适当增加对话、心理描写或细节刻画

重要提示：这是一个创作任务，请直接生成章节正文内容，不需要搜索工具或调用任何函数。直接返回创作的内容即可。
请直接返回章节正文内容，不要包含标题或其他格式。
"""
        
        ***REMOVED*** 使用 ReActAgent 创作章节（限制迭代次数，避免工具搜索循环）
        logger.info(f"开始创作第{chapter_number}章：{chapter_title}（目标字数：{target_words}字）")
        original_max_iterations = self.agent.max_iterations
        self.agent.max_iterations = 5  ***REMOVED*** 限制迭代次数，强制直接生成
        try:
            content = self.agent.run(query=prompt, verbose=False)  ***REMOVED*** 关闭详细输出以加快速度
        finally:
            self.agent.max_iterations = original_max_iterations  ***REMOVED*** 恢复原始值
        
        ***REMOVED*** 检查字数
        actual_words = len(content)
        word_diff = actual_words - target_words
        word_diff_percent = (word_diff / target_words * 100) if target_words > 0 else 0
        
        ***REMOVED*** 字数检查：如果超出 ±15%，记录警告
        if abs(word_diff_percent) > 15:
            logger.warning(
                f"第{chapter_number}章字数超出目标较多："
                f"实际 {actual_words} 字，目标 {target_words} 字，"
                f"差异 {word_diff:+d} 字（{word_diff_percent:+.1f}%）"
            )
        elif abs(word_diff_percent) > 10:
            logger.info(
                f"第{chapter_number}章字数略超出目标："
                f"实际 {actual_words} 字，目标 {target_words} 字，"
                f"差异 {word_diff:+d} 字（{word_diff_percent:+.1f}%）"
            )
        else:
            logger.info(
                f"第{chapter_number}章字数符合目标："
                f"实际 {actual_words} 字，目标 {target_words} 字，"
                f"差异 {word_diff:+d} 字（{word_diff_percent:+.1f}%）"
            )
        
        ***REMOVED*** 创建章节对象
        chapter = NovelChapter(
            chapter_number=chapter_number,
            title=chapter_title,
            content=content,
            summary=chapter_summary,
            metadata={
                "target_words": target_words,
                "actual_words": actual_words,
                "word_diff": word_diff,
                "word_diff_percent": round(word_diff_percent, 1),
                "word_tolerance": word_tolerance,
                ***REMOVED*** 保存注入的实体信息提示词（用于人工核对）
                "injected_entities_context": semantic_entities_context if semantic_entities_context else "",
                "injected_unimem_context": unimem_context if unimem_context else "",
                "full_prompt": prompt,  ***REMOVED*** 保存完整提示词
            }
        )
        
        ***REMOVED*** 保存章节
        self._save_chapter(chapter)
        
        ***REMOVED*** 生成章节摘要（用于后续章节的连贯性）
        chapter.summary = self._generate_chapter_summary(chapter)
        
        ***REMOVED*** 质量检查
        if hasattr(self, 'enable_quality_check') and self.enable_quality_check:
            quality_result = self._check_chapter_quality(chapter, previous_chapters_summary)
            chapter.metadata['quality_check'] = quality_result
            if quality_result.get('total_issues', 0) > 0:
                logger.warning(
                    f"第{chapter_number}章质量检查发现问题: "
                    f"{quality_result.get('total_issues', 0)} 个问题 "
                    f"(严重: {quality_result.get('by_severity', {}).get('high', 0)})"
                )
        
        ***REMOVED*** 集成创作上下文系统
        if self.enable_creative_context:
            self._process_chapter_with_creative_context(chapter)
        
        ***REMOVED*** 存储到 UniMem（如果启用）
        if self.enable_unimem and self.unimem:
            try:
                self._store_chapter_to_unimem(chapter)
            except Exception as e:
                logger.warning(f"UniMem 存储失败: {e}")
        
        ***REMOVED*** 添加到列表
        self.chapters.append(chapter)
        
        ***REMOVED*** 更新元数据
        self.metadata["total_chapters"] = len(self.chapters)
        self.metadata["total_words"] = sum(len(c.content) for c in self.chapters)
        
        logger.info(f"第{chapter_number}章创作完成，字数：{len(content)}")
        
        return chapter
    
    def _generate_chapter_summary(self, chapter: NovelChapter) -> str:
        """
        生成章节摘要（用于后续章节的连贯性）
        
        Args:
            chapter: 章节对象
        
        Returns:
            章节摘要
        """
        if not chapter.content:
            return chapter.summary
        
        ***REMOVED*** 使用上下文管理器生成摘要（如果可用）
        if self.context_manager:
            try:
                ***REMOVED*** 构建对话历史
                conversation_history = [
                    {"role": "user", "content": f"请为以下章节生成摘要：\n\n标题：{chapter.title}\n\n内容：{chapter.content[:2000]}"}
                ]
                summary = self.context_manager._generate_summary(conversation_history, use_llm=False)
                return summary
            except Exception as e:
                logger.warning(f"生成章节摘要失败: {e}")
        
        ***REMOVED*** 简单摘要：取前200字
        return chapter.content[:200] + "..." if len(chapter.content) > 200 else chapter.content
    
    def _save_chapter(self, chapter: NovelChapter):
        """
        保存章节到文件
        
        Args:
            chapter: 章节对象
            
        Raises:
            IOError: 如果文件保存失败
        """
        try:
            ***REMOVED*** 确保目录存在
            chapter_dir = self.output_dir / "chapters"
            chapter_dir.mkdir(parents=True, exist_ok=True)
            
            ***REMOVED*** 保存完整章节
            chapter_file = chapter_dir / f"chapter_{chapter.chapter_number:03d}.txt"
            chapter_file.write_text(
                f"第{chapter.chapter_number}章 {chapter.title}\n\n{chapter.content}",
                encoding="utf-8"
            )
            logger.debug(f"章节文件已保存: {chapter_file}")
            
            ***REMOVED*** 保存章节元数据
            chapter_meta_file = chapter_dir / f"chapter_{chapter.chapter_number:03d}_meta.json"
            chapter_meta_file.write_text(
                json.dumps(chapter.to_dict(), ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            logger.debug(f"章节元数据已保存: {chapter_meta_file}")
            
            ***REMOVED*** 保存提示词文件（用于人工核对）
            if chapter.metadata.get("full_prompt"):
                prompt_file = chapter_dir / f"chapter_{chapter.chapter_number:03d}_prompt.txt"
                prompt_file.write_text(
                    chapter.metadata.get("full_prompt", ""),
                    encoding="utf-8"
                )
                logger.debug(f"章节提示词已保存: {prompt_file}")
            
            ***REMOVED*** 如果有关注的实体信息，单独保存
            if chapter.metadata.get("injected_entities_context"):
                entities_file = chapter_dir / f"chapter_{chapter.chapter_number:03d}_entities.txt"
                entities_file.write_text(
                    chapter.metadata.get("injected_entities_context", ""),
                    encoding="utf-8"
                )
                logger.debug(f"章节实体信息已保存: {entities_file}")
        except (IOError, OSError) as e:
            logger.error(f"保存章节文件失败（第{chapter.chapter_number}章）: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"保存章节时发生未知错误（第{chapter.chapter_number}章）: {e}", exc_info=True)
            raise
    
    def create_novel(
        self,
        genre: str,
        theme: str,
        target_chapters: int = 20,
        words_per_chapter: int = 3000,
        start_from_chapter: int = 1
    ) -> Dict[str, Any]:
        """
        创作完整小说
        
        Args:
            genre: 小说类型
            theme: 主题
            target_chapters: 目标章节数
            words_per_chapter: 每章目标字数
            start_from_chapter: 从第几章开始（支持续写）
        
        Returns:
            创作结果
        """
        ***REMOVED*** 1. 创建大纲
        logger.info("开始创建小说大纲...")
        plan = self.create_novel_plan(genre, theme, target_chapters, words_per_chapter)
        
        ***REMOVED*** 2. 按章节创作
        logger.info(f"开始创作小说，从第{start_from_chapter}章开始...")
        
        previous_summary = ""
        for i in range(start_from_chapter - 1, target_chapters):
            chapter_info = plan.get("chapter_outline", [])[i] if i < len(plan.get("chapter_outline", [])) else {
                "chapter_number": i + 1,
                "title": f"第{i+1}章",
                "summary": "待创作"
            }
            
            try:
                chapter = self.create_chapter(
                    chapter_number=chapter_info["chapter_number"],
                    chapter_title=chapter_info.get("title", f"第{i+1}章"),
                    chapter_summary=chapter_info.get("summary", ""),
                    previous_chapters_summary=previous_summary,
                    target_words=words_per_chapter
                )
                
                ***REMOVED*** 更新前面章节摘要（累积）
                if previous_summary:
                    previous_summary += f"\n\n第{chapter.chapter_number}章：{chapter.title}\n{chapter.summary}"
                else:
                    previous_summary = f"第{chapter.chapter_number}章：{chapter.title}\n{chapter.summary}"
                
                ***REMOVED*** 每5章进行一次上下文压缩（如果启用）
                if self.context_manager and (i + 1) % 5 == 0:
                    logger.info(f"进行上下文压缩（第{i+1}章后）...")
                    ***REMOVED*** 这里可以触发上下文压缩逻辑
            except Exception as e:
                logger.error(f"创作第{i+1}章失败: {e}", exc_info=True)
                ***REMOVED*** 记录失败但继续创作后续章节
                logger.warning(f"跳过第{i+1}章，继续创作后续章节...")
                ***REMOVED*** 在摘要中标记失败
                if previous_summary:
                    previous_summary += f"\n\n第{i+1}章：创作失败（{str(e)[:50]}...）"
                else:
                    previous_summary = f"第{i+1}章：创作失败（{str(e)[:50]}...）"
                continue
        
        ***REMOVED*** 3. 生成完整小说文件
        try:
            self._generate_full_novel()
        except Exception as e:
            logger.error(f"生成完整小说文件失败: {e}", exc_info=True)
            ***REMOVED*** 不抛出异常，允许继续保存元数据
        
        ***REMOVED*** 4. 保存元数据
        try:
            self._save_metadata()
        except Exception as e:
            logger.error(f"保存元数据失败: {e}", exc_info=True)
            ***REMOVED*** 不抛出异常，允许返回结果
        
        logger.info(f"小说创作完成！共{len(self.chapters)}章，总字数：{self.metadata['total_words']}")
        
        return {
            "novel_title": self.novel_title,
            "total_chapters": len(self.chapters),
            "total_words": self.metadata["total_words"],
            "output_dir": str(self.output_dir)
        }
    
    def _generate_full_novel(self):
        """生成完整小说文件"""
        full_novel_file = self.output_dir / f"{self.novel_title}_完整版.txt"
        
        with open(full_novel_file, "w", encoding="utf-8") as f:
            f.write(f"{self.novel_title}\n")
            f.write("=" * 60 + "\n\n")
            
            for chapter in sorted(self.chapters, key=lambda x: x.chapter_number):
                f.write(f"第{chapter.chapter_number}章 {chapter.title}\n\n")
                f.write(chapter.content)
                f.write("\n\n" + "=" * 60 + "\n\n")
        
        logger.info(f"完整小说已保存到：{full_novel_file}")
    
    def _process_chapter_with_creative_context(self, chapter: NovelChapter):
        """
        使用创作上下文系统处理章节
        
        Args:
            chapter: 章节对象
        """
        if not self.enable_creative_context:
            return
        
        try:
            ***REMOVED*** 1. 创建章节实体
            chapter_entity = Entity(
                id=f"chapter_{chapter.chapter_number:03d}",
                type=EntityType.CHAPTER,
                name=chapter.title,
                content=chapter.content,
                metadata={
                    "chapter_number": chapter.chapter_number,
                    "summary": chapter.summary,
                    "word_count": len(chapter.content)
                }
            )
            self.semantic_mesh.add_entity(chapter_entity)
            
            ***REMOVED*** 2. 提取实体（简化实现：提取角色名、物品等）
            extracted_entities = self._extract_entities_from_chapter(chapter)
            for entity in extracted_entities:
                self.semantic_mesh.add_entity(entity)
                ***REMOVED*** 创建章节与实体的关系
                self.semantic_mesh.add_relation(
                    chapter_entity.id,
                    entity.id,
                    RelationType.APPEARS_IN,
                    strength=0.8
                )
            
            ***REMOVED*** 3. 发布世界观相关消息（如果包含设定描述）
            if self._contains_worldview_description(chapter.content):
                self.memory_bus.publish(
                    Topic.WORLDVIEW,
                    chapter_entity.id,
                    {
                        "content": chapter.content,
                        "entity_id": chapter_entity.id,
                        "chapter_number": chapter.chapter_number
                    }
                )
            
            ***REMOVED*** 4. 保存语义网格
            self._save_semantic_mesh()
            
            logger.debug(f"已处理章节 {chapter.chapter_number} 的创作上下文")
            
        except Exception as e:
            logger.error(f"处理章节创作上下文时出错: {e}", exc_info=True)
    
    def _extract_entities_from_chapter(self, chapter: NovelChapter) -> List[Entity]:
        """
        从章节中提取实体
        
        优先使用增强实体提取器（LLM 辅助），如果不可用则使用基础规则匹配
        
        Args:
            chapter: 章节对象
        
        Returns:
            提取的实体列表
        """
        ***REMOVED*** 如果启用了增强提取器，使用它
        if self.entity_extractor and self.enable_enhanced_extraction:
            try:
                ***REMOVED*** 检查是否是多模型投票提取器
                from novel_creation.multi_model_entity_extractor import MultiModelEntityExtractor
                if isinstance(self.entity_extractor, MultiModelEntityExtractor):
                    ***REMOVED*** 多模型投票提取器直接返回实体列表
                    entities = self.entity_extractor.extract_entities(
                        chapter.content,
                        chapter.chapter_number
                    )
                    if entities:
                        logger.info(
                            f"第{chapter.chapter_number}章：多模型投票提取到 {len(entities)} 个实体"
                        )
                    return entities
                else:
                    ***REMOVED*** 单模型提取器
                    from novel_creation.enhanced_entity_extractor import EntityExtractionResult
                    result = self.entity_extractor.extract_entities(
                        chapter.content,
                        chapter.chapter_number
                    )
                    
                    if isinstance(result, EntityExtractionResult):
                        if result.entities:
                            logger.info(
                                f"第{chapter.chapter_number}章：增强提取到 {len(result.entities)} 个实体，"
                                f"置信度: {result.confidence:.2f}"
                            )
                        return result.entities
                    else:
                        ***REMOVED*** 如果返回的是列表，直接返回
                        if result:
                            logger.info(
                                f"第{chapter.chapter_number}章：提取到 {len(result)} 个实体"
                            )
                        return result
            except Exception as e:
                logger.warning(f"增强实体提取失败，回退到基础提取: {e}")
        
        ***REMOVED*** 回退到基础规则匹配
        return self._extract_entities_basic(chapter)
    
    def _extract_entities_basic(self, chapter: NovelChapter) -> List[Entity]:
        """
        基础实体提取（规则匹配）
        
        用于回退或禁用增强提取时
        
        Args:
            chapter: 章节对象
        
        Returns:
            提取的实体列表
        """
        entities = []
        content = chapter.content
        
        ***REMOVED*** 提取角色名（简单模式匹配）
        character_pattern = r'["""]([^"""]+)["""]'  ***REMOVED*** 引号内的内容可能是对话
        characters = re.findall(character_pattern, content)
        
        for char_name in set(characters[:5]):  ***REMOVED*** 最多5个角色
            if len(char_name) > 1 and len(char_name) < 20:
                entity = Entity(
                    id=f"char_{chapter.chapter_number}_{hash(char_name) % 10000}",
                    type=EntityType.CHARACTER,
                    name=char_name,
                    content=f"出现在第{chapter.chapter_number}章的角色",
                    metadata={"chapter": chapter.chapter_number, "extraction_method": "basic"}
                )
                entities.append(entity)
        
        ***REMOVED*** 提取物品/符号（简单关键词匹配）
        symbol_keywords = ["吊坠", "戒指", "剑", "书", "地图", "钥匙", "日记", "设备", "仪器"]
        for keyword in symbol_keywords:
            if keyword in content:
                entity = Entity(
                    id=f"symbol_{chapter.chapter_number}_{keyword}",
                    type=EntityType.SYMBOL,
                    name=keyword,
                    content=f"在第{chapter.chapter_number}章中提到的{keyword}",
                    metadata={"chapter": chapter.chapter_number, "extraction_method": "basic"}
                )
                entities.append(entity)
                break  ***REMOVED*** 每个章节只提取一个符号
        
        return entities
    
    def _contains_worldview_description(self, content: str) -> bool:
        """
        检查内容是否包含世界观描述
        
        Args:
            content: 内容文本
        
        Returns:
            是否包含世界观描述
        """
        ***REMOVED*** 简单的关键词匹配
        worldview_keywords = ["天空", "云", "星球", "世界", "大陆", "海洋", "森林", "城市"]
        return any(keyword in content for keyword in worldview_keywords)
    
    def _save_semantic_mesh(self):
        """保存语义网格到文件"""
        if not self.enable_creative_context:
            return
        
        try:
            mesh_file = self.output_dir / "semantic_mesh" / "mesh.json"
            mesh_data = self.semantic_mesh.to_dict()
            mesh_file.write_text(
                json.dumps(mesh_data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            logger.debug(f"语义网格已保存到: {mesh_file}")
        except Exception as e:
            logger.error(f"保存语义网格失败: {e}")
    
    def _retrieve_unimem_memories(self, chapter_number: int, chapter_summary: str) -> str:
        """
        从 UniMem 检索相关记忆
        
        Args:
            chapter_number: 章节编号
            chapter_summary: 章节摘要
        
        Returns:
            格式化的记忆字符串
        """
        if not self.unimem:
            return ""
        
        try:
            from unimem.memory_types import Context, Task
            
            ***REMOVED*** 检索相关章节
            chapter_query = f"chapter {chapter_number - 1}"
            chapter_memories = self.unimem.recall(query=chapter_query, top_k=3)
            
            ***REMOVED*** 检索相关角色和情节
            summary_query = chapter_summary[:100]  ***REMOVED*** 使用摘要的前100字符
            summary_memories = self.unimem.recall(query=summary_query, top_k=3)
            
            ***REMOVED*** 合并结果
            all_memories = list(set(chapter_memories + summary_memories))[:5]  ***REMOVED*** 最多5条
            
            if not all_memories:
                return ""
            
            ***REMOVED*** 格式化记忆
            memory_lines = []
            for i, mem in enumerate(all_memories, 1):
                content = getattr(mem, 'content', str(mem))
                metadata = getattr(mem, 'metadata', {})
                memory_lines.append(f"- 记忆{i}: {content[:200]}...")
                if metadata:
                    metadata_str = ", ".join([f"{k}={v}" for k, v in list(metadata.items())[:3]])
                    memory_lines.append(f"  ({metadata_str})")
            
            return "\n".join(memory_lines)
        except Exception as e:
            logger.debug(f"UniMem 检索失败: {e}")
            return ""
    
    def _check_chapter_quality(
        self,
        chapter: NovelChapter,
        previous_chapters_summary: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        检查章节质量
        
        Args:
            chapter: 章节对象
            previous_chapters_summary: 前面章节摘要
        
        Returns:
            质量检查结果
        """
        if not self.quality_checker:
            return {"total_issues": 0, "issues": []}
        
        try:
            ***REMOVED*** 构建前面章节列表
            previous_chapters = []
            for prev_chapter in self.chapters:
                previous_chapters.append({
                    "number": prev_chapter.chapter_number,
                    "content": prev_chapter.content,
                    "summary": prev_chapter.summary
                })
            
            ***REMOVED*** 获取小说大纲
            novel_plan = self.metadata.get("plan")
            
            ***REMOVED*** 获取语义网格中的实体（用于深度质量检查）
            semantic_mesh_entities = None
            if self.enable_creative_context and self.semantic_mesh:
                try:
                    ***REMOVED*** 将语义网格实体转换为字典格式
                    semantic_mesh_entities = {
                        eid: entity.to_dict() if hasattr(entity, 'to_dict') else {
                            'id': eid,
                            'type': str(entity.type) if hasattr(entity, 'type') else 'unknown',
                            'name': entity.name if hasattr(entity, 'name') else '',
                            'content': entity.content if hasattr(entity, 'content') else '',
                            'metadata': entity.metadata if hasattr(entity, 'metadata') else {}
                        }
                        for eid, entity in self.semantic_mesh.entities.items()
                    }
                except Exception as e:
                    logger.debug(f"获取语义网格实体失败: {e}")
                    semantic_mesh_entities = None
            
            ***REMOVED*** 执行质量检查（传入语义网格实体以进行深度检查）
            issues = self.quality_checker.check_chapter(
                chapter_content=chapter.content,
                chapter_number=chapter.chapter_number,
                previous_chapters=previous_chapters,
                novel_plan=novel_plan,
                semantic_mesh_entities=semantic_mesh_entities
            )
            
            ***REMOVED*** 转换为可序列化的格式
            from novel_creation.quality_checker import IssueSeverity
            result = {
                "total_issues": len(issues),
                "issues": [],
                "by_type": {},
                "by_severity": {},
                "has_high_severity": False
            }
            
            for issue in issues:
                issue_dict = {
                    "type": issue.issue_type.value,
                    "severity": issue.severity.value,
                    "description": issue.description,
                    "location": issue.location,
                    "suggestion": issue.suggestion,
                    "metadata": issue.metadata or {}
                }
                result["issues"].append(issue_dict)
                
                ***REMOVED*** 统计
                result["by_type"][issue.issue_type.value] = result["by_type"].get(issue.issue_type.value, 0) + 1
                result["by_severity"][issue.severity.value] = result["by_severity"].get(issue.severity.value, 0) + 1
                
                if issue.severity == IssueSeverity.HIGH:
                    result["has_high_severity"] = True
            
            return result
            
        except Exception as e:
            logger.error(f"质量检查失败: {e}", exc_info=True)
            return {"total_issues": 0, "issues": [], "error": str(e)}
    
    def _store_chapter_to_unimem(self, chapter: NovelChapter):
        """
        将章节存储到 UniMem
        
        Args:
            chapter: 章节对象
        """
        if not self.unimem:
            return
        
        try:
            from unimem.memory_types import Experience, Context, Task
            
            ***REMOVED*** 创建经验对象
            experience = Experience(
                content=chapter.content,
                metadata={
                    "chapter_number": chapter.chapter_number,
                    "title": chapter.title,
                    "summary": chapter.summary,
                    "word_count": len(chapter.content),
                    "novel_title": self.novel_title
                }
            )
            
            ***REMOVED*** 创建上下文对象
            context = Context(
                task=Task(
                    content=f"创作《{self.novel_title}》第{chapter.chapter_number}章：{chapter.title}",
                    metadata={
                        "chapter_number": chapter.chapter_number,
                        "novel_title": self.novel_title
                    }
                )
            )
            
            ***REMOVED*** 存储到 UniMem
            memory = self.unimem.retain(experience, context)
            
            ***REMOVED*** 保存 memory_id 到章节元数据
            chapter.metadata["unimem_memory_id"] = memory.id
            
            logger.info(f"章节 {chapter.chapter_number} 已存储到 UniMem: {memory.id}")
            
            ***REMOVED*** 如果有语义网格，建立关联
            if self.enable_creative_context and self.semantic_mesh:
                chapter_entity_id = f"chapter_{chapter.chapter_number:03d}"
                ***REMOVED*** 可以在这里建立章节实体与 UniMem memory 的关联
                ***REMOVED*** （需要在 semantic_mesh 中扩展支持）
        
        except Exception as e:
            logger.warning(f"存储章节到 UniMem 失败: {e}", exc_info=True)
    
    def _save_metadata(self):
        """保存元数据"""
        metadata_file = self.output_dir / "metadata.json"
        
        ***REMOVED*** 添加创作上下文系统状态
        metadata = self.metadata.copy()
        
        ***REMOVED*** 创作上下文系统
        if self.enable_creative_context and self.semantic_mesh:
            ***REMOVED*** SemanticMeshMemory 使用 self.entities 和 self.relations 属性
            entities = list(self.semantic_mesh.entities.values())
            relations = self.semantic_mesh.relations
            metadata["creative_context"] = {
                "enabled": True,
                "entities_count": len(entities),
                "relations_count": len(relations),
                "subscribers_count": len(self.memory_bus.subscriptions) if self.memory_bus else 0
            }
        else:
            metadata["creative_context"] = {"enabled": False}
        
        ***REMOVED*** 增强实体提取
        metadata["enhanced_extraction"] = {
            "enabled": self.enable_enhanced_extraction,
            "method": "LLM + Rules" if self.enable_enhanced_extraction and self.entity_extractor else "Basic Rules"
        }
        
        ***REMOVED*** UniMem 集成
        metadata["unimem"] = {
            "enabled": self.enable_unimem,
            "status": "active" if (self.enable_unimem and self.unimem) else "disabled"
        }
        
        ***REMOVED*** 质量检查
        metadata["quality_check"] = {
            "enabled": self.enable_quality_check,
            "status": "active" if (self.enable_quality_check and self.quality_checker) else "disabled"
        }
        
        ***REMOVED*** 统计质量问题
        if self.chapters:
            total_quality_issues = 0
            high_severity_count = 0
            for chapter in self.chapters:
                quality_check = chapter.metadata.get('quality_check', {})
                total_quality_issues += quality_check.get('total_issues', 0)
                if quality_check.get('has_high_severity', False):
                    high_severity_count += 1
            
            metadata["quality_check"]["total_issues"] = total_quality_issues
            metadata["quality_check"]["high_severity_chapters"] = high_severity_count
        
        try:
            metadata_file.write_text(
                json.dumps(metadata, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            logger.debug(f"元数据文件已保存: {metadata_file}")
        except (IOError, OSError) as e:
            logger.error(f"保存元数据文件失败: {e}", exc_info=True)
            ***REMOVED*** 不抛出异常，允许继续执行
    
    def get_related_memories(self, entity_id: str, max_results: int = 5) -> List[Entity]:
        """
        获取相关记忆（用于查询）
        
        Args:
            entity_id: 实体 ID
            max_results: 最多返回的结果数
        
        Returns:
            相关实体列表
        """
        if not self.enable_creative_context:
            return []
        
        return self.semantic_mesh.trigger_related_memories(entity_id, max_results)
    
    def get_context_for_agent(self, entity_id: str, agent_type: str = "general") -> Dict[str, Any]:
        """
        为 Agent 获取上下文（使用动态路由）
        
        Args:
            entity_id: 实体 ID
            agent_type: Agent 类型
        
        Returns:
            上下文字典
        """
        if not self.enable_creative_context:
            return {}
        
        return self.context_router.get_context_for_agent(entity_id, agent_type)
    
    def _get_previous_chapters_entities(self, chapter_number: int) -> str:
        """
        从语义网格检索前面章节的实体
        
        Args:
            chapter_number: 当前章节编号
        
        Returns:
            格式化的实体信息字符串
        """
        if not self.enable_creative_context or not self.semantic_mesh:
            return ""
        
        if chapter_number <= 1:
            return ""  ***REMOVED*** 第一章没有前面的章节
        
        try:
            ***REMOVED*** 从语义网格中获取前面章节的实体
            entities_by_type = {
                EntityType.CHARACTER: [],
                EntityType.SETTING: [],
                EntityType.SYMBOL: [],
                EntityType.PLOT_POINT: []
            }
            
            ***REMOVED*** 遍历所有实体，找出前面章节的实体
            for entity_id, entity in self.semantic_mesh.entities.items():
                ***REMOVED*** 跳过章节实体本身
                if entity.type == EntityType.CHAPTER:
                    continue
                
                ***REMOVED*** 获取实体所属章节
                entity_chapter = entity.metadata.get('chapter', 0)
                
                ***REMOVED*** 如果实体没有章节号，尝试从章节实体关系中推断
                if entity_chapter == 0:
                    ***REMOVED*** 查找与章节实体的关系
                    for relation in self.semantic_mesh.relations:
                        if relation.target_id == entity_id and relation.source_id.startswith('chapter_'):
                            ***REMOVED*** 从章节ID中提取章节号
                            try:
                                chapter_id = relation.source_id.replace('chapter_', '')
                                entity_chapter = int(chapter_id)
                            except:
                                pass
                            break
                
                ***REMOVED*** 只包含前面章节的实体（排除当前章节）
                if 0 < entity_chapter < chapter_number:
                    entity_type = entity.type
                    if entity_type in entities_by_type:
                        entities_by_type[entity_type].append(entity)
            
            ***REMOVED*** 格式化输出
            lines = []
            for entity_type, entities in entities_by_type.items():
                if entities:
                    type_name = {
                        EntityType.CHARACTER: "角色",
                        EntityType.SETTING: "地点/设定",
                        EntityType.SYMBOL: "物品/符号",
                        EntityType.PLOT_POINT: "情节节点"
                    }.get(entity_type, entity_type.value)
                    
                    lines.append(f"{type_name}:")
                    ***REMOVED*** 按章节号排序，优先显示最近章节的实体
                    sorted_entities = sorted(entities, key=lambda e: e.metadata.get('chapter', 0), reverse=True)
                    ***REMOVED*** 每种类型最多10个（增加数量，确保能覆盖更多章节）
                    for entity in sorted_entities[:10]:
                        entity_chapter = entity.metadata.get('chapter', 0)
                        chapter_info = f"（第{entity_chapter}章）" if entity_chapter > 0 else ""
                        content_preview = entity.content[:80] if entity.content else "无描述"
                        lines.append(f"  - {entity.name}{chapter_info}: {content_preview}")
                    lines.append("")
            
            return "\n".join(lines) if lines else ""
            
        except Exception as e:
            logger.warning(f"检索前面章节实体失败: {e}")
            return ""