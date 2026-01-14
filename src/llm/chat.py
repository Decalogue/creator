"""
LLM Chat 模块
提供统一的 LLM 调用接口
"""
from .deepseek import client, deepseek_v3_2, deepseek_v3_2_stream


__all__ = [
    "client",
    "deepseek_v3_2",
    "deepseek_v3_2_stream",
]
