"""
并行创作优化模块

实现并行章节生成、依赖管理和资源管理。
"""

from .parallel_executor import ParallelExecutor
from .dependency_manager import DependencyManager, DependencyGraph
from .resource_manager import ResourceManager

__all__ = [
    "ParallelExecutor",
    "DependencyManager",
    "DependencyGraph",
    "ResourceManager",
]

