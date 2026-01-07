"""
人物管理模块

基于"换壳理论"的人物成长线管理。
"""

from .growth_arc_manager import (
    CharacterGrowthArcManager,
    GrowthArc,
    GrowthArcStage,
)

__all__ = [
    "CharacterGrowthArcManager",
    "GrowthArc",
    "GrowthArcStage",
]

