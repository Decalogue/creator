"""
工作流定义

定义工作流步骤和流程

设计特点：
- 步骤定义：支持多种步骤类型（RETAIN, RECALL, REFLECT, CUSTOM）
- 依赖管理：支持步骤之间的依赖关系
- 条件执行：支持根据上下文条件决定是否执行步骤
- 状态跟踪：跟踪每个步骤的执行状态和结果
- 循环检测：自动检测循环依赖
- 验证机制：验证工作流定义的合法性
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable, Set
from enum import Enum
from datetime import datetime

from ..types import Experience, Memory, Task, Context


class StepStatus(Enum):
    """步骤状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class StepType(Enum):
    """步骤类型"""
    RETAIN = "retain"
    RECALL = "recall"
    REFLECT = "reflect"
    CUSTOM = "custom"


@dataclass
class Step:
    """
    工作流步骤
    
    定义单个步骤的执行逻辑
    """
    id: str
    name: str
    step_type: StepType
    func: Callable  ***REMOVED*** 执行函数
    dependencies: List[str] = field(default_factory=list)  ***REMOVED*** 依赖的步骤ID
    condition: Optional[Callable] = None  ***REMOVED*** 执行条件
    retry_count: int = 0  ***REMOVED*** 重试次数
    timeout: Optional[float] = None  ***REMOVED*** 超时时间（秒）
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowStep:
    """
    工作流步骤实例
    
    包含步骤的执行状态和结果
    """
    step: Step
    status: StepStatus = StepStatus.PENDING
    result: Any = None
    error: Optional[Exception] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    retry_count: int = 0


@dataclass
class Workflow:
    """
    工作流定义
    
    定义完整的工作流程，包含多个步骤和它们之间的依赖关系
    """
    id: str
    name: str
    description: str
    steps: List[Step]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_step(self, step_id: str) -> Optional[Step]:
        """获取步骤"""
        for step in self.steps:
            if step.id == step_id:
                return step
        return None
    
    def get_ready_steps(self, completed_steps: Set[str]) -> List[Step]:
        """
        获取可以执行的步骤
        
        返回所有依赖都已满足的步骤，这些步骤可以并行执行。
        
        Args:
            completed_steps: 已完成的步骤ID集合
            
        Returns:
            可以执行的步骤列表（所有依赖都已满足）
        """
        if not completed_steps:
            completed_steps = set()
        
        ready = []
        for step in self.steps:
            ***REMOVED*** 检查所有依赖是否都已完成
            if all(dep in completed_steps for dep in step.dependencies):
                ready.append(step)
        return ready
    
    def _detect_cycles(self) -> Optional[List[str]]:
        """
        检测循环依赖
        
        使用 DFS（深度优先搜索）检测依赖图中的循环。
        
        Returns:
            如果存在循环，返回循环路径；否则返回 None
        """
        ***REMOVED*** 构建依赖图
        graph: Dict[str, List[str]] = {step.id: step.dependencies for step in self.steps}
        
        ***REMOVED*** DFS 检测循环
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        path: List[str] = []
        cycle_path: Optional[List[str]] = None
        
        def dfs(node: str) -> bool:
            """深度优先搜索检测循环"""
            nonlocal cycle_path
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for dep in graph.get(node, []):
                if dep not in visited:
                    if dfs(dep):
                        return True
                elif dep in rec_stack:
                    ***REMOVED*** 找到循环：从循环起点到当前节点
                    cycle_start = path.index(dep)
                    cycle_path = path[cycle_start:] + [dep]
                    return True
            
            rec_stack.remove(node)
            path.pop()
            return False
        
        for step_id in graph:
            if step_id not in visited:
                if dfs(step_id):
                    return cycle_path
        
        return None
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        验证工作流定义
        
        检查工作流的合法性，包括：
        - 步骤ID唯一性
        - 依赖是否存在
        - 循环依赖检测
        
        Returns:
            (是否有效, 错误信息)
            
        Examples:
            >>> workflow = Workflow(...)
            >>> is_valid, error = workflow.validate()
            >>> if not is_valid:
            ...     print(f"Validation failed: {error}")
        """
        if not self.steps:
            return False, "工作流必须包含至少一个步骤"
        
        ***REMOVED*** 检查步骤ID唯一性
        step_ids = [step.id for step in self.steps]
        if len(step_ids) != len(set(step_ids)):
            duplicates = [sid for sid in step_ids if step_ids.count(sid) > 1]
            return False, f"步骤ID必须唯一，发现重复: {set(duplicates)}"
        
        ***REMOVED*** 检查依赖是否存在
        step_ids_set = set(step_ids)
        for step in self.steps:
            for dep_id in step.dependencies:
                if dep_id not in step_ids_set:
                    return False, f"步骤 {step.id} 的依赖 {dep_id} 不存在"
        
        ***REMOVED*** 检查循环依赖
        cycle = self._detect_cycles()
        if cycle:
            return False, f"检测到循环依赖: {' -> '.join(cycle)}"
        
        return True, None
