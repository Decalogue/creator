"""
工具调用层：Function Calling 注册表与工具发现

主要服务于 Creator 创作流程：编排层（如 orchestrator/react.ReActAgent）通过
default_registry 与 get_discovery() 发现、执行工具，支撑创作助手的计算、查询、
文档检索等能力。详见 README.md。
"""
from .base import Tool, ToolRegistry, default_registry
from .search_tool_docs import SearchToolDocsTool, ReadToolDocTool
from .discovery import ToolDiscovery, get_discovery

# 内置工具：仅保留创作相关能力（工具发现，供编排层按需查找文档）
default_registry.register(SearchToolDocsTool())
default_registry.register(ReadToolDocTool())

# 初始化工具发现系统（自动同步工具文档）
_discovery = get_discovery()

__all__ = [
    "Tool",
    "ToolRegistry",
    "default_registry",
    "SearchToolDocsTool",
    "ReadToolDocTool",
    "ToolDiscovery",
    "get_discovery",
]
