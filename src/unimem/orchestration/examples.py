"""
编排使用示例

展示如何使用编排器创建工作流

示例包括：
- 基本的串行执行流程（RETAIN -> RECALL -> REFLECT）
- 并行执行多个检索任务
- 条件执行（根据上下文决定是否执行步骤）
"""

from typing import Dict
from datetime import datetime
from .orchestrator import Orchestrator
from .workflow import Workflow, StepType
from ..types import Experience, Context, Task


def create_retain_recall_reflect_workflow(orchestrator: Orchestrator) -> Workflow:
    """
    创建典型的 RETAIN -> RECALL -> REFLECT 工作流
    
    展示基本的串行执行流程
    """
    ***REMOVED*** 1. RETAIN 步骤
    experience = Experience(
        content="用户喜欢在早上喝咖啡，并且偏爱深度烘焙的豆子。",
        timestamp=datetime.now(),
        context="早餐偏好讨论"
    )
    context = Context(session_id="session_001", user_id="user_123")
    
    retain_step = orchestrator.create_retain_step(
        step_id="retain_1",
        experience=experience,
        context=context,
    )
    
    ***REMOVED*** 2. RECALL 步骤（依赖 RETAIN）
    recall_step = orchestrator.create_recall_step(
        step_id="recall_1",
        query="用户的早餐偏好是什么？",
        context=context,
        top_k=5,
        dependencies=["retain_1"],
    )
    
    ***REMOVED*** 3. REFLECT 步骤（依赖 RECALL）
    task = Task(
        id="task_001",
        description="更新用户画像",
        context="根据最新交互更新用户对咖啡的偏好"
    )
    
    reflect_step = orchestrator.create_reflect_step(
        step_id="reflect_1",
        task=task,
        memory_source_step="recall_1",
        dependencies=["recall_1"],
    )
    
    ***REMOVED*** 创建工作流
    workflow = Workflow(
        id="retain_recall_reflect",
        name="典型的记忆操作流程",
        description="RETAIN -> RECALL -> REFLECT 的完整流程",
        steps=[retain_step, recall_step, reflect_step],
    )
    
    return workflow


def create_parallel_retrieval_workflow(orchestrator: Orchestrator) -> Workflow:
    """
    创建并行检索工作流
    
    展示并行执行多个检索任务
    """
    context = Context(session_id="session_001", user_id="user_123")
    
    ***REMOVED*** 多个并行的 RECALL 步骤
    recall_steps = [
        orchestrator.create_recall_step(
            step_id=f"recall_{i}",
            query=query,
            context=context,
            top_k=5,
        )
        for i, query in enumerate([
            "用户的早餐偏好",
            "用户的编程偏好",
            "用户的界面设计偏好",
        ])
    ]
    
    ***REMOVED*** 合并结果的步骤（依赖所有检索步骤）
    def merge_results(ctx: Dict, unimem):
        """合并多个检索结果"""
        all_results = []
        for i in range(3):
            result = ctx.get(f"step_recall_{i}_result")
            if result:
                all_results.extend(result)
        
        ***REMOVED*** 去重
        seen_ids = set()
        unique_results = []
        for r in all_results:
            memory_id = r.memory.id if hasattr(r, 'memory') else r.id
            if memory_id not in seen_ids:
                seen_ids.add(memory_id)
                unique_results.append(r)
        
        return unique_results
    
    merge_step = orchestrator.create_custom_step(
        step_id="merge_results",
        name="合并检索结果",
        func=merge_results,
        dependencies=[f"recall_{i}" for i in range(3)],
    )
    
    workflow = Workflow(
        id="parallel_retrieval",
        name="并行检索工作流",
        description="并行执行多个检索任务，然后合并结果",
        steps=recall_steps + [merge_step],
    )
    
    return workflow


def create_conditional_workflow(orchestrator: Orchestrator) -> Workflow:
    """
    创建条件执行工作流
    
    展示根据条件决定是否执行某些步骤
    """
    context = Context(session_id="session_001", user_id="user_123")
    
    ***REMOVED*** 1. 检索步骤
    recall_step = orchestrator.create_recall_step(
        step_id="recall_check",
        query="用户是否有咖啡偏好记录？",
        context=context,
        top_k=1,
    )
    
    ***REMOVED*** 2. 条件步骤：如果有记录则更新，否则创建
    def update_or_create_func(ctx: Dict, unimem):
        """根据检索结果决定更新或创建"""
        recall_result = ctx.get("step_recall_check_result", [])
        
        if recall_result:
            ***REMOVED*** 有记录，执行更新
            task = Task(
                id="task_update",
                description="更新现有记录",
                context="更新用户咖啡偏好"
            )
            memories = [r.memory for r in recall_result if hasattr(r, 'memory')]
            return unimem.reflect(memories, task)
        else:
            ***REMOVED*** 无记录，创建新记录
            experience = Experience(
                content="用户喜欢在早上喝咖啡",
                timestamp=datetime.now(),
                context="创建新偏好记录"
            )
            return unimem.retain(experience, context)
    
    ***REMOVED*** 条件：检查是否有检索结果
    def has_results(ctx: Dict) -> bool:
        result = ctx.get("step_recall_check_result", [])
        return len(result) > 0
    
    update_step = orchestrator.create_custom_step(
        step_id="update_or_create",
        name="更新或创建",
        func=update_or_create_func,
        dependencies=["recall_check"],
        condition=has_results,  ***REMOVED*** 只在有结果时执行
    )
    
    create_step = orchestrator.create_custom_step(
        step_id="create_new",
        name="创建新记录",
        func=lambda ctx, unimem: unimem.retain(
            Experience(
                content="用户喜欢在早上喝咖啡",
                timestamp=datetime.now(),
                context="创建新偏好记录"
            ),
            context
        ),
        dependencies=["recall_check"],
        condition=lambda ctx: len(ctx.get("step_recall_check_result", [])) == 0,  ***REMOVED*** 只在无结果时执行
    )
    
    workflow = Workflow(
        id="conditional_workflow",
        name="条件执行工作流",
        description="根据检索结果决定更新或创建",
        steps=[recall_step, update_step, create_step],
    )
    
    return workflow

