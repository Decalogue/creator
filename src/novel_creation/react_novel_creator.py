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
from collections import defaultdict
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
            "target_chapters": 0,  ***REMOVED*** 目标章节数（用于节奏控制）
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
            },
            "issue_patterns": {  ***REMOVED*** Phase 6: 问题模式追踪
                "common_issues": {},  ***REMOVED*** 常见问题类型统计
                "issue_frequency": {},  ***REMOVED*** 问题频率统计
                "prevention_success": {}  ***REMOVED*** 预防成功记录
            },
            "long_term_coherence": {  ***REMOVED*** Phase 7: 长期连贯性追踪
                "character_profiles": {},  ***REMOVED*** 人物档案
                "worldview_profiles": {},  ***REMOVED*** 世界观档案
                "coherence_reports": [],  ***REMOVED*** 连贯性报告
                "key_node_reviews": []  ***REMOVED*** 关键节点回顾
            }
        }
        
        ***REMOVED*** 修复策略库和验证器（Phase 1: 改进重写机制）
        try:
            from novel_creation.fix_strategy_library import FixStrategyLibrary
            from novel_creation.fix_validator import FixValidator
            from novel_creation.fix_outcome_predictor import FixOutcomePredictor
            self.fix_strategy_library = FixStrategyLibrary()
            self.fix_validator = FixValidator()
            self.fix_outcome_predictor = FixOutcomePredictor(self.fix_strategy_library)
            logger.info("修复策略库、验证器和预测器已启用（Phase 1 & 2）")
        except ImportError as e:
            logger.warning(f"无法导入修复策略库、验证器或预测器: {e}")
            self.fix_strategy_library = None
            self.fix_validator = None
            self.fix_outcome_predictor = None
        
        ***REMOVED*** 增强实体提取器（支持多模型投票）
        self.entity_extractor = None
        self.enable_enhanced_extraction = enable_enhanced_extraction
        ***REMOVED*** 控制是否只使用单模型（kimi_k2），不启用多模型投票
        ***REMOVED*** 通过环境变量控制：如果设置 USE_SINGLE_MODEL_EXTRACTION=1，则只使用 kimi_k2
        use_single_model_only = False
        import os
        if os.getenv("USE_SINGLE_MODEL_EXTRACTION", "0") == "1":
            use_single_model_only = True
            logger.info("检测到 USE_SINGLE_MODEL_EXTRACTION=1，将只使用 kimi_k2 进行实体提取")
        
        if enable_enhanced_extraction:
            try:
                ***REMOVED*** 如果设置了只使用单模型，直接使用 kimi_k2
                if use_single_model_only:
                    from novel_creation.enhanced_entity_extractor import EnhancedEntityExtractor
                    from llm.chat import kimi_k2
                    self.entity_extractor = EnhancedEntityExtractor(
                        llm_client=kimi_k2,
                        use_ner=False
                    )
                    logger.info("增强实体提取器已启用（仅使用 Kimi K2 模型）")
                else:
                    ***REMOVED*** 尝试使用多模型投票提取器（更准确）
                    try:
                        from novel_creation.multi_model_entity_extractor import MultiModelEntityExtractor
                        from llm.chat import kimi_k2, deepseek_v3_2
                        
                        ***REMOVED*** 使用 Kimi K2 和 DeepSeek V3.2 进行投票（推荐配置：Kimi 实体提取最强，DeepSeek 作为验证）
                        ***REMOVED*** 优先保留 Kimi 的所有结果，DeepSeek 作为补充
                        llm_clients = [kimi_k2, deepseek_v3_2]
                        self.entity_extractor = MultiModelEntityExtractor(
                            llm_clients=llm_clients,
                            vote_threshold=2,  ***REMOVED*** 投票阈值（但主模型结果优先保留）
                            use_ner=False,
                            primary_model_index=0  ***REMOVED*** Kimi K2 作为主模型（索引0），优先保留其所有结果
                        )
                        logger.info(f"多模型投票实体提取器已启用（{len(llm_clients)} 个模型：Kimi K2 + DeepSeek V3.2）")
                    except (ImportError, Exception) as e:
                        logger.debug(f"多模型提取器初始化失败，回退到单模型: {e}")
                        ***REMOVED*** 回退到单模型提取器
                        from novel_creation.enhanced_entity_extractor import EnhancedEntityExtractor
                        try:
                            from llm.chat import kimi_k2
                            llm_client = kimi_k2
                            logger.info("增强实体提取器已启用（使用 Kimi K2 模型）")
                        except ImportError:
                            from llm.chat import deepseek_v3_2
                            llm_client = deepseek_v3_2
                            logger.info("增强实体提取器已启用（使用 DeepSeek V3.2 模型）")
                        
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
        use_progressive: Optional[bool] = None,  ***REMOVED*** None = 自动选择（章节数 >= 50 时使用渐进式）
        previous_volume_context: Optional[Dict[str, Any]] = None,
        start_chapter: int = 1,
    ) -> Dict[str, Any]:
        """
        创建小说大纲
        
        支持两种模式：
        1. 一次性生成（适合 <= 30 章）
        2. 渐进式生成（适合 > 30 章，特别是 100 章）
        
        若提供 previous_volume_context，则生成接续前卷的本卷大纲（章节号从 start_chapter 起）。
        
        Args:
            genre: 小说类型
            theme: 主题
            target_chapters: 目标章节数
            words_per_chapter: 每章目标字数
            use_progressive: 是否使用渐进式
            previous_volume_context: 前卷接续上下文（含 background、characters、last_chapters_outline 等）
            start_chapter: 本卷起始章节号（如 101 表示第二卷从第 101 章起）
        
        Returns:
            小说大纲
        """
        if use_progressive is None:
            use_progressive = target_chapters >= 50
        
        if use_progressive:
            logger.info(f"使用渐进式大纲生成（适合 {target_chapters} 章长篇小说）")
            return self._create_novel_plan_progressive(
                genre, theme, target_chapters, words_per_chapter,
                previous_volume_context=previous_volume_context,
                start_chapter=start_chapter,
            )
        else:
            logger.info(f"使用一次性大纲生成（适合 {target_chapters} 章中短篇小说）")
            return self._create_novel_plan_onetime(
                genre, theme, target_chapters, words_per_chapter,
                previous_volume_context=previous_volume_context,
                start_chapter=start_chapter,
            )

    def _deduplicate_chapter_titles(self, chapter_outline: list) -> list:
        """
        保证章节标题在一部作品内不重复。对重复标题追加（二）（三）等后缀。
        """
        if not chapter_outline:
            return chapter_outline
        _SUFFIX = ("", "（二）", "（三）", "（四）", "（五）", "（六）", "（七）", "（八）", "（九）", "（十）")
        seen: Dict[str, int] = {}
        out = []
        for ch in chapter_outline:
            if not isinstance(ch, dict):
                out.append(ch)
                continue
            raw_title = (ch.get("title") or "").strip() or f"第{ch.get('chapter_number', len(out)+1)}章"
            count = seen.get(raw_title, 0) + 1
            seen[raw_title] = count
            if count > 1:
                suffix = _SUFFIX[count] if count < len(_SUFFIX) else f"（{count}）"
                title = raw_title + suffix
                ch = {**ch, "title": title}
            out.append(ch)
        return out

    def _create_novel_plan_onetime(
        self,
        genre: str,
        theme: str,
        target_chapters: int,
        words_per_chapter: int,
        previous_volume_context: Optional[Dict[str, Any]] = None,
        start_chapter: int = 1,
    ) -> Dict[str, Any]:
        """
        一次性生成小说大纲。支持接续前卷（previous_volume_context + start_chapter）。
        """
        continuation_block = ""
        if previous_volume_context:
            prev_id = previous_volume_context.get("previous_project_id", "前卷")
            continuation_block = f"""
**【接续前卷】本卷为《{self.novel_title}》，接续前卷「{prev_id}」。请严格延续前卷设定与剧情，章节号从第 {start_chapter} 章开始。**

前卷接续信息（必须沿用并在此基础上发展）：
- 背景设定：{previous_volume_context.get("background", "")[:800]}
- 主要角色：{json.dumps(previous_volume_context.get("characters", [])[:15], ensure_ascii=False)[:1200]}
- 故事主线：{previous_volume_context.get("main_plot", "")[:600]}
- 前卷结尾方向/未解决伏笔：{previous_volume_context.get("ending_direction", "")[:500]}
- 最后几章大纲摘要：{previous_volume_context.get("last_chapters_outline", "")[:1000]}
- 前卷结尾正文片段（当前状态）：{previous_volume_context.get("end_state_snippets", "")[:800]}
{("- " + previous_volume_context.get("semantic_mesh_summary", "")) if previous_volume_context.get("semantic_mesh_summary") else ""}

要求：本卷大纲的 chapter_number 必须从 {start_chapter} 连续到 {start_chapter + target_chapters - 1}，且情节、人物、世界观与前卷无缝衔接。
"""
        prompt = f"""请为小说《{self.novel_title}》创建详细的大纲（一次性生成所有章节）。{continuation_block}

小说信息：
- 类型：{genre}
- 主题：{theme}
- 目标章节数：{target_chapters}
- 每章目标字数：{words_per_chapter}
- 本卷章节号范围：第 {start_chapter} 章 至 第 {start_chapter + target_chapters - 1} 章

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

重要提示：
1. 这是一个创作任务，请直接生成内容，不需要搜索工具或调用任何函数
2. **必须只返回 JSON 格式**，不要包含任何代码、解释或其他内容
3. JSON 格式要求：
   - 所有字符串使用英文双引号
   - 不要包含注释
   - 确保 JSON 完整且有效

示例格式：
{{
  "background": "背景设定描述",
  "characters": [
    {{"name": "角色名", "description": "角色描述"}}
  ],
  "chapter_outline": [
    {{"chapter_number": 1, "title": "第一章标题", "summary": "章节摘要"}}
  ],
  "main_plot": "故事主线",
  "key_plot_points": ["关键情节1", "关键情节2"]
}}

请严格按照上述 JSON 格式返回，不要添加任何其他内容。
"""
        
        ***REMOVED*** 使用 ReActAgent 生成大纲（限制迭代次数，避免工具搜索循环）
        original_max_iterations = self.agent.max_iterations
        self.agent.max_iterations = 3  ***REMOVED*** 减少迭代次数，强制直接生成JSON
        try:
            result = self.agent.run(query=prompt, verbose=False)  ***REMOVED*** 关闭详细输出以加快速度
        finally:
            self.agent.max_iterations = original_max_iterations  ***REMOVED*** 恢复原始值
        
        ***REMOVED*** 尝试解析 JSON（增强容错能力）
        plan = None
        json_str = None
        
        try:
            ***REMOVED*** 提取 JSON 部分（优先查找JSON代码块）
            json_str = None
            
            ***REMOVED*** 首先查找 ```json 代码块
            if "```json" in result:
                json_start = result.find("```json") + 7
                json_end = result.find("```", json_start)
                if json_end == -1:
                    json_end = len(result)
                json_str = result[json_start:json_end].strip()
            ***REMOVED*** 然后查找普通 ``` 代码块
            elif "```" in result:
                json_start = result.find("```") + 3
                json_end = result.find("```", json_start)
                if json_end == -1:
                    json_end = len(result)
                json_str = result[json_start:json_end].strip()
                ***REMOVED*** 检查是否真的是JSON（包含 { 和 }）
                if "{" not in json_str or "}" not in json_str:
                    json_str = None
            
            ***REMOVED*** 如果代码块中不是JSON，查找独立的JSON对象
            if not json_str or "{" not in json_str:
                ***REMOVED*** 查找第一个 { 到最后一个 }
                if "{" in result and "}" in result:
                    json_start = result.find("{")
                    json_end = result.rfind("}") + 1
                    candidate = result[json_start:json_end].strip()
                    ***REMOVED*** 验证是否看起来像JSON（不以public class等开头）
                    if not candidate.lower().startswith(("public", "class", "def ", "import", "package")):
                        json_str = candidate
                else:
                    json_str = result.strip()
            
            ***REMOVED*** 如果还是没有有效的JSON，尝试查找第一个有效的JSON对象
            if not json_str or not ("{" in json_str and "}" in json_str):
                ***REMOVED*** 查找可能的JSON对象
                json_matches = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', result)
                if json_matches:
                    ***REMOVED*** 使用最长的匹配作为候选
                    json_str = max(json_matches, key=len)
            
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
            except Exception as e:
                logger.debug(f"保存调试文件失败: {e}")
            
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
                        {"chapter_number": start_chapter + i, "title": f"第{start_chapter + i}章", "summary": "待创作"}
                        for i in range(target_chapters)
                    ],
                    "main_plot": "待完善",
                    "key_plot_points": [],
                    "start_chapter": start_chapter,
                }
        except Exception as e:
            logger.error(f"解析大纲时发生未知错误: {e}", exc_info=True)
            ***REMOVED*** 创建基本结构
            plan = {
                "background": "待完善",
                "characters": [],
                "chapter_outline": [
                    {"chapter_number": start_chapter + i, "title": f"第{start_chapter + i}章", "summary": "待创作"}
                    for i in range(target_chapters)
                ],
                "main_plot": "待完善",
                "key_plot_points": [],
                "start_chapter": start_chapter,
            }
        
        ***REMOVED*** 接续前卷时：章节号从 start_chapter 起
        if start_chapter > 1 and plan.get("chapter_outline") and isinstance(plan["chapter_outline"], list):
            for ch in plan["chapter_outline"]:
                if isinstance(ch, dict) and "chapter_number" in ch:
                    ch["chapter_number"] = ch.get("chapter_number", 0) + (start_chapter - 1)
        if previous_volume_context:
            plan["previous_project_id"] = previous_volume_context.get("previous_project_id", "")
        plan["start_chapter"] = start_chapter
        ***REMOVED*** 保证章节标题不重复后再保存
        if plan.get("chapter_outline") and isinstance(plan["chapter_outline"], list):
            plan["chapter_outline"] = self._deduplicate_chapter_titles(plan["chapter_outline"])
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
        phase_size: int = 20,
        previous_volume_context: Optional[Dict[str, Any]] = None,
        start_chapter: int = 1,
    ) -> Dict[str, Any]:
        """
        渐进式生成小说大纲。支持接续前卷（previous_volume_context + start_chapter）。
        """
        logger.info("Stage 1: 生成整体大纲...")
        overall_outline = self._generate_overall_outline(
            genre, theme, target_chapters, words_per_chapter,
            previous_volume_context=previous_volume_context,
            start_chapter=start_chapter,
        )
        
        logger.info("Stage 2: 生成第一阶段详细大纲...")
        phase_1_outline = self._generate_phase_outline(
            phase_number=1,
            phase_size=phase_size,
            overall_outline=overall_outline,
            previous_phases=[],
            genre=genre,
            theme=theme,
            words_per_chapter=words_per_chapter,
            volume_start_chapter=start_chapter,
            target_chapters_total=target_chapters,
        )
        
        phase_1_chapters = self._deduplicate_chapter_titles(phase_1_outline.get("chapters", []))
        plan = {
            "plan_type": "progressive",
            "phase_size": phase_size,
            "overall": overall_outline,
            "phases": [phase_1_outline],
            "current_phase": 1,
            "chapter_outline": phase_1_chapters,
            "background": overall_outline.get("background", ""),
            "characters": overall_outline.get("characters", []),
            "main_plot": overall_outline.get("main_plot", ""),
            "key_plot_points": overall_outline.get("key_plot_points", []),
            "target_chapters": target_chapters,
            "start_chapter": start_chapter,
        }
        if previous_volume_context:
            plan["previous_project_id"] = previous_volume_context.get("previous_project_id", "")
        
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
        words_per_chapter: int,
        previous_volume_context: Optional[Dict[str, Any]] = None,
        start_chapter: int = 1,
    ) -> Dict[str, Any]:
        """
        生成整体大纲（粗略规划）。支持接续前卷时注入前卷信息。
        """
        num_phases = (target_chapters + 19) // 20
        continuation_block = ""
        if previous_volume_context:
            prev_id = previous_volume_context.get("previous_project_id", "前卷")
            continuation_block = f"""
**【接续前卷】本卷《{self.novel_title}》接续前卷「{prev_id}」，章节从第 {start_chapter} 章开始。请严格延续前卷设定与主线，在此基础上规划本卷 {target_chapters} 章的整体发展。**

前卷接续信息：
- 背景：{previous_volume_context.get("background", "")[:600]}
- 主要角色：{json.dumps(previous_volume_context.get("characters", [])[:12], ensure_ascii=False)[:800]}
- 主线：{previous_volume_context.get("main_plot", "")[:500]}
- 结尾方向/未解决伏笔：{previous_volume_context.get("ending_direction", "")[:400]}
- 最后几章摘要：{previous_volume_context.get("last_chapters_outline", "")[:600]}
"""
        prompt = f"""请为小说《{self.novel_title}》创建整体大纲（粗略规划）。{continuation_block}

小说信息：
- 类型：{genre}
- 主题：{theme}
- 目标章节数：{target_chapters}
- 每章目标字数：{words_per_chapter}
- 本卷章节号：第 {start_chapter} 章 至 第 {start_chapter + target_chapters - 1} 章

请提供：
1. **故事背景设定**：世界观、时代背景、主要设定
2. **主要角色介绍**：**重要：需要8-12个主要角色**，包括：
   - 主角（1-2个）：核心人物，推动主线
   - 重要配角（3-4个）：与主角有深度互动，推动关键情节
   - 反派/对立角色（2-3个）：制造冲突和张力
   - 辅助角色（2-3个）：提供信息、制造转折、丰富情节
   - 每个角色需要：name（姓名）、role（角色定位）、description（性格、背景、动机）
   - **人物关系要复杂**：有合作、对立、背叛、联盟等多种关系
   - **人物要有成长弧线**：角色在故事中会发生变化
3. **故事主线**：整个故事的 {num_phases} 个主要阶段，每个阶段的核心目标
4. **关键情节节点**：每20章一个关键转折点（共 {num_phases} 个转折点）
5. **结局方向**：**重要：这是第一部，结局必须留有悬念，不要圆满的大结局**
   - 结局应该设置悬念、疑问或未解决的危机
   - 可以是新的威胁出现、关键谜题未解、角色命运未定等
   - 为后续章节留下伏笔和期待
   - 避免所有问题都得到解决、所有角色都获得圆满结局

重点：这是整体规划，不需要详细到每章，只需要主要阶段和关键转折点。
每个阶段的描述应该简洁（50-100字），但能体现该阶段的核心冲突和发展方向。

请以 JSON 格式返回，包含以下字段：
- background: 背景设定
- characters: 主要角色列表（**必须8-12个角色**，每个角色包含 name, role, description）
  - role字段说明：主角/重要配角/反派/辅助角色
  - description字段应包含：性格特点、背景故事、动机目标、与其他角色的关系
- main_plot: 故事主线（{num_phases}个阶段的描述）
- key_plot_points: 关键情节节点列表（每个节点包含 phase_number, chapter_range, description）
- ending_direction: 结局方向（**必须包含悬念，不要圆满结局**）

**人物设计要求**：
- 人物数量：8-12个主要角色（不能少于8个）
- 人物关系：要有复杂的网络关系，包括盟友、敌人、背叛者、隐藏身份等
- 人物成长：每个主要角色都要有明确的成长弧线或变化轨迹
- 人物功能：不同角色承担不同功能（推动情节、制造冲突、提供信息、制造转折等）

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
    
    def _try_parse_phase_outline_json(self, json_str: str) -> Tuple[Optional[Dict[str, Any]], Optional[Exception]]:
        """解析阶段大纲 JSON，尝试修复常见 LLM 输出问题（如尾部逗号）。成功返回 (dict, None)，失败返回 (None, error)。"""
        err = None
        try:
            return json.loads(json_str), None
        except json.JSONDecodeError as e:
            err = e
        
        repaired = re.sub(r',\s*([}\]])', r'\1', json_str)
        try:
            return json.loads(repaired), None
        except json.JSONDecodeError as e2:
            err = e2
        return None, err
    
    def _generate_phase_outline(
        self,
        phase_number: int,
        phase_size: int,
        overall_outline: Dict[str, Any],
        previous_phases: List[Dict[str, Any]],
        genre: str,
        theme: str,
        words_per_chapter: int,
        volume_start_chapter: int = 1,
        target_chapters_total: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        生成阶段详细大纲。支持多卷：volume_start_chapter 为本卷起始章（如 101），
        target_chapters_total 为本卷总章数，则阶段章节号为 101-120、121-140 等。
        """
        if target_chapters_total is None:
            target_chapters_total = overall_outline.get('target_chapters', phase_number * phase_size)
        start_chapter = volume_start_chapter + (phase_number - 1) * phase_size
        end_chapter = min(volume_start_chapter + phase_number * phase_size - 1, volume_start_chapter + target_chapters_total - 1)
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
        
        ***REMOVED*** 判断是否是最后一个阶段（需要悬念结局）
        is_final_phase = False
        if end_chapter >= volume_start_chapter + target_chapters_total - phase_size // 2:
            is_final_phase = True
        
        ending_note = ""
        if is_final_phase:
            ending_note = """
**重要：这是第一部的最后阶段，结局必须留有悬念！**
- 最后几章（特别是第95-100章）应该设置悬念、疑问或未解决的危机
- 可以是新的威胁出现、关键谜题未解、角色命运未定、更大的阴谋浮出水面等
- 为后续章节（第二部）留下伏笔和期待
- 避免所有问题都得到解决、所有角色都获得圆满结局
- 结局应该让读者产生"接下来会发生什么？"的疑问
"""
        
        prompt = f"""请为小说《{self.novel_title}》的第{start_chapter}-{end_chapter}章创建详细大纲。

整体大纲：
{json.dumps(overall_outline, ensure_ascii=False, indent=2)}{previous_phases_summary}

阶段信息：
- 阶段编号：{phase_number}
- 章节范围：第{start_chapter}-{end_chapter}章（共 {num_chapters} 章）
- 该阶段的核心目标：{phase_target}
{ending_note}

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
{ending_note if is_final_phase else ""}

请以 JSON 格式返回，包含以下字段：
- phase_number: 阶段编号
- summary: 该阶段的核心发展（200-300字）
- key_events: 该阶段的关键事件列表（字符串数组）
- chapters: 章节大纲列表（每项包含 chapter_number, title, summary, key_entities；key_entities 为字符串数组）

**JSON 格式要求（必须严格遵守）**：
- 只输出一个合法的 JSON 对象，不要用 markdown 代码块包裹，不要任何前后说明
- 禁止尾部逗号（如 ] 或 }} 前的多余逗号）
- 字符串内换行用 \\n，引号须转义

重要提示：这是创作任务，请直接生成 JSON，不需要搜索或调用工具。
"""
        json_only_reminder = "\n\n【重试】请仅输出上述 JSON 对象，不要 ``` 包裹、不要注释、不要尾部逗号。"
        
        def run_and_parse(retry_with_reminder: bool = False) -> Tuple[Optional[Dict[str, Any]], str]:
            """返回 (解析结果或 None, 原始 JSON 串)"""
            q = prompt + (json_only_reminder if retry_with_reminder else "")
            orig = self.agent.max_iterations
            self.agent.max_iterations = 5
            try:
                result = self.agent.run(query=q, verbose=False)
            finally:
                self.agent.max_iterations = orig
            
            if "```json" in result:
                js = result.find("```json") + 7
                je = result.find("```", js)
                json_str = result[js:je].strip() if je > js else result.strip()
            elif "{" in result:
                js = result.find("{")
                je = result.rfind("}") + 1
                json_str = result[js:je] if je > js else result
            else:
                json_str = result.strip()
            
            parsed, err = self._try_parse_phase_outline_json(json_str)
            if parsed is not None:
                if 'chapters' in parsed:
                    for i, ch in enumerate(parsed['chapters']):
                        ch['chapter_number'] = start_chapter + i
                return parsed, json_str
            
            pos = getattr(err, 'pos', None) if err else None
            if pos is not None and json_str:
                excerpt = json_str[max(0, pos - 80):pos + 80]
                logger.debug(f"阶段大纲 JSON 解析错误位置附近: ...{excerpt!r}...")
            logger.warning(f"解析阶段大纲 JSON 失败: {err}")
            return None, json_str
        
        phase_outline, last_raw = run_and_parse(retry_with_reminder=False)
        if phase_outline is None:
            logger.info("阶段大纲解析失败，重试一次（强调仅输出 JSON）...")
            phase_outline, last_raw = run_and_parse(retry_with_reminder=True)
        
        if phase_outline is None:
            logger.warning("阶段大纲解析与重试均失败，使用默认占位结构（每章「待创作」）")
            try:
                debug_path = self.output_dir / "phase_outline_raw_failed.txt"
                debug_path.write_text(last_raw or "", encoding="utf-8")
                logger.info(f"已保存 Stage 2 原始响应到 {debug_path} 便于排查")
            except Exception:
                pass
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
    
    def _determine_chapter_position(self, chapter_number: int, total_chapters: int) -> str:
        """
        确定章节在整个小说中的位置（Phase 5: 节奏优化）
        
        Args:
            chapter_number: 章节编号
            total_chapters: 总章节数
        
        Returns:
            位置类型：'opening'（开头，前25%）、'development'（发展，25%-75%）、
                     'climax'（高潮，75%-90%）、'ending'（结尾，后10%）
        """
        if total_chapters == 0:
            return 'development'  ***REMOVED*** 默认
        
        position_ratio = chapter_number / total_chapters
        
        if position_ratio <= 0.25:
            return 'opening'
        elif position_ratio <= 0.75:
            return 'development'
        elif position_ratio <= 0.90:
            return 'climax'
        else:
            return 'ending'
    
    def _get_rhythm_adjusted_target_words(
        self, 
        base_target_words: int, 
        chapter_position: str,
        recent_rhythm_data: Optional[List[float]] = None
    ) -> int:
        """
        根据章节位置和节奏历史数据调整目标字数（Phase 5: 节奏优化）
        
        Args:
            base_target_words: 基础目标字数
            chapter_position: 章节位置（'opening'/'development'/'climax'/'ending'）
            recent_rhythm_data: 最近章节的字数列表（用于节奏变化）
        
        Returns:
            调整后的目标字数
        """
        ***REMOVED*** 根据位置调整字数（±15%）
        position_adjustments = {
            'opening': 0.95,    ***REMOVED*** 开头章节稍短，快速进入
            'development': 1.0,  ***REMOVED*** 发展章节保持标准
            'climax': 1.15,     ***REMOVED*** 高潮章节允许更长
            'ending': 0.90      ***REMOVED*** 结尾章节稍短，简洁收尾
        }
        
        adjusted_words = int(base_target_words * position_adjustments.get(chapter_position, 1.0))
        
        ***REMOVED*** 根据历史节奏数据进一步调整（避免连续相同长度）
        if recent_rhythm_data and len(recent_rhythm_data) >= 2:
            avg_recent = sum(recent_rhythm_data[-3:]) / len(recent_rhythm_data[-3:])
            ***REMOVED*** 如果最近章节长度变化很小（<5%），增加变化
            if abs(avg_recent - base_target_words) / base_target_words < 0.05:
                ***REMOVED*** 根据位置增加变化
                if chapter_position == 'climax':
                    adjusted_words = int(adjusted_words * 1.10)  ***REMOVED*** 高潮章节更长
                elif chapter_position == 'ending':
                    adjusted_words = int(adjusted_words * 0.95)  ***REMOVED*** 结尾章节更短
        
        ***REMOVED*** 确保在合理范围内（基础字数的80%-120%）
        min_words = int(base_target_words * 0.8)
        max_words = int(base_target_words * 1.2)
        return max(min_words, min(max_words, adjusted_words))
    
    def _get_enhanced_rhythm_instruction(
        self,
        chapter_position: str,
        chapter_number: int,
        recent_rhythm_score: Optional[float] = None
    ) -> str:
        """
        生成增强的节奏控制提示词（Phase 5: 节奏优化）
        
        Args:
            chapter_position: 章节位置
            recent_rhythm_score: 最近的节奏得分（用于动态调整）
        
        Returns:
            增强的节奏控制提示词
        """
        ***REMOVED*** 基础节奏结构
        base_instruction = """
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
        
        ***REMOVED*** 根据章节位置添加特定指导
        position_specific = {
            'opening': f"""
