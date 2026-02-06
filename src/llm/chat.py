from .deepseek import deepseek_v3_2, deepseek_v3_2_stream
from .kimi import kimi_k2_5, kimi_k2_5_stream, kimi_k2, kimi_k2_stream
from .glm import glm, glm_stream
from .gemini import gemini_3_flash, gemini_3_flash_stream
from .claude import claude_opus_4_5, claude_opus_4_5_stream

# 模型 ID（小写） -> (llm_fn, stream_fn)，供 /api/chat 等统一路由使用
CHAT_MODELS = {
    "deepseek-v3-2": (deepseek_v3_2, deepseek_v3_2_stream),
    "kimi-k2": (kimi_k2, kimi_k2_stream),
    "kimi-k2-5": (kimi_k2_5, kimi_k2_5_stream),
    "glm-4-7": (glm, glm_stream),
    "gemini-3-flash": (gemini_3_flash, gemini_3_flash_stream),
    "claude-opus-4-5": (claude_opus_4_5, claude_opus_4_5_stream),
}


def chat_model_key(name: str) -> str:
    """请求中的 model 转为注册表 key（小写、去空白）。"""
    return (name or "").strip().lower()


__all__ = [
    "CHAT_MODELS",
    "chat_model_key",
    "deepseek_v3_2",
    "deepseek_v3_2_stream",
    "kimi_k2_5",
    "kimi_k2_5_stream",
    "kimi_k2",
    "kimi_k2_stream",
    "glm",
    "glm_stream",
    "gemini_3_flash",
    "gemini_3_flash_stream",
    "claude_opus_4_5",
    "claude_opus_4_5_stream",
]
