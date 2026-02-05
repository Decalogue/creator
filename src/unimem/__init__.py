"""
UniMem: 统一记忆系统

整合六大核心架构的优势：
- HindSight: 操作接口层（Retain/Recall/Reflect）
- CogMem: 存储管理层（FoA/DA/LTM）
- A-Mem: 网络组织层（原子笔记网络）
- LightRAG: 网络组织层（图结构）
- LightMem: 更新机制层（睡眠更新）
- MemMachine: 存储管理层（多类型记忆）

设计理念：分层存储 + 多维检索 + 涟漪更新 + 操作驱动
"""

from .core import UniMem
from .memory_types import Experience, Memory, Task, Context, context_for_agent
from .orchestration import Orchestrator, Workflow, Step, WorkflowStep

__version__ = "1.0.0"
__all__ = [
    "UniMem",
    "Experience",
    "Memory",
    "Task",
    "Context",
    "context_for_agent",
    # 编排相关
    "Orchestrator",
    "Workflow",
    "Step",
    "WorkflowStep",
]