**开头阶段节奏要求**（第{chapter_number}章位于小说开头部分）：
- **快速进入**：前200字内必须出现核心冲突或关键事件
- **节奏紧凑**：减少环境描写，优先使用对话和动作推进情节
- **建立悬念**：在开头就埋下吸引读者的钩子
- **人物登场**：快速引入主要角色，通过行动而非描述展现性格
""",
            'development': f"""
**发展阶段节奏要求**（第{chapter_number}章位于小说发展部分）：
- **节奏变化**：在快节奏和慢节奏之间交替，避免单调
- **情节推进**：每章必须有明确的情节进展，不能原地踏步
- **人物深化**：通过对话和心理描写深化人物形象
- **冲突升级**：逐步提升冲突强度，为高潮做准备
""",
            'climax': f"""
**高潮阶段节奏要求**（第{chapter_number}章位于小说高潮部分）：
- **节奏加快**：使用短句、快节奏的对话和动作描写
- **情绪冲击**：通过激烈的冲突和转折给读者带来情绪冲击
- **关键转折**：本章应包含重要的情节转折或关键发现
- **紧张感**：保持高紧张感，避免拖沓
""",
            'ending': f"""
**结尾阶段节奏要求**（第{chapter_number}章位于小说结尾部分）：
- **节奏收束**：逐步放缓节奏，为结局做准备
- **线索收拢**：开始收拢前面的伏笔和线索
- **情绪沉淀**：在紧张后适当加入情绪沉淀和反思
- **为结局铺垫**：为最终结局做好铺垫
"""
        }
        
        position_instruction = position_specific.get(chapter_position, "")
        
        ***REMOVED*** 根据历史节奏得分添加调整建议
        rhythm_adjustment = ""
        if recent_rhythm_score is not None and recent_rhythm_score < 0.7:
            rhythm_adjustment = f"""
