from .base import Tool, ToolRegistry, default_registry
from .calculator import CalculatorTool
from .weather import WeatherTool
from .time import TimeTool
from .search_tool_docs import SearchToolDocsTool, ReadToolDocTool
from .discovery import ToolDiscovery, get_discovery

***REMOVED*** 自动注册所有内置工具
default_registry.register(CalculatorTool())
default_registry.register(WeatherTool())
default_registry.register(TimeTool())
***REMOVED*** 注册工具发现相关的工具（这些工具让 Agent 可以主动查找其他工具）
default_registry.register(SearchToolDocsTool())
default_registry.register(ReadToolDocTool())

***REMOVED*** 初始化工具发现系统（自动同步工具文档）
_discovery = get_discovery()

__all__ = [
    "Tool",
    "ToolRegistry",
    "default_registry",
    "CalculatorTool",
    "WeatherTool",
    "TimeTool",
    "SearchToolDocsTool",
    "ReadToolDocTool",
    "ToolDiscovery",
    "get_discovery",
]
