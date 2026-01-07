"""
并行执行器

实现并行章节生成，支持依赖管理和资源管理。
"""

import logging
import concurrent.futures
from typing import Dict, Any, List, Optional, Callable, Set
from dataclasses import dataclass

from .dependency_manager import DependencyManager, Task
from .resource_manager import ResourceManager, ResourceLimits

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """执行结果"""
    task_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0


class ParallelExecutor:
    """并行执行器
    
    实现并行章节生成，支持：
    - 依赖管理：根据依赖关系确定执行顺序
    - 资源管理：控制并发数和 API 调用频率
    - 并行执行：使用线程池并行执行任务
    """
    
    def __init__(
        self,
        dependency_manager: Optional[DependencyManager] = None,
        resource_manager: Optional[ResourceManager] = None,
        max_workers: int = 5
    ):
        """
        初始化并行执行器
        
        Args:
            dependency_manager: 依赖管理器
            resource_manager: 资源管理器
            max_workers: 最大并发工作线程数
        """
        self.dependency_manager = dependency_manager or DependencyManager()
        self.resource_manager = resource_manager or ResourceManager(
            limits=ResourceLimits(max_workers=max_workers)
        )
        self.max_workers = max_workers
        
        logger.info(f"ParallelExecutor initialized: max_workers={max_workers}")
    
    def execute_tasks(
        self,
        tasks: List[Task],
        executor_func: Callable[[Task], Any],
        wait_for_all: bool = True
    ) -> Dict[str, ExecutionResult]:
        """
        并行执行任务列表
        
        Args:
            tasks: 任务列表
            executor_func: 执行函数，接受 Task 对象，返回执行结果
            wait_for_all: 是否等待所有任务完成
            
        Returns:
            执行结果字典，key 为任务ID，value 为执行结果
        """
        ***REMOVED*** 1. 添加所有任务到依赖管理器
        for task in tasks:
            if not self.dependency_manager.add_task(task):
                logger.error(f"Failed to add task {task.id}")
        
        ***REMOVED*** 2. 获取执行顺序
        execution_order = self.dependency_manager.get_execution_order()
        
        if not execution_order:
            logger.error("Failed to get execution order (cycle detected?)")
            return {}
        
        logger.info(f"Execution order: {execution_order}")
        
        ***REMOVED*** 3. 并行执行
        results = {}
        completed_tasks: Set[str] = set()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            
            ***REMOVED*** 初始可执行任务
            ready_tasks = self.dependency_manager.get_ready_tasks(completed_tasks)
            
            ***REMOVED*** 提交初始任务
            for task_id in ready_tasks:
                task = self.dependency_manager.get_task(task_id)
                if task and self.resource_manager.acquire_worker():
                    future = executor.submit(self._execute_task, task, executor_func)
                    futures[future] = task_id
            
            ***REMOVED*** 处理完成的任务并提交新任务
            while futures:
                done, not_done = concurrent.futures.wait(
                    futures.keys(),
                    timeout=1.0,
                    return_when=concurrent.futures.FIRST_COMPLETED
                )
                
                for future in done:
                    task_id = futures[future]
                    task = self.dependency_manager.get_task(task_id)
                    
                    try:
                        result = future.result()
                        results[task_id] = result
                        completed_tasks.add(task_id)
                        
                        logger.info(f"Task {task_id} completed: {result.success}")
                    except Exception as e:
                        logger.error(f"Task {task_id} failed: {e}", exc_info=True)
                        results[task_id] = ExecutionResult(
                            task_id=task_id,
                            success=False,
                            error=str(e)
                        )
                        completed_tasks.add(task_id)
                    
                    ***REMOVED*** 释放资源
                    self.resource_manager.release_worker()
                    del futures[future]
                    
                    ***REMOVED*** 检查是否有新的可执行任务
                    new_ready_tasks = self.dependency_manager.get_ready_tasks(completed_tasks)
                    for new_task_id in new_ready_tasks:
                        if new_task_id not in [futures.get(f) for f in futures.keys()]:
                            new_task = self.dependency_manager.get_task(new_task_id)
                            if new_task and self.resource_manager.acquire_worker():
                                new_future = executor.submit(
                                    self._execute_task,
                                    new_task,
                                    executor_func
                                )
                                futures[new_future] = new_task_id
                
                if not wait_for_all and len(completed_tasks) >= len(tasks):
                    ***REMOVED*** 取消未完成的任务
                    for future in not_done:
                        future.cancel()
                    break
        
        logger.info(f"Execution completed: {len(results)}/{len(tasks)} tasks")
        return results
    
    def _execute_task(
        self,
        task: Task,
        executor_func: Callable[[Task], Any]
    ) -> ExecutionResult:
        """
        执行单个任务
        
        Args:
            task: 任务对象
            executor_func: 执行函数
            
        Returns:
            执行结果
        """
        import time
        start_time = time.time()
        
        try:
            ***REMOVED*** 等待 API 资源（如果需要）
            if not self.resource_manager.can_make_api_call():
                if not self.resource_manager.wait_for_resource("api", timeout=60.0):
                    return ExecutionResult(
                        task_id=task.id,
                        success=False,
                        error="API resource timeout"
                    )
            
            ***REMOVED*** 记录 API 调用
            self.resource_manager.record_api_call()
            
            ***REMOVED*** 执行任务
            result = executor_func(task)
            
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                task_id=task.id,
                success=True,
                result=result,
                execution_time=execution_time
            )
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error executing task {task.id}: {e}", exc_info=True)
            
            return ExecutionResult(
                task_id=task.id,
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    def execute_chapters_parallel(
        self,
        chapter_tasks: List[Dict[str, Any]],
        chapter_executor: Callable[[Dict[str, Any]], Any]
    ) -> Dict[str, ExecutionResult]:
        """
        并行执行章节生成
        
        Args:
            chapter_tasks: 章节任务列表，每个任务包含：
                - id: 章节ID
                - dependencies: 依赖的章节ID列表
                - content: 章节内容或生成参数
            chapter_executor: 章节执行函数
            
        Returns:
            执行结果字典
        """
        ***REMOVED*** 转换为 Task 对象
        tasks = []
        for chapter_task in chapter_tasks:
            task = Task(
                id=chapter_task.get("id", f"chapter_{len(tasks)}"),
                task_type="chapter",
                dependencies=chapter_task.get("dependencies", []),
                metadata=chapter_task
            )
            tasks.append(task)
        
        ***REMOVED*** 定义执行函数包装器
        def executor_wrapper(task: Task) -> Any:
            return chapter_executor(task.metadata)
        
        ***REMOVED*** 执行任务
        return self.execute_tasks(tasks, executor_wrapper)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取执行统计信息"""
        return {
            "dependency_stats": self.dependency_manager.get_statistics(),
            "resource_stats": self.resource_manager.get_usage_stats()
        }