⚠️ **节奏优化提醒**：
前续章节节奏得分较低（{recent_rhythm_score:.2f}），请特别注意：
1. **增加节奏变化**：确保章节长度有适当变化（±15%）
2. **对话占比**：确保对话占比在25-35%之间
3. **内容交替**：每200-300字必须切换内容类型（对话/动作/描写）
4. **避免单调**：不要连续多段都是相同类型的内容
"""
        
        return base_instruction + position_instruction + rhythm_adjustment
    
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
                else:
                    logger.debug(f"第{chapter_number}章：未检索到前面章节的实体信息")
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
        
        ***REMOVED*** 检查历史字数偏差，如果偏差>20%，添加惩罚机制
        word_control_strictness = ""
        quality_history = self.quality_tracker.get("chapter_quality_history", [])
        if len(quality_history) >= 3:
            recent_deviations = [
                m.get("word_diff_percent", 0) 
                for m in quality_history[-3:]
            ]
            avg_deviation = sum(recent_deviations) / len(recent_deviations) if recent_deviations else 0
            if avg_deviation > 20:
                word_control_strictness = f"""
⚠️ **字数控制紧急要求**：
前续章节字数偏差过大（平均偏差{avg_deviation:+.1f}%），必须严格控制字数！
- **严格执行**：字数必须控制在{target_range_min}-{target_range_max}字范围内
- **偏差惩罚**：如果超过{target_range_max}字，将强制截断，导致情节不完整
- **建议策略**：
  1. 在创作过程中定期估算字数
  2. 如果接近{target_range_max}字，立即停止添加新内容，简洁结尾
  3. 优先删除冗余的环境描写和重复的心理活动
  4. 保持对话占比在25-35%之间，通过对话推进情节而非增加描写
"""
        
        word_control_instruction = f"""
**字数控制原则（质量优先）**：
1. **核心原则**：**质量优先，字数控制是次要的**
   - 如果内容优质，字数可以适当浮动（±20%以内都可以接受）
   - 优先保证情节完整、人物生动、文笔流畅
   - 不要为了字数而牺牲内容质量

2. **字数目标**：
   - **理想字数**：{target_words} 字（目标范围：{target_range_min}-{target_range_max} 字）
   - **可接受范围**：如果内容优质，{int(target_words*0.8)}-{int(target_words*1.2)} 字都可以接受
   - **上限**：不超过 {max_words_allowed} 字（超过将被智能截断）

3. **字数控制技巧**（在保证质量的前提下）：
   - **如果内容优质但字数略多**：可以保留，优质内容比严格字数控制更重要
   - **如果内容优质但字数略少**：可以保留，不要为了凑字数而添加冗余内容
   - **如果字数明显过多（>{int(target_words*1.2)}字）**：在保持质量的前提下，适当精简：
     * 删除冗余的环境描写和重复的心理活动
     * 合并相似的描述，使用更简洁的表达
     * 精简对话，保留关键信息
   - **如果字数明显过少（<{int(target_words*0.8)}字）**：在保持质量的前提下，适当补充：
     * 增加必要的对话，推进情节和展现人物
     * 补充关键的动作描写和环境描写
     * 增加人物的心理活动和反应

4. **质量检查优先**：
   - 首先确保内容质量：情节完整、人物生动、对话自然、描写恰当
   - 然后考虑字数：在保证质量的前提下，尽量接近目标字数
   - **如果必须在质量和字数之间选择，优先选择质量**
