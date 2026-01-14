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
        enable_creative_context: bool = True
    ):
        """
        初始化小说创作器
        
        Args:
            novel_title: 小说标题
            output_dir: 输出目录，默认为 novel_creation/outputs/{novel_title}/
            enable_context_offloading: 是否启用上下文卸载
            enable_creative_context: 是否启用创作上下文系统（语义网格、动态路由、Pub/Sub）
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
"""
        
        ***REMOVED*** 使用 ReActAgent 生成大纲
        result = self.agent.run(query=prompt, verbose=True)
        
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
        plan_file = self.output_dir / "novel_plan.json"
        plan_file.write_text(
            json.dumps(plan, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        
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
        ***REMOVED*** 构建创作提示词
        context_info = ""
        if previous_chapters_summary:
            context_info = f"""
前面章节摘要：
{previous_chapters_summary}

请确保新章节与前面章节保持连贯性。
"""
        
        prompt = f"""请创作小说《{self.novel_title}》的第{chapter_number}章。

章节信息：
- 标题：{chapter_title}
- 摘要：{chapter_summary}
- 目标字数：{target_words}字
{context_info}

创作要求：
1. 严格按照章节摘要展开情节
2. 保持与前面章节的连贯性
3. 控制字数在目标范围内
4. 注意人物性格的一致性
5. 保持文笔流畅，情节紧凑

请直接返回章节正文内容，不要包含标题或其他格式。
"""
        
        ***REMOVED*** 使用 ReActAgent 创作章节
        logger.info(f"开始创作第{chapter_number}章：{chapter_title}")
        content = self.agent.run(query=prompt, verbose=True)
        
        ***REMOVED*** 创建章节对象
        chapter = NovelChapter(
            chapter_number=chapter_number,
            title=chapter_title,
            content=content,
            summary=chapter_summary,
            metadata={
                "target_words": target_words,
                "actual_words": len(content),
            }
        )
        
        ***REMOVED*** 保存章节
        self._save_chapter(chapter)
        
        ***REMOVED*** 生成章节摘要（用于后续章节的连贯性）
        chapter.summary = self._generate_chapter_summary(chapter)
        
        ***REMOVED*** 集成创作上下文系统
        if self.enable_creative_context:
            self._process_chapter_with_creative_context(chapter)
        
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
        """保存章节到文件"""
        ***REMOVED*** 保存完整章节
        chapter_file = self.output_dir / "chapters" / f"chapter_{chapter.chapter_number:03d}.txt"
        chapter_file.write_text(
            f"第{chapter.chapter_number}章 {chapter.title}\n\n{chapter.content}",
            encoding="utf-8"
        )
        
        ***REMOVED*** 保存章节元数据
        chapter_meta_file = self.output_dir / "chapters" / f"chapter_{chapter.chapter_number:03d}_meta.json"
        chapter_meta_file.write_text(
            json.dumps(chapter.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    
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
        
        ***REMOVED*** 3. 生成完整小说文件
        self._generate_full_novel()
        
        ***REMOVED*** 4. 保存元数据
        self._save_metadata()
        
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
        从章节中提取实体（简化实现）
        
        实际应该使用 NER 模型或 LLM 进行实体提取
        
        Args:
            chapter: 章节对象
        
        Returns:
            提取的实体列表
        """
        entities = []
        content = chapter.content
        
        ***REMOVED*** 简化的实体提取（示例）
        ***REMOVED*** 实际应该使用更智能的方法
        
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
                    metadata={"chapter": chapter.chapter_number}
                )
                entities.append(entity)
        
        ***REMOVED*** 提取物品/符号（简单关键词匹配）
        symbol_keywords = ["吊坠", "戒指", "剑", "书", "地图", "钥匙"]
        for keyword in symbol_keywords:
            if keyword in content:
                entity = Entity(
                    id=f"symbol_{chapter.chapter_number}_{keyword}",
                    type=EntityType.SYMBOL,
                    name=keyword,
                    content=f"在第{chapter.chapter_number}章中提到的{keyword}",
                    metadata={"chapter": chapter.chapter_number}
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
    
    def _save_metadata(self):
        """保存元数据"""
        metadata_file = self.output_dir / "metadata.json"
        
        ***REMOVED*** 添加创作上下文系统状态
        metadata = self.metadata.copy()
        if self.enable_creative_context:
            metadata["creative_context"] = {
                "enabled": True,
                "entities_count": len(self.semantic_mesh.entities),
                "relations_count": len(self.semantic_mesh.relations),
                "subscribers_count": len(self.memory_bus.subscriptions)
            }
        else:
            metadata["creative_context"] = {"enabled": False}
        
        metadata_file.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    
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