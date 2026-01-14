"""
统一编排器接口
支持 ReAct、Puppeteer、混合等多种编排方式
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

from novel_creation.react_novel_creator import NovelChapter

logger = logging.getLogger(__name__)


class NovelOrchestrator(ABC):
    """
    统一编排接口
    
    所有编排方式（ReAct、Puppeteer、混合）都实现这个接口
    """
    
    @abstractmethod
    def create_chapter(
        self,
        chapter_number: int,
        chapter_title: str,
        chapter_summary: str,
        previous_chapters_summary: Optional[str] = None,
        target_words: int = 3000,
        **kwargs
    ) -> NovelChapter:
        """
        创作章节
        
        Args:
            chapter_number: 章节编号
            chapter_title: 章节标题
            chapter_summary: 章节摘要
            previous_chapters_summary: 前面章节摘要
            target_words: 目标字数
            **kwargs: 其他参数
        
        Returns:
            NovelChapter 对象
        """
        pass
    
    @abstractmethod
    def get_context(self, chapter_number: int) -> Dict[str, Any]:
        """
        获取上下文
        
        Args:
            chapter_number: 章节编号
        
        Returns:
            上下文字典
        """
        pass
    
    @abstractmethod
    def store_memory(self, chapter: NovelChapter):
        """
        存储记忆
        
        Args:
            chapter: 章节对象
        """
        pass
    
    @abstractmethod
    def retrieve_memories(self, query: str, top_k: int = 5) -> List[Any]:
        """
        检索记忆
        
        Args:
            query: 查询字符串
            top_k: 返回数量
        
        Returns:
            记忆列表
        """
        pass


class ReActOrchestrator(NovelOrchestrator):
    """
    ReAct 编排实现
    
    使用 ReAct + 动态上下文系统
    """
    
    def __init__(
        self,
        novel_title: str,
        enable_creative_context: bool = True,
        enable_unimem: bool = False
    ):
        """
        初始化 ReAct 编排器
        
        Args:
            novel_title: 小说标题
            enable_creative_context: 是否启用创作上下文系统
            enable_unimem: 是否启用 UniMem（可选）
        """
        from novel_creation.react_novel_creator import ReactNovelCreator
        
        self.creator = ReactNovelCreator(
            novel_title=novel_title,
            enable_context_offloading=True,
            enable_creative_context=enable_creative_context
        )
        
        ***REMOVED*** 可选：集成 UniMem
        self.unimem = None
        if enable_unimem:
            try:
                from unimem import UniMem
                self.unimem = UniMem()
                logger.info("UniMem 已集成到 ReAct 编排器")
            except Exception as e:
                logger.warning(f"UniMem 集成失败: {e}")
    
    def create_chapter(self, **kwargs) -> NovelChapter:
        """创作章节"""
        return self.creator.create_chapter(**kwargs)
    
    def get_context(self, chapter_number: int) -> Dict[str, Any]:
        """获取上下文"""
        context = {}
        
        ***REMOVED*** 从语义网格获取
        if self.creator.enable_creative_context:
            chapter_entity_id = f"chapter_{chapter_number:03d}"
            related = self.creator.get_related_memories(chapter_entity_id)
            context['semantic_mesh'] = {
                'related_entities': [e.to_dict() for e in related]
            }
        
        ***REMOVED*** 从 UniMem 获取（如果启用）
        if self.unimem:
            try:
                memories = self.unimem.recall(
                    query=f"chapter {chapter_number}",
                    top_k=5
                )
                context['unimem'] = memories
            except Exception as e:
                logger.warning(f"UniMem 检索失败: {e}")
        
        return context
    
    def store_memory(self, chapter: NovelChapter):
        """存储记忆"""
        ***REMOVED*** 语义网格已自动存储（通过 _process_chapter_with_creative_context）
        
        ***REMOVED*** 存储到 UniMem（如果启用）
        if self.unimem:
            try:
                from unimem.memory_types import Experience, Context, Task
                
                experience = Experience(
                    content=chapter.content,
                    metadata={
                        "chapter_number": chapter.chapter_number,
                        "title": chapter.title,
                        "summary": chapter.summary
                    }
                )
                
                context = Context(
                    task=Task(
                        content=f"创作第{chapter.chapter_number}章",
                        metadata={"chapter_number": chapter.chapter_number}
                    )
                )
                
                memory = self.unimem.retain(experience, context)
                logger.info(f"章节 {chapter.chapter_number} 已存储到 UniMem: {memory.id}")
            except Exception as e:
                logger.warning(f"UniMem 存储失败: {e}")
    
    def retrieve_memories(self, query: str, top_k: int = 5) -> List[Any]:
        """检索记忆"""
        results = []
        
        ***REMOVED*** 从 UniMem 检索（如果启用）
        if self.unimem:
            try:
                memories = self.unimem.recall(query=query, top_k=top_k)
                results.extend(memories)
            except Exception as e:
                logger.warning(f"UniMem 检索失败: {e}")
        
        return results


class PuppeteerOrchestrator(NovelOrchestrator):
    """
    Puppeteer 编排实现
    
    使用 Puppeteer + UniMem 系统
    """
    
    def __init__(
        self,
        novel_title: str,
        puppeteer_config: Optional[Dict[str, Any]] = None
    ):
        """
        初始化 Puppeteer 编排器
        
        Args:
            novel_title: 小说标题
            puppeteer_config: Puppeteer 配置
        """
        ***REMOVED*** TODO: 实现 Puppeteer 集成
        ***REMOVED*** from puppeteer import PuppeteerSystem
        ***REMOVED*** self.puppeteer = PuppeteerSystem(config=puppeteer_config)
        
        ***REMOVED*** UniMem 是必需的
        try:
            from unimem import UniMem
            self.unimem = UniMem()
            logger.info("UniMem 已集成到 Puppeteer 编排器")
        except Exception as e:
            raise RuntimeError(f"Puppeteer 编排器需要 UniMem: {e}")
        
        self.novel_title = novel_title
        logger.warning("Puppeteer 编排器尚未完全实现")
    
    def create_chapter(self, **kwargs) -> NovelChapter:
        """创作章节（待实现）"""
        raise NotImplementedError("Puppeteer 编排器尚未完全实现")
    
    def get_context(self, chapter_number: int) -> Dict[str, Any]:
        """获取上下文"""
        ***REMOVED*** 从 UniMem 获取
        try:
            memories = self.unimem.recall(
                query=f"chapter {chapter_number}",
                top_k=10
            )
            return {'unimem': memories}
        except Exception as e:
            logger.warning(f"UniMem 检索失败: {e}")
            return {}
    
    def store_memory(self, chapter: NovelChapter):
        """存储记忆"""
        ***REMOVED*** 存储到 UniMem
        try:
            from unimem.memory_types import Experience, Context, Task
            
            experience = Experience(
                content=chapter.content,
                metadata={
                    "chapter_number": chapter.chapter_number,
                    "title": chapter.title
                }
            )
            
            context = Context(
                task=Task(
                    content=f"创作第{chapter.chapter_number}章",
                    metadata={"chapter_number": chapter.chapter_number}
                )
            )
            
            memory = self.unimem.retain(experience, context)
            logger.info(f"章节 {chapter.chapter_number} 已存储到 UniMem: {memory.id}")
        except Exception as e:
            logger.warning(f"UniMem 存储失败: {e}")
    
    def retrieve_memories(self, query: str, top_k: int = 5) -> List[Any]:
        """检索记忆"""
        try:
            return self.unimem.recall(query=query, top_k=top_k)
        except Exception as e:
            logger.warning(f"UniMem 检索失败: {e}")
            return []


class HybridOrchestrator(NovelOrchestrator):
    """
    混合编排实现
    
    根据章节特点自动选择编排方式
    """
    
    def __init__(
        self,
        novel_title: str,
        react_config: Optional[Dict[str, Any]] = None,
        puppeteer_config: Optional[Dict[str, Any]] = None
    ):
        """
        初始化混合编排器
        
        Args:
            novel_title: 小说标题
            react_config: ReAct 配置
            puppeteer_config: Puppeteer 配置
        """
        self.react = ReActOrchestrator(
            novel_title=novel_title,
            enable_creative_context=True,
            enable_unimem=True,
            **(react_config or {})
        )
        
        ***REMOVED*** Puppeteer 编排器（可选）
        self.puppeteer = None
        try:
            self.puppeteer = PuppeteerOrchestrator(
                novel_title=novel_title,
                puppeteer_config=puppeteer_config
            )
        except Exception as e:
            logger.warning(f"Puppeteer 编排器不可用: {e}")
        
        self.novel_title = novel_title
    
    def create_chapter(
        self,
        chapter_number: int,
        chapter_title: str,
        chapter_summary: str,
        previous_chapters_summary: Optional[str] = None,
        target_words: int = 3000,
        orchestrator_type: Optional[str] = None,
        **kwargs
    ) -> NovelChapter:
        """
        创作章节
        
        Args:
            orchestrator_type: 指定编排方式（'react' 或 'puppeteer'），None 时自动选择
            **kwargs: 其他参数
        """
        ***REMOVED*** 自动选择编排方式
        if orchestrator_type is None:
            orchestrator_type = self._select_orchestrator(chapter_summary)
        
        if orchestrator_type == 'puppeteer' and self.puppeteer:
            return self.puppeteer.create_chapter(
                chapter_number=chapter_number,
                chapter_title=chapter_title,
                chapter_summary=chapter_summary,
                previous_chapters_summary=previous_chapters_summary,
                target_words=target_words,
                **kwargs
            )
        else:
            ***REMOVED*** 默认使用 ReAct
            return self.react.create_chapter(
                chapter_number=chapter_number,
                chapter_title=chapter_title,
                chapter_summary=chapter_summary,
                previous_chapters_summary=previous_chapters_summary,
                target_words=target_words,
                **kwargs
            )
    
    def _select_orchestrator(self, chapter_summary: str) -> str:
        """
        根据章节摘要自动选择编排方式
        
        Args:
            chapter_summary: 章节摘要
        
        Returns:
            'react' 或 'puppeteer'
        """
        ***REMOVED*** 简单规则：包含"对话"、"心理"等关键词时使用 ReAct
        ***REMOVED*** 包含"行动"、"战斗"等关键词时使用 Puppeteer（如果可用）
        
        action_keywords = ["行动", "战斗", "执行", "操作"]
        if any(keyword in chapter_summary for keyword in action_keywords):
            if self.puppeteer:
                return 'puppeteer'
        
        ***REMOVED*** 默认使用 ReAct
        return 'react'
    
    def get_context(self, chapter_number: int) -> Dict[str, Any]:
        """获取上下文（合并两个编排器的上下文）"""
        context = {}
        
        ***REMOVED*** 从 ReAct 获取
        react_context = self.react.get_context(chapter_number)
        context.update(react_context)
        
        ***REMOVED*** 从 Puppeteer 获取（如果可用）
        if self.puppeteer:
            puppeteer_context = self.puppeteer.get_context(chapter_number)
            ***REMOVED*** 合并 UniMem 结果
            if 'unimem' in puppeteer_context:
                if 'unimem' not in context:
                    context['unimem'] = []
                context['unimem'].extend(puppeteer_context['unimem'])
        
        return context
    
    def store_memory(self, chapter: NovelChapter):
        """存储记忆（存储到两个编排器）"""
        self.react.store_memory(chapter)
        if self.puppeteer:
            self.puppeteer.store_memory(chapter)
    
    def retrieve_memories(self, query: str, top_k: int = 5) -> List[Any]:
        """检索记忆（合并两个编排器的结果）"""
        results = []
        
        ***REMOVED*** 从 ReAct 检索
        results.extend(self.react.retrieve_memories(query, top_k))
        
        ***REMOVED*** 从 Puppeteer 检索（如果可用）
        if self.puppeteer:
            results.extend(self.puppeteer.retrieve_memories(query, top_k))
        
        ***REMOVED*** 去重
        seen = set()
        unique_results = []
        for r in results:
            r_id = getattr(r, 'id', str(r))
            if r_id not in seen:
                seen.add(r_id)
                unique_results.append(r)
        
        return unique_results[:top_k]