"""
        
        ***REMOVED*** Phase 5: 增强的节奏控制提示（根据章节位置和历史节奏数据动态生成）
        ***REMOVED*** 确定章节位置
        total_chapters = self.metadata.get("target_chapters", 0)
        chapter_position = self._determine_chapter_position(chapter_number, total_chapters)
        
        ***REMOVED*** 获取最近的节奏得分
        recent_rhythm_score = None
        quality_history = self.quality_tracker.get("chapter_quality_history", [])
        if quality_history:
            ***REMOVED*** 从最近的阶段性质量检查中获取节奏得分
            periodic_checks = self.metadata.get("periodic_quality_checks", [])
            if periodic_checks:
                latest_check = periodic_checks[-1]
                recent_rhythm_score = latest_check.get("scores", {}).get("plot_rhythm")
        
        ***REMOVED*** 生成增强的节奏控制提示词
        rhythm_control_instruction = self._get_enhanced_rhythm_instruction(
            chapter_position,
            chapter_number,
            recent_rhythm_score
        )
        
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
3. **语言要求（重要）**：
   - **通俗易懂**：使用简单直白的语言，避免复杂科学术语和专业名词
   - **生活化表达**：即使涉及科技概念，也要用生活化的比喻和描述，让绝大多数人都能理解
   - **避免术语堆砌**：不要使用过多专业术语，如必须使用，要配合简单解释
   - **保证可读性**：语言要流畅自然，让读者看得爽，不要因为术语过多而影响阅读体验
4. {word_control_instruction.strip()}
5. {rhythm_control_instruction.strip()}
6. {dialogue_quality_instruction.strip()}
7. **章节结尾悬念要求（必须严格执行）**：
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
{self._get_ending_suspense_instruction(chapter_number, total_chapters)}
8. **一致性要求（必须）**：
   - **角色一致性**：角色名称、性格、外貌、说话方式必须与前面章节完全一致，参考前面章节的实体信息
   - **世界观一致性**：世界观设定（时间、地点、科技、魔法、生物等）必须与前面章节保持一致
   - **时间线一致性**：时间顺序必须合理，不能出现时间倒流或混乱的情况
   - **情节逻辑一致性**：情节发展必须符合大纲，不能出现逻辑矛盾
   - **连贯性**：本章开头应自然承接上一章的结尾，不能突兀或跳跃
9. **描写质量要求（重要）**：
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
10. 保持文笔流畅，情节紧凑
11. 确保实体（角色、地点、物品）与前面章节保持一致
   {self._get_quality_adjustment_instruction(chapter_number)}
{self._generate_preventive_prompt_additions(chapter_number)}
{self._get_ending_suspense_instruction(chapter_number, total_chapters)}

重要提示：这是一个创作任务，请直接生成章节正文内容，不需要搜索工具或调用任何函数。直接返回创作的内容即可。
请直接返回章节正文内容，不要包含标题或其他格式。
"""
        
        ***REMOVED*** 使用 ReActAgent 创作章节（限制迭代次数，避免工具搜索循环）
        logger.info(f"开始创作第{chapter_number}章：{chapter_title}（目标字数：{target_words}字，上限：{max_words_allowed}字）")
        original_max_iterations = self.agent.max_iterations
        original_max_new_tokens = self.agent.max_new_tokens
        
        ***REMOVED*** 自适应生成策略：根据质量反馈调整
        generation_strategy = self._get_adaptive_generation_strategy(chapter_number)
        
        ***REMOVED*** 初始生成策略：质量优先，字数控制通过prompt实现
        ***REMOVED*** max_new_tokens 始终不低于 2048，确保有足够的生成空间
        MIN_TOKEN_LIMIT = 2048
        
        ***REMOVED*** 计算基础token限制（确保至少2048，根据目标字数适当调整）
        ***REMOVED*** 目标2048字时，使用3072 token（1.5倍），确保有足够空间生成优质内容
        base_max_tokens = max(MIN_TOKEN_LIMIT, int(target_words * 1.5))
        
        ***REMOVED*** 初始生成时，使用较高的token限制，质量优先
        max_tokens_for_generation = base_max_tokens
        logger.info(f"初始生成：使用token限制 {max_tokens_for_generation}（质量优先，字数控制通过prompt实现）")
        
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
        
        ***REMOVED*** 检查字数是否过少（少于目标字数的50%），如果是则重试生成
        min_acceptable_words = int(target_words * 0.5)  ***REMOVED*** 最少接受目标字数的50%
        if actual_words < min_acceptable_words:
            logger.warning(
                f"第{chapter_number}章生成内容过短（{actual_words}字 < {min_acceptable_words}字，目标{target_words}字），"
                f"可能是生成失败，尝试重新生成..."
            )
            ***REMOVED*** 重试生成（最多重试1次）
            try:
                retry_content = self.agent.run(query=prompt, verbose=False)
                retry_words = len(retry_content)
                if retry_words >= min_acceptable_words:
                    logger.info(
                        f"第{chapter_number}章重试生成成功：{retry_words}字（目标{target_words}字）"
                    )
                    content = retry_content
                    original_words = retry_words
                    actual_words = retry_words
                else:
                    logger.warning(
                        f"第{chapter_number}章重试生成仍然过短（{retry_words}字），保留原始内容"
                    )
            except Exception as e:
                logger.warning(f"第{chapter_number}章重试生成失败: {e}，保留原始内容")
        
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
                
                ***REMOVED*** 判断是否需要重写（优化后的触发条件）
                should_rewrite = self._should_rewrite_chapter(quality_result, chapter_number)
                
                ***REMOVED*** 🔴 额外安全检查：如果问题数为0，强制不重写
                if quality_result.get('total_issues', 0) == 0:
                    should_rewrite = False
                    logger.debug(f"第{chapter_number}章问题数为0，强制不触发重写")
                
                ***REMOVED*** Phase 6: 质量预测和预防性提示
                if chapter_number > 1:
                    try:
                        ***REMOVED*** 预测可能的问题
                        predicted_issues = self._predict_quality_issues(chapter_number, chapter_summary)
                        if predicted_issues:
                            logger.info(f"第{chapter_number}章质量预测：预测到{len(predicted_issues)}个可能问题")
                            for pred in predicted_issues:
                                logger.debug(f"  - {pred.get('type')}: 概率{pred.get('probability', 0):.2f}")
                    except Exception as e:
                        logger.debug(f"质量预测失败: {e}")
                
                ***REMOVED*** 记录单章质量指标
                try:
                    self._track_chapter_quality(chapter_number, quality_result, actual_words, target_words)
                    ***REMOVED*** Phase 6: 更新问题模式追踪
                    self._update_issue_patterns(quality_result)
                except Exception as e:
                    logger.warning(f"追踪第{chapter_number}章质量指标失败: {e}")
            except Exception as e:
                logger.warning(f"第{chapter_number}章质量检查失败: {e}，跳过质量检查")
                chapter.metadata['quality_check'] = {"total_issues": 0, "error": str(e)}
        
        ***REMOVED*** 基于反馈重写（如果质量问题较多）- 支持多轮重写
        if should_rewrite and quality_result:
            try:
                logger.info(f"开始重写第{chapter_number}章...")
                original_issue_count = quality_result.get('total_issues', 0)
                original_content_for_rewrite = content
                original_content_for_save = content  ***REMOVED*** 在重写循环开始前初始化，确保总是有值
                current_quality_result = quality_result
                max_rewrite_rounds = 3  ***REMOVED*** 最多重写3轮
                rewrite_round = 0
                rewrite_history = []
                
                for rewrite_round in range(1, max_rewrite_rounds + 1):
                    logger.info(f"第{chapter_number}章第{rewrite_round}轮重写...")
                    
                    rewritten_content = self._rewrite_chapter_with_feedback(
                        chapter_number=chapter_number,
                        chapter_title=chapter_title,
                        chapter_summary=chapter_summary,
                        original_content=original_content_for_rewrite if rewrite_round == 1 else content,
                        quality_result=current_quality_result,
                        previous_chapters_summary=previous_chapters_summary,
                        target_words=target_words,
                        semantic_entities_context=semantic_entities_context,
                        unimem_context=unimem_context,
                        rewrite_round=rewrite_round,
                        rewrite_history=rewrite_history
                    )
                    
                    if not rewritten_content or len(rewritten_content) < min_words:
                        logger.warning(f"第{chapter_number}章第{rewrite_round}轮重写失败或内容过短")
                        if rewrite_round == 1:
                            ***REMOVED*** 第一轮就失败，保留原始内容
                            break
                        ***REMOVED*** 使用上一轮的重写结果
                        break
                    
                    ***REMOVED*** 更新章节内容
                    content = rewritten_content
                    actual_words = len(content)
                    
                    ***REMOVED*** 更新章节对象（临时，用于质量检查）
                    chapter.content = content
                    
                    ***REMOVED*** 重新进行质量检查
                    try:
                        quality_result_after_rewrite = self._check_chapter_quality(chapter, previous_chapters_summary)
                        total_issues_after = quality_result_after_rewrite.get('total_issues', 0)
                        improvement = original_issue_count - total_issues_after
                        
                        rewrite_history.append({
                            'round': rewrite_round,
                            'issue_count': total_issues_after,
                            'improvement': improvement
                        })
                        
                        logger.info(
                            f"第{chapter_number}章第{rewrite_round}轮重写后质量检查："
                            f"{total_issues_after} 个问题（原始：{original_issue_count}，改善：{improvement:+d}）"
                        )
                        
                        ***REMOVED*** 🔴 质量保护：如果重写后问题数增加，回退到原始内容
                        if improvement < 0:
                            logger.warning(
                                f"第{chapter_number}章第{rewrite_round}轮重写后问题数增加（{original_issue_count} -> {total_issues_after}），"
                                f"回退到原始内容"
                            )
                            ***REMOVED*** 回退到原始内容
                            if rewrite_round == 1:
                                content = original_content_for_save
                            else:
                                ***REMOVED*** 使用上一轮的结果（如果存在）
                                break
                            current_quality_result = quality_result
                            break
                        
                        ***REMOVED*** 判断是否需要继续重写（优化后的停止条件）
                        ***REMOVED*** 1. 如果问题数减少超过50%，或者问题数<=1，则停止重写（成功）
                        if improvement >= original_issue_count * 0.5 or total_issues_after <= 1:
                            logger.info(
                                f"第{chapter_number}章重写效果优秀（改善{improvement}个问题，{improvement/original_issue_count*100:.1f}%），停止重写"
                            )
                            current_quality_result = quality_result_after_rewrite
                            break
                        
                        ***REMOVED*** 2. 如果问题数减少超过30%，且已经是第2轮，可以考虑停止
                        if improvement >= original_issue_count * 0.3 and rewrite_round >= 2:
                            logger.info(
                                f"第{chapter_number}章重写效果良好（改善{improvement}个问题，{improvement/original_issue_count*100:.1f}%），停止重写"
                            )
                            current_quality_result = quality_result_after_rewrite
                            break
                        
                        ***REMOVED*** 3. 如果问题数没有减少，且已经是第3轮，停止重写（避免无效循环）
                        if improvement <= 0 and rewrite_round >= 3:
                            logger.warning(
                                f"第{chapter_number}章第{rewrite_round}轮重写仍无改善，已尝试3轮，停止重写"
                            )
                            current_quality_result = quality_result_after_rewrite
                            break
                        
                        ***REMOVED*** 4. 如果问题数没有减少，且是第2轮，继续尝试第3轮（使用更激进的策略）
                        if improvement <= 0 and rewrite_round == 2:
                            logger.warning(
                                f"第{chapter_number}章第{rewrite_round}轮重写未改善问题数，将在第3轮尝试备用策略"
                            )
                            ***REMOVED*** Phase 8: 记录失败策略，避免重复尝试
                            ***REMOVED*** 从当前质量结果中获取问题列表
                            current_issues = current_quality_result.get('issues', []) if current_quality_result else []
                            if self.fix_strategy_library and current_issues:
                                for issue in current_issues[:2]:  ***REMOVED*** 只处理前2个问题
                                    issue_type = issue.get('type', '')
                                    ***REMOVED*** 记录当前策略失败
                                    current_strategy_str = issue.get('predicted_strategy', 'standard')
                                    ***REMOVED*** 将字符串转换为 FixStrategy 枚举
                                    try:
                                        from novel_creation.fix_strategy_library import FixStrategy
                                        ***REMOVED*** 尝试通过值匹配枚举
                                        current_strategy = None
                                        for strategy in FixStrategy:
                                            if strategy.value == current_strategy_str:
                                                current_strategy = strategy
                                                break
                                        ***REMOVED*** 如果找不到匹配的，使用默认值
                                        if current_strategy is None:
                                            current_strategy = FixStrategy.ITERATIVE  ***REMOVED*** 默认使用迭代策略
                                    except Exception as e:
                                        logger.debug(f"转换策略类型失败: {e}，跳过记录")
                                        continue
                                    
                                    self.fix_strategy_library.record_fix_attempt(
                                        issue_type=issue_type,
                                        strategy_type=current_strategy,
                                        success=False,
                                        validation_score=0.0,
                                        metadata={
                                            'content_length': len(original_content_for_save),
                                            'severity': issue.get('severity', 'medium'),
                                            'rewrite_round': rewrite_round,
                                            'chapter_number': chapter_number,
                                            'reason': 'no_improvement'
                                        }
                                    )
                            
                            ***REMOVED*** Phase 8: 尝试备用策略（从预测器获取）
                            if self.fix_outcome_predictor and current_issues:
                                for issue in current_issues[:2]:  ***REMOVED*** 只处理前2个问题
                                    issue_type = issue.get('type', '')
                                    try:
                                        ***REMOVED*** 获取备用策略
                                        prediction = self.fix_outcome_predictor.predict_success_probability(
                                            issue_type=issue_type,
                                            content_length=len(original_content_for_save),
                                            fix_strategy=issue.get('predicted_strategy', 'standard'),
                                            severity=issue.get('severity', 'medium'),
                                            previous_attempts=rewrite_round
                                        )
                                        if hasattr(prediction, 'alternative_strategy') and prediction.alternative_strategy:
                                            issue['predicted_strategy'] = prediction.alternative_strategy
                                            logger.info(
                                                f"第{chapter_number}章问题 {issue_type} 切换到备用策略: {prediction.alternative_strategy}"
                                            )
                                    except Exception as e:
                                        logger.debug(f"获取备用策略失败: {e}")
                            
                            ***REMOVED*** 继续下一轮重写，尝试备用策略（自适应重试机制）
                            current_quality_result = quality_result_after_rewrite
                            continue
                        
                        ***REMOVED*** 5. 如果问题数有所减少但不够，继续重写
                        if 0 < improvement < original_issue_count * 0.3:
                            logger.info(
                                f"第{chapter_number}章第{rewrite_round}轮重写有改善（改善{improvement}个问题），继续重写以进一步改进"
                            )
                            current_quality_result = quality_result_after_rewrite
                            continue
                        
                        ***REMOVED*** 默认继续下一轮重写
                        current_quality_result = quality_result_after_rewrite
                        
                    except Exception as e:
                        logger.warning(f"第{chapter_number}章第{rewrite_round}轮重写后质量检查失败: {e}")
                        ***REMOVED*** 如果质量检查失败，但内容有效，使用当前内容
                        if rewrite_round == 1:
                            break
                
                ***REMOVED*** 最终更新章节对象和元数据
                if rewrite_round >= 1 and content != original_content_for_save:
                    actual_words = len(content)
                    word_diff = actual_words - target_words
                    word_diff_percent = (word_diff / target_words * 100) if target_words > 0 else 0
                    
                    chapter.content = content
                    chapter.metadata['rewritten'] = True
                    chapter.metadata['rewrite_rounds'] = rewrite_round
                    chapter.metadata['rewrite_history'] = rewrite_history
                    chapter.metadata['original_word_count'] = len(original_content_for_save)
                    chapter.metadata['rewritten_word_count'] = actual_words
                    chapter.metadata['actual_words'] = actual_words
                    chapter.metadata['word_diff'] = word_diff
                    chapter.metadata['word_diff_percent'] = round(word_diff_percent, 1)
                    chapter.metadata['original_issue_count'] = original_issue_count
                    chapter.metadata['final_issue_count'] = current_quality_result.get('total_issues', 0)
                    chapter.metadata['quality_check_after_rewrite'] = current_quality_result
                    chapter.metadata['quality_check'] = current_quality_result  ***REMOVED*** 更新为重写后的结果
                    
                    logger.info(
                        f"第{chapter_number}章重写完成（{rewrite_round}轮）："
                        f"原始 {len(original_content_for_save)} 字 → 重写后 {actual_words} 字，"
                        f"问题数：{original_issue_count} → {current_quality_result.get('total_issues', 0)}"
                    )
                    
                    ***REMOVED*** 重新保存章节（包含重写信息）
                    try:
                        self._save_chapter(chapter)
                        logger.debug(f"第{chapter_number}章重写后的内容已保存")
                    except Exception as e:
                        logger.warning(f"保存重写后的章节失败: {e}")
                else:
                    logger.warning(f"第{chapter_number}章重写失败，保留原始内容")
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
    
    def _update_issue_patterns(self, quality_result: Dict[str, Any]) -> None:
        """
        更新问题模式追踪（Phase 6: 初始生成质量提升）
        
        Args:
            quality_result: 质量检查结果
        """
        if "issue_patterns" not in self.quality_tracker:
            self.quality_tracker["issue_patterns"] = {}
        
        issue_patterns = self.quality_tracker["issue_patterns"]
        issues = quality_result.get("issues", [])
        
        for issue in issues:
            issue_type = issue.get("type")
            if issue_type:
                if issue_type not in issue_patterns:
                    issue_patterns[issue_type] = {
                        "count": 0,
                        "first_seen": datetime.now().isoformat(),
                        "last_seen": datetime.now().isoformat(),
                        "metadata": []
                    }
                
                issue_patterns[issue_type]["count"] += 1
                issue_patterns[issue_type]["last_seen"] = datetime.now().isoformat()
                
                ***REMOVED*** 记录问题元数据（用于分析）
                metadata = issue.get("metadata", {})
                if metadata:
                    issue_patterns[issue_type]["metadata"].append(metadata)
                    ***REMOVED*** 只保留最近10条元数据
                    if len(issue_patterns[issue_type]["metadata"]) > 10:
                        issue_patterns[issue_type]["metadata"] = issue_patterns[issue_type]["metadata"][-10:]
    
    def _get_ending_suspense_instruction(self, chapter_number: int, total_chapters: int) -> str:
        """
        获取结尾悬念指令（特别针对最后几章）
        
        Args:
            chapter_number: 当前章节编号
            total_chapters: 总章节数
        
        Returns:
            悬念指令字符串（如果是最後几章则返回特殊指令，否则返回空字符串）
        """
        if total_chapters == 0:
            return ""
        
        ***REMOVED*** 判断是否是最后10章（第一部结尾）
        if chapter_number >= total_chapters - 10:
            return f"""
**特别重要：这是第一部的最后阶段（第{chapter_number}章/共{total_chapters}章），结局必须留有悬念！**
- **禁止圆满结局**：不要解决所有问题，不要给所有角色圆满的结局
- **必须设置悬念**：最后几章（特别是第{max(95, total_chapters-5)}-{total_chapters}章）必须设置以下悬念之一：
  * 新的威胁或危机出现
  * 关键谜题未解（留下疑问）
  * 角色命运未定（生死、去向不明）
  * 更大的阴谋浮出水面
  * 意外的转折或发现
- **为第二部留下伏笔**：结局应该让读者产生"接下来会发生什么？"、"真相是什么？"、"他们能成功吗？"等疑问
- **第{total_chapters}章特别要求**：最后一章必须是一个强烈的悬念结尾，可以是：
  * 突然出现的威胁
  * 未解之谜的揭示
  * 关键角色的失踪或危险
  * 更大的阴谋的暗示
  * 开放式结局，留下多个悬念
"""
        return ""
    
    def _generate_preventive_prompt_additions(self, chapter_number: int) -> str:
        """
        基于历史问题模式生成预防性提示（Phase 6: 初始生成质量提升）
        
        Args:
            chapter_number: 当前章节编号
        
        Returns:
            预防性提示字符串
        """
        preventive_instructions = []
        issue_patterns = self.quality_tracker.get("issue_patterns", {})
        
        ***REMOVED*** 检查最近10章的问题模式
        recent_issues = self.quality_tracker.get("chapter_quality_history", [])[-10:]
        
        ***REMOVED*** 统计最近问题类型频率
        recent_issue_counts = defaultdict(int)
        for chapter_data in recent_issues:
            for issue in chapter_data.get("issues", []):
                issue_type = issue.get("type")
                if issue_type:
                    recent_issue_counts[issue_type] += 1
        
        ***REMOVED*** 针对高频问题添加预防性提示
        if recent_issue_counts.get("style_issue.心理活动过多", 0) >= 3:
            preventive_instructions.append(
                "**预防性提示：严格控制心理活动描写**：前续章节心理活动过多，本章心理活动句子（包含'想'、'觉得'、'认为'、'感觉'等词语）**不得超过8句**。优先通过对话和行动展现人物内心。"
            )
        if recent_issue_counts.get("style_issue.对话占比过低", 0) >= 3:
            preventive_instructions.append(
                "**预防性提示：确保对话占比**：前续章节对话占比过低，本章对话占比**必须达到25-35%**。每段对话后必须有动作或心理描写，避免纯对话堆砌。"
            )
        if recent_issue_counts.get("plot_inconsistency", 0) >= 2:
            preventive_instructions.append(
                "**预防性提示：加强情节逻辑连贯性**：前续章节出现情节不一致，本章请务必确保情节发展符合大纲和前面章节的逻辑，避免突兀的转折。"
            )
        if recent_issue_counts.get("character_inconsistency", 0) >= 2:
            preventive_instructions.append(
                "**预防性提示：保持人物性格一致**：前续章节人物性格出现漂移，本章请严格按照人物档案（如果存在）和前面章节的设定，保持角色性格、行为、说话方式的一致性。"
            )
        
        if preventive_instructions:
            return "\n\n" + "\n".join(preventive_instructions) + "\n"
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
        except Exception as e:
            logger.debug(f"解析章节范围 '{chapter_range}' 失败: {e}")
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
        
        ***REMOVED*** 保存目标章节数到metadata（用于节奏控制）
        self.metadata["target_chapters"] = target_chapters
        
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
                    ***REMOVED*** 更新 chapter_outline（合并所有阶段的章节，并去重标题）
                    all_chapters = []
                    for phase in phases:
                        all_chapters.extend(phase.get("chapters", []))
                    plan["chapter_outline"] = self._deduplicate_chapter_titles(all_chapters)
                    
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
                        
                        ***REMOVED*** Phase 7: 深度连贯性检查
                        try:
                            self._deep_coherence_check(chapter_number)
                        except Exception as e:
                            logger.warning(f"深度连贯性检查失败: {e}")
                
                ***REMOVED*** Phase 7: 关键节点回顾
                try:
                    self._check_key_node_review(chapter_number, plan)
                except Exception as e:
                    logger.debug(f"关键节点回顾检查失败: {e}")
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
    
    def _should_rewrite_chapter(self, quality_result: Dict[str, Any], chapter_number: int) -> bool:
        """
        判断是否需要重写章节（优化后的触发条件）
        
        根据问题类型和严重程度更精细的触发策略：
        - 严重问题（一致性、对话占比过低）>= 1：立即触发
        - 对话问题 >= 2：触发
        - 心理活动问题 >= 1（严重）：触发
        - 总问题数 >= 4：触发
        - 中等严重度问题 >= 3：触发
        
        Args:
            quality_result: 质量检查结果
            chapter_number: 章节编号
        
        Returns:
            是否需要重写
        """
        ***REMOVED*** 安全检查：如果质量检查失败或没有结果，不重写
        if not quality_result or quality_result.get('error'):
            logger.debug(f"第{chapter_number}章质量检查失败或无结果，不触发重写")
            return False
        
        total_issues = quality_result.get('total_issues', 0)
        
        ***REMOVED*** 🔴 关键修复：如果问题数为0，绝对不重写
        if total_issues == 0:
            logger.debug(f"第{chapter_number}章无质量问题（问题数=0），不触发重写")
            return False
        
        issues = quality_result.get('issues', [])
        
        ***REMOVED*** 如果 issues 为空但 total_issues > 0，说明数据结构有问题，不重写
        if not issues and total_issues > 0:
            logger.warning(f"第{chapter_number}章质量检查结果格式异常（total_issues={total_issues}但issues为空），不触发重写")
            return False
        
        ***REMOVED*** 确保 by_severity 和 by_type 字段存在，如果不存在则从 issues 中统计
        by_severity = quality_result.get('by_severity', {})
        by_type = quality_result.get('by_type', {})
        
        if not by_severity or not by_type:
            ***REMOVED*** 从 issues 中统计
            by_severity = {'high': 0, 'medium': 0, 'low': 0}
            by_type = {}
            for issue in issues:
                severity = issue.get('severity', 'low')
                by_severity[severity] = by_severity.get(severity, 0) + 1
                issue_type = issue.get('type', 'unknown')
                by_type[issue_type] = by_type.get(issue_type, 0) + 1
        
        high_severity = by_severity.get('high', 0)
        medium_severity = by_severity.get('medium', 0)
        
        ***REMOVED*** 1. 严重问题 >= 1：立即触发
        if high_severity >= 1:
            logger.info(
                f"第{chapter_number}章检测到严重问题（{high_severity}个），触发重写"
            )
            return True
        
        ***REMOVED*** 2. 统计各类问题数量
        from novel_creation.quality_checker import IssueType
        
        ***REMOVED*** 对话相关问题
        dialogue_issues = [
            issue for issue in issues
            if '对话' in issue.get('description', '') or 
               'dialogue' in issue.get('description', '').lower() or
               issue.get('type') == IssueType.STYLE_ISSUE.value
        ]
        dialogue_issue_count = len(dialogue_issues)
        
        ***REMOVED*** 心理活动问题
        thought_issues = [
            issue for issue in issues
            if '心理活动' in issue.get('description', '') or
               'thought' in issue.get('description', '').lower() or
               'thought_sentence_count' in issue.get('metadata', {})
        ]
        thought_issue_count = len(thought_issues)
        
        ***REMOVED*** 一致性问题
        consistency_issues = [
            issue for issue in issues
            if issue.get('type') in [
                IssueType.CHARACTER_INCONSISTENCY.value,
                IssueType.WORLDVIEW_INCONSISTENCY.value,
                IssueType.TIMELINE_INCONSISTENCY.value,
                IssueType.PLOT_INCONSISTENCY.value
            ]
        ]
        consistency_issue_count = len(consistency_issues)
        
        ***REMOVED*** 3. 对话问题 >= 2：触发
        if dialogue_issue_count >= 2:
            logger.info(
                f"第{chapter_number}章检测到对话问题较多（{dialogue_issue_count}个），触发重写"
            )
            return True
        
        ***REMOVED*** 4. 心理活动问题 >= 1（严重）或 >= 2（中等）：触发
        thought_severe = sum(1 for issue in thought_issues if issue.get('severity') == 'high')
        if thought_severe >= 1 or thought_issue_count >= 2:
            logger.info(
                f"第{chapter_number}章检测到心理活动问题（{thought_issue_count}个，严重{thought_severe}个），触发重写"
            )
            return True
        
        ***REMOVED*** 5. 一致性问题 >= 1（任何严重程度）：触发
        if consistency_issue_count >= 1:
            logger.info(
                f"第{chapter_number}章检测到一致性问题（{consistency_issue_count}个），触发重写"
            )
            return True
        
        ***REMOVED*** 6. 总问题数 >= 4：触发
        if total_issues >= 4:
            logger.info(
                f"第{chapter_number}章质量问题较多（总计{total_issues}个），触发重写"
            )
            return True
        
        ***REMOVED*** 7. 中等严重度问题 >= 3：触发
        if medium_severity >= 3:
            logger.info(
                f"第{chapter_number}章中等问题较多（{medium_severity}个），触发重写"
            )
            return True
        
        return False
    
    def _format_rewrite_history(self, rewrite_history: Optional[List[Dict[str, Any]]]) -> str:
        """格式化重写历史信息"""
        if not rewrite_history:
            return ""
        history_lines = ["**重写历史**："]
        for h in rewrite_history:
            history_lines.append(f"- 第{h['round']}轮：问题数 {h['issue_count']}（改善 {h['improvement']:+d}）")
        return "\n".join(history_lines)
    
    def _format_rewrite_round_warning(self, rewrite_round: int) -> str:
        """格式化重写轮次警告信息"""
        if rewrite_round <= 1:
            return ""
        return f"\n⚠️ **重要**：这是第{rewrite_round}轮重写。如果上一轮重写效果不佳，请尝试不同的改进策略。特别关注仍未解决的问题。"
    
    def _build_rewrite_few_shot_examples(
        self,
        issue_groups: Dict[str, List[Dict[str, Any]]],
        rewrite_strategy: str
    ) -> str:
        """构建few-shot示例，帮助LLM更好地理解如何改进"""
        examples = []
        
        ***REMOVED*** 对话问题示例
        if issue_groups.get('dialogue'):
            examples.append("""
**改进示例（对话问题）**：
❌ 不好（对话占比过低）：
他感到困惑。这到底是怎么回事？他想不明白。他觉得有什么地方不对。

✅ 好（增加对话，达到25-35%占比）：
他皱起眉头，看向对方："这到底是怎么回事？"
"我也觉得有什么地方不对。"对方回答，语气中带着同样的困惑。
"我们得弄清楚。"他站起身，走向门口。
""")
        
        ***REMOVED*** 心理活动问题示例
        if issue_groups.get('description'):
            has_thought_issue = any('心理活动' in issue.get('description', '') 
                                  for issue in issue_groups['description'])
            if has_thought_issue:
                examples.append("""
**改进示例（心理活动过多）**：
❌ 不好（重复心理活动）：
他想，这不对劲。他觉得有问题。他认为应该离开。他感觉危险正在靠近。他想到了之前的警告。

✅ 好（通过对话和行动展现内心）：
"这不对劲。"他停下脚步，警惕地环顾四周。
"我也觉得有问题。"艾薇跟上来，压低声音，"我们是不是应该——"
"离开。"他打断她，已经转身向门口走去。
之前的警告在脑海中闪现，让他加快了脚步。
""")
            
            has_env_issue = any('环境描写' in issue.get('description', '') 
                              for issue in issue_groups['description'])
            if has_env_issue:
                examples.append("""
**改进示例（环境描写冗余）**：
❌ 不好（大段纯形容词）：
房间很宽敞。墙壁是白色的。地面是木质的。天花板很高。窗户很大。阳光从窗户照进来。

✅ 好（结合动作推进情节）：
他推开房门，宽敞的空间让他停下脚步。白色的墙壁在阳光下显得刺眼，他眯起眼睛，目光扫过木质的地板，最后落在远处的大窗户上。阳光透过窗户洒进来，在地板上投下斑驳的光影。他缓步走过去，每一步都在空旷的房间里回响。
""")
        
        ***REMOVED*** 一致性问题示例
        if issue_groups.get('consistency'):
            examples.append("""
**改进示例（一致性问题）**：
❌ 不好（人物性格不一致）：
林墨性格开朗，总是笑嘻嘻地和同事打招呼。（但在前面章节中，林墨是孤僻的天才）

✅ 好（保持人物性格一致）：
林墨面无表情地从人群中穿过，对同事的招呼只是轻微点头，完全符合他孤僻天才的性格。只有在独自一人时，他的眼中才会闪过一丝对失踪父母的担忧。
""")
        
        if not examples:
            return ""
        
        return "\n" + "="*60 + "\n" + "**Few-Shot改进示例**（请参考以下方式改进）：\n" + "="*60 + "\n".join(examples) + "\n" + "="*60 + "\n"
    
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
        unimem_context: str = "",
        rewrite_round: int = 1,
        rewrite_history: Optional[List[Dict[str, Any]]] = None
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
            rewrite_round: 重写轮次（1, 2, 3...）
            rewrite_history: 重写历史记录
        
        Returns:
            重写后的内容，如果失败则返回None
        """
        try:
            ***REMOVED*** 按问题类型分组
            issues = quality_result.get('issues', [])
            from novel_creation.quality_checker import IssueType
            
            ***REMOVED*** 按类型和严重程度分组问题
            issue_groups = {
                'consistency': [],  ***REMOVED*** 一致性问题（最严重）
                'dialogue': [],     ***REMOVED*** 对话问题
                'description': [],  ***REMOVED*** 描述问题
                'other': []         ***REMOVED*** 其他问题
            }
            
            for issue in issues:
                issue_type = issue.get('type', '')
                description = issue.get('description', '')
                severity = issue.get('severity', 'medium')
                
                ***REMOVED*** 一致性问题（最优先）
                if issue_type in [
                    IssueType.CHARACTER_INCONSISTENCY.value,
                    IssueType.WORLDVIEW_INCONSISTENCY.value,
                    IssueType.TIMELINE_INCONSISTENCY.value,
                    IssueType.PLOT_INCONSISTENCY.value
                ]:
                    issue_groups['consistency'].append(issue)
                ***REMOVED*** 对话问题
                elif '对话' in description or 'dialogue' in description.lower():
                    issue_groups['dialogue'].append(issue)
                ***REMOVED*** 描述问题
                elif '心理活动' in description or '环境描写' in description or 'thought' in description.lower():
                    issue_groups['description'].append(issue)
                else:
                    issue_groups['other'].append(issue)
            
            ***REMOVED*** 构建分组反馈
            feedback_sections = []
            
            ***REMOVED*** 1. 一致性问题（最严重，必须优先解决）
            if issue_groups['consistency']:
                consistency_text = "【严重问题：一致性问题】\n"
                for issue in issue_groups['consistency']:
                    consistency_text += f"- {issue.get('description', '')}\n"
                    if issue.get('suggestion'):
                        consistency_text += f"  建议：{issue.get('suggestion')}\n"
                consistency_text += "\n⚠️ 必须修正：这些问题会导致读者混淆，必须完全修正。"
                feedback_sections.append(consistency_text)
            
            ***REMOVED*** 2. 对话问题
            if issue_groups['dialogue']:
                dialogue_text = "【对话质量问题】\n"
                for issue in issue_groups['dialogue']:
                    desc = issue.get('description', '')
                    dialogue_text += f"- {desc}\n"
                    if '对话占比过低' in desc:
                        metadata = issue.get('metadata', {})
                        dialogue_ratio = metadata.get('dialogue_ratio', 0) * 100
                        dialogue_text += f"  当前对话占比：{dialogue_ratio:.1f}%\n"
                        dialogue_text += "  目标：对话占比必须达到20-40%，理想范围为25-35%\n"
                        dialogue_text += "  改进示例：\n"
                        dialogue_text += "    不好：'他感到困惑。'（纯叙述，无对话）\n"
                        dialogue_text += "    好：'他皱着眉头问道：\\\"这是什么意思？\\\"（对话推进情节）\n"
                    elif '对话占比过高' in desc:
                        dialogue_text += "  目标：对话占比不应超过40%，需要增加动作、心理、环境描写\n"
                feedback_sections.append(dialogue_text)
            
            ***REMOVED*** 3. 描述问题
            if issue_groups['description']:
                description_text = "【描述质量问题】\n"
                for issue in issue_groups['description']:
                    desc = issue.get('description', '')
                    description_text += f"- {desc}\n"
                    if '心理活动' in desc:
                        metadata = issue.get('metadata', {})
                        thought_count = metadata.get('thought_sentence_count', 0)
                        description_text += f"  当前心理活动句子数：{thought_count}（限制：10句）\n"
                        description_text += "  改进示例：\n"
                        description_text += "    不好：'他想...他觉得...他认为...'（重复心理活动）\n"
                        description_text += "    好：通过对话和行动展现人物内心，减少'想'、'觉得'等词语\n"
                    elif '环境描写' in desc:
                        description_text += "  改进示例：\n"
                        description_text += "    不好：'房间很宽敞。墙壁是白色的。地面是木质的...'（大段纯形容词）\n"
                        description_text += "    好：'他推开房门，宽敞的空间让他停下脚步，目光扫过白色的墙壁和木质的地板...'（结合动作）\n"
                feedback_sections.append(description_text)
            
            ***REMOVED*** 4. 其他问题（只关注最重要的，次要问题可以容忍）
            critical_other_issues = [
                issue for issue in issue_groups['other']
                if issue.get('severity') == 'high' or '节奏' in issue.get('description', '')
            ]
            if critical_other_issues:
                other_text = "【其他重要质量问题】\n"
                for issue in critical_other_issues[:2]:  ***REMOVED*** 最多2个关键问题
                    other_text += f"- {issue.get('description', '')}\n"
                    if issue.get('suggestion'):
                        other_text += f"  建议：{issue.get('suggestion')}\n"
                feedback_sections.append(other_text)
            
            if not feedback_sections:
                feedback_sections = ["检测到质量问题，需要改进"]
            
            feedback_text = "\n\n".join(feedback_sections)
            
            ***REMOVED*** 确定质量目标
            quality_targets = []
            if issue_groups['dialogue']:
                dialogue_issues = issue_groups['dialogue']
                for issue in dialogue_issues:
                    if '对话占比过低' in issue.get('description', ''):
                        quality_targets.append("**对话占比必须达到25%以上**（硬性要求）")
                    elif '对话占比过高' in issue.get('description', ''):
                        quality_targets.append("**对话占比控制在35%以下**")
            if issue_groups['description']:
                quality_targets.append("**心理活动句子不超过10句**（硬性限制）")
            if issue_groups['consistency']:
                quality_targets.append("**所有一致性问题必须完全修正**")
            
            quality_targets_text = "\n".join(quality_targets) if quality_targets else "解决所有上述质量问题"
            
            ***REMOVED*** 根据重写轮次和问题类型选择不同的重写策略
            if rewrite_round > 1 and rewrite_history:
                ***REMOVED*** 如果上一轮重写无效，使用更激进的策略
                last_round = rewrite_history[-1]
                if last_round.get('improvement', 0) <= 0:
                    rewrite_strategy = "aggressive"  ***REMOVED*** 激进策略
                else:
                    rewrite_strategy = "focused"  ***REMOVED*** 聚焦策略
            else:
                rewrite_strategy = "standard"  ***REMOVED*** 标准策略
            
            ***REMOVED*** 构建针对性的few-shot示例
            few_shot_examples = self._build_rewrite_few_shot_examples(
                issue_groups, rewrite_strategy
            )
            
            ***REMOVED*** 从quality_result获取原始问题数
            original_issue_count = quality_result.get('total_issues', 0)
            
            ***REMOVED*** 🔴 质量保护：如果原始问题数为0，不应该重写（但这里已经通过了检查，添加额外提示）
            if original_issue_count == 0:
                logger.warning(f"第{chapter_number}章原始问题数为0，但触发了重写，这不应该发生")
                return None
            
            ***REMOVED*** Phase 1: 使用修复策略库选择目标问题（渐进式修复：每次只修复1-2个最高优先级问题）
            ***REMOVED*** 优化：优先选择历史成功率更高的问题
            target_issues = []
            if self.fix_strategy_library and self.fix_outcome_predictor:
                ***REMOVED*** 收集所有候选问题，计算预测成功率
                all_candidate_issues = []
                priority_order = ['consistency', 'dialogue', 'description', 'other']
                
                for priority in priority_order:
                    if issue_groups[priority]:
                        for issue in issue_groups[priority]:
                            issue_type = issue.get('type', '')
                            severity = issue.get('severity', 'medium')
                            
                            ***REMOVED*** 获取最佳策略（支持自适应重试：如果上一轮失败，尝试备用策略）
                            best_strategy = self.fix_strategy_library.get_best_strategy_for_issue(issue_type)
                            
                            ***REMOVED*** 自适应重试：如果上一轮重写失败，尝试备用策略
                            use_alternative = False
                            if rewrite_round > 1 and rewrite_history:
                                last_round = rewrite_history[-1] if rewrite_history else {}
                                if last_round.get('improvement', 0) <= 0:
                                    ***REMOVED*** 上一轮失败，尝试备用策略
                                    use_alternative = True
                            
                            if best_strategy:
                                strategy_name = best_strategy.value if hasattr(best_strategy, 'value') else str(best_strategy)
                                
                                ***REMOVED*** 预测成功率
                                try:
                                    prediction = self.fix_outcome_predictor.predict_success_probability(
                                        issue_type=issue_type,
                                        content_length=len(original_content),
                                        fix_strategy=strategy_name,
                                        severity=severity,
                                        previous_attempts=rewrite_round - 1
                                    )
                                    
                                    ***REMOVED*** 如果上一轮失败，尝试备用策略
                                    if use_alternative and hasattr(prediction, 'alternative_strategy') and prediction.alternative_strategy:
                                        strategy_name = prediction.alternative_strategy
                                        logger.info(
                                            f"第{chapter_number}章问题 {issue_type} 上一轮策略失败，"
                                            f"尝试备用策略: {strategy_name}"
                                        )
                                        ***REMOVED*** 重新预测备用策略的成功率
                                        prediction = self.fix_outcome_predictor.predict_success_probability(
                                            issue_type=issue_type,
                                            content_length=len(original_content),
                                            fix_strategy=strategy_name,
                                            severity=severity,
                                            previous_attempts=rewrite_round - 1
                                        )
                                    
                                    ***REMOVED*** 记录预测成功率到issue中
                                    success_prob = getattr(prediction, 'success_probability', 0.5)
                                    issue['predicted_success_prob'] = success_prob
                                    issue['predicted_strategy'] = strategy_name
                                    issue['priority'] = priority
                                    
                                    all_candidate_issues.append(issue)
                                except Exception as e:
                                    logger.warning(f"预测问题 {issue_type} 成功率失败: {e}")
                                    ***REMOVED*** 如果预测失败，使用默认值
                                    issue['predicted_success_prob'] = 0.5
                                    issue['predicted_strategy'] = strategy_name
                                    issue['priority'] = priority
                                    all_candidate_issues.append(issue)
                
                ***REMOVED*** 按预测成功率排序（成功率高的优先），同时考虑优先级
                ***REMOVED*** 评分 = 成功率 * 0.7 + 优先级权重 * 0.3
                priority_weights = {'consistency': 1.0, 'dialogue': 0.8, 'description': 0.6, 'other': 0.4}
                
                def calculate_score(issue):
                    success_prob = issue.get('predicted_success_prob', 0.5)
                    priority = issue.get('priority', 'other')
                    priority_weight = priority_weights.get(priority, 0.4)
                    return success_prob * 0.7 + priority_weight * 0.3
                
                all_candidate_issues.sort(key=calculate_score, reverse=True)
                
                ***REMOVED*** 选择前1-2个问题，但至少成功率要>=0.3（第一轮）或>=0.25（后续轮）
                min_success_prob = 0.4 if rewrite_round == 1 else 0.3
                filtered_issues = [
                    issue for issue in all_candidate_issues 
                    if issue.get('predicted_success_prob', 0.5) >= min_success_prob
                ]
                
                if filtered_issues:
                    target_issues = filtered_issues[:2]  ***REMOVED*** 最多选择2个
                    ***REMOVED*** 构建成功率字符串（避免f-string嵌套问题）
                    success_probs = [f"{i.get('predicted_success_prob', 0):.2f}" for i in target_issues]
                    logger.info(
                        f"第{chapter_number}章渐进式修复：选择{len(target_issues)}个问题 "
                        f"(成功率: {success_probs})"
                    )
                else:
                    ***REMOVED*** 如果没有满足最低成功率的问题，选择成功率最高的1个
                    if all_candidate_issues:
                        target_issues = [all_candidate_issues[0]]
                        logger.warning(
                            f"第{chapter_number}章所有问题预测成功率都低于{min_success_prob}，"
                            f"选择成功率最高的1个（{all_candidate_issues[0].get('predicted_success_prob', 0):.2f}）"
                        )
                    else:
                        target_issues = issues[:1] if issues else []
            elif self.fix_strategy_library:
                ***REMOVED*** 如果没有预测器，使用原来的逻辑
                priority_order = ['consistency', 'dialogue', 'description', 'other']
                for priority in priority_order:
                    if issue_groups[priority]:
                        target_issues = issue_groups[priority][:2]
                        logger.info(f"第{chapter_number}章渐进式修复：选择{len(target_issues)}个{priority}问题")
                        break
            else:
                ***REMOVED*** 如果没有策略库，使用所有问题
                target_issues = issues
            
            ***REMOVED*** 如果target_issues为空，使用所有问题作为后备
            if not target_issues:
                target_issues = issues[:1] if issues else []
            
            ***REMOVED*** 检查原始内容的字数，如果超过目标，需要在重写时优化字数
            original_word_count = len(original_content)
            word_count_optimization_needed = original_word_count > target_words * 1.1  ***REMOVED*** 超过目标10%需要优化
            word_count_supplement_needed = original_word_count < target_words * 0.9  ***REMOVED*** 低于目标10%需要补充
            
            ***REMOVED*** 构建字数优化/补充要求文本（在f-string外部构建，避免反斜杠问题）
            word_count_instruction = ""
            if word_count_optimization_needed:
                word_count_instruction = f"""
