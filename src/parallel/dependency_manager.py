"""
依赖管理器

管理创作任务之间的依赖关系，支持依赖图构建和拓扑排序。
"""

import logging
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


@dataclass
class Task:
    """任务节点"""
    id: str
    task_type: str  ***REMOVED*** chapter, scene, etc.
    dependencies: List[str] = field(default_factory=list)  ***REMOVED*** 依赖的任务ID列表
    metadata: Dict[str, Any] = field(default_factory=dict)


class DependencyGraph:
    """依赖图
    
    管理任务之间的依赖关系，支持：
    - 添加任务和依赖
    - 拓扑排序
    - 检测循环依赖
    - 获取可执行任务列表
    """
    
    def __init__(self):
        """初始化依赖图"""
        self.tasks: Dict[str, Task] = {}
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)  ***REMOVED*** task_id -> 依赖的任务ID集合
        self.dependents: Dict[str, Set[str]] = defaultdict(set)  ***REMOVED*** task_id -> 依赖此任务的任务ID集合
        logger.info("DependencyGraph initialized")
    
    def add_task(self, task: Task) -> bool:
        """
        添加任务
        
        Args:
            task: 任务对象
            
        Returns:
            是否成功添加
        """
        if task.id in self.tasks:
            logger.warning(f"Task {task.id} already exists")
            return False
        
        self.tasks[task.id] = task
        
        ***REMOVED*** 添加依赖关系
        for dep_id in task.dependencies:
            if dep_id not in self.tasks:
                logger.warning(f"Dependency {dep_id} not found for task {task.id}")
                continue
            
            self.dependencies[task.id].add(dep_id)
            self.dependents[dep_id].add(task.id)
        
        logger.debug(f"Added task {task.id} with {len(task.dependencies)} dependencies")
        return True
    
    def remove_task(self, task_id: str) -> bool:
        """移除任务"""
        if task_id not in self.tasks:
            return False
        
        ***REMOVED*** 移除依赖关系
        for dep_id in self.dependencies[task_id]:
            self.dependents[dep_id].discard(task_id)
        
        for dependent_id in self.dependents[task_id]:
            self.dependencies[dependent_id].discard(task_id)
        
        del self.tasks[task_id]
        del self.dependencies[task_id]
        del self.dependents[task_id]
        
        return True
    
    def has_cycle(self) -> bool:
        """
        检测是否存在循环依赖
        
        Returns:
            是否存在循环依赖
        """
        ***REMOVED*** 使用 DFS 检测循环
        visited = set()
        rec_stack = set()
        
        def dfs(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            
            for dep_id in self.dependencies.get(node_id, set()):
                if dep_id not in visited:
                    if dfs(dep_id):
                        return True
                elif dep_id in rec_stack:
                    return True
            
            rec_stack.remove(node_id)
            return False
        
        for task_id in self.tasks:
            if task_id not in visited:
                if dfs(task_id):
                    return True
        
        return False
    
    def topological_sort(self) -> List[str]:
        """
        拓扑排序
        
        Returns:
            排序后的任务ID列表（如果存在循环依赖，返回空列表）
        """
        if self.has_cycle():
            logger.error("Cycle detected in dependency graph")
            return []
        
        ***REMOVED*** Kahn's algorithm
        in_degree = {task_id: len(self.dependencies.get(task_id, set())) 
                    for task_id in self.tasks}
        
        queue = deque([task_id for task_id, degree in in_degree.items() if degree == 0])
        result = []
        
        while queue:
            task_id = queue.popleft()
            result.append(task_id)
            
            for dependent_id in self.dependents.get(task_id, set()):
                in_degree[dependent_id] -= 1
                if in_degree[dependent_id] == 0:
                    queue.append(dependent_id)
        
        if len(result) != len(self.tasks):
            logger.error("Topological sort failed: not all tasks included")
            return []
        
        return result
    
    def get_ready_tasks(self, completed_tasks: Set[str]) -> List[str]:
        """
        获取可执行的任务列表（所有依赖都已完成）
        
        Args:
            completed_tasks: 已完成的任务ID集合
            
        Returns:
            可执行的任务ID列表
        """
        ready = []
        
        for task_id, deps in self.dependencies.items():
            if task_id in completed_tasks:
                continue
            
            ***REMOVED*** 检查所有依赖是否都已完成
            if all(dep_id in completed_tasks for dep_id in deps):
                ready.append(task_id)
        
        return ready
    
    def get_dependencies(self, task_id: str) -> Set[str]:
        """获取任务的所有依赖"""
        return self.dependencies.get(task_id, set()).copy()
    
    def get_dependents(self, task_id: str) -> Set[str]:
        """获取依赖此任务的所有任务"""
        return self.dependents.get(task_id, set()).copy()


class DependencyManager:
    """依赖管理器
    
    管理创作任务的依赖关系，支持：
    - 构建依赖图
    - 检测循环依赖
    - 获取执行顺序
    - 动态更新依赖
    """
    
    def __init__(self):
        """初始化依赖管理器"""
        self.graph = DependencyGraph()
        logger.info("DependencyManager initialized")
    
    def add_task(self, task: Task) -> bool:
        """添加任务"""
        if not self.graph.add_task(task):
            return False
        
        ***REMOVED*** 检查循环依赖
        if self.graph.has_cycle():
            logger.error(f"Cycle detected after adding task {task.id}")
            self.graph.remove_task(task.id)
            return False
        
        return True
    
    def get_execution_order(self) -> List[str]:
        """
        获取执行顺序（拓扑排序）
        
        Returns:
            任务ID列表，按执行顺序排列
        """
        return self.graph.topological_sort()
    
    def get_ready_tasks(self, completed_tasks: Set[str]) -> List[str]:
        """
        获取可执行的任务列表
        
        Args:
            completed_tasks: 已完成的任务ID集合
            
        Returns:
            可执行的任务ID列表
        """
        return self.graph.get_ready_tasks(completed_tasks)
    
    def mark_completed(self, task_id: str) -> bool:
        """
        标记任务为已完成
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功标记
        """
        if task_id not in self.graph.tasks:
            logger.warning(f"Task {task_id} not found")
            return False
        
        ***REMOVED*** 这里可以添加完成标记的逻辑
        logger.debug(f"Task {task_id} marked as completed")
        return True
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务对象"""
        return self.graph.tasks.get(task_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_tasks": len(self.graph.tasks),
            "has_cycle": self.graph.has_cycle(),
            "max_dependencies": max(
                (len(deps) for deps in self.graph.dependencies.values()),
                default=0
            )
        }

