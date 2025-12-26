from .base import Tool, ToolRegistry, default_registry
from .calculator import CalculatorTool
from .weather import WeatherTool
from .time import TimeTool

***REMOVED*** 自动注册所有内置工具
default_registry.register(CalculatorTool())
default_registry.register(WeatherTool())
default_registry.register(TimeTool())

__all__ = [
    "Tool",
    "ToolRegistry",
    "default_registry",
    "CalculatorTool",
    "WeatherTool",
    "TimeTool",
]