**字数优化要求**（质量优先）：
- 当前内容{original_word_count}字，超出目标{original_word_count - target_words}字
- **核心原则**：质量优先，字数控制是次要的
- 如果当前内容质量很高，可以保留（优质内容比严格字数控制更重要）
- 如果需要在保持质量的前提下优化字数，可以通过以下方式：
  * 删除冗余的环境描写和重复的心理活动（不影响核心情节）
  * 合并相似的描述，使用更简洁的表达（保持文笔流畅）
  * 精简对话，保留关键信息，删除无意义的寒暄（保持对话质量）
  * 优化长句，使用更简洁的句式（保持表达清晰）
- **目标**：重写后字数尽量控制在{int(target_words*0.9)}-{int(target_words*1.1)}字范围内，但如果内容优质，{int(target_words*0.8)}-{int(target_words*1.2)}字都可以接受"""
            elif word_count_supplement_needed:
                word_count_instruction = f"""
**字数补充要求**（质量优先）：
- 当前内容{original_word_count}字，低于目标{target_words - original_word_count}字
- **核心原则**：质量优先，字数控制是次要的
- 如果当前内容质量很高但字数略少，可以保留（不要为了凑字数而添加冗余）
- 如果需要在保持质量的前提下补充内容，可以通过以下方式：
  * 增加必要的对话，推进情节和展现人物（确保对话有目的性）
  * 补充关键的动作描写和环境描写（服务于情节）
  * 增加人物的心理活动和反应（展现人物性格）
  * 扩展关键情节的细节（增强可读性）
