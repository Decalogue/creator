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
import statistics
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
        enable_quality_check: bool = True,
        llm_client = None
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
            llm_client: LLM客户端函数（如gemini_3_flash、deepseek_v3_2），用于章节和大纲生成
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
        
        ***REMOVED*** 保存LLM客户端
        self.llm_client = llm_client
        
        ***REMOVED*** 创建 ReActAgent
        self.agent = ReActAgent(
            max_iterations=20,  ***REMOVED*** 小说创作可能需要更多迭代
            enable_context_offloading=enable_context_offloading,
            llm_client=llm_client  ***REMOVED*** 传递LLM客户端给ReActAgent
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
        
        ***REMOVED*** 质量指标追踪器
        self.quality_tracker = {
            "chapter_quality_history": [],  ***REMOVED*** 每章的质量指标
            "periodic_quality_checks": [],  ***REMOVED*** 阶段性质量检查结果
            "quality_trends": {
                "coherence": [],
                "character_consistency": [],
                "plot_rhythm": [],
                "worldview_consistency": [],
                "suspense": []
            }
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
        words_per_chapter: int = 3000,
        use_progressive: Optional[bool] = None  ***REMOVED*** None = 自动选择（章节数 >= 50 时使用渐进式）
    ) -> Dict[str, Any]:
        """
        创建小说大纲
        
        支持两种模式：
        1. 一次性生成（适合 <= 30 章）
        2. 渐进式生成（适合 > 30 章，特别是 100 章）
        
        Args:
            genre: 小说类型（如：科幻、玄幻、都市等）
            theme: 主题
            target_chapters: 目标章节数
            words_per_chapter: 每章目标字数
            use_progressive: 是否使用渐进式大纲（None = 自动选择，章节数 >= 50 时使用渐进式）
        
        Returns:
            小说大纲
        """
        ***REMOVED*** 自动选择：章节数 >= 50 时使用渐进式
        if use_progressive is None:
            use_progressive = target_chapters >= 50
        
        if use_progressive:
            logger.info(f"使用渐进式大纲生成（适合 {target_chapters} 章长篇小说）")
            return self._create_novel_plan_progressive(genre, theme, target_chapters, words_per_chapter)
        else:
            logger.info(f"使用一次性大纲生成（适合 {target_chapters} 章中短篇小说）")
            return self._create_novel_plan_onetime(genre, theme, target_chapters, words_per_chapter)
    
    def _create_novel_plan_onetime(
        self,
        genre: str,
        theme: str,
        target_chapters: int,
        words_per_chapter: int
    ) -> Dict[str, Any]:
        """
        一次性生成小说大纲（原有方法）
        
        适合中短篇小说（<= 30 章）
        
        Args:
            genre: 小说类型
            theme: 主题
            target_chapters: 目标章节数
            words_per_chapter: 每章目标字数
        
        Returns:
            小说大纲
        """
        prompt = f"""请为小说《{self.novel_title}》创建详细的大纲（一次性生成所有章节）。

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
        
        ***REMOVED*** 尝试解析 JSON（增强容错能力）
        plan = None
        json_str = None
        
        try:
            ***REMOVED*** 提取 JSON 部分
            if "```json" in result:
                json_start = result.find("```json") + 7
                json_end = result.find("```", json_start)
                if json_end == -1:
                    json_end = len(result)
                json_str = result[json_start:json_end].strip()
            elif "```" in result:
                json_start = result.find("```") + 3
                json_end = result.find("```", json_start)
                if json_end == -1:
                    json_end = len(result)
                json_str = result[json_start:json_end].strip()
            elif "{" in result:
                json_start = result.find("{")
                json_end = result.rfind("}") + 1
                json_str = result[json_start:json_end]
            else:
                json_str = result.strip()
            
            ***REMOVED*** 尝试修复常见的 JSON 格式错误
            if json_str:
                ***REMOVED*** 替换中文引号为英文引号
                json_str = json_str.replace('"', '"').replace('"', '"')
                json_str = json_str.replace(''', "'").replace(''', "'")
                ***REMOVED*** 移除尾随逗号（在 } 或 ] 前）
                json_str = re.sub(r',\s*}', '}', json_str)
                json_str = re.sub(r',\s*]', ']', json_str)
                ***REMOVED*** 修复未转义的换行符（在字符串值中）
                json_str = re.sub(r'(?<!\\)\n(?![\\"])', '\\n', json_str)
            
            plan = json.loads(json_str)
            logger.info("大纲 JSON 解析成功")
            
        except json.JSONDecodeError as e:
            logger.warning(f"解析大纲 JSON 失败: {e}")
            logger.debug(f"JSON 字符串（前500字符）: {json_str[:500] if json_str else 'None'}")
            
            ***REMOVED*** 保存原始响应以便调试
            try:
                debug_file = self.output_dir / "novel_plan_raw_response.txt"
                debug_file.write_text(result, encoding="utf-8")
                logger.debug(f"原始响应已保存到: {debug_file}")
            except Exception:
                pass
            
            ***REMOVED*** 尝试使用 LLM 修复 JSON（如果失败则使用占位符）
            try:
                repair_prompt = f"""以下是一个格式错误的 JSON，请修复它并返回正确的 JSON 格式（只返回 JSON，不要其他内容）：

{json_str[:2000] if json_str else result[:2000]}

请确保：
1. 所有引号都是英文双引号
2. 没有尾随逗号
3. 字符串中的特殊字符已正确转义
4. JSON 结构完整且有效"""
                
                repair_result = self.agent.run(query=repair_prompt, verbose=False)
                ***REMOVED*** 提取修复后的 JSON
                if "```json" in repair_result:
                    repair_start = repair_result.find("```json") + 7
                    repair_end = repair_result.find("```", repair_start)
                    repair_json = repair_result[repair_start:repair_end].strip()
                elif "{" in repair_result:
                    repair_start = repair_result.find("{")
                    repair_end = repair_result.rfind("}") + 1
                    repair_json = repair_result[repair_start:repair_end]
                else:
                    repair_json = repair_result.strip()
                
                plan = json.loads(repair_json)
                logger.info("通过 LLM 修复成功解析大纲 JSON")
            except Exception as repair_error:
                logger.warning(f"LLM 修复 JSON 也失败: {repair_error}")
                ***REMOVED*** 如果修复也失败，创建基本结构
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
        except Exception as e:
            logger.error(f"解析大纲时发生未知错误: {e}", exc_info=True)
            ***REMOVED*** 创建基本结构
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
            "plan": plan,
            "plan_type": "onetime"
        })
        
        return plan
    
    def _create_novel_plan_progressive(
        self,
        genre: str,
        theme: str,
        target_chapters: int,
        words_per_chapter: int,
        phase_size: int = 20  ***REMOVED*** 每个阶段20章
    ) -> Dict[str, Any]:
        """
        渐进式生成小说大纲
        
        适合长篇小说（>= 50 章），分阶段生成详细大纲
        
        Args:
            genre: 小说类型
            theme: 主题
            target_chapters: 目标章节数
            words_per_chapter: 每章目标字数
            phase_size: 每个阶段的章节数（默认20章）
        
        Returns:
            三级大纲结构（整体大纲 + 阶段大纲）
        """
        logger.info("Stage 1: 生成整体大纲...")
        
        ***REMOVED*** Stage 1: 生成整体大纲（粗略）
        overall_outline = self._generate_overall_outline(genre, theme, target_chapters, words_per_chapter)
        
        logger.info("Stage 2: 生成第一阶段详细大纲...")
        
        ***REMOVED*** Stage 2: 生成第一阶段详细大纲（1-20章）
        phase_1_outline = self._generate_phase_outline(
            phase_number=1,
            phase_size=phase_size,
            overall_outline=overall_outline,
            previous_phases=[],
            genre=genre,
            theme=theme,
            words_per_chapter=words_per_chapter
        )
        
        ***REMOVED*** 构建三级大纲结构
        plan = {
            "plan_type": "progressive",
            "phase_size": phase_size,
            "overall": overall_outline,
            "phases": [phase_1_outline],
            "current_phase": 1,
            ***REMOVED*** 为了向后兼容，提供 chapter_outline（基于第一阶段）
            "chapter_outline": phase_1_outline.get("chapters", []),
            ***REMOVED*** 其他字段（向后兼容）
            "background": overall_outline.get("background", ""),
            "characters": overall_outline.get("characters", []),
            "main_plot": overall_outline.get("main_plot", ""),
            "key_plot_points": overall_outline.get("key_plot_points", []),
            "target_chapters": target_chapters
        }
        
        ***REMOVED*** 保存大纲
        try:
            plan_file = self.output_dir / "novel_plan.json"
            plan_file.write_text(
                json.dumps(plan, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            logger.info(f"渐进式大纲文件已保存: {plan_file}")
        except (IOError, OSError) as e:
            logger.error(f"保存大纲文件失败: {e}", exc_info=True)
        
        ***REMOVED*** 更新元数据
        self.metadata.update({
            "genre": genre,
            "theme": theme,
            "target_chapters": target_chapters,
            "words_per_chapter": words_per_chapter,
            "plan": plan
        })
        
        return plan
    
    def _generate_overall_outline(
        self,
        genre: str,
        theme: str,
        target_chapters: int,
        words_per_chapter: int
    ) -> Dict[str, Any]:
        """
        生成整体大纲（粗略规划）
        
        包含：背景设定、主要角色、故事主线、关键转折点
        
        Args:
            genre: 小说类型
            theme: 主题
            target_chapters: 目标章节数
            words_per_chapter: 每章目标字数
        
        Returns:
            整体大纲
        """
        num_phases = (target_chapters + 19) // 20  ***REMOVED*** 向上取整
        
        prompt = f"""请为小说《{self.novel_title}》创建整体大纲（粗略规划）。

小说信息：
- 类型：{genre}
- 主题：{theme}
- 目标章节数：{target_chapters}
- 每章目标字数：{words_per_chapter}

请提供：
1. **故事背景设定**：世界观、时代背景、主要设定
2. **主要角色介绍**：主角、重要配角的姓名、性格、背景
3. **故事主线**：整个故事的 {num_phases} 个主要阶段，每个阶段的核心目标
4. **关键情节节点**：每20章一个关键转折点（共 {num_phases} 个转折点）
5. **结局方向**：故事的大致结局方向

重点：这是整体规划，不需要详细到每章，只需要主要阶段和关键转折点。
每个阶段的描述应该简洁（50-100字），但能体现该阶段的核心冲突和发展方向。

请以 JSON 格式返回，包含以下字段：
- background: 背景设定
- characters: 主要角色列表（每个角色包含 name, role, description）
- main_plot: 故事主线（{num_phases}个阶段的描述）
- key_plot_points: 关键情节节点列表（每个节点包含 phase_number, chapter_range, description）
- ending_direction: 结局方向

重要提示：这是一个创作任务，请直接生成内容，不需要搜索工具或调用任何函数。直接返回 JSON 格式的结果。
"""
        
        original_max_iterations = self.agent.max_iterations
        self.agent.max_iterations = 5
        try:
            result = self.agent.run(query=prompt, verbose=False)
        finally:
            self.agent.max_iterations = original_max_iterations
        
        try:
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
            
            outline = json.loads(json_str)
        except Exception as e:
            logger.warning(f"解析整体大纲 JSON 失败: {e}，使用默认结构")
            outline = {
                "background": f"{genre}类型小说，主题：{theme}",
                "characters": [],
                "main_plot": f"故事分为 {num_phases} 个主要阶段",
                "key_plot_points": [
                    {
                        "phase_number": i + 1,
                        "chapter_range": f"第{i*20+1}-{(i+1)*20}章",
                        "description": f"阶段{i+1}的核心发展"
                    }
                    for i in range(num_phases)
                ],
                "ending_direction": "待完善"
            }
        
        return outline
    
    def _generate_phase_outline(
        self,
        phase_number: int,
        phase_size: int,
        overall_outline: Dict[str, Any],
        previous_phases: List[Dict[str, Any]],
        genre: str,
        theme: str,
        words_per_chapter: int
    ) -> Dict[str, Any]:
        """
        生成阶段详细大纲（每20章一组）
        
        Args:
            phase_number: 阶段编号（从1开始）
            phase_size: 每阶段的章节数
            overall_outline: 整体大纲
            previous_phases: 前面阶段的大纲列表
            genre: 小说类型
            theme: 主题
            words_per_chapter: 每章目标字数
        
        Returns:
            阶段大纲（包含该阶段所有章节的详细大纲）
        """
        start_chapter = (phase_number - 1) * phase_size + 1
        target_chapters = overall_outline.get('target_chapters', phase_number * phase_size)
        end_chapter = min(phase_number * phase_size, target_chapters)
        num_chapters = end_chapter - start_chapter + 1
        
        ***REMOVED*** 获取该阶段的关键转折点描述
        key_plot_points = overall_outline.get('key_plot_points', [])
        phase_target = ""
        if phase_number <= len(key_plot_points):
            phase_target = key_plot_points[phase_number - 1].get('description', '待完善')
        else:
            phase_target = f"阶段{phase_number}的核心发展"
        
        ***REMOVED*** 格式化前面阶段的发展
        previous_phases_summary = ""
        if previous_phases:
            previous_phases_summary = "\n\n前面阶段的发展：\n"
            for i, phase in enumerate(previous_phases, 1):
                phase_summary = phase.get('summary', '')
                key_events = phase.get('key_events', [])
                previous_phases_summary += f"阶段{i}（第{(i-1)*phase_size+1}-{i*phase_size}章）：\n"
                previous_phases_summary += f"  核心发展：{phase_summary}\n"
                if key_events:
                    previous_phases_summary += f"  关键事件：{', '.join(key_events[:3])}\n"
        
        prompt = f"""请为小说《{self.novel_title}》的第{start_chapter}-{end_chapter}章创建详细大纲。

整体大纲：
{json.dumps(overall_outline, ensure_ascii=False, indent=2)}{previous_phases_summary}

阶段信息：
- 阶段编号：{phase_number}
- 章节范围：第{start_chapter}-{end_chapter}章（共 {num_chapters} 章）
- 该阶段的核心目标：{phase_target}

请为这 {num_chapters} 章创建详细大纲，每章包括：
- chapter_number: 章节编号
- title: 章节标题
- summary: 章节摘要（100-200字，描述主要情节）
- key_entities: 本章关键实体（角色、地点、物品）

重点要求：
1. 符合整体大纲中该阶段的核心目标
2. 考虑前面阶段的发展，保持连贯性
3. 每章都要有明确的情节进展，避免流水账
4. 章节之间要有逻辑连接和递进关系
5. 符合{genre}类型的风格和节奏

请以 JSON 格式返回，包含以下字段：
- phase_number: 阶段编号
- summary: 该阶段的核心发展（200-300字）
- key_events: 该阶段的关键事件列表
- chapters: 章节大纲列表（每项包含 chapter_number, title, summary, key_entities）

重要提示：这是一个创作任务，请直接生成内容，不需要搜索工具或调用任何函数。直接返回 JSON 格式的结果。
"""
        
        original_max_iterations = self.agent.max_iterations
        self.agent.max_iterations = 5
        try:
            result = self.agent.run(query=prompt, verbose=False)
        finally:
            self.agent.max_iterations = original_max_iterations
        
        try:
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
            
            phase_outline = json.loads(json_str)
            
            ***REMOVED*** 确保章节编号正确
            if 'chapters' in phase_outline:
                for i, chapter in enumerate(phase_outline['chapters']):
                    chapter['chapter_number'] = start_chapter + i
            
        except Exception as e:
            logger.warning(f"解析阶段大纲 JSON 失败: {e}，使用默认结构")
            phase_outline = {
                "phase_number": phase_number,
                "summary": f"阶段{phase_number}的核心发展",
                "key_events": [],
                "chapters": [
                    {
                        "chapter_number": start_chapter + i,
                        "title": f"第{start_chapter + i}章",
                        "summary": "待创作",
                        "key_entities": []
                    }
                    for i in range(num_chapters)
                ]
            }
        
        return phase_outline
    
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
        
        ***REMOVED*** 计算字数范围
        ***REMOVED*** 基于番茄小说爆款数据统计：
        ***REMOVED*** - 建议范围：1500-3000字
        ***REMOVED*** - 完美落点：2100字（我们使用2048字）
        ***REMOVED*** - 目标：2048字（或用户指定）
        ***REMOVED*** - 下限：1500字（统计建议）
        ***REMOVED*** - 上限：3000字（统计建议，避免注水）
        min_words = 1500  ***REMOVED*** 番茄小说统计建议的下限
        ***REMOVED*** 允许上限：根据目标字数调整，但不超过3000字
        if target_words <= 2000:
            ***REMOVED*** 如果目标字数 <= 2000，使用固定上限3000字
            max_words_allowed = 3000
        else:
            ***REMOVED*** 如果目标字数 > 2000，按1.5倍计算，但不超过3000字
            max_words_allowed = min(int(target_words * 1.5), 3000)
        
        ***REMOVED*** 字数控制提示（基于番茄小说爆款数据统计）
        ***REMOVED*** 计算允许的字数范围（目标±10%）
        target_range_min = int(target_words * 0.9)
        target_range_max = int(target_words * 1.1)
        
        word_control_instruction = f"""
**字数控制（基于番茄小说爆款数据统计，严格执行）**：
- **目标字数：{target_words} 字（完美落点，必须严格控制）**
- **理想范围：{target_range_min}-{target_range_max} 字（目标±10%）**
- **严格上限：{max_words_allowed} 字（绝对不可超过）**

**字数估算方法（请严格遵循）**：
1. **中文字数统计**：每个汉字、标点符号都算1个字
2. **估算技巧**：
   - 一段对话（含引号、标点）约20-30字
   - 一段动作描写约50-80字
   - 一段心理描写约40-60字
   - 一段环境描写约60-100字
3. **创作过程中持续估算**：
   - 每写完一段，立即估算当前总字数
   - 如果接近 {target_range_max} 字，立即停止展开新情节
   - 如果超过 {target_range_max} 字，删除冗余内容

**重要提示（必须严格执行）**：
1. **优先控制在 {target_words} 字左右**（最好在 {target_range_min}-{target_range_max} 字范围内）
2. **绝对禁止超过 {max_words_allowed} 字**，超过将被截断
3. **字数检查点**：
   - 开头部分（25%）：约 {int(target_words * 0.25)} 字时检查
   - 发展部分（40%）：约 {int(target_words * 0.65)} 字时检查
   - 高潮部分（25%）：约 {int(target_words * 0.90)} 字时检查
   - 结尾部分（10%）：约 {target_range_max} 字时必须结束
4. **字数统计方式**：请在实际创作时估算字数，严格控制在 {target_range_min}-{target_range_max} 字范围内

**内容控制技巧**：
- 如果字数接近 {target_range_max} 字：**立即停止**，简洁结尾，删除冗余描写
- 如果字数不足 {target_range_min} 字：适当增加对话、动作、细节，但不要超过 {target_range_max} 字
- 避免冗长的环境描写、重复的心理活动、过长的对话、重复的内心独白
- **优先保留核心情节**：如果必须删减，优先删除环境描写、重复的心理活动

**最终检查**：创作完成后，字数必须在 {target_range_min}-{target_range_max} 字范围内，超过将被智能截断
"""
        
        ***REMOVED*** 情节节奏控制提示
        rhythm_control_instruction = """
**情节节奏控制（重要）**：
请按照以下节奏结构创作章节，确保情节推进有起有伏：
1. **开头（约25%篇幅）**：快速进入情节，引入本章核心冲突或推进主线
   - 避免冗长的铺垫，直接进入情节
   - 可以承接上一章的结尾，或开启新的冲突
2. **发展（约40%篇幅）**：展开情节，推进冲突，展现人物
   - 通过对话、行动、心理描写推进情节
   - 展现人物性格和关系变化
   - 逐步提升紧张感或冲突强度
3. **高潮（约25%篇幅）**：冲突达到顶点或出现转折
   - 本章的核心冲突达到高潮
   - 可以是激烈的对抗、重要的发现、关键的转折
   - 给读者带来情绪冲击
4. **结尾（约10%篇幅）**：自然过渡，为下一章埋下伏笔
   - 解决或部分解决本章冲突
   - 留下悬念或伏笔，吸引读者继续阅读
   - 为下一章的情节发展做铺垫

**节奏变化要求**：
- 确保对话、动作、描写交替出现，避免长时间单一类型的内容
- 在紧张的情节中适当加入对话或心理描写，在平静的情节中适当加入动作或冲突
- 避免连续多段都是环境描写或心理活动，保持节奏的流动性
"""
        
        ***REMOVED*** 对话质量优化提示（强化版）
        dialogue_quality_instruction = """
**对话质量要求（必须严格遵守）**：
1. **对话占比（硬性要求）**：对话必须占章节总字数的 20-40%，这是质量评估的核心指标
   - **最小值：20%**：如果对话占比低于20%，将被判定为质量问题
   - **理想范围：25-35%**：这是最佳对话占比，有助于平衡情节推进和人物展现
   - **最大值：40%**：如果对话占比超过40%，需要适当减少对话
   - **检查方法**：创作完成后，统计所有引号内的对话字数，确保占总字数的20-40%
   
2. **对话分布要求**：
   - 对话应均匀分布在整个章节中，不要集中在前半部分或后半部分
   - 每1000字至少包含3-5段对话
   - 避免连续多段纯描写而没有对话（超过200字必须有对话）

3. **对话功能**：每段对话都必须有明确目的
   - 推进情节：对话应该推动故事发展，而非仅仅交代信息
   - 展现人物：通过对话展现人物性格、关系、动机
   - 制造冲突：对话可以制造或激化冲突
   - 提供信息：必要的信息通过对话自然传达

4. **对话风格**：保持角色语言风格一致
   - 每个角色应有独特的说话方式（用词、语气、节奏）
   - 避免所有角色说话风格雷同
   - 对话应符合角色的身份、性格、教育背景

5. **对话技巧**：
   - 避免"信息转储"：不要通过对话大量交代背景信息
   - 使用潜台词：对话可以包含言外之意
   - 结合动作：对话必须配合动作、表情、环境描写，避免纯对话

**重要提示**：如果创作完成后发现对话占比不足20%，必须增加对话以达到要求。对话是小说质量的关键指标。
"""
        
        prompt = f"""请创作小说《{self.novel_title}》的第{chapter_number}章。
{unimem_context}
{semantic_entities_context}

章节信息：
- 标题：{chapter_title}
- 摘要：{chapter_summary}
- 目标字数：{target_words}字（严格控制在{target_range_min}-{target_range_max}字范围内，上限{max_words_allowed}字）
{context_info}

创作要求：
1. 严格按照章节摘要展开情节
2. 保持与前面章节的连贯性
3. {word_control_instruction.strip()}
4. {rhythm_control_instruction.strip()}
5. {dialogue_quality_instruction.strip()}
6. **章节结尾悬念要求（必须严格执行）**：
   - **硬性要求**：章节结尾（最后50-100字）必须设置悬念、转折或疑问，这是质量评估的核心指标
   - **必须包含以下元素之一**：
     * 疑问句结尾：必须包含"？"号，如"这到底是怎么回事？"、"他究竟是谁？"、"会发生什么？"
     * 转折词：必须包含"但是"、"然而"、"没想到"、"竟然"、"原来"等转折词
     * 意外发现：使用"突然"、"猛然"、"竟然发现"等词语
     * 省略号：使用"..."制造悬念和留白
     * 暗示未来：如"事情才刚刚开始..."、"真正的考验还在后面..."、"更大的危机即将到来..."
   - **结尾结构**：
     * 最后一段必须包含悬念元素（疑问句、转折词、省略号或意外发现）
     * 结尾应在50-100字内完成，简洁有力
     * 必须让读者产生"接下来会发生什么？"的疑问
   - **禁止**：平淡的结尾、完整的总结、没有悬念的描述
   - **检查方法**：创作完成后，检查结尾最后100字，确保包含上述悬念元素之一
7. **一致性要求（必须）**：
   - **角色一致性**：角色名称、性格、外貌、说话方式必须与前面章节完全一致，参考前面章节的实体信息
   - **世界观一致性**：世界观设定（时间、地点、科技、魔法、生物等）必须与前面章节保持一致
   - **时间线一致性**：时间顺序必须合理，不能出现时间倒流或混乱的情况
   - **情节逻辑一致性**：情节发展必须符合大纲，不能出现逻辑矛盾
   - **连贯性**：本章开头应自然承接上一章的结尾，不能突兀或跳跃
8. **描写质量要求（重要）**：
   - **环境描写控制**：
     * 避免冗余的环境描写：环境描写应简洁有力，结合动作和情节推进
     * 禁止大段纯形容词描述：超过50字的纯环境描写必须与动作或对话结合
     * 每段环境描写后必须有动作、对话或心理活动，不能连续多段纯环境描写
   
   - **心理活动描写控制（硬性限制）**：
     * 心理活动句子数量限制：全章"想"、"觉得"、"认为"、"感觉"等心理活动句子不超过10句
     * 避免重复的心理活动：不要反复描述同一人物的相同想法
     * 心理活动应服务于情节：每句心理活动都应推进情节或展现人物，避免无意义的内心独白
     * 优先使用对话和行动展现内心，而非过多心理描写
   
   - **描写平衡**：
     * 描写应服务于情节：所有描写都应推进情节或展现人物，避免无意义的描写
     * 确保对话、动作、描写的平衡：避免长时间单一类型的内容
9. 保持文笔流畅，情节紧凑
10. 确保实体（角色、地点、物品）与前面章节保持一致
{self._get_quality_adjustment_instruction(chapter_number)}

重要提示：这是一个创作任务，请直接生成章节正文内容，不需要搜索工具或调用任何函数。直接返回创作的内容即可。
请直接返回章节正文内容，不要包含标题或其他格式。
"""
        
        ***REMOVED*** 使用 ReActAgent 创作章节（限制迭代次数，避免工具搜索循环）
        logger.info(f"开始创作第{chapter_number}章：{chapter_title}（目标字数：{target_words}字，上限：{max_words_allowed}字）")
        original_max_iterations = self.agent.max_iterations
        original_max_new_tokens = self.agent.max_new_tokens
        
        ***REMOVED*** 自适应生成策略：根据质量反馈调整
        generation_strategy = self._get_adaptive_generation_strategy(chapter_number)
        
        ***REMOVED*** 根据目标字数计算最大 token 数
        ***REMOVED*** 中文token转换：DeepSeek模型中，中文1个字符通常需要1-1.5个tokens
        ***REMOVED*** 策略优化：从1.2倍降低到1.1倍，更严格控制生成长度
        ***REMOVED*** 通过后处理截断来严格控制最终字数（在目标+20%范围内）
        ***REMOVED*** 目标 2048 字 → 约 2253 tokens（更保守，减少截断需求）
        base_max_tokens = int(target_words * 1.1)  ***REMOVED*** 从1.2降低到1.1，更保守
        
        ***REMOVED*** 根据自适应策略和历史生成情况调整token限制
        if generation_strategy.get("strict_word_control", False):
            ***REMOVED*** 如果历史生成明显超过目标（>30%），使用更严格的限制
            max_tokens_for_generation = int(base_max_tokens * 0.85)  ***REMOVED*** 更严格
            logger.info(f"启用严格字数控制模式，token限制: {max_tokens_for_generation}")
        else:
            ***REMOVED*** 根据历史平均字数动态调整（更细粒度）
            quality_history = self.quality_tracker.get("chapter_quality_history", [])
            if len(quality_history) >= 3:
                ***REMOVED*** 计算最近3章的平均字数偏差
                recent_deviations = [
                    abs(m.get("word_diff_percent", 0)) 
                    for m in quality_history[-3:]
                ]
                avg_deviation = sum(recent_deviations) / len(recent_deviations)
                
                ***REMOVED*** 根据平均偏差动态调整（更细粒度）
                if avg_deviation > 40:  ***REMOVED*** 偏差>40%，非常严格
                    max_tokens_for_generation = int(base_max_tokens * 0.85)
                    logger.info(f"检测到高偏差（{avg_deviation:.1f}%），使用严格token限制: {max_tokens_for_generation}")
                elif avg_deviation > 30:  ***REMOVED*** 偏差>30%，较严格
                    max_tokens_for_generation = int(base_max_tokens * 0.90)
                    logger.info(f"检测到中等偏差（{avg_deviation:.1f}%），使用较严格token限制: {max_tokens_for_generation}")
                elif avg_deviation > 20:  ***REMOVED*** 偏差>20%，稍微严格
                    max_tokens_for_generation = int(base_max_tokens * 0.95)
                    logger.info(f"检测到轻微偏差（{avg_deviation:.1f}%），使用稍微严格token限制: {max_tokens_for_generation}")
                else:
                    ***REMOVED*** 偏差<=20%，使用基础限制
                    max_tokens_for_generation = base_max_tokens
            else:
                ***REMOVED*** 前3章，使用基础限制
                max_tokens_for_generation = base_max_tokens
        
        self.agent.max_iterations = 5  ***REMOVED*** 限制迭代次数，强制直接生成
        self.agent.max_new_tokens = max_tokens_for_generation  ***REMOVED*** 设置最大生成 token 数
        
        ***REMOVED*** 生成内容
        try:
            content = self.agent.run(query=prompt, verbose=False)  ***REMOVED*** 关闭详细输出以加快速度
        finally:
            self.agent.max_iterations = original_max_iterations  ***REMOVED*** 恢复原始值
            self.agent.max_new_tokens = original_max_new_tokens  ***REMOVED*** 恢复原始值
        
        ***REMOVED*** 检查字数
        original_words = len(content)
        actual_words = original_words
        
        ***REMOVED*** 自适应截断策略：
        ***REMOVED*** 1. 如果超过上限3000字，截断到上限
        ***REMOVED*** 2. 如果超过目标字数的20%（目标2048 → 2458字），截断到目标+15%（2355字）
        ***REMOVED***    这样可以更严格地控制字数，使其更接近目标
        strict_cutoff = int(target_words * 1.20)  ***REMOVED*** 目标+20%，超过此值需要截断
        
        if original_words > max_words_allowed:
            ***REMOVED*** 超过上限，截断到上限
            logger.warning(
                f"第{chapter_number}章字数超出上限（{original_words}字 > {max_words_allowed}字），"
                f"截断到{max_words_allowed}字"
            )
            content = self._truncate_content(content, max_words_allowed, chapter_summary)
            actual_words = len(content)
        elif original_words > strict_cutoff:
            ***REMOVED*** 超过目标+20%，截断到目标+15%（更接近目标）
            target_after_truncate = int(target_words * 1.15)
            logger.warning(
                f"第{chapter_number}章字数超出严格阈值（{original_words}字 > {strict_cutoff}字），"
                f"截断到{target_after_truncate}字（目标：{target_words}字）"
            )
            content = self._truncate_content(content, target_after_truncate, chapter_summary)
            actual_words = len(content)
        
        ***REMOVED*** 计算字数差异（基于截断后的实际字数）
        word_diff = actual_words - target_words
        word_diff_percent = (word_diff / target_words * 100) if target_words > 0 else 0
        
        ***REMOVED*** 字数检查：记录实际字数情况
        if original_words > max_words_allowed:
            ***REMOVED*** 已经截断了，记录原始字数和截断后字数
            logger.info(
                f"第{chapter_number}章字数已截断："
                f"原始 {original_words} 字 → 截断后 {actual_words} 字，"
                f"目标 {target_words} 字，上限 {max_words_allowed} 字"
            )
        elif actual_words > target_words:
            ***REMOVED*** 超过目标但在上限内，记录为可接受
            logger.info(
                f"第{chapter_number}章字数略超出目标但可接受："
                f"实际 {actual_words} 字，目标 {target_words} 字，"
                f"差异 {word_diff:+d} 字（{word_diff_percent:+.1f}%），"
                f"上限 {max_words_allowed} 字"
            )
        elif actual_words < min_words:
            logger.info(
                f"第{chapter_number}章字数略少于目标："
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
                "min_words": min_words,
                "max_words_allowed": max_words_allowed,
                ***REMOVED*** 保存注入的实体信息提示词（用于人工核对）
                "injected_entities_context": semantic_entities_context if semantic_entities_context else "",
                "injected_unimem_context": unimem_context if unimem_context else "",
                "full_prompt": prompt,  ***REMOVED*** 保存完整提示词
            }
        )
        
        ***REMOVED*** 保存章节（关键操作，失败应抛出异常）
        try:
            self._save_chapter(chapter)
        except Exception as e:
            logger.error(f"保存第{chapter_number}章失败: {e}", exc_info=True)
            raise  ***REMOVED*** 保存失败是关键错误，需要重试或跳过
        
        ***REMOVED*** 生成章节摘要（非关键操作，失败仅记录警告）
        try:
            chapter.summary = self._generate_chapter_summary(chapter)
        except Exception as e:
            logger.warning(f"生成第{chapter_number}章摘要失败: {e}，使用章节摘要作为默认摘要")
            chapter.summary = chapter_summary  ***REMOVED*** 使用原始摘要作为后备
        
        ***REMOVED*** 质量检查（非关键操作，失败仅记录警告）
        quality_result = None
        should_rewrite = False
        if hasattr(self, 'enable_quality_check') and self.enable_quality_check:
            try:
                quality_result = self._check_chapter_quality(chapter, previous_chapters_summary)
                chapter.metadata['quality_check'] = quality_result
                
                total_issues = quality_result.get('total_issues', 0)
                high_severity = quality_result.get('by_severity', {}).get('high', 0)
                
                if total_issues > 0:
                    logger.warning(
                        f"第{chapter_number}章质量检查发现问题: "
                        f"{total_issues} 个问题 "
                        f"(严重: {high_severity})"
                    )
                
                ***REMOVED*** 判断是否需要重写
                ***REMOVED*** 触发条件：1) 严重问题数 >= 1，或 2) 总问题数 >= 3
                if high_severity >= 1 or total_issues >= 3:
                    should_rewrite = True
                    logger.info(
                        f"第{chapter_number}章质量问题较多（严重:{high_severity}, 总计:{total_issues}），"
                        f"将基于反馈进行重写"
                    )
                
                ***REMOVED*** 记录单章质量指标
                try:
                    self._track_chapter_quality(chapter_number, quality_result, actual_words, target_words)
                except Exception as e:
                    logger.warning(f"追踪第{chapter_number}章质量指标失败: {e}")
            except Exception as e:
                logger.warning(f"第{chapter_number}章质量检查失败: {e}，跳过质量检查")
                chapter.metadata['quality_check'] = {"total_issues": 0, "error": str(e)}
        
        ***REMOVED*** 基于反馈重写（如果质量问题较多）
        if should_rewrite and quality_result:
            try:
                logger.info(f"开始重写第{chapter_number}章...")
                rewritten_content = self._rewrite_chapter_with_feedback(
                    chapter_number=chapter_number,
                    chapter_title=chapter_title,
                    chapter_summary=chapter_summary,
                    original_content=content,
                    quality_result=quality_result,
                    previous_chapters_summary=previous_chapters_summary,
                    target_words=target_words,
                    semantic_entities_context=semantic_entities_context,
                    unimem_context=unimem_context
                )
                
                if rewritten_content and len(rewritten_content) > min_words:
                    ***REMOVED*** 更新章节内容
                    original_content = content
                    content = rewritten_content
                    actual_words = len(content)
                    word_diff = actual_words - target_words
                    word_diff_percent = (word_diff / target_words * 100) if target_words > 0 else 0
                    
                    ***REMOVED*** 更新章节对象
                    chapter.content = content
                    chapter.metadata['rewritten'] = True
                    chapter.metadata['original_word_count'] = len(original_content)
                    chapter.metadata['rewritten_word_count'] = actual_words
                    chapter.metadata['actual_words'] = actual_words
                    chapter.metadata['word_diff'] = word_diff
                    chapter.metadata['word_diff_percent'] = round(word_diff_percent, 1)
                    
                    logger.info(
                        f"第{chapter_number}章重写完成："
                        f"原始 {len(original_content)} 字 → 重写后 {actual_words} 字"
                    )
                    
                    ***REMOVED*** 重新进行质量检查
                    try:
                        quality_result_after_rewrite = self._check_chapter_quality(chapter, previous_chapters_summary)
                        chapter.metadata['quality_check_after_rewrite'] = quality_result_after_rewrite
                        chapter.metadata['quality_check'] = quality_result_after_rewrite  ***REMOVED*** 更新为重写后的结果
                        
                        total_issues_after = quality_result_after_rewrite.get('total_issues', 0)
                        logger.info(
                            f"第{chapter_number}章重写后质量检查："
                            f"{total_issues_after} 个问题（重写前：{quality_result.get('total_issues', 0)} 个）"
                        )
                    except Exception as e:
                        logger.warning(f"重写后质量检查失败: {e}")
                    
                    ***REMOVED*** 重新保存章节（包含重写信息）
                    try:
                        self._save_chapter(chapter)
                        logger.debug(f"第{chapter_number}章重写后的内容已保存")
                    except Exception as e:
                        logger.warning(f"保存重写后的章节失败: {e}")
                else:
                    logger.warning(f"第{chapter_number}章重写失败或内容过短，保留原始内容")
            except Exception as e:
                logger.warning(f"第{chapter_number}章重写过程出错: {e}，保留原始内容", exc_info=True)
        
        ***REMOVED*** 集成创作上下文系统（非关键操作，失败仅记录警告）
        if self.enable_creative_context:
            try:
                self._process_chapter_with_creative_context(chapter)
            except Exception as e:
                logger.warning(f"处理第{chapter_number}章创作上下文失败: {e}，跳过上下文处理")
        
        ***REMOVED*** 存储到 UniMem（非关键操作，失败仅记录警告）
        if self.enable_unimem and self.unimem:
            try:
                self._store_chapter_to_unimem(chapter)
            except Exception as e:
                logger.warning(f"UniMem 存储第{chapter_number}章失败: {e}")
        
        ***REMOVED*** 添加到列表（关键操作）
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
    
    def _generate_layered_summary(
        self,
        chapter_number: int,
        recent_chapters: List[NovelChapter],
        phase_summaries: List[Dict[str, Any]],
        key_plot_points: List[Dict[str, Any]],
        recent_window: int = 10  ***REMOVED*** 最近N章详细摘要
    ) -> str:
        """
        生成分层章节摘要（用于后续章节的连贯性）
        
        采用三层结构：
        1. 最近N章详细摘要（保持连贯性）
        2. 阶段摘要（压缩前面阶段的信息）
        3. 关键节点摘要（关键转折点）
        
        Args:
            chapter_number: 当前章节编号
            recent_chapters: 最近章节列表
            phase_summaries: 前面阶段的摘要列表（每个阶段包含 phase_number, summary, key_events）
            key_plot_points: 关键情节节点列表
            recent_window: 最近N章（默认10章，详细摘要）
        
        Returns:
            分层摘要字符串
        """
        lines = []
        
        ***REMOVED*** 1. 最近N章详细摘要（保持连贯性）
        if recent_chapters:
            ***REMOVED*** 只取最近N章
            recent_window_chapters = recent_chapters[-recent_window:]
            if recent_window_chapters:
                lines.append("=" * 60)
                lines.append(f"最近章节摘要（第{recent_window_chapters[0].chapter_number}-{recent_window_chapters[-1].chapter_number}章）：")
                lines.append("=" * 60)
                for chapter in recent_window_chapters:
                    lines.append(f"\n第{chapter.chapter_number}章：{chapter.title}")
                    lines.append(f"{chapter.summary}")
                lines.append("")
        
        ***REMOVED*** 2. 阶段摘要（压缩前面阶段的信息）
        if phase_summaries:
            lines.append("=" * 60)
            lines.append("前面阶段的发展：")
            lines.append("=" * 60)
            for phase_info in phase_summaries:
                phase_num = phase_info.get('phase_number', 0)
                phase_summary = phase_info.get('summary', '')
                key_events = phase_info.get('key_events', [])
                
                lines.append(f"\n阶段{phase_num}：")
                lines.append(f"  核心发展：{phase_summary}")
                if key_events:
                    lines.append(f"  关键事件：{', '.join(key_events[:3])}")  ***REMOVED*** 只取前3个关键事件
            lines.append("")
        
        ***REMOVED*** 3. 关键节点摘要（关键转折点）
        if key_plot_points:
            relevant_plot_points = [
                pt for pt in key_plot_points
                if pt.get('chapter_range', '').startswith('第') and
                self._extract_chapter_number_from_range(pt.get('chapter_range', '')) < chapter_number
            ]
            
            if relevant_plot_points:
                lines.append("=" * 60)
                lines.append("关键转折点：")
                lines.append("=" * 60)
                for pt in relevant_plot_points[-3:]:  ***REMOVED*** 只取最近3个关键节点
                    chapter_range = pt.get('chapter_range', '')
                    description = pt.get('description', '')
                    lines.append(f"  {chapter_range}：{description}")
                lines.append("")
        
        return "\n".join(lines)
    
    def _get_quality_adjustment_instruction(self, chapter_number: int) -> str:
        """
        根据质量反馈生成动态调整指令
        
        Args:
            chapter_number: 当前章节编号
        
        Returns:
            调整指令字符串
        """
        quality_adjustments = self.metadata.get("quality_adjustments", {})
        if not quality_adjustments:
            return ""
        
        instructions = []
        
        ***REMOVED*** 节奏问题调整
        rhythm_issue = quality_adjustments.get("rhythm_issue")
        if rhythm_issue and chapter_number > rhythm_issue.get("chapter", 0):
            score = rhythm_issue.get("score", 0)
            instructions.append(f"**节奏优化（重要）**：前续章节节奏得分{score:.2f}较低，需要立即改进。请确保：1) 对话占比在25-35%之间；2) 每段对话配合动作或心理描写；3) 避免连续多段都是环境描写或心理活动；4) 保持对话、动作、描写的交替出现。")
        
        ***REMOVED*** 悬念问题调整（强化版）
        suspense_issue = quality_adjustments.get("suspense_issue")
        if suspense_issue and chapter_number > suspense_issue.get("chapter", 0):
            score = suspense_issue.get("score", 0)
            instructions.append(
                f"**悬念优化（紧急）**：前续章节悬念得分{score:.2f}较低（<0.7），这是严重质量问题，必须立即改进！"
                "请在本章结尾（最后50-100字）必须包含以下悬念元素之一："
                "1) 疑问句（必须包含'？'号），如'这到底是怎么回事？'、'他究竟是谁？'、'会发生什么？'；"
                "2) 转折词（必须包含'但是'、'然而'、'没想到'、'竟然'、'原来'等词之一）；"
                "3) 意外发现（必须包含'突然'、'猛然'、'竟然发现'等词，或使用省略号'...'）；"
                "4) 暗示未来（必须暗示未来事件或冲突，如'事情才刚刚开始...'、'更大的危机即将到来...'）。"
                "结尾必须简洁有力，让读者产生'接下来会发生什么？'的疑问。"
                "创作完成后，必须检查结尾最后100字，确保包含上述悬念元素之一！"
            )
        
        ***REMOVED*** 对话质量问题调整
        dialogue_issue = quality_adjustments.get("dialogue_issue")
        if dialogue_issue and chapter_number > dialogue_issue.get("chapter", 0):
            issue_type = dialogue_issue.get("type", "")
            if issue_type == "low_ratio":
                dialogue_ratio = dialogue_issue.get("dialogue_ratio", 0)
                instructions.append(
                    f"**对话优化（紧急）**：前续章节对话占比过低（{dialogue_ratio*100:.1f}% < 15%），"
                    "这是严重质量问题，必须立即修正！请："
                    "1) 对话占比必须达到20-40%（硬性要求）；"
                    "2) 每1000字至少包含3-5段对话；"
                    "3) 避免连续超过200字的纯描写而没有对话；"
                    "4) 通过对话推进情节，展现人物性格；"
                    "5) 在对话中配合动作描写和情绪表达。"
                    "创作完成后，必须统计对话占比，确保达到20%以上！"
                )
            elif issue_type == "high_ratio":
                instructions.append("**对话优化（重要）**：前续章节对话占比过高（>45%），需要立即减少对话。请适当减少对话，增加动作描写、心理描写和环境描写。")
            elif issue_type == "lack_action":
                instructions.append("**对话优化（重要）**：前续章节对话缺乏动作或情绪，需要立即改进。请在对话中增加动作描写和情绪表达，使对话更生动。")
        
        ***REMOVED*** 描写质量问题调整
        description_issue = quality_adjustments.get("description_issue")
        if description_issue and chapter_number > description_issue.get("chapter", 0):
            issue_type = description_issue.get("type", "")
            if issue_type == "redundant":
                instructions.append("**描写优化（重要）**：前续章节环境描写冗余，需要立即精简。请：1) 精简环境描写，避免大段纯形容词描述；2) 将环境描写与动作和情节推进结合；3) 避免超过2段以形容词为主但缺少动作的段落。")
            elif issue_type == "excessive_thought":
                thought_count = description_issue.get("thought_count", 0)
                instructions.append(
                    f"**描写优化（重要）**：前续章节心理活动描写过多（{thought_count}句 > 10句），需要立即减少。"
                    "请严格执行：1) 心理活动句子（包含'想'、'觉得'、'认为'、'感觉'等词）不超过10句（硬性限制）；"
                    "2) 优先使用对话和行动展现人物内心，而非过多内心独白；"
                    "3) 避免重复的心理活动描写；"
                    "4) 每句心理活动都应推进情节或展现人物，避免无意义的内心独白。"
                )
        
        ***REMOVED*** 一致性问题调整
        consistency_issue = quality_adjustments.get("consistency_issue")
        if consistency_issue and chapter_number > consistency_issue.get("chapter", 0):
            issue_type = consistency_issue.get("type", "")
            if issue_type == "character":
                instructions.append("**一致性优化（重要）**：前续章节发现角色名称不一致问题，需要立即修正。请：1) 仔细检查角色名称是否与前面章节完全一致；2) 参考前面章节的实体信息，确保角色性格、外貌、说话方式一致。")
            elif issue_type == "worldview":
                instructions.append("**一致性优化（重要）**：前续章节发现世界观设定不一致问题，需要立即修正。请确保世界观设定（时间、地点、科技、魔法、生物等）与前面章节完全一致。")
            elif issue_type == "timeline":
                instructions.append("**一致性优化（重要）**：前续章节发现时间线混乱问题，需要立即修正。请确保时间顺序合理，不能出现时间倒流或混乱的情况。")
        
        if instructions:
            return "\n11. " + "\n".join(instructions)
        return ""
    
    def _truncate_content(self, content: str, target_length: int, chapter_summary: str) -> str:
        """
        智能截断章节内容，保留核心情节
        
        优化策略：
        1. 优先保留对话和关键动作（核心情节）
        2. 优先删除环境描写和重复的心理活动
        3. 确保结尾完整（至少保留最后一段）
        
        Args:
            content: 原始内容
            target_length: 目标长度（字符数）
            chapter_summary: 章节摘要（用于判断核心情节）
        
        Returns:
            截断后的内容
        """
        if len(content) <= target_length:
            return content
        
        ***REMOVED*** 按段落分割
        paragraphs = content.split('\n\n')
        if not paragraphs:
            ***REMOVED*** 如果没有段落分隔，直接按句子截断
            return self._truncate_by_sentences(content, target_length)
        
        ***REMOVED*** 分析段落重要性（简单启发式）
        ***REMOVED*** 对话段落（包含引号）优先级高
        ***REMOVED*** 环境描写（包含大量形容词、名词）优先级低
        para_importance = []
        for para in paragraphs:
            importance = 1.0
            ***REMOVED*** 对话段落优先级高
            if '"' in para or '"' in para or '「' in para or '」' in para:
                importance = 2.0
            ***REMOVED*** 环境描写优先级低（包含大量形容词、名词，但缺少动词）
            elif len(re.findall(r'[的的地得]', para)) > len(para) * 0.1:
                ***REMOVED*** 如果"的"字占比高，可能是环境描写
                if len(re.findall(r'[看听感觉]', para)) < 3:  ***REMOVED*** 缺少动作词
                    importance = 0.5
            
            para_importance.append((importance, para))
        
        ***REMOVED*** 按重要性排序，但保持大致顺序（只做局部调整）
        ***REMOVED*** 优先保留重要段落，删除不重要段落
        truncated = []
        current_length = 0
        remaining_paras = para_importance.copy()
        
        ***REMOVED*** 先尝试保留所有段落，如果超出再删除不重要的
        for importance, para in para_importance:
            para_length = len(para) + 2  ***REMOVED*** +2 for \n\n
            
            if current_length + para_length <= target_length:
                truncated.append(para)
                current_length += para_length
            else:
                ***REMOVED*** 超出目标长度，尝试删除不重要的段落
                ***REMOVED*** 如果当前段落不重要，跳过
                if importance < 1.0 and current_length > target_length * 0.8:
                    ***REMOVED*** 如果已经达到80%目标长度，且当前段落不重要，跳过
                    continue
                
                ***REMOVED*** 否则尝试按句子截断最后一个段落
                remaining = target_length - current_length - 2
                if remaining > 100:  ***REMOVED*** 至少保留100字
                    para_truncated = self._truncate_by_sentences(para, remaining)
                    if para_truncated:
                        truncated.append(para_truncated)
                        current_length += len(para_truncated) + 2
                break
        
        result = '\n\n'.join(truncated)
        
        ***REMOVED*** 如果仍然超出，直接截断到目标长度
        if len(result) > target_length:
            result = result[:target_length]
            ***REMOVED*** 尝试在最后一个句号处截断
            last_period = result.rfind('。')
            if last_period > target_length * 0.8:  ***REMOVED*** 如果句号在80%之后，保留到句号
                result = result[:last_period + 1]
            else:
                ***REMOVED*** 如果找不到合适的句号，尝试找其他标点
                for punct in ['！', '？', '…', '.', '!', '?']:
                    last_punct = result.rfind(punct)
                    if last_punct > target_length * 0.8:
                        result = result[:last_punct + 1]
                        break
        
        return result
    
    def _truncate_by_sentences(self, text: str, target_length: int) -> str:
        """
        按句子截断文本
        
        Args:
            text: 原始文本
            target_length: 目标长度
        
        Returns:
            截断后的文本
        """
        if len(text) <= target_length:
            return text
        
        ***REMOVED*** 按句号、问号、感叹号分割句子
        sentences = re.split(r'([。！？])', text)
        result = ""
        
        for i in range(0, len(sentences), 2):
            if i + 1 < len(sentences):
                sentence = sentences[i] + sentences[i + 1]
            else:
                sentence = sentences[i]
            
            if len(result) + len(sentence) <= target_length:
                result += sentence
            else:
                break
        
        return result
    
    def _extract_chapter_number_from_range(self, chapter_range: str) -> int:
        """
        从章节范围字符串中提取起始章节号
        例如："第1-20章" -> 1
        """
        try:
            match = re.search(r'第(\d+)-', chapter_range)
            if match:
                return int(match.group(1))
            ***REMOVED*** 如果格式不同，尝试提取单个数字
            match = re.search(r'(\d+)', chapter_range)
            if match:
                return int(match.group(1))
        except Exception:
            pass
        return 0
    
    def _generate_phase_summary(self, phase_chapters: List[NovelChapter], phase_number: int) -> Dict[str, Any]:
        """
        生成阶段摘要（每20章一个阶段）
        
        Args:
            phase_chapters: 该阶段的所有章节列表
            phase_number: 阶段编号
        
        Returns:
            阶段摘要字典（包含 phase_number, summary, key_events）
        """
        if not phase_chapters:
            return {
                "phase_number": phase_number,
                "summary": "阶段信息缺失",
                "key_events": []
            }
        
        ***REMOVED*** 提取关键事件（从章节标题和摘要中）
        key_events = []
        phase_summary_parts = []
        
        for chapter in phase_chapters:
            ***REMOVED*** 章节标题可能包含关键事件信息
            title = chapter.title or ""
            summary = chapter.summary or ""
            
            ***REMOVED*** 简单提取：标题中的关键信息
            if title and title != f"第{chapter.chapter_number}章":
                key_events.append(title)
            
            ***REMOVED*** 摘要的前100字作为阶段摘要的一部分
            if summary:
                phase_summary_parts.append(summary[:100])
        
        ***REMOVED*** 合并阶段摘要（取前500字）
        phase_summary = " ".join(phase_summary_parts)[:500]
        if len(phase_summary) < 200:
            ***REMOVED*** 如果摘要太短，使用章节摘要的组合
            phase_summary = f"阶段{phase_number}包含{len(phase_chapters)}章，主要发展：{phase_summary}"
        
        ***REMOVED*** 限制关键事件数量（最多5个）
        key_events = key_events[:5]
        
        return {
            "phase_number": phase_number,
            "summary": phase_summary,
            "key_events": key_events
        }
    
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
        start_from_chapter: int = 1,
        use_progressive: Optional[bool] = None  ***REMOVED*** None = 自动选择（章节数 >= 50 时使用渐进式）
    ) -> Dict[str, Any]:
        """
        创作完整小说
        
        Args:
            genre: 小说类型
            theme: 主题
            target_chapters: 目标章节数
            words_per_chapter: 每章目标字数
            start_from_chapter: 从第几章开始（支持续写）
            use_progressive: 是否使用渐进式大纲（None = 自动选择，章节数 >= 50 时使用渐进式）
        
        Returns:
            创作结果
        """
        ***REMOVED*** 1. 创建大纲
        logger.info("开始创建小说大纲...")
        plan = self.create_novel_plan(genre, theme, target_chapters, words_per_chapter, use_progressive)
        
        ***REMOVED*** 2. 按章节创作
        logger.info(f"开始创作小说，从第{start_from_chapter}章开始...")
        
        ***REMOVED*** 分层摘要管理
        previous_summary = ""
        plan_type = plan.get("plan_type", "onetime")
        phase_size = plan.get("phase_size", 20) if plan_type == "progressive" else target_chapters
        recent_window = 10  ***REMOVED*** 最近10章详细摘要
        
        ***REMOVED*** 阶段摘要列表（每完成一个阶段，生成阶段摘要）
        phase_summaries = []
        current_phase_chapters = []  ***REMOVED*** 当前阶段的章节列表
        
        for i in range(start_from_chapter - 1, target_chapters):
            chapter_number = i + 1
            
            ***REMOVED*** 渐进式大纲：检查是否需要生成新阶段大纲
            if plan_type == "progressive":
                current_phase = (chapter_number - 1) // phase_size + 1
                phases = plan.get("phases", [])
                
                ***REMOVED*** 如果需要新阶段大纲，自动生成
                if current_phase > len(phases):
                    logger.info(f"需要生成阶段{current_phase}的大纲（第{(current_phase-1)*phase_size+1}-{current_phase*phase_size}章）...")
                    overall_outline = plan.get("overall", {})
                    new_phase_outline = self._generate_phase_outline(
                        phase_number=current_phase,
                        phase_size=phase_size,
                        overall_outline=overall_outline,
                        previous_phases=phases,
                        genre=genre,
                        theme=theme,
                        words_per_chapter=words_per_chapter
                    )
                    phases.append(new_phase_outline)
                    plan["phases"] = phases
                    plan["current_phase"] = current_phase
                    ***REMOVED*** 更新 chapter_outline（合并所有阶段的章节）
                    all_chapters = []
                    for phase in phases:
                        all_chapters.extend(phase.get("chapters", []))
                    plan["chapter_outline"] = all_chapters
                    
                    ***REMOVED*** 保存更新后的大纲
                    try:
                        plan_file = self.output_dir / "novel_plan.json"
                        plan_file.write_text(
                            json.dumps(plan, ensure_ascii=False, indent=2),
                            encoding="utf-8"
                        )
                        logger.info(f"阶段{current_phase}大纲已生成并保存")
                    except Exception as e:
                        logger.warning(f"保存更新后的大纲失败: {e}")
            
            ***REMOVED*** 获取章节信息
            chapter_outline = plan.get("chapter_outline", [])
            if i < len(chapter_outline):
                chapter_info = chapter_outline[i]
            else:
                chapter_info = {
                    "chapter_number": chapter_number,
                    "title": f"第{chapter_number}章",
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
                
                ***REMOVED*** 更新分层摘要
                ***REMOVED*** 注意：此时 chapter 已经通过 create_chapter 添加到 self.chapters 了
                current_phase_chapters.append(chapter)
                
                ***REMOVED*** 获取最近章节（用于详细摘要）
                ***REMOVED*** 包含当前章节（因为 create_chapter 已经将其添加到 self.chapters）
                recent_chapters = self.chapters[-recent_window:] if len(self.chapters) > recent_window else self.chapters
                
                ***REMOVED*** 获取关键节点信息（从整体大纲）
                key_plot_points = plan.get("overall", {}).get("key_plot_points", []) if plan_type == "progressive" else []
                
                ***REMOVED*** 生成分层摘要（用于下一章）
                ***REMOVED*** 注意：这里生成的是用于下一章的摘要，所以不需要包含当前章节
                ***REMOVED*** 但为了保持连贯性，我们仍然包含当前章节
                previous_summary = self._generate_layered_summary(
                    chapter_number=chapter_number,
                    recent_chapters=recent_chapters,
                    phase_summaries=phase_summaries,
                    key_plot_points=key_plot_points,
                    recent_window=recent_window
                )
                
                ***REMOVED*** 检查是否完成一个阶段（需要生成阶段摘要）
                if plan_type == "progressive":
                    current_phase = (chapter_number - 1) // phase_size + 1
                    phase_end_chapter = current_phase * phase_size
                    
                    ***REMOVED*** 如果完成一个阶段，生成阶段摘要
                    if chapter_number == phase_end_chapter or chapter_number == target_chapters:
                        logger.info(f"阶段{current_phase}完成，生成阶段摘要...")
                        phase_summary = self._generate_phase_summary(current_phase_chapters, current_phase)
                        phase_summaries.append(phase_summary)
                        current_phase_chapters = []  ***REMOVED*** 重置当前阶段章节列表
                        
                        ***REMOVED*** 保存阶段摘要到计划中
                        phases = plan.get("phases", [])
                        if current_phase <= len(phases):
                            phases[current_phase - 1]["phase_summary"] = phase_summary
                            plan["phases"] = phases
                
                ***REMOVED*** 每5章进行一次上下文压缩（如果启用）
                if self.context_manager and (i + 1) % 5 == 0:
                    logger.info(f"进行上下文压缩（第{i+1}章后）...")
                    ***REMOVED*** 这里可以触发上下文压缩逻辑
                
                ***REMOVED*** 每10章进行一次阶段性质量检查
                if (i + 1) % 10 == 0:
                    logger.info(f"进行阶段性质量检查（第{i+1}章后）...")
                    periodic_quality_result = self._periodic_quality_check(chapter_number)
                    if periodic_quality_result:
                        logger.info(f"阶段性质量检查完成：{periodic_quality_result.get('summary', '')}")
                        ***REMOVED*** 如果发现问题，记录到元数据
                        if not self.metadata.get("periodic_quality_checks"):
                            self.metadata["periodic_quality_checks"] = []
                        self.metadata["periodic_quality_checks"].append(periodic_quality_result)
                        
                        ***REMOVED*** 如果使用渐进式大纲，检查是否需要调整后续大纲
                        if plan_type == "progressive" and periodic_quality_result.get("needs_attention", False):
                            logger.info("检测到质量问题，考虑调整后续大纲...")
                            self._consider_outline_adjustment(plan, chapter_number, periodic_quality_result)
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
            
            ***REMOVED*** 4. 更新实体重要性（用于分层实体管理）
            self._update_entity_importance(chapter, extracted_entities)
            
            ***REMOVED*** 5. 保存语义网格
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
    
    def _rewrite_chapter_with_feedback(
        self,
        chapter_number: int,
        chapter_title: str,
        chapter_summary: str,
        original_content: str,
        quality_result: Dict[str, Any],
        previous_chapters_summary: Optional[str] = None,
        target_words: int = 2048,
        semantic_entities_context: str = "",
        unimem_context: str = ""
    ) -> Optional[str]:
        """
        基于质量检查反馈重写章节
        
        Args:
            chapter_number: 章节编号
            chapter_title: 章节标题
            chapter_summary: 章节摘要
            original_content: 原始内容
            quality_result: 质量检查结果
            previous_chapters_summary: 前面章节摘要
            target_words: 目标字数
            semantic_entities_context: 语义实体上下文
            unimem_context: UniMem上下文
        
        Returns:
            重写后的内容，如果失败则返回None
        """
        try:
            ***REMOVED*** 构建反馈信息
            issues = quality_result.get('issues', [])
            feedback_summary = []
            
            for issue in issues[:5]:  ***REMOVED*** 最多列出5个问题
                feedback_summary.append(
                    f"- {issue.get('description', '')} "
                    f"（{issue.get('severity', 'unknown')}严重度）"
                )
            
            if not feedback_summary:
                feedback_summary = ["检测到质量问题，需要改进"]
            
            feedback_text = "\n".join(feedback_summary)
            
            ***REMOVED*** 构建重写提示词
            rewrite_prompt = f"""请重写小说《{self.novel_title}》的第{chapter_number}章。

**章节信息**：
- 标题：{chapter_title}
- 摘要：{chapter_summary}
- 目标字数：{target_words}字

**原始内容**（存在以下质量问题，需要改进）：
{original_content[:2000]}...

**质量检查反馈**：
{feedback_text}

**改进要求**：
1. 必须解决上述质量问题
2. 保持章节的核心情节和主要事件不变
3. 确保字数控制在目标范围内（{target_words}字，允许±10%）
4. 保持与前面章节的连贯性
5. 确保对话占比在20-40%之间
6. 避免冗余的环境描写和过度的心理活动

**前面章节摘要**（用于保持连贯性）：
{previous_chapters_summary if previous_chapters_summary else "无"}

{semantic_entities_context}

{unimem_context}

**重要提示**：请直接生成改进后的完整章节内容，不需要说明或注释。确保内容质量明显优于原始版本。"""

            ***REMOVED*** 生成重写内容
            original_max_iterations = self.agent.max_iterations
            self.agent.max_iterations = 5
            try:
                rewritten_content = self.agent.run(query=rewrite_prompt, verbose=False)
            finally:
                self.agent.max_iterations = original_max_iterations
            
            ***REMOVED*** 清理内容（移除可能的markdown标记等）
            if "```" in rewritten_content:
                ***REMOVED*** 移除代码块标记
                lines = rewritten_content.split('\n')
                cleaned_lines = []
                in_code_block = False
                for line in lines:
                    if line.strip().startswith('```'):
                        in_code_block = not in_code_block
                        continue
                    if not in_code_block:
                        cleaned_lines.append(line)
                rewritten_content = '\n'.join(cleaned_lines)
            
            ***REMOVED*** 确保内容长度合理
            if len(rewritten_content) < target_words * 0.5:  ***REMOVED*** 至少是目标字数的50%
                logger.warning(f"重写内容过短（{len(rewritten_content)}字），可能重写失败")
                return None
            
            return rewritten_content.strip()
            
        except Exception as e:
            logger.error(f"重写章节失败: {e}", exc_info=True)
            return None
    
    def _periodic_quality_check(self, current_chapter_number: int) -> Optional[Dict[str, Any]]:
        """
        阶段性质量检查（每10章执行一次）
        
        Args:
            current_chapter_number: 当前章节编号
        
        Returns:
            质量检查结果
        """
        if current_chapter_number < 10:
            return None
        
        try:
            logger.info(f"开始阶段性质量检查（第{current_chapter_number}章）...")
            
            ***REMOVED*** 获取最近10章
            recent_chapters = self.chapters[-10:] if len(self.chapters) >= 10 else self.chapters
            
            ***REMOVED*** 1. 检查连贯性
            coherence_score = self._calculate_coherence_score(recent_chapters)
            
            ***REMOVED*** 2. 检查人物一致性
            character_consistency_score = self._calculate_character_consistency_score(recent_chapters)
            
            ***REMOVED*** 3. 检查情节节奏
            plot_rhythm_score = self._calculate_plot_rhythm_score(recent_chapters)
            
            ***REMOVED*** 4. 检查世界观一致性
            worldview_consistency_score = self._calculate_worldview_consistency_score(recent_chapters)
            
            ***REMOVED*** 5. 检查悬念/伏笔
            suspense_score = self._calculate_suspense_score(recent_chapters)
            
            ***REMOVED*** 综合评分
            overall_score = (
                coherence_score * 0.3 +
                character_consistency_score * 0.25 +
                plot_rhythm_score * 0.2 +
                worldview_consistency_score * 0.15 +
                suspense_score * 0.1
            )
            
            result = {
                "chapter_range": f"第{current_chapter_number-9}-{current_chapter_number}章",
                "check_time": datetime.now().isoformat(),
                "scores": {
                    "coherence": round(coherence_score, 2),
                    "character_consistency": round(character_consistency_score, 2),
                    "plot_rhythm": round(plot_rhythm_score, 2),
                    "worldview_consistency": round(worldview_consistency_score, 2),
                    "suspense": round(suspense_score, 2),
                    "overall": round(overall_score, 2)
                },
                "summary": f"综合评分: {overall_score:.2f} (连贯性:{coherence_score:.2f}, 人物:{character_consistency_score:.2f}, 节奏:{plot_rhythm_score:.2f}, 世界观:{worldview_consistency_score:.2f}, 悬念:{suspense_score:.2f})"
            }
            
            ***REMOVED*** 如果综合评分低于0.7，记录警告
            if overall_score < 0.7:
                logger.warning(f"阶段性质量检查发现质量问题: {result['summary']}")
                result["needs_attention"] = True
            else:
                result["needs_attention"] = False
            
            return result
            
        except Exception as e:
            logger.error(f"阶段性质量检查失败: {e}", exc_info=True)
            return None
    
    def _calculate_coherence_score(self, chapters: List[NovelChapter]) -> float:
        """计算连贯性得分（0-1）"""
        if len(chapters) < 2:
            return 1.0
        
        score = 1.0
        
        ***REMOVED*** 检查主要人物是否连续出现
        main_characters = set()
        for chapter in chapters:
            if self.semantic_mesh:
                try:
                    chapter_entities = [
                        e for e in self.semantic_mesh.entities.values()
                        if chapter.chapter_number in e.metadata.get('appearance_chapters', [])
                    ]
                    chapter_characters = {e.name for e in chapter_entities if e.type.value == "character"}
                    if chapter_characters:
                        if main_characters and not (main_characters & chapter_characters):
                            score -= 0.1
                        main_characters.update(chapter_characters)
                except Exception:
                    pass
        
        return max(0.0, min(1.0, score))
    
    def _calculate_character_consistency_score(self, chapters: List[NovelChapter]) -> float:
        """计算人物一致性得分（0-1）"""
        if not self.semantic_mesh:
            return 0.8
        return 1.0  ***REMOVED*** 简化实现，后续可以增强
    
    def _calculate_plot_rhythm_score(self, chapters: List[NovelChapter]) -> float:
        """
        计算情节节奏得分（0-1）
        
        改进算法：结合字数方差和情节结构分析
        """
        if len(chapters) < 3:
            return 0.8
        
        word_counts = [len(ch.content) for ch in chapters]
        if len(word_counts) < 3:
            return 0.8
        
        try:
            ***REMOVED*** 1. 字数方差分析（原有逻辑）
            variance = statistics.variance(word_counts) if len(word_counts) > 1 else 0
            mean = statistics.mean(word_counts)
            cv = (variance ** 0.5) / mean if mean > 0 else 0
            
            base_score = 0.8
            if 0.1 < cv < 0.3:
                base_score = 0.9
            elif cv < 0.1:
                base_score = 0.6
            elif cv > 0.5:
                base_score = 0.5
            
            ***REMOVED*** 2. 情节结构分析（新增）
            ***REMOVED*** 检查对话占比（理想范围：20%-40%）
            dialogue_scores = []
            for ch in chapters[-5:]:  ***REMOVED*** 检查最近5章
                content = ch.content
                ***REMOVED*** 支持中文引号："和"（U+201C和U+201D）、'和'（U+2018和U+2019）
                ***REMOVED*** 以及日式引号：「和」（U+300C和U+300D）、『和』（U+300E和U+300F）
                ***REMOVED*** 以及英文引号："和"、'和'
                ***REMOVED*** 使用Unicode转义确保正确匹配
                dialogues = []
                
                ***REMOVED*** 中文双引号："和"（使用Unicode转义）
                pattern1 = r'[\u201C]([^\u201D]+?)[\u201D]'
                dialogues.extend(re.findall(pattern1, content))
                
                ***REMOVED*** 中文单引号：'和'（使用Unicode转义）
                pattern2 = r'[\u2018]([^\u2019]+?)[\u2019]'
                dialogues.extend(re.findall(pattern2, content))
                
                ***REMOVED*** 日式引号：「和」（使用Unicode转义）
                pattern3 = r'[\u300C]([^\u300D]+?)[\u300D]'
                dialogues.extend(re.findall(pattern3, content))
                
                ***REMOVED*** 日式双引号：『和』（使用Unicode转义）
                pattern4 = r'[\u300E]([^\u300F]+?)[\u300F]'
                dialogues.extend(re.findall(pattern4, content))
                
                ***REMOVED*** 英文引号："和"、'和'
                pattern5 = r'["\']([^"\']+?)["\']'
                dialogues.extend(re.findall(pattern5, content))
                dialogue_length = sum(len(d) for d in dialogues)
                dialogue_ratio = dialogue_length / len(content) if len(content) > 0 else 0
                
                if 0.2 <= dialogue_ratio <= 0.4:
                    dialogue_scores.append(1.0)
                elif 0.15 <= dialogue_ratio < 0.2 or 0.4 < dialogue_ratio <= 0.45:
                    dialogue_scores.append(0.8)
                else:
                    dialogue_scores.append(0.6)
            
            avg_dialogue_score = sum(dialogue_scores) / len(dialogue_scores) if dialogue_scores else 0.8
            
            ***REMOVED*** 3. 综合评分（字数方差60%，对话占比40%）
            score = base_score * 0.6 + avg_dialogue_score * 0.4
            
        except Exception:
            score = 0.8
        
        return max(0.0, min(1.0, score))
    
    def _calculate_worldview_consistency_score(self, chapters: List[NovelChapter]) -> float:
        """计算世界观一致性得分（0-1）"""
        if not self.semantic_mesh:
            return 0.8
        return 1.0  ***REMOVED*** 简化实现，后续可以增强
    
    def _calculate_suspense_score(self, chapters: List[NovelChapter]) -> float:
        """
        计算悬念得分（0-1）
        
        改进算法：结合关键词检测和情节分析
        """
        if not chapters:
            return 0.5
        
        suspense_keywords = ["？", "?", "...", "！", "!", "突然", "竟然", "没想到", "原来", "但是", "然而", "不过", "然而", "可是"]
        suspense_scores = []
        
        for chapter in chapters[-5:]:  ***REMOVED*** 检查最近5章
            content = chapter.content
            ending = content[-200:] if len(content) > 200 else content
            
            ***REMOVED*** 1. 关键词检测（原有逻辑）
            keyword_count = sum(1 for keyword in suspense_keywords if keyword in ending)
            keyword_score = min(1.0, keyword_count / 3.0)  ***REMOVED*** 最多3个关键词得满分
            
            ***REMOVED*** 2. 章节结尾分析（新增）
            ***REMOVED*** 检查结尾是否有疑问句、转折、意外发现等
            has_question = "？" in ending or "?" in ending
            has_turn = any(word in ending for word in ["但是", "然而", "不过", "可是", "原来", "竟然", "没想到"])
            has_suspense = "..." in ending or "突然" in ending
            
            structure_score = 0.0
            if has_question:
                structure_score += 0.3
            if has_turn:
                structure_score += 0.4
            if has_suspense:
                structure_score += 0.3
            
            ***REMOVED*** 3. 综合评分（关键词40%，结构60%）
            chapter_score = keyword_score * 0.4 + structure_score * 0.6
            suspense_scores.append(chapter_score)
        
        ***REMOVED*** 计算平均得分
        score = sum(suspense_scores) / len(suspense_scores) if suspense_scores else 0.5
        return max(0.0, min(1.0, score))
    
    def _track_chapter_quality(self, chapter_number: int, quality_result: Dict[str, Any], actual_words: int, target_words: int):
        """
        追踪单章质量指标
        
        Args:
            chapter_number: 章节编号
            quality_result: 质量检查结果
            actual_words: 实际字数
            target_words: 目标字数
        """
        try:
            ***REMOVED*** 计算字数控制得分（0-1）
            word_diff_percent = abs((actual_words - target_words) / target_words) if target_words > 0 else 0
            if word_diff_percent <= 0.1:
                word_control_score = 1.0
            elif word_diff_percent <= 0.2:
                word_control_score = 0.8
            elif word_diff_percent <= 0.3:
                word_control_score = 0.6
            else:
                word_control_score = 0.4
            
            ***REMOVED*** 记录质量指标
            quality_metrics = {
                "chapter_number": chapter_number,
                "timestamp": datetime.now().isoformat(),
                "word_count": actual_words,
                "target_words": target_words,
                "word_control_score": round(word_control_score, 2),
                "quality_issues": quality_result.get("total_issues", 0),
                "high_severity_issues": quality_result.get("by_severity", {}).get("high", 0)
            }
            
            self.quality_tracker["chapter_quality_history"].append(quality_metrics)
            
            ***REMOVED*** 更新质量趋势（每10章计算一次平均值）
            if chapter_number % 10 == 0:
                recent_chapters = self.chapters[-10:] if len(self.chapters) >= 10 else self.chapters
                if recent_chapters:
                    coherence = self._calculate_coherence_score(recent_chapters)
                    character = self._calculate_character_consistency_score(recent_chapters)
                    rhythm = self._calculate_plot_rhythm_score(recent_chapters)
                    worldview = self._calculate_worldview_consistency_score(recent_chapters)
                    suspense = self._calculate_suspense_score(recent_chapters)
                    
                    self.quality_tracker["quality_trends"]["coherence"].append({
                        "chapter": chapter_number,
                        "score": coherence
                    })
                    self.quality_tracker["quality_trends"]["character_consistency"].append({
                        "chapter": chapter_number,
                        "score": character
                    })
                    self.quality_tracker["quality_trends"]["plot_rhythm"].append({
                        "chapter": chapter_number,
                        "score": rhythm
                    })
                    self.quality_tracker["quality_trends"]["worldview_consistency"].append({
                        "chapter": chapter_number,
                        "score": worldview
                    })
                    self.quality_tracker["quality_trends"]["suspense"].append({
                        "chapter": chapter_number,
                        "score": suspense
                    })
            
            ***REMOVED*** 基于质量问题类型动态调整后续章节的prompt
            self._update_quality_adjustments(chapter_number, quality_result)
            
        except Exception as e:
            logger.debug(f"追踪质量指标失败: {e}")
    
    def _update_quality_adjustments(self, chapter_number: int, quality_result: Dict[str, Any]):
        """
        根据质量检查结果更新质量调整指令
        
        Args:
            chapter_number: 章节编号
            quality_result: 质量检查结果
        """
        try:
            issues = quality_result.get("issues", [])
            if not issues:
                return
            
            ***REMOVED*** 初始化quality_adjustments
            if not self.metadata.get("quality_adjustments"):
                self.metadata["quality_adjustments"] = {}
            
            ***REMOVED*** 统计问题类型
            issue_types = {}
            for issue in issues:
                issue_type = issue.get("type", "")
                if issue_type not in issue_types:
                    issue_types[issue_type] = []
                issue_types[issue_type].append(issue)
            
            ***REMOVED*** 根据问题类型更新调整指令
            from novel_creation.quality_checker import IssueType
            
            ***REMOVED*** 对话质量问题
            style_issues = issue_types.get(IssueType.STYLE_ISSUE.value, [])
            for issue in style_issues:
                desc = issue.get("description", "")
                metadata = issue.get("metadata", {})
                
                ***REMOVED*** 对话占比过低
                if "对话占比过低" in desc or "dialogue_ratio" in metadata:
                    dialogue_ratio = metadata.get("dialogue_ratio", 0)
                    if dialogue_ratio < 0.15:
                        self.metadata["quality_adjustments"]["dialogue_issue"] = {
                            "type": "low_ratio",
                            "chapter": chapter_number,
                            "description": desc,
                            "dialogue_ratio": dialogue_ratio
                        }
                        logger.info(f"检测到对话占比过低（{dialogue_ratio*100:.1f}%），将在后续章节中调整")
                
                ***REMOVED*** 对话占比过高
                elif "对话占比过高" in desc:
                    dialogue_ratio = metadata.get("dialogue_ratio", 0)
                    if dialogue_ratio > 0.45:
                        self.metadata["quality_adjustments"]["dialogue_issue"] = {
                            "type": "high_ratio",
                            "chapter": chapter_number,
                            "description": desc,
                            "dialogue_ratio": dialogue_ratio
                        }
                        logger.info(f"检测到对话占比过高（{dialogue_ratio*100:.1f}%），将在后续章节中调整")
                
                ***REMOVED*** 对话缺乏动作或情绪
                elif "对话缺乏动作" in desc or "对话缺乏情绪" in desc or "dialogue_with_action" in metadata:
                    self.metadata["quality_adjustments"]["dialogue_issue"] = {
                        "type": "lack_action",
                        "chapter": chapter_number,
                        "description": desc
                    }
                    logger.info(f"检测到对话缺乏动作或情绪，将在后续章节中调整")
                
                ***REMOVED*** 环境描写冗余
                elif "环境描写可能冗余" in desc or "redundant_count" in metadata:
                    self.metadata["quality_adjustments"]["description_issue"] = {
                        "type": "redundant",
                        "chapter": chapter_number,
                        "description": desc,
                        "redundant_count": metadata.get("redundant_count", 0)
                    }
                    logger.info(f"检测到环境描写冗余，将在后续章节中调整")
                
                ***REMOVED*** 心理活动过多
                elif "心理活动描写过多" in desc or "thought_sentence_count" in metadata:
                    self.metadata["quality_adjustments"]["description_issue"] = {
                        "type": "excessive_thought",
                        "chapter": chapter_number,
                        "description": desc,
                        "thought_count": metadata.get("thought_sentence_count", 0)
                    }
                    logger.info(f"检测到心理活动描写过多，将在后续章节中调整")
            
            ***REMOVED*** 一致性问题
            character_issues = issue_types.get(IssueType.CHARACTER_INCONSISTENCY.value, [])
            if character_issues:
                self.metadata["quality_adjustments"]["consistency_issue"] = {
                    "type": "character",
                    "chapter": chapter_number,
                    "description": character_issues[0].get("description", ""),
                    "count": len(character_issues)
                }
                logger.info(f"检测到角色一致性问题（{len(character_issues)}个），将在后续章节中调整")
            
            worldview_issues = issue_types.get(IssueType.WORLDVIEW_INCONSISTENCY.value, [])
            if worldview_issues:
                self.metadata["quality_adjustments"]["consistency_issue"] = {
                    "type": "worldview",
                    "chapter": chapter_number,
                    "description": worldview_issues[0].get("description", ""),
                    "count": len(worldview_issues)
                }
                logger.info(f"检测到世界观一致性问题（{len(worldview_issues)}个），将在后续章节中调整")
            
            timeline_issues = issue_types.get(IssueType.TIMELINE_INCONSISTENCY.value, [])
            if timeline_issues:
                self.metadata["quality_adjustments"]["consistency_issue"] = {
                    "type": "timeline",
                    "chapter": chapter_number,
                    "description": timeline_issues[0].get("description", ""),
                    "count": len(timeline_issues)
                }
                logger.info(f"检测到时间线一致性问题（{len(timeline_issues)}个），将在后续章节中调整")
            
        except Exception as e:
            logger.debug(f"更新质量调整指令失败: {e}")
    
    def get_quality_summary(self) -> Dict[str, Any]:
        """
        获取质量指标摘要
        
        Returns:
            质量指标摘要
        """
        if not self.quality_tracker["chapter_quality_history"]:
            return {"message": "暂无质量数据"}
        
        history = self.quality_tracker["chapter_quality_history"]
        
        ***REMOVED*** 计算平均指标
        avg_word_control = sum(m["word_control_score"] for m in history) / len(history)
        avg_issues = sum(m["quality_issues"] for m in history) / len(history)
        avg_high_severity = sum(m["high_severity_issues"] for m in history) / len(history)
        
        ***REMOVED*** 计算趋势
        trends = {}
        for metric_name, trend_data in self.quality_tracker["quality_trends"].items():
            if trend_data:
                scores = [d["score"] for d in trend_data]
                trends[metric_name] = {
                    "current": scores[-1] if scores else 0,
                    "average": sum(scores) / len(scores) if scores else 0,
                    "trend": "improving" if len(scores) > 1 and scores[-1] > scores[0] else "stable" if len(scores) > 1 and abs(scores[-1] - scores[0]) < 0.1 else "declining"
                }
        
        return {
            "total_chapters": len(history),
            "average_metrics": {
                "word_control_score": round(avg_word_control, 2),
                "quality_issues": round(avg_issues, 2),
                "high_severity_issues": round(avg_high_severity, 2)
            },
            "quality_trends": trends,
            "latest_periodic_check": self.metadata.get("periodic_quality_checks", [])[-1] if self.metadata.get("periodic_quality_checks") else None
        }
    
    def _consider_outline_adjustment(
        self,
        plan: Dict[str, Any],
        current_chapter: int,
        quality_result: Dict[str, Any]
    ):
        """
        考虑调整后续大纲（根据质量反馈）
        
        Args:
            plan: 小说大纲
            current_chapter: 当前章节编号
            quality_result: 阶段性质量检查结果
        """
        try:
            ***REMOVED*** 如果综合评分低于0.7，考虑调整大纲
            overall_score = quality_result.get("scores", {}).get("overall", 1.0)
            if overall_score < 0.7:
                logger.warning(
                    f"综合评分 {overall_score:.2f} 低于0.7，建议调整后续大纲策略"
                )
                ***REMOVED*** 记录调整建议到元数据
                if not self.metadata.get("outline_adjustment_suggestions"):
                    self.metadata["outline_adjustment_suggestions"] = []
                
                suggestion = {
                    "chapter": current_chapter,
                    "quality_score": overall_score,
                    "suggestion": "考虑简化后续情节，加强连贯性",
                    "timestamp": datetime.now().isoformat()
                }
                self.metadata["outline_adjustment_suggestions"].append(suggestion)
            
            ***REMOVED*** 如果节奏得分过低，建议调整后续章节的节奏（阈值从0.6提高到0.7，更早触发）
            rhythm_score = quality_result.get("scores", {}).get("plot_rhythm", 1.0)
            if rhythm_score < 0.7:
                logger.info(f"情节节奏得分 {rhythm_score:.2f} 较低（<0.7），建议后续章节增加节奏变化")
                ***REMOVED*** 记录到元数据，用于动态调整
                if not self.metadata.get("quality_adjustments"):
                    self.metadata["quality_adjustments"] = {}
                self.metadata["quality_adjustments"]["rhythm_issue"] = {
                    "score": rhythm_score,
                    "chapter": current_chapter,
                    "suggestion": "增加对话占比（25-35%），优化情节节奏，确保对话、动作、描写交替出现"
                }
            
            ***REMOVED*** 如果悬念得分过低，建议调整后续章节的悬念设置（阈值从0.6提高到0.7，更早触发）
            suspense_score = quality_result.get("scores", {}).get("suspense", 1.0)
            if suspense_score < 0.7:
                logger.info(f"悬念得分 {suspense_score:.2f} 较低（<0.7），建议后续章节增加悬念设置")
                if not self.metadata.get("quality_adjustments"):
                    self.metadata["quality_adjustments"] = {}
                self.metadata["quality_adjustments"]["suspense_issue"] = {
                    "score": suspense_score,
                    "chapter": current_chapter,
                    "suggestion": "在章节结尾（最后50-100字）必须设置悬念：使用疑问句、转折词、省略号或意外发现"
                }
                
        except Exception as e:
            logger.debug(f"大纲调整建议生成失败: {e}")
    
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
        
        ***REMOVED*** 质量追踪数据
        metadata["quality_tracker"] = self.quality_tracker
        
        try:
            metadata_file.write_text(
                json.dumps(metadata, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            logger.debug(f"元数据文件已保存: {metadata_file}")
        except (IOError, OSError) as e:
            logger.error(f"保存元数据文件失败: {e}", exc_info=True)
            ***REMOVED*** 不抛出异常，允许继续执行
    
    def _get_adaptive_generation_strategy(self, chapter_number: int) -> Dict[str, Any]:
        """
        根据质量反馈获取自适应生成策略
        
        Args:
            chapter_number: 当前章节编号
        
        Returns:
            生成策略字典
        """
        strategy = {
            "strict_word_control": False,
            "enhanced_coherence": False,
            "rhythm_control": False,
            "suspense_control": False
        }
        
        ***REMOVED*** 从第3章开始检查字数控制（更早检测问题）
        if chapter_number >= 3:
            quality_history = self.quality_tracker.get("chapter_quality_history", [])
            if quality_history:
                ***REMOVED*** 检查最近3章的字数控制情况
                recent_history = quality_history[-3:]
                
                ***REMOVED*** 计算最近3章的平均字数偏差百分比
                recent_deviations = [
                    abs(m.get("word_diff_percent", 0)) 
                    for m in recent_history
                ]
                avg_deviation = sum(recent_deviations) / len(recent_deviations) if recent_deviations else 0
                
                ***REMOVED*** 计算最近3章的平均字数控制得分
                recent_scores = [m.get("word_control_score", 1.0) for m in recent_history]
                avg_word_control = sum(recent_scores) / len(recent_scores) if recent_scores else 1.0
                
                ***REMOVED*** 如果平均偏差>25%或平均得分<0.7，启用严格字数控制
                if avg_deviation > 25 or avg_word_control < 0.7:
                    strategy["strict_word_control"] = True
                    logger.info(
                        f"检测到字数控制问题（平均偏差{avg_deviation:.1f}%，平均得分{avg_word_control:.2f}），"
                        f"启用严格字数控制模式"
                    )
        
        ***REMOVED*** 如果章节数 >= 10，检查其他质量指标
        if chapter_number >= 10:
            recent_checks = self.metadata.get("periodic_quality_checks", [])
            if recent_checks:
                latest_check = recent_checks[-1]
                scores = latest_check.get("scores", {})
                
                ***REMOVED*** 如果连贯性得分低，增强连贯性检查
                coherence_score = scores.get("coherence", 1.0)
                if coherence_score < 0.7:
                    strategy["enhanced_coherence"] = True
                    logger.info(f"检测到连贯性问题（得分{coherence_score:.2f}），增强连贯性检查")
                
                ***REMOVED*** 如果节奏得分低，启用节奏控制（阈值从0.6提高到0.7，更早触发）
                rhythm_score = scores.get("plot_rhythm", 1.0)
                if rhythm_score < 0.7:
                    strategy["rhythm_control"] = True
                    logger.info(f"检测到节奏问题（得分{rhythm_score:.2f} < 0.7），启用节奏控制")
                
                ***REMOVED*** 如果悬念得分低，启用悬念控制（新增）
                suspense_score = scores.get("suspense", 1.0)
                if suspense_score < 0.7:
                    strategy["suspense_control"] = True
                    logger.info(f"检测到悬念问题（得分{suspense_score:.2f} < 0.7），启用悬念控制")
        
        return strategy
    
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
    
    def _calculate_entity_importance(
        self,
        entity: Entity,
        current_chapter: int
    ) -> float:
        """
        计算实体重要性分数
        
        用于分层实体管理，优先传递重要实体
        
        Args:
            entity: 实体对象
            current_chapter: 当前章节编号
        
        Returns:
            重要性分数（越高越重要）
        """
        score = 0.0
        
        ***REMOVED*** 1. 出现频率（越高越重要）
        appearance_count = entity.metadata.get('appearance_count', 1)
        score += appearance_count * 0.3
        
        ***REMOVED*** 2. 最近出现章节（越近越重要）
        last_appearance = entity.metadata.get('last_appearance_chapter', 0)
        if last_appearance > 0:
            recency = max(0, current_chapter - last_appearance)
            ***REMOVED*** 最近20章内的实体得分更高，超过20章后衰减
            recency_score = max(0, (20 - min(recency, 20)) / 20.0)
            score += recency_score * 0.2
        else:
            ***REMOVED*** 如果没有记录，使用首次出现章节
            entity_chapter = entity.metadata.get('chapter', 0)
            if entity_chapter > 0:
                recency = max(0, current_chapter - entity_chapter)
                recency_score = max(0, (20 - min(recency, 20)) / 20.0)
                score += recency_score * 0.1
        
        ***REMOVED*** 3. 实体类型权重（角色 > 地点 > 物品）
        type_weight = {
            EntityType.CHARACTER: 1.0,
            EntityType.SETTING: 0.7,
            EntityType.SYMBOL: 0.5,
            EntityType.PLOT_POINT: 0.6
        }
        score *= type_weight.get(entity.type, 0.5)
        
        ***REMOVED*** 4. 是否为关键实体（标记的关键实体，如主角、主要配角）
        if entity.metadata.get('is_key', False):
            score *= 2.0
        
        ***REMOVED*** 5. 实体描述长度（有详细描述的实体通常更重要）
        if entity.content and len(entity.content) > 50:
            score *= 1.2
        
        return score
    
    def _is_key_character(self, entity: Entity) -> bool:
        """
        判断是否为关键角色（主角或主要配角）
        
        Args:
            entity: 实体对象
        
        Returns:
            是否为关键角色
        """
        if entity.type != EntityType.CHARACTER:
            return False
        
        ***REMOVED*** 检查实体名称和描述中的关键词
        name = entity.name.lower()
        content = (entity.content or "").lower()
        
        ***REMOVED*** 关键词：主角、主角、主要角色、男主、女主等
        key_keywords = ['主角', '男主', '女主', '主要', '核心', '主人公', '主人']
        
        ***REMOVED*** 检查名称或描述中是否包含关键词
        if any(keyword in name or keyword in content for keyword in key_keywords):
            return True
        
        ***REMOVED*** 检查出现频率（出现次数多可能是主要角色）
        appearance_count = entity.metadata.get('appearance_count', 0)
        if appearance_count >= 5:  ***REMOVED*** 出现5次以上可能是主要角色
            return True
        
        return False
    
    def _update_entity_importance(
        self,
        chapter: NovelChapter,
        extracted_entities: List[Entity]
    ):
        """
        更新实体重要性（每章创作后）
        
        更新实体的出现次数和最近出现章节，用于重要性评分
        注意：实体应该已经在语义网格中（由 _process_chapter_with_creative_context 添加）
        
        Args:
            chapter: 章节对象
            extracted_entities: 提取的实体列表
        """
        if not self.semantic_mesh:
            return
        
        for entity in extracted_entities:
            ***REMOVED*** 从语义网格中获取实体（实体应该已经通过 add_entity 添加）
            mesh_entity = self.semantic_mesh.entities.get(entity.id)
            
            if mesh_entity:
                ***REMOVED*** 更新语义网格中的实体
                ***REMOVED*** 增加出现次数
                mesh_entity.metadata['appearance_count'] = mesh_entity.metadata.get('appearance_count', 0) + 1
                ***REMOVED*** 更新最近出现章节
                mesh_entity.metadata['last_appearance_chapter'] = chapter.chapter_number
                ***REMOVED*** 更新实体内容（如果新内容更详细）
                if entity.content and (not mesh_entity.content or len(entity.content) > len(mesh_entity.content)):
                    mesh_entity.content = entity.content
                ***REMOVED*** 如果新实体是关键角色，标记它
                if self._is_key_character(entity):
                    mesh_entity.metadata['is_key'] = True
                    logger.debug(f"标记关键角色: {mesh_entity.name}")
            else:
                ***REMOVED*** 实体不在语义网格中（不应该发生，但为了健壮性处理）
                logger.warning(f"实体 {entity.id} 不在语义网格中，跳过重要性更新")
    
    def _get_previous_chapters_entities(self, chapter_number: int, max_entities: int = 64) -> str:
        """
        从语义网格检索前面章节的实体（分层实体管理）
        
        采用分层筛选机制：
        1. 核心实体（始终包含）：关键角色和核心设定
        2. 重要实体（按重要性筛选）：根据出现频率、最近出现、实体类型等评分
        
        Args:
            chapter_number: 当前章节编号
            max_entities: 最大实体数量（默认64个，平衡信息量和Token消耗，确保各类型实体都有足够配额）
        
        Returns:
            格式化的实体信息字符串
        """
        if not self.enable_creative_context or not self.semantic_mesh:
            return ""
        
        if chapter_number <= 1:
            return ""  ***REMOVED*** 第一章没有前面的章节
        
        try:
            ***REMOVED*** 收集所有前面章节的实体
            candidate_entities = []
            
            for entity_id, entity in self.semantic_mesh.entities.items():
                ***REMOVED*** 跳过章节实体本身
                if entity.type == EntityType.CHAPTER:
                    continue
                
                ***REMOVED*** 获取实体所属章节
                entity_chapter = entity.metadata.get('chapter', 0)
                
                ***REMOVED*** 如果实体没有章节号，尝试从章节实体关系中推断
                if entity_chapter == 0:
                    for relation in self.semantic_mesh.relations:
                        if relation.target_id == entity_id and relation.source_id.startswith('chapter_'):
                            try:
                                chapter_id = relation.source_id.replace('chapter_', '')
                                entity_chapter = int(chapter_id)
                            except:
                                pass
                            break
                
                ***REMOVED*** 只包含前面章节的实体（排除当前章节）
                if 0 < entity_chapter < chapter_number:
                    candidate_entities.append(entity)
            
            if not candidate_entities:
                return ""
            
            ***REMOVED*** 计算每个实体的重要性分数
            entity_scores = []
            for entity in candidate_entities:
                score = self._calculate_entity_importance(entity, chapter_number)
                entity_scores.append((score, entity))
            
            ***REMOVED*** 按重要性排序
            entity_scores.sort(key=lambda x: x[0], reverse=True)
            
            ***REMOVED*** 分层选择实体（按类型配额分配，确保类型多样性）
            ***REMOVED*** 1. 核心实体（关键角色和核心设定，最多10个）
            ***REMOVED*** 先收集所有关键实体，然后对同名实体去重
            all_key_entities = [
                (score, entity) for score, entity in entity_scores
                if entity.metadata.get('is_key', False)
            ]
            
            ***REMOVED*** 对同名关键实体去重（避免主角的多个版本都成为核心实体）
            key_entities_by_name = {}
            for score, entity in all_key_entities:
                name_key = (entity.name.lower(), entity.type)  ***REMOVED*** 使用(名称, 类型)作为key
                if name_key not in key_entities_by_name:
                    key_entities_by_name[name_key] = []
                key_entities_by_name[name_key].append((score, entity))
            
            ***REMOVED*** 对每组同名关键实体，只保留最重要的一个
            deduplicated_key_entities = []
            for name_key, same_name_entities in key_entities_by_name.items():
                if len(same_name_entities) == 1:
                    deduplicated_key_entities.append(same_name_entities[0])
                else:
                    ***REMOVED*** 选择最重要的：优先级 = 最近出现章节 > 重要性分数
                    best = max(
                        same_name_entities,
                        key=lambda x: (
                            x[1].metadata.get('last_appearance_chapter', x[1].metadata.get('chapter', 0)),
                            x[0]  ***REMOVED*** 重要性分数
                        )
                    )
                    deduplicated_key_entities.append(best)
            
            ***REMOVED*** 按重要性排序，选择前10个
            deduplicated_key_entities.sort(key=lambda x: x[0], reverse=True)
            core_entities = [entity for score, entity in deduplicated_key_entities[:10]]
            
            ***REMOVED*** 统计核心实体中各类型的数量（用于配额调整）
            core_entities_by_type = {
                EntityType.CHARACTER: [e for e in core_entities if e.type == EntityType.CHARACTER],
                EntityType.SETTING: [e for e in core_entities if e.type == EntityType.SETTING],
                EntityType.SYMBOL: [e for e in core_entities if e.type == EntityType.SYMBOL],
                EntityType.PLOT_POINT: [e for e in core_entities if e.type == EntityType.PLOT_POINT]
            }
            
            ***REMOVED*** 2. 按类型分组候选实体（排除核心实体）
            remaining_entity_scores = [
                (score, entity) for score, entity in entity_scores
                if entity not in core_entities
            ]
            
            ***REMOVED*** 按类型分组
            entities_by_type_candidates = {
                EntityType.CHARACTER: [],
                EntityType.SETTING: [],
                EntityType.SYMBOL: [],
                EntityType.PLOT_POINT: []
            }
            
            for score, entity in remaining_entity_scores:
                entity_type = entity.type
                if entity_type in entities_by_type_candidates:
                    entities_by_type_candidates[entity_type].append((score, entity))
            
            ***REMOVED*** 3. 按类型设置最小配额（确保类型多样性）
            ***REMOVED*** 总配额 = max_entities - 核心实体数
            remaining_slots = max_entities - len(core_entities)
            
            ***REMOVED*** 类型配额分配策略（扩充到64后，给各类型更多空间）：
            ***REMOVED*** - 角色：35%（因为核心实体中可能已有较多角色）
            ***REMOVED*** - 地点/设定：35%（重要场景需要保持一致性，提高配额）
            ***REMOVED*** - 物品/符号：25%（重要物品需要保持一致性，提高配额）
            ***REMOVED*** - 情节节点：5%（辅助信息）
            ***REMOVED*** 同时确保每种类型至少有最低配额，即使核心实体已经包含该类型
            type_quotas = {
                EntityType.CHARACTER: max(8, int(remaining_slots * 0.35)),   ***REMOVED*** 至少8个
                EntityType.SETTING: max(5, int(remaining_slots * 0.35)),     ***REMOVED*** 至少5个
                EntityType.SYMBOL: max(4, int(remaining_slots * 0.25)),      ***REMOVED*** 至少4个
                EntityType.PLOT_POINT: max(2, int(remaining_slots * 0.05))   ***REMOVED*** 至少2个
            }
            
            ***REMOVED*** 从每种类型中选择实体（按重要性排序）
            selected_entities = list(core_entities)  ***REMOVED*** 先加入核心实体
            
            for entity_type, quota in type_quotas.items():
                type_entities = entities_by_type_candidates.get(entity_type, [])
                ***REMOVED*** 按重要性排序
                type_entities.sort(key=lambda x: x[0], reverse=True)
                ***REMOVED*** 选择前quota个（但不超过实际可用数量）
                selected_entities.extend([entity for score, entity in type_entities[:quota]])
            
            ***REMOVED*** 如果还有剩余配额，按重要性补充（优先补充非角色类型）
            current_count = len(selected_entities)
            if current_count < max_entities:
                remaining_quota = max_entities - current_count
                ***REMOVED*** 从剩余实体中按重要性选择，但优先选择非角色类型
                remaining_candidates = [
                    (score, entity) for score, entity in remaining_entity_scores
                    if entity not in selected_entities
                ]
                ***REMOVED*** 按类型优先级排序：SETTING > SYMBOL > PLOT_POINT > CHARACTER
                type_priority = {
                    EntityType.SETTING: 3,
                    EntityType.SYMBOL: 2,
                    EntityType.PLOT_POINT: 1,
                    EntityType.CHARACTER: 0
                }
                remaining_candidates.sort(
                    key=lambda x: (type_priority.get(x[1].type, 0), x[0]),
                    reverse=True
                )
                selected_entities.extend([entity for score, entity in remaining_candidates[:remaining_quota]])
            
            if not selected_entities:
                return ""
            
            ***REMOVED*** 按类型分组
            entities_by_type = {
                EntityType.CHARACTER: [],
                EntityType.SETTING: [],
                EntityType.SYMBOL: [],
                EntityType.PLOT_POINT: []
            }
            
            for entity in selected_entities:
                entity_type = entity.type
                if entity_type in entities_by_type:
                    entities_by_type[entity_type].append(entity)
            
            ***REMOVED*** 对同名实体进行去重（保留最重要的一个）
            ***REMOVED*** 策略：对于同名同类型的实体，只保留重要性最高或最近出现的
            ***REMOVED*** 去重后节省的配额可以用来选择更多不同的实体
            total_before_dedup = sum(len(entities) for entities in entities_by_type.values())
            saved_quota = 0
            
            for entity_type in entities_by_type:
                entities = entities_by_type[entity_type]
                if not entities:
                    continue
                
                ***REMOVED*** 按名称分组
                entities_by_name = {}
                for entity in entities:
                    name_key = entity.name.lower()  ***REMOVED*** 使用小写名称作为key
                    if name_key not in entities_by_name:
                        entities_by_name[name_key] = []
                    entities_by_name[name_key].append(entity)
                
                ***REMOVED*** 对每组同名实体，只保留最重要的一个
                deduplicated_entities = []
                for name_key, same_name_entities in entities_by_name.items():
                    if len(same_name_entities) == 1:
                        ***REMOVED*** 只有一个，直接保留
                        deduplicated_entities.append(same_name_entities[0])
                    else:
                        ***REMOVED*** 多个同名实体，选择最重要的
                        ***REMOVED*** 优先级：1. 关键实体 2. 最近出现的章节 3. 重要性分数
                        best_entity = max(
                            same_name_entities,
                            key=lambda e: (
                                1 if e.metadata.get('is_key', False) else 0,  ***REMOVED*** 关键实体优先
                                e.metadata.get('last_appearance_chapter', e.metadata.get('chapter', 0)),  ***REMOVED*** 最近出现优先
                                self._calculate_entity_importance(e, chapter_number)  ***REMOVED*** 重要性分数
                            )
                        )
                        deduplicated_entities.append(best_entity)
                        
                        ***REMOVED*** 计算节省的配额
                        saved_quota += len(same_name_entities) - 1
                        
                        ***REMOVED*** 记录合并信息（用于调试）
                        if len(same_name_entities) > 3:  ***REMOVED*** 只记录重复较多的
                            chapters = sorted([e.metadata.get('chapter', 0) for e in same_name_entities])
                            logger.debug(
                                f"第{chapter_number}章：合并同名实体 '{best_entity.name}' "
                                f"（{len(same_name_entities)}个，来自第{min(chapters)}-{max(chapters)}章，节省{len(same_name_entities)-1}个配额）"
                            )
                
                entities_by_type[entity_type] = deduplicated_entities
            
            ***REMOVED*** 去重后，如果节省了配额，用这些配额选择更多不同的实体
            total_after_dedup = sum(len(entities) for entities in entities_by_type.values())
            if saved_quota > 0 and total_after_dedup < max_entities:
                ***REMOVED*** 计算可用配额
                available_quota = max_entities - total_after_dedup
                logger.debug(
                    f"第{chapter_number}章：去重节省了{saved_quota}个配额，"
                    f"当前使用{total_after_dedup}个，可用配额{available_quota}个"
                )
                
                ***REMOVED*** 从剩余候选实体中选择更多（优先选择非角色类型）
                remaining_candidates = [
                    (score, entity) for score, entity in remaining_entity_scores
                    if entity not in [e for entities in entities_by_type.values() for e in entities]
                ]
                
                if remaining_candidates:
                    ***REMOVED*** 按类型优先级排序：SETTING > SYMBOL > PLOT_POINT > CHARACTER
                    type_priority = {
                        EntityType.SETTING: 3,
                        EntityType.SYMBOL: 2,
                        EntityType.PLOT_POINT: 1,
                        EntityType.CHARACTER: 0
                    }
                    remaining_candidates.sort(
                        key=lambda x: (type_priority.get(x[1].type, 0), x[0]),
                        reverse=True
                    )
                    
                    ***REMOVED*** 选择更多实体，但确保不超过max_entities
                    additional_entities = []
                    for score, entity in remaining_candidates:
                        if len(additional_entities) >= available_quota:
                            break
                        ***REMOVED*** 检查是否与已选实体同名（避免再次重复）
                        name_key = entity.name.lower()
                        entity_type = entity.type
                        existing_names = {e.name.lower() for e in entities_by_type[entity_type]}
                        if name_key not in existing_names:
                            additional_entities.append(entity)
                            entities_by_type[entity_type].append(entity)
                    
                    if additional_entities:
                        logger.debug(
                            f"第{chapter_number}章：利用节省的配额，额外选择了{len(additional_entities)}个不同实体"
                        )
            
            ***REMOVED*** 格式化输出
            lines = []
            type_names = {
                EntityType.CHARACTER: "角色",
                EntityType.SETTING: "地点/设定",
                EntityType.SYMBOL: "物品/符号",
                EntityType.PLOT_POINT: "情节节点"
            }
            
            for entity_type, entities in entities_by_type.items():
                if entities:
                    type_name = type_names.get(entity_type, entity_type.value)
                    lines.append(f"{type_name}:")
                    
                    ***REMOVED*** 按重要性排序（核心实体优先）
                    sorted_entities = sorted(
                        entities,
                        key=lambda e: (
                            0 if e.metadata.get('is_key', False) else 1,  ***REMOVED*** 关键实体优先
                            -self._calculate_entity_importance(e, chapter_number)  ***REMOVED*** 然后按重要性
                        )
                    )
                    
                    for entity in sorted_entities:
                        entity_chapter = entity.metadata.get('chapter', 0)
                        ***REMOVED*** 如果有last_appearance_chapter，显示最近出现的章节
                        last_chapter = entity.metadata.get('last_appearance_chapter', entity_chapter)
                        if last_chapter > entity_chapter:
                            chapter_info = f"（第{entity_chapter}章首次，最近第{last_chapter}章）"
                        else:
                            chapter_info = f"（第{entity_chapter}章）" if entity_chapter > 0 else ""
                        content_preview = entity.content[:80] if entity.content else "无描述"
                        key_marker = "【关键】" if entity.metadata.get('is_key', False) else ""
                        lines.append(f"  - {entity.name}{key_marker}{chapter_info}: {content_preview}")
                    
                    lines.append("")
            
            result = "\n".join(lines)
            
            ***REMOVED*** 记录筛选统计（按类型统计）
            type_counts = {
                EntityType.CHARACTER: sum(1 for e in selected_entities if e.type == EntityType.CHARACTER),
                EntityType.SETTING: sum(1 for e in selected_entities if e.type == EntityType.SETTING),
                EntityType.SYMBOL: sum(1 for e in selected_entities if e.type == EntityType.SYMBOL),
                EntityType.PLOT_POINT: sum(1 for e in selected_entities if e.type == EntityType.PLOT_POINT)
            }
            logger.debug(
                f"实体筛选：第{chapter_number}章，候选实体 {len(candidate_entities)} 个，"
                f"选中 {len(selected_entities)} 个（核心 {len(core_entities)} 个，"
                f"角色 {type_counts[EntityType.CHARACTER]} 个，地点 {type_counts[EntityType.SETTING]} 个，"
                f"物品 {type_counts[EntityType.SYMBOL]} 个，情节 {type_counts[EntityType.PLOT_POINT]} 个）"
            )
            
            return result
            
        except Exception as e:
            logger.warning(f"检索前面章节实体失败: {e}")
            return ""