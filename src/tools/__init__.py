"""
Function Calling 模块
提供统一的函数调用接口，支持 OpenAI Function Calling 格式

注意：虽然内部使用 "Skill" 命名，但这是一个标准的 Function Calling 系统。
"""
from .base import Skill, SkillRegistry, default_registry
from .calculator import CalculatorSkill
from .weather import WeatherSkill
from .time import TimeSkill

***REMOVED*** 自动注册所有内置技能
default_registry.register(CalculatorSkill())
default_registry.register(WeatherSkill())
default_registry.register(TimeSkill())

__all__ = [
    "Skill",
    "SkillRegistry",
    "default_registry",
    "CalculatorSkill",
    "WeatherSkill",
    "TimeSkill",
]