- **目标**：重写后字数尽量达到{int(target_words*0.9)}-{int(target_words*1.1)}字范围内，但如果内容优质，{int(target_words*0.8)}-{int(target_words*1.2)}字都可以接受"""
            
            ***REMOVED*** 构建当前字数信息
            word_count_info = ""
            if word_count_optimization_needed:
                word_count_info = f"- **当前字数**：{original_word_count}字（超出目标{original_word_count - target_words}字，需要在重写时优化字数）"
            elif word_count_supplement_needed:
                word_count_info = f"- **当前字数**：{original_word_count}字（低于目标{target_words - original_word_count}字，需要在重写时补充内容）"
            
            ***REMOVED*** 构建针对性的修复策略提示（从修复策略库获取）
            strategy_prompts = []
            if self.fix_strategy_library and target_issues:
                for issue in target_issues:
                    issue_type = issue.get('type', '')
                    issue_metadata = issue.get('metadata', {})
                    
                    ***REMOVED*** 确保 chapter_summary 在 metadata 中（用于策略模板填充）
                    if 'chapter_summary' not in issue_metadata:
                        issue_metadata['chapter_summary'] = chapter_summary[:200] if chapter_summary else ""
                    
                    ***REMOVED*** 获取修复策略
                    strategy = self.fix_strategy_library.get_strategy(issue_type, issue_metadata)
                    if strategy and strategy.fix_prompt_template:
                        ***REMOVED*** 填充策略模板
                        try:
                            ***REMOVED*** 准备所有可能的变量
                            template_vars = {
                                **issue_metadata,  ***REMOVED*** 先添加元数据
                                'chapter_summary': chapter_summary[:200] if chapter_summary else "",
                                'few_shot_examples': "\n".join(f"- {ex}" for ex in strategy.few_shot_examples) if strategy.few_shot_examples else "",
                                ***REMOVED*** 添加常见缺失变量（使用默认值）
                                'thought_count': issue_metadata.get('thought_sentence_count', issue_metadata.get('thought_count', 0)),
                                'dialogue_count': issue_metadata.get('dialogue_count', 0),
                                'dialogue_with_action': issue_metadata.get('dialogue_with_action', 0),
                                'dialogue_ratio_percent': issue_metadata.get('dialogue_ratio', 0) * 100 if 'dialogue_ratio' in issue_metadata else 0,
                            }
                            
                            ***REMOVED*** 安全填充模板（只使用存在的变量）
                            filled_prompt = strategy.fix_prompt_template
                            ***REMOVED*** 使用format_map，如果缺少变量会抛出KeyError，我们捕获它
                            try:
                                filled_prompt = filled_prompt.format(**template_vars)
                            except KeyError as ke:
                                ***REMOVED*** 如果缺少变量，使用默认值
                                logger.debug(f"策略模板缺少变量 {ke}，使用默认值")
                                ***REMOVED*** 为缺失的变量添加默认值
                                missing_var = str(ke).strip("'")
                                template_vars[missing_var] = ""
                                filled_prompt = filled_prompt.format(**template_vars)
                            
                            strategy_prompts.append(filled_prompt)
                        except Exception as e:
                            logger.warning(f"填充修复策略模板失败: {e}")
                            ***REMOVED*** 如果填充失败，使用通用描述
                            strategy_prompts.append(f"**问题**：{issue.get('description', '')}\n**修复要求**：请解决此问题")
            
            strategy_prompts_text = "\n\n".join(strategy_prompts) if strategy_prompts else ""
            
            ***REMOVED*** 构建针对性修复策略文本（在f-string外部处理，避免反斜杠问题）
            strategy_section = ""
            if strategy_prompts_text:
                strategy_section = f"**针对性修复策略**（基于历史成功率优化）：\n{strategy_prompts_text}\n"
            
            ***REMOVED*** 构建重写提示词（增强版）
            rewrite_prompt = f"""请重写小说《{self.novel_title}》的第{chapter_number}章。

