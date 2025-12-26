"""
Skills 系统
基于 Anthropic Skills 设计，实现渐进式披露机制
"""
from .manager import SkillManager, default_manager
from .skill import Skill, SkillMetadata

__all__ = [
    "SkillManager",
    "default_manager",
    "Skill",
    "SkillMetadata",
]
