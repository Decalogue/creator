"""
创作编排器

基于 Puppeteer 框架实现智能 Agent 编排，支持小说和剧本创作。
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .novel_workflow import NovelWorkflow, NovelTask, NovelResult
from .script_workflow import ScriptWorkflow, ScriptTask, ScriptResult

logger = logging.getLogger(__name__)


@dataclass
class PuppeteerConfig:
    """Puppeteer 配置"""
    max_iterations: int = 10
    max_parallel_paths: int = 3
    checkpoint_path: Optional[str] = None


class CreativeOrchestrator:
    """创作编排器
    
    基于 Puppeteer 框架，协调多个创作 Agent 完成小说或剧本创作任务。
    """
    
    def __init__(
        self,
        puppeteer: Any,  ***REMOVED*** GraphReasoning 实例
        unimem: Any,  ***REMOVED*** UniMem 实例
        config: Optional[PuppeteerConfig] = None
    ):
        """
        初始化创作编排器
        
        Args:
            puppeteer: Puppeteer 框架实例（GraphReasoning）
            unimem: UniMem 记忆系统实例
            config: 配置选项
        """
        self.puppeteer = puppeteer
        self.unimem = unimem
        self.config = config or PuppeteerConfig()
        
        ***REMOVED*** 初始化工作流
        self.novel_workflow = NovelWorkflow(unimem=unimem)
        self.script_workflow = ScriptWorkflow(unimem=unimem)
        
        logger.info("CreativeOrchestrator initialized")
    
    def execute_novel_workflow(self, task: NovelTask) -> NovelResult:
        """
        执行小说创作工作流
        
        Args:
            task: 小说创作任务
            
        Returns:
            小说创作结果
        """
        try:
            logger.info(f"Starting novel workflow for task: {task.title}")
            
            ***REMOVED*** 1. 准备上下文（从 UniMem 检索相关记忆）
            context = self._prepare_context(task)
            
            ***REMOVED*** 2. 执行工作流
            result = self.novel_workflow.execute(task, context, self.puppeteer)
            
            ***REMOVED*** 3. 保存结果到 UniMem
            if result.success:
                self._save_to_memory(result, "novel")
            
            logger.info(f"Novel workflow completed: {result.success}")
            return result
            
        except Exception as e:
            logger.error(f"Error executing novel workflow: {e}", exc_info=True)
            return NovelResult(
                success=False,
                content="",
                error=str(e),
                metadata={}
            )
    
    def execute_script_workflow(self, task: ScriptTask) -> ScriptResult:
        """
        执行剧本创作工作流
        
        Args:
            task: 剧本创作任务
            
        Returns:
            剧本创作结果
        """
        try:
            logger.info(f"Starting script workflow for task: {task.title}")
            
            ***REMOVED*** 1. 准备上下文
            context = self._prepare_context(task)
            
            ***REMOVED*** 2. 执行工作流
            result = self.script_workflow.execute(task, context, self.puppeteer)
            
            ***REMOVED*** 3. 保存结果到 UniMem
            if result.success:
                self._save_to_memory(result, "script")
            
            logger.info(f"Script workflow completed: {result.success}")
            return result
            
        except Exception as e:
            logger.error(f"Error executing script workflow: {e}", exc_info=True)
            return ScriptResult(
                success=False,
                content="",
                error=str(e),
                metadata={}
            )
    
    def _prepare_context(self, task: Any) -> Dict[str, Any]:
        """准备上下文（从 UniMem 检索相关记忆）"""
        context = {
            "task": task,
            "memories": []
        }
        
        try:
            ***REMOVED*** 从 UniMem 检索相关记忆
            if hasattr(task, 'title') and task.title:
                query = task.title
            elif hasattr(task, 'description') and task.description:
                query = task.description
            else:
                query = "创作"
            
            ***REMOVED*** 调用 UniMem 的 recall 方法
            if self.unimem:
                retrieval_results = self.unimem.recall(query, top_k=10)
                if retrieval_results:
                    context["memories"] = [
                        {
                            "id": r.id,
                            "content": r.content,
                            "metadata": r.metadata
                        }
                        for r in retrieval_results
                    ]
        except Exception as e:
            logger.warning(f"Error preparing context: {e}")
        
        return context
    
    def _save_to_memory(self, result: Any, content_type: str) -> None:
        """保存创作结果到 UniMem"""
        try:
            from ..unimem.types import Experience, MemoryType
            
            ***REMOVED*** 创建经验对象
            experience = Experience(
                content=result.content,
                context=f"{content_type}创作结果",
                metadata={
                    "type": content_type,
                    "task": result.metadata,
                    "success": result.success
                }
            )
            
            ***REMOVED*** 保存到 UniMem
            if self.unimem:
                self.unimem.retain(experience)
                logger.debug(f"Saved {content_type} result to UniMem")
        except Exception as e:
            logger.warning(f"Error saving to memory: {e}")

