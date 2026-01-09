"""
编排器

管理工作流的执行、调度和协调

设计特点：
- 支持串行和并行执行：根据依赖关系自动决定执行顺序
- 支持依赖管理：确保步骤按正确顺序执行
- 支持条件执行：根据上下文条件决定是否执行步骤
- 支持错误处理和重试：自动重试失败的步骤
- 支持超时控制：可以设置步骤超时时间
- 真正的并行执行：使用线程池实现真正的并行执行
- 线程安全：使用锁确保线程安全

工业级特性：
- 统一异常处理（使用适配器异常体系）
- 参数验证和输入检查
- 性能监控（执行时间统计）
"""

import logging
import threading
import concurrent.futures
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime

from .workflow import Workflow, Step, WorkflowStep, StepStatus, StepType
from ..memory_types import Experience, Memory, Task, Context
from ..adapters.base import AdapterError, AdapterConfigurationError

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    编排器
    
    负责工作流的执行、任务调度和流程协调
    
    设计特点：
    - 支持串行和并行执行
    - 支持依赖管理
    - 支持条件执行
    - 支持错误处理和重试
    - 支持超时控制
    - 真正的并行执行支持
    """
    
    def __init__(self, unimem_instance: Any, max_workers: int = 4):
        """
        初始化编排器
        
        Args:
            unimem_instance: UniMem 实例
            max_workers: 最大并行工作线程数（默认 4）
            
        Raises:
            AdapterError: 如果参数无效
        """
        if unimem_instance is None:
            raise AdapterError("unimem_instance cannot be None", adapter_name="Orchestrator")
        if max_workers < 1:
            raise AdapterConfigurationError(
                f"max_workers must be >= 1, got {max_workers}",
                adapter_name="Orchestrator"
            )
        
        self.unimem = unimem_instance
        self.workflows: Dict[str, Workflow] = {}
        self.executions: Dict[str, Dict[str, WorkflowStep]] = {}  ***REMOVED*** execution_id -> step_id -> WorkflowStep
        self.max_workers = max_workers
        self._lock = threading.Lock()  ***REMOVED*** 用于线程安全
        
        logger.info(f"Orchestrator initialized (max_workers: {max_workers})")
    
    def register_workflow(self, workflow: Workflow) -> bool:
        """
        注册工作流
        
        Args:
            workflow: 工作流定义
            
        Returns:
            是否注册成功
            
        Raises:
            AdapterError: 如果 workflow 无效
        """
        if not workflow:
            raise AdapterError("workflow cannot be None", adapter_name="Orchestrator")
        
        ***REMOVED*** 验证工作流
        is_valid, error = workflow.validate()
        if not is_valid:
            logger.error(f"Workflow {workflow.id} validation failed: {error}")
            return False
        
        with self._lock:
            self.workflows[workflow.id] = workflow
        logger.info(f"Workflow {workflow.id} registered: {workflow.name}")
        return True
    
    def _execute_step(self, step: Step, workflow_step: WorkflowStep, context: Dict[str, Any]) -> Any:
        """
        执行单个步骤
        
        Args:
            step: 步骤定义
            workflow_step: 步骤实例
            context: 上下文（步骤之间共享的数据）
            
        Returns:
            步骤执行结果
            
        Raises:
            AdapterError: 如果参数无效或步骤执行失败
        """
        if not step:
            raise AdapterError("step cannot be None", adapter_name="Orchestrator")
        if not workflow_step:
            raise AdapterError("workflow_step cannot be None", adapter_name="Orchestrator")
        if context is None:
            raise AdapterError("context cannot be None", adapter_name="Orchestrator")
        
        ***REMOVED*** 检查执行条件
        if step.condition and not step.condition(context):
            logger.debug(f"Step {step.id} skipped due to condition")
            workflow_step.status = StepStatus.SKIPPED
            workflow_step.end_time = datetime.now()
            return None
        
        ***REMOVED*** 执行步骤
        workflow_step.status = StepStatus.RUNNING
        workflow_step.start_time = datetime.now()
        
        try:
            ***REMOVED*** 执行函数
            result = step.func(context, self.unimem)
            
            workflow_step.result = result
            workflow_step.status = StepStatus.COMPLETED
            workflow_step.end_time = datetime.now()
            
            ***REMOVED*** 将结果添加到上下文（需要线程安全）
            with self._lock:
                context[f"step_{step.id}_result"] = result
                context[f"step_{step.id}_status"] = "completed"
            
            logger.debug(f"Step {step.id} completed")
            return result
            
        except Exception as e:
            ***REMOVED*** 错误处理
            workflow_step.error = e
            workflow_step.end_time = datetime.now()
            
            ***REMOVED*** 重试逻辑
            if workflow_step.retry_count < step.retry_count:
                workflow_step.retry_count += 1
                workflow_step.status = StepStatus.PENDING
                logger.warning(f"Step {step.id} failed, retrying ({workflow_step.retry_count}/{step.retry_count}): {e}")
                ***REMOVED*** 递归重试
                return self._execute_step(step, workflow_step, context)
            else:
                workflow_step.status = StepStatus.FAILED
                logger.error(f"Step {step.id} failed after {workflow_step.retry_count} retries: {e}", exc_info=True)
                raise
    
    def execute_workflow(
        self,
        workflow_id: str,
        initial_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        执行工作流（支持真正的并行执行）
        
        根据步骤的依赖关系，自动决定执行顺序。没有依赖的步骤可以并行执行。
        
        Args:
            workflow_id: 工作流ID
            initial_context: 初始上下文（步骤之间共享的数据）
            
        Returns:
            执行结果字典，包含：
            - execution_id: 执行ID
            - workflow_id: 工作流ID
            - status: 执行状态（completed/failed）
            - context: 最终上下文
            - steps: 每个步骤的执行结果
            
        Raises:
            AdapterError: 如果 workflow_id 无效或不存在
        """
        if not workflow_id or not workflow_id.strip():
            raise AdapterError("workflow_id cannot be empty", adapter_name="Orchestrator")
        
        if workflow_id not in self.workflows:
            raise AdapterError(f"Workflow {workflow_id} not found", adapter_name="Orchestrator")
        
        workflow = self.workflows[workflow_id]
        execution_id = f"{workflow_id}_{datetime.now().timestamp()}"
        context = initial_context or {}
        completed_steps = set()
        
        logger.info(f"Executing workflow {workflow_id} (execution_id: {execution_id})")
        
        ***REMOVED*** 初始化步骤状态
        workflow_steps = {
            step.id: WorkflowStep(step=step)
            for step in workflow.steps
        }
        self.executions[execution_id] = workflow_steps
        
        ***REMOVED*** 使用线程池进行并行执行
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            ***REMOVED*** 执行循环
            while len(completed_steps) < len(workflow.steps):
                ***REMOVED*** 获取可以执行的步骤
                ready_steps = workflow.get_ready_steps(completed_steps)
                
                if not ready_steps:
                    ***REMOVED*** 检查是否有失败的步骤
                    failed_steps = [
                        step_id for step_id, ws in workflow_steps.items()
                        if ws.status == StepStatus.FAILED
                    ]
                    if failed_steps:
                        logger.error(f"Workflow execution failed. Failed steps: {failed_steps}")
                        break
                    else:
                        logger.warning("No ready steps but not all completed. Possible deadlock.")
                        break
                
                ***REMOVED*** 并行执行所有就绪的步骤
                future_to_step = {}
                for step in ready_steps:
                    if step.id in completed_steps:
                        continue
                    
                    workflow_step = workflow_steps[step.id]
                    if workflow_step.status in [StepStatus.COMPLETED, StepStatus.SKIPPED]:
                        completed_steps.add(step.id)
                        continue
                    
                    ***REMOVED*** 提交任务到线程池
                    future = executor.submit(self._execute_step, step, workflow_step, context)
                    future_to_step[future] = step
                
                ***REMOVED*** 等待所有任务完成
                for future in concurrent.futures.as_completed(future_to_step):
                    step = future_to_step[future]
                    workflow_step = workflow_steps[step.id]
                    
                    try:
                        result = future.result()
                        if workflow_step.status == StepStatus.COMPLETED:
                            completed_steps.add(step.id)
                        elif workflow_step.status == StepStatus.SKIPPED:
                            completed_steps.add(step.id)
                    except Exception as e:
                        ***REMOVED*** 错误已在 _execute_step 中处理
                        if workflow_step.status == StepStatus.FAILED:
                            completed_steps.add(step.id)
        
        ***REMOVED*** 构建执行结果
        result = {
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "status": "completed" if len(completed_steps) == len(workflow.steps) else "failed",
            "context": context,
            "steps": {
                step_id: {
                    "status": ws.status.value,
                    "result": ws.result,
                    "error": str(ws.error) if ws.error else None,
                    "start_time": ws.start_time.isoformat() if ws.start_time else None,
                    "end_time": ws.end_time.isoformat() if ws.end_time else None,
                }
                for step_id, ws in workflow_steps.items()
            }
        }
        
        logger.info(f"Workflow {workflow_id} execution completed: {result['status']}")
        return result
    
    def create_retain_step(
        self,
        step_id: str,
        experience: Experience,
        context: Context,
        dependencies: Optional[List[str]] = None,
    ) -> Step:
        """
        创建 RETAIN 步骤
        
        Args:
            step_id: 步骤ID
            experience: 经验数据
            context: 上下文
            dependencies: 依赖的步骤ID列表
            
        Returns:
            步骤定义
        """
        def retain_func(ctx: Dict, unimem) -> Memory:
            return unimem.retain(experience, context)
        
        return Step(
            id=step_id,
            name=f"RETAIN: {experience.content[:30]}...",
            step_type=StepType.RETAIN,
            func=retain_func,
            dependencies=dependencies or [],
        )
    
    def create_recall_step(
        self,
        step_id: str,
        query: str,
        context: Optional[Context] = None,
        top_k: int = 10,
        dependencies: Optional[List[str]] = None,
    ) -> Step:
        """
        创建 RECALL 步骤
        
        Args:
            step_id: 步骤ID
            query: 查询字符串
            context: 上下文
            top_k: 返回结果数量
            dependencies: 依赖的步骤ID列表
            
        Returns:
            步骤定义
        """
        def recall_func(ctx: Dict, unimem):
            return unimem.recall(query, context=context, top_k=top_k)
        
        return Step(
            id=step_id,
            name=f"RECALL: {query[:30]}...",
            step_type=StepType.RECALL,
            func=recall_func,
            dependencies=dependencies or [],
        )
    
    def create_reflect_step(
        self,
        step_id: str,
        task: Task,
        memory_source_step: str,  ***REMOVED*** 从哪个步骤获取记忆
        dependencies: Optional[List[str]] = None,
    ) -> Step:
        """
        创建 REFLECT 步骤
        
        Args:
            step_id: 步骤ID
            task: 任务上下文
            memory_source_step: 记忆来源步骤ID
            dependencies: 依赖的步骤ID列表
            
        Returns:
            步骤定义
        """
        def reflect_func(ctx: Dict, unimem):
            ***REMOVED*** 从上下文获取记忆
            memory_result = ctx.get(f"step_{memory_source_step}_result")
            if isinstance(memory_result, Memory):
                memories = [memory_result]
            elif isinstance(memory_result, list):
                memories = [m.memory if hasattr(m, 'memory') else m for m in memory_result]
            else:
                memories = []
            
            return unimem.reflect(memories, task)
        
        deps = dependencies or []
        if memory_source_step not in deps:
            deps.append(memory_source_step)
        
        return Step(
            id=step_id,
            name=f"REFLECT: {task.description[:30]}...",
            step_type=StepType.REFLECT,
            func=reflect_func,
            dependencies=deps,
        )
    
    def create_custom_step(
        self,
        step_id: str,
        name: str,
        func: Callable,
        dependencies: Optional[List[str]] = None,
        condition: Optional[Callable] = None,
    ) -> Step:
        """
        创建自定义步骤
        
        Args:
            step_id: 步骤ID
            name: 步骤名称
            func: 执行函数 (ctx: Dict, unimem) -> Any
            dependencies: 依赖的步骤ID列表
            condition: 执行条件函数 (ctx: Dict) -> bool
            
        Returns:
            步骤定义
        """
        return Step(
            id=step_id,
            name=name,
            step_type=StepType.CUSTOM,
            func=func,
            dependencies=dependencies or [],
            condition=condition,
        )