**章节信息**：
- 标题：{chapter_title}
- 摘要：{chapter_summary}
- 目标字数：{target_words}字（允许±10%，即{int(target_words*0.9)}-{int(target_words*1.1)}字）
{word_count_info}

**原始内容**（存在以下质量问题，需要改进）：
{original_content[:2500]}...

**质量检查反馈**（按优先级分组）：
{feedback_text}

{strategy_section}

**重写后的质量目标**：
{quality_targets_text}
{word_count_instruction}

{few_shot_examples}

**重写策略**（当前使用：{rewrite_strategy}策略）：
{f"**{rewrite_strategy.upper()}策略**：" if rewrite_strategy != "standard" else ""}
{f"- 这是第{rewrite_round}轮重写，上一轮重写效果不佳（改善{last_round.get('improvement', 0)}个问题）" if rewrite_strategy == "aggressive" and rewrite_history else ""}
{f"- 需要**更彻底地重构**，不仅仅是表面修改，而是重新组织内容结构" if rewrite_strategy == "aggressive" else ""}
{f"- 聚焦解决最关键的问题，次要问题可以先忽略" if rewrite_strategy == "focused" else ""}

**重写要求**：
1. **必须解决上述所有质量问题**，特别是标记为"严重"的问题
   - 一致性问题：必须完全修正，不能有任何矛盾
   - 对话问题：对话占比必须达到目标范围（20-40%）
   - 描述问题：精简冗余描写，控制心理活动

2. **⚠️ 重要：不要引入新问题**
   - 只修改检测到的具体问题，不要"优化"没有问题的内容
   - 保持核心情节、人物性格、世界观设定完全不变
   - 如果某个部分没有问题，保持原样，不要修改
   - 重写后的问题数必须 ≤ 原始问题数，不能增加

3. **保持章节的核心情节和主要事件不变**，只改进表达方式
   - 核心情节：{chapter_summary[:100]}...
   - 主要人物：保持性格和说话方式一致
   - 关键事件：不能删除或改变主要事件

3. **确保字数控制在目标范围内**（{target_words}字，允许±10%）
   - 当前字数：{len(original_content)}字
   - 目标范围：{int(target_words*0.9)}-{int(target_words*1.1)}字
   - 如果超出，优先删除冗余描写，保留核心情节

4. **保持与前面章节的连贯性**，确保人物、世界观、时间线一致
   - 人物性格：不能突然改变
   - 世界观：不能出现矛盾设定
   - 时间线：不能混乱或跳跃

5. **对话占比必须达到20-40%**（理想范围25-35%）
   - 每1000字至少包含3-5段对话
   - 对话必须推进情节，不能只是寒暄
   - 对话要配合动作描写，避免纯对话

6. **避免冗余的环境描写**
   - 环境描写应简洁有力，结合动作推进情节
   - 避免超过2段以形容词为主但缺少动作的段落
   - 每段环境描写后必须有动作、对话或心理活动

7. **控制心理活动描写**
   - 全章"想"、"觉得"、"认为"、"感觉"等心理活动句子不超过10句
   - 优先使用对话和行动展现人物内心
   - 避免重复的心理活动描写

**前面章节摘要**（用于保持连贯性）：
{previous_chapters_summary if previous_chapters_summary else "无"}

{semantic_entities_context}

{unimem_context}

**重写轮次信息**：
- 当前重写轮次：第{rewrite_round}轮（最多3轮）
{self._format_rewrite_history(rewrite_history) if rewrite_history else ""}
{self._format_rewrite_round_warning(rewrite_round) if rewrite_round > 1 else ""}

