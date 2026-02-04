"""
编排层：多种 Agentic 推理/编排方式

- react: ReAct (Reasoning + Acting)，思考-行动-观察循环
- 后续可增加：基座原生 Agentic、其他推理模型等
"""

from orchestrator.react import ReActAgent

__all__ = [
    "ReActAgent",
]
