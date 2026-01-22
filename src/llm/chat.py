"""
LLM Chat 模块
提供统一的 LLM 调用接口
"""
from .deepseek import client, deepseek_v3_2, deepseek_v3_2_stream
from .kimi import kimi_k2, kimi_k2_stream
from .glm import glm, glm_stream
from .gemini import gemini_3_flash, gemini_3_flash_stream
from .claude import claude_opus_4_5, claude_opus_4_5_stream


__all__ = [
    "client",
    "deepseek_v3_2",
    "deepseek_v3_2_stream",
    "kimi_k2",
    "kimi_k2_stream",
    "glm",
    "glm_stream",
    "gemini_3_flash",
    "gemini_3_flash_stream",
    "claude_opus_4_5",
    "claude_opus_4_5_stream",
]
