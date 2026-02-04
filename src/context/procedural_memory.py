"""
过程记忆与角色感知（Procedural & Role-Aware Memory）

参考 LEGOMem：将执行轨迹拆分为可复用单元，按角色（编排器 vs 任务 Agent）差异化存储与检索。
- 编排器：full_task 级记忆（任务描述、高层计划、端到端轨迹）
- 任务 Agent：subtask 级记忆（单步输入/输出、结果）

与 semantic_mesh（实体/事实）互补：过程记忆存「怎么做的」，不存「故事里有什么」。
"""

from typing import Any, Dict, List, Optional

from unimem.memory_types import (
    Experience,
    Context,
    Task,
    MemoryType,
    PROCEDURAL_TAG,
    ROLE_ORCHESTRATOR,
    ROLE_TASK_AGENT,
    SCOPE_FULL_TASK,
    SCOPE_SUBTASK,
    agent_tag,
)


def _procedural_tags(
    role: str,
    scope: str,
    agent_name: Optional[str] = None,
) -> List[str]:
    """构建过程记忆的 tags 列表（用于 retain 的 context.metadata["tags"]）"""
    tags = [PROCEDURAL_TAG, f"role:{role}", f"scope:{scope}"]
    if agent_name:
        tags.append(agent_tag(agent_name))
    return tags


def store_procedural(
    unimem: Any,
    content: str,
    role: str,
    scope: str,
    agent_name: Optional[str] = None,
    novel_title: Optional[str] = None,
    task_summary: Optional[str] = None,
    decision_trace: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Optional[Any]:
    """
    存储一条过程记忆（可复用轨迹单元）。

    Args:
        unimem: UniMem 实例（core.UniMem）
        content: 记忆内容（如计划摘要、章节写作结果摘要）
        role: 角色，ROLE_ORCHESTRATOR 或 ROLE_TASK_AGENT
        scope: 范围，SCOPE_FULL_TASK 或 SCOPE_SUBTASK
        agent_name: 任务 Agent 名称，如 planner, writer, quality
        novel_title: 作品名（可选）
        task_summary: 任务摘要（可选，写入 context）
        decision_trace: 决策痕迹（可选，传入 context.metadata）
        metadata: 额外元数据（与 decision_trace 等合并）

    Returns:
        存储后的 Memory，失败返回 None
    """
    if not unimem:
        return None
    try:
        experience = Experience(
            content=content,
            metadata=metadata or {},
        )
        meta = {
            "memory_type": MemoryType.EXPERIENCE.value,
            "tags": _procedural_tags(role, scope, agent_name),
        }
        if novel_title:
            meta["novel_title"] = novel_title
        if decision_trace:
            meta["decision_trace"] = decision_trace
        task_content = task_summary or content[:200]
        context = Context(
            task=Task(content=task_content, metadata={"novel_title": novel_title} if novel_title else {}),
            metadata=meta,
        )
        memory = unimem.retain(experience, context)
        return memory
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("store_procedural failed: %s", e, exc_info=True)
        return None


def recall_procedural(
    unimem: Any,
    query: str,
    role: Optional[str] = None,
    scope: Optional[str] = None,
    agent_name: Optional[str] = None,
    top_k: int = 10,
) -> List[Any]:
    """
    按角色/范围检索过程记忆（角色感知）。

    Args:
        unimem: UniMem 实例
        query: 查询字符串（如「大纲 计划」「章节 写作」）
        role: 仅检索该角色，如 ROLE_ORCHESTRATOR / ROLE_TASK_AGENT
        scope: 仅检索该范围，如 SCOPE_FULL_TASK / SCOPE_SUBTASK
        agent_name: 仅检索该任务 Agent，如 writer, planner
        top_k: 返回条数

    Returns:
        RetrievalResult 列表（或空列表）
    """
    if not unimem:
        return []
    tags_include = [PROCEDURAL_TAG]
    if role:
        tags_include.append(role if role.startswith("role:") else f"role:{role}")
    if scope:
        tags_include.append(scope if scope.startswith("scope:") else f"scope:{scope}")
    if agent_name:
        tags_include.append(agent_tag(agent_name))
    try:
        results = unimem.recall(
            query=query,
            memory_type=MemoryType.EXPERIENCE,
            tags_include=tags_include,
            top_k=top_k,
        )
        return results or []
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("recall_procedural failed: %s", e, exc_info=True)
        return []
