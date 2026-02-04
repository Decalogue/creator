"""
技能/能力层：渐进式披露的 SOP 与文档

主要服务于 Creator 创作流程：与 tools 互补，提供可重复调用的 SOP、
风格说明、创作规范等，由编排层或创作助手按需加载。详见 README.md。
"""
from .manager import SkillManager, default_manager
from .skill import Skill, SkillMetadata

__all__ = [
    "SkillManager",
    "default_manager",
    "Skill",
    "SkillMetadata",
]