**重要提示**：
- 请直接生成改进后的完整章节内容，不需要说明或注释
- 确保内容质量**明显优于**原始版本，问题数必须减少
- 重写后必须满足上述所有质量目标，特别是对话占比和心理活动限制"""
            
            ***REMOVED*** 添加重写轮次提示（在f-string外部处理，避免反斜杠问题）
            if rewrite_round > 1:
                rewrite_prompt += f"\n- **这是第{rewrite_round}轮重写，请使用更彻底的改进方法**"
            else:
                rewrite_prompt += "\n- **这是第一次重写，请全面改进**"
            
            rewrite_prompt += "\n"

            ***REMOVED*** 生成重写内容
            original_max_iterations = self.agent.max_iterations
            original_max_new_tokens = self.agent.max_new_tokens
            
            ***REMOVED*** 重写时：质量优先，max_new_tokens 始终不低于 2048
            ***REMOVED*** 字数控制通过 prompt 实现，而不是通过降低 token 限制
            MIN_TOKEN_LIMIT = 2048
            
            ***REMOVED*** 根据目标字数计算，但确保至少 2048
            if word_count_optimization_needed:
                ***REMOVED*** 字数过多，但保持足够的 token 空间（至少 2048）
                rewrite_token_limit = max(MIN_TOKEN_LIMIT, int(target_words * 1.2 * 1.1))
                self.agent.max_new_tokens = rewrite_token_limit
                logger.info(f"重写时字数优化：原始{original_word_count}字，目标{target_words}字，使用token限制{rewrite_token_limit}（通过prompt优化字数）")
            elif word_count_supplement_needed:
                ***REMOVED*** 字数不足，使用较高的 token 限制来补充
                rewrite_token_limit = max(MIN_TOKEN_LIMIT, int(target_words * 1.5 * 1.1))
                self.agent.max_new_tokens = rewrite_token_limit
                logger.info(f"重写时字数补充：原始{original_word_count}字，目标{target_words}字，使用token限制{rewrite_token_limit}进行补充")
            else:
                ***REMOVED*** 字数在合理范围内，使用基础限制（至少 2048）
                rewrite_token_limit = max(MIN_TOKEN_LIMIT, int(target_words * 1.3 * 1.1))
                self.agent.max_new_tokens = rewrite_token_limit
            
            self.agent.max_iterations = 5
            try:
                rewritten_content = self.agent.run(query=rewrite_prompt, verbose=False)
            finally:
                self.agent.max_iterations = original_max_iterations
                self.agent.max_new_tokens = original_max_new_tokens
            
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
            
            ***REMOVED*** Phase 1: 使用修复验证器验证修复效果（安全重写模式）
            validation_results = {}
            overall_score = 0.0
            is_successful = False
            
            if self.fix_validator and target_issues:
                validation_results = self.fix_validator.validate_fix(
                    original_content,
                    rewritten_content,
                    target_issues
                )
                
                ***REMOVED*** 计算总体验证评分
                overall_score = self.fix_validator.calculate_overall_validation_score(validation_results)
                is_successful = self.fix_validator.is_fix_successful(validation_results, min_score=0.6)
                
                logger.info(
                    f"第{chapter_number}章修复验证："
                    f"总体评分={overall_score:.2f}, "
                    f"成功={is_successful}, "
                    f"验证了{len(validation_results)}个问题"
                )
                
                ***REMOVED*** 记录验证结果详情
                for issue_type, result in validation_results.items():
                    logger.debug(
                        f"  问题 {issue_type}: "
                        f"已解决={result.fixed}, "
                        f"仍存在={result.still_exists}, "
                        f"引入新问题={result.introduced_new}, "
                        f"评分={result.verification_score:.2f}"
                    )
                
                ***REMOVED*** Phase 2: 记录修复历史（用于学习）
                if self.fix_strategy_library:
                    for issue in target_issues:
                        issue_type = issue.get('type', '')
                        severity = issue.get('severity', 'medium')
                        
                        ***REMOVED*** 获取使用的策略
                        strategy = self.fix_strategy_library.get_best_strategy_for_issue(issue_type)
                        if strategy:
                            ***REMOVED*** 获取该问题的验证结果
                            validation_result = validation_results.get(issue_type)
                            validation_score = validation_result.verification_score if validation_result else overall_score
                            
                            ***REMOVED*** 判断是否成功（验证评分 >= 0.6 且问题已解决）
                            fix_success = (
                                validation_result.fixed if validation_result else False
                            ) and validation_score >= 0.6
                            
                            ***REMOVED*** 记录修复尝试
                            self.fix_strategy_library.record_fix_attempt(
                                issue_type=issue_type,
                                strategy_type=strategy,
                                success=fix_success,
                                validation_score=validation_score,
                                metadata={
                                    'content_length': len(original_content),
                                    'severity': severity,
                                    'rewrite_round': rewrite_round,
                                    'chapter_number': chapter_number
                                }
                            )
                            
                            logger.debug(
                                f"记录修复历史：问题类型={issue_type}, "
                                f"策略={strategy.value}, "
                                f"成功={fix_success}, "
                                f"评分={validation_score:.2f}"
                            )
                
                ***REMOVED*** 如果验证失败，记录但继续（让上层决定是否回退）
                if not is_successful:
                    logger.warning(
                        f"第{chapter_number}章修复验证失败："
                        f"总体评分{overall_score:.2f}低于阈值0.6，"
                        f"或引入了新问题"
                    )
                    ***REMOVED*** 不直接返回None，让上层根据质量检查结果决定
            
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
                except Exception as e:
                    logger.debug(f"计算角色一致性得分时出错: {e}")
        
        return max(0.0, min(1.0, score))
    
    def _calculate_character_consistency_score(self, chapters: List[NovelChapter]) -> float:
        """计算人物一致性得分（0-1）"""
        if not self.semantic_mesh:
            return 0.8
        return 1.0  ***REMOVED*** 简化实现，后续可以增强
    
    def _build_character_profiles(self, chapters: List[NovelChapter]) -> Dict[str, Dict[str, Any]]:
        """
        建立人物档案（Phase 7: 长期连贯性增强）
        
        Args:
            chapters: 章节列表
        
        Returns:
            人物档案字典 {character_name: {name, personality, appearance, relationships, ...}}
        """
        profiles = {}
        
        if not self.semantic_mesh:
            return profiles
        
        try:
            ***REMOVED*** 从语义网格中提取人物实体
            character_entities = [
                e for e in self.semantic_mesh.entities.values()
                if e.type.value == "character"
            ]
            
            for entity in character_entities:
                name = entity.name
                if name not in profiles:
                    profiles[name] = {
                        "name": name,
                        "personality": entity.metadata.get("personality", ""),
                        "appearance": entity.metadata.get("appearance", ""),
                        "relationships": entity.metadata.get("relationships", {}),
                        "first_appearance": entity.metadata.get("first_appearance_chapter", 0),
                        "appearance_chapters": entity.metadata.get("appearance_chapters", []),
                        "key_events": entity.metadata.get("key_events", []),
                        "last_updated": entity.updated_at
                    }
        except Exception as e:
            logger.warning(f"建立人物档案失败: {e}")
        
        return profiles
    
    def _build_worldview_profiles(self, chapters: List[NovelChapter]) -> Dict[str, Dict[str, Any]]:
        """
        建立世界观档案（Phase 7: 长期连贯性增强）
        
        Args:
            chapters: 章节列表
        
        Returns:
            世界观档案字典 {category: {settings, first_mentioned, consistency_notes}}
        """
        profiles = {}
        
        if not self.semantic_mesh:
            return profiles
        
        try:
            ***REMOVED*** 从语义网格中提取世界观相关实体
            worldview_categories = ["location", "setting", "concept", "creature", "item"]
            
            for category in worldview_categories:
                category_entities = [
                    e for e in self.semantic_mesh.entities.values()
                    if e.type.value == category
                ]
                
                if category_entities:
                    profiles[category] = {
                        "settings": [e.name for e in category_entities],
                        "first_mentioned": min(
                            [e.metadata.get("first_appearance_chapter", 0) for e in category_entities],
                            default=0
                        ),
                        "consistency_notes": [],
                        "last_updated": datetime.now().isoformat()
                    }
        except Exception as e:
            logger.warning(f"建立世界观档案失败: {e}")
        
        return profiles
    
    def _deep_coherence_check(self, current_chapter_number: int):
        """
        深度连贯性检查（Phase 7: 长期连贯性增强）
        每10章进行一次，检测人物性格漂移和世界观设定变化
        
        Args:
            current_chapter_number: 当前章节编号
        """
        if current_chapter_number < 10:
            return
        
        try:
            logger.info(f"开始深度连贯性检查（第{current_chapter_number}章）...")
            
            ***REMOVED*** 获取所有章节
            all_chapters = self.chapters
            
            ***REMOVED*** 建立人物档案
            character_profiles = self._build_character_profiles(all_chapters)
            
            ***REMOVED*** 建立世界观档案
            worldview_profiles = self._build_worldview_profiles(all_chapters)
            
            ***REMOVED*** 更新长期连贯性追踪
            long_term_coherence = self.quality_tracker.get("long_term_coherence", {})
            long_term_coherence["character_profiles"] = character_profiles
            long_term_coherence["worldview_profiles"] = worldview_profiles
            
            ***REMOVED*** 检测人物性格漂移
            character_drift_issues = []
            for name, profile in character_profiles.items():
                appearance_chapters = profile.get("appearance_chapters", [])
                if len(appearance_chapters) >= 5:
                    ***REMOVED*** 检查人物在不同章节中的表现是否一致
                    ***REMOVED*** 这里可以添加更复杂的检测逻辑
                    pass
            
            ***REMOVED*** 检测世界观设定变化
            worldview_change_issues = []
            ***REMOVED*** 检查世界观设定是否一致
            ***REMOVED*** 这里可以添加更复杂的检测逻辑
            
            ***REMOVED*** 生成连贯性报告
            coherence_report = {
                "chapter_number": current_chapter_number,
                "check_time": datetime.now().isoformat(),
                "character_count": len(character_profiles),
                "worldview_categories": len(worldview_profiles),
                "character_drift_issues": character_drift_issues,
                "worldview_change_issues": worldview_change_issues,
                "summary": f"检查了{len(character_profiles)}个人物和{len(worldview_profiles)}个世界观类别"
            }
            
            if not long_term_coherence.get("coherence_reports"):
                long_term_coherence["coherence_reports"] = []
            long_term_coherence["coherence_reports"].append(coherence_report)
            
            self.quality_tracker["long_term_coherence"] = long_term_coherence
            
            logger.info(f"深度连贯性检查完成：{coherence_report['summary']}")
            
        except Exception as e:
            logger.error(f"深度连贯性检查失败: {e}", exc_info=True)
    
    def _check_key_node_review(self, chapter_number: int, plan: Dict[str, Any]):
        """
        关键节点回顾（Phase 7: 长期连贯性增强）
        在关键情节节点回顾前面章节，确保重要设定和人物关系一致
        
        Args:
            chapter_number: 当前章节编号
            plan: 小说大纲
        """
        try:
            ***REMOVED*** 获取关键节点信息
            key_plot_points = plan.get("overall", {}).get("key_plot_points", [])
            if not key_plot_points:
                return
            
            ***REMOVED*** 检查当前章节是否接近关键节点
            for plot_point in key_plot_points:
                plot_chapter = plot_point.get("chapter", 0)
                ***REMOVED*** 在关键节点前3章开始回顾
                if plot_chapter - 3 <= chapter_number <= plot_chapter:
                    logger.info(f"检测到关键节点（第{plot_chapter}章），开始回顾前面章节...")
                    
                    ***REMOVED*** 回顾前面章节的关键信息
                    review_chapters = self.chapters[max(0, chapter_number-20):chapter_number]
                    
                    ***REMOVED*** 提取关键信息
                    key_characters = set()
                    key_settings = set()
                    key_events = []
                    
                    for ch in review_chapters:
                        ***REMOVED*** 从语义网格提取关键实体
                        if self.semantic_mesh:
                            chapter_entities = [
                                e for e in self.semantic_mesh.entities.values()
                                if ch.chapter_number in e.metadata.get("appearance_chapters", [])
                            ]
                            for entity in chapter_entities:
                                if entity.type.value == "character":
                                    key_characters.add(entity.name)
                                elif entity.type.value in ["location", "setting"]:
                                    key_settings.add(entity.name)
                    
                    ***REMOVED*** 生成回顾报告
                    review_report = {
                        "chapter_number": chapter_number,
                        "target_plot_point": plot_point.get("title", ""),
                        "target_chapter": plot_chapter,
                        "review_time": datetime.now().isoformat(),
                        "reviewed_chapters": f"第{max(1, chapter_number-20)}-{chapter_number}章",
                        "key_characters": list(key_characters),
                        "key_settings": list(key_settings),
                        "key_events": key_events,
                        "summary": f"回顾了{len(review_chapters)}章，提取了{len(key_characters)}个关键人物和{len(key_settings)}个关键设定"
                    }
                    
                    ***REMOVED*** 保存到长期连贯性追踪
                    long_term_coherence = self.quality_tracker.get("long_term_coherence", {})
                    if not long_term_coherence.get("key_node_reviews"):
                        long_term_coherence["key_node_reviews"] = []
                    long_term_coherence["key_node_reviews"].append(review_report)
                    self.quality_tracker["long_term_coherence"] = long_term_coherence
                    
                    logger.info(f"关键节点回顾完成：{review_report['summary']}")
                    break
                    
        except Exception as e:
            logger.warning(f"关键节点回顾失败: {e}")
    
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
        
        使用 LLM 评估章节的悬念程度，更准确地识别悬疑元素
        """
        if not chapters:
            return 0.5
        
        try:
            from llm.chat import deepseek_v3_2
        except ImportError:
            logger.warning("无法导入 deepseek_v3_2，回退到简单规则评估")
            return self._calculate_suspense_score_fallback(chapters)
        
        suspense_scores = []
        chapters_to_check = chapters[-5:]  ***REMOVED*** 检查最近5章
        
        for chapter in chapters_to_check:
            try:
                ***REMOVED*** 构建评估 prompt
                prompt = f"""请评估以下小说章节的悬念程度，给出0-1之间的分数（保留2位小数）。

评估标准：
1. 情节悬念：是否有未解之谜、危险信号、紧张冲突
2. 氛围营造：是否营造了紧张、不安、神秘的氛围
3. 结尾设计：章节结尾是否留下悬念、疑问或转折
4. 心理描写：是否通过心理活动增强悬念感
5. 信息控制：是否通过信息不对称制造悬念

章节标题：{chapter.title}
章节内容：
{chapter.content}

请只返回一个0-1之间的浮点数（如0.75），不要包含其他文字。"""
                
                messages = [
                    {"role": "user", "content": prompt}
                ]
                
                _, response = deepseek_v3_2(messages, max_new_tokens=100)
                
                ***REMOVED*** 提取分数
                score_match = re.search(r'0?\.\d+|1\.0|0\.0', response.strip())
                if score_match:
                    score = float(score_match.group())
                    score = max(0.0, min(1.0, score))  ***REMOVED*** 确保在0-1范围内
                    suspense_scores.append(score)
                    logger.debug(f"第{chapter.chapter_number}章悬念得分（LLM评估）: {score:.2f}")
                else:
                    ***REMOVED*** 如果无法解析，使用默认值
                    logger.warning(f"无法解析第{chapter.chapter_number}章的悬念得分，使用默认值0.5")
                    suspense_scores.append(0.5)
                    
            except Exception as e:
                logger.warning(f"评估第{chapter.chapter_number}章悬念得分时出错: {e}，使用默认值0.5")
                suspense_scores.append(0.5)
        
        ***REMOVED*** 计算平均得分
        if suspense_scores:
            score = sum(suspense_scores) / len(suspense_scores)
            logger.info(f"平均悬念得分（LLM评估）: {score:.2f} (基于{len(suspense_scores)}章)")
            return max(0.0, min(1.0, score))
        else:
            return 0.5
    
    def _calculate_suspense_score_fallback(self, chapters: List[NovelChapter]) -> float:
        """
        回退方案：使用简单的关键词和规则检测
        """
        if not chapters:
            return 0.5
        
        suspense_keywords = ["？", "?", "...", "！", "!", "突然", "竟然", "没想到", "原来", "但是", "然而", "不过", "可是"]
        suspense_scores = []
        
        for chapter in chapters[-5:]:  ***REMOVED*** 检查最近5章
            content = chapter.content
            ending = content[-200:] if len(content) > 200 else content
            
            ***REMOVED*** 1. 关键词检测
            keyword_count = sum(1 for keyword in suspense_keywords if keyword in ending)
            keyword_score = min(1.0, keyword_count / 3.0)  ***REMOVED*** 最多3个关键词得满分
            
            ***REMOVED*** 2. 章节结尾分析
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
                            except (ValueError, AttributeError) as e:
                                logger.debug(f"无法从关系 {relation.source_id} 提取章节号: {e}")
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
            ***REMOVED*** 支持所有实体类型
            core_entities_by_type = {}
            for entity_type in EntityType:
                if entity_type != EntityType.CHAPTER:  ***REMOVED*** 排除章节实体
                    core_entities_by_type[entity_type] = [e for e in core_entities if e.type == entity_type]
            
            ***REMOVED*** 2. 按类型分组候选实体（排除核心实体）
            remaining_entity_scores = [
                (score, entity) for score, entity in entity_scores
                if entity not in core_entities
            ]
            
            ***REMOVED*** 按类型分组（支持所有实体类型）
            entities_by_type_candidates = {}
            for entity_type in EntityType:
                if entity_type != EntityType.CHAPTER:  ***REMOVED*** 排除章节实体
                    entities_by_type_candidates[entity_type] = []
            
            for score, entity in remaining_entity_scores:
                entity_type = entity.type
                if entity_type in entities_by_type_candidates:
                    entities_by_type_candidates[entity_type].append((score, entity))
            
            ***REMOVED*** 3. 按类型设置最小配额（确保类型多样性）
            ***REMOVED*** 总配额 = max_entities - 核心实体数
            remaining_slots = max_entities - len(core_entities)
            
            ***REMOVED*** 类型配额分配策略（支持所有实体类型）：
            ***REMOVED*** - 角色：20%
            ***REMOVED*** - 地点/设定：20%
            ***REMOVED*** - 组织：8%
            ***REMOVED*** - 物品：15%
            ***REMOVED*** - 生物：5%
            ***REMOVED*** - 概念：12%
            ***REMOVED*** - 时间：5%
            ***REMOVED*** - 其他类型：15%（符号、情节节点等）
            type_quotas = {
                EntityType.CHARACTER: max(8, int(remaining_slots * 0.20)),   ***REMOVED*** 至少8个
                EntityType.LOCATION: max(5, int(remaining_slots * 0.20)),     ***REMOVED*** 至少5个
                EntityType.SETTING: max(3, int(remaining_slots * 0.10)),     ***REMOVED*** 至少3个（兼容旧类型）
                EntityType.ORGANIZATION: max(3, int(remaining_slots * 0.08)), ***REMOVED*** 至少3个
                EntityType.ITEM: max(4, int(remaining_slots * 0.15)),        ***REMOVED*** 至少4个
                EntityType.CREATURE: max(2, int(remaining_slots * 0.05)),     ***REMOVED*** 至少2个
                EntityType.CONCEPT: max(3, int(remaining_slots * 0.12)),     ***REMOVED*** 至少3个
                EntityType.TIME: max(2, int(remaining_slots * 0.05)),        ***REMOVED*** 至少2个
                EntityType.SYMBOL: max(2, int(remaining_slots * 0.05)),     ***REMOVED*** 至少2个
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
                ***REMOVED*** 按类型优先级排序（支持所有实体类型）
                type_priority = {
                    EntityType.LOCATION: 5,
                    EntityType.SETTING: 4,
                    EntityType.ORGANIZATION: 4,
                    EntityType.ITEM: 3,
                    EntityType.CONCEPT: 3,
                    EntityType.SYMBOL: 2,
                    EntityType.CREATURE: 2,
                    EntityType.TIME: 2,
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
            
            ***REMOVED*** 按类型分组（支持所有实体类型）
            entities_by_type = {}
            for entity_type in EntityType:
                if entity_type != EntityType.CHAPTER:  ***REMOVED*** 排除章节实体
                    entities_by_type[entity_type] = []
            
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
                    ***REMOVED*** 按类型优先级排序（支持所有实体类型）
                    type_priority = {
                        EntityType.LOCATION: 5,
                        EntityType.SETTING: 4,
                        EntityType.ORGANIZATION: 4,
                        EntityType.ITEM: 3,
                        EntityType.CONCEPT: 3,
                        EntityType.SYMBOL: 2,
                        EntityType.CREATURE: 2,
                        EntityType.TIME: 2,
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
                EntityType.LOCATION: "地点",
                EntityType.SETTING: "设定",
                EntityType.ORGANIZATION: "组织",
                EntityType.ITEM: "物品",
                EntityType.CREATURE: "生物",
                EntityType.CONCEPT: "概念",
                EntityType.TIME: "时间",
                EntityType.SYMBOL: "符号",
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