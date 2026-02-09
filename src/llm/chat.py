from typing import Any, Callable, Generator, List, Tuple

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


def get_llm_fn(model_id: str) -> Tuple[Any, Any]:
    """
    根据 model_id 获取 (同步函数, 流式函数)。
    未注册时抛出 ValueError。
    """
    key = chat_model_key(model_id)
    if key not in CHAT_MODELS:
        raise ValueError(f"未知模型: {model_id}，可选: {list(CHAT_MODELS.keys())}")
    return CHAT_MODELS[key][0], CHAT_MODELS[key][1]


def call_llm(
    model_id: str,
    messages: List[Any],
    max_new_tokens: int = 8192,
) -> Tuple[str, str]:
    """
    统一入口：按 model_id 调用对应模型，返回 (reasoning_content, content)。
    """
    fn, _ = get_llm_fn(model_id)
    return fn(messages, max_new_tokens=max_new_tokens)


def call_llm_stream(
    model_id: str,
    messages: List[Any],
    max_new_tokens: int = 8192,
    buffer_size: int = 10,
) -> Generator[str, None, None]:
    """
    统一入口：按 model_id 调用对应模型流式接口，逐块 yield 文本。
    """
    _, stream_fn = get_llm_fn(model_id)
    yield from stream_fn(
        messages,
        max_new_tokens=max_new_tokens,
        buffer_size=buffer_size,
    )


def _default_novel_model_id() -> str:
    """从配置读取创作默认模型 ID（B.1 配置驱动）。"""
    try:
        from config import NOVEL_LLM_MODEL
        return (NOVEL_LLM_MODEL or "").strip() or "kimi-k2-5"
    except Exception:
        return "kimi-k2-5"


def get_default_novel_llm() -> Callable[..., Tuple[str, str]]:
    """
    返回创作默认模型的同步函数（配置驱动，B.1）。
    等价于 CHAT_MODELS[config.NOVEL_LLM_MODEL][0]，未注册时回退 deepseek_v3_2。
    """
    model_id = _default_novel_model_id()
    key = chat_model_key(model_id)
    if key in CHAT_MODELS:
        return CHAT_MODELS[key][0]
    return deepseek_v3_2


def get_default_novel_llm_stream() -> Any:
    """返回创作默认模型的流式函数（配置驱动，B.1）。未注册时回退 deepseek_v3_2_stream。"""
    model_id = _default_novel_model_id()
    key = chat_model_key(model_id)
    if key in CHAT_MODELS:
        return CHAT_MODELS[key][1]
    return deepseek_v3_2_stream


def call_llm_for_novel(
    messages: List[Any],
    max_new_tokens: int = 8192,
) -> Tuple[str, str]:
    """
    使用配置中的创作默认模型进行同步调用（B.1 配置驱动）。
    统一输入：messages, max_new_tokens；统一输出：(reasoning_content, content)。
    """
    return call_llm(_default_novel_model_id(), messages, max_new_tokens=max_new_tokens)


def call_llm_for_novel_stream(
    messages: List[Any],
    max_new_tokens: int = 8192,
    buffer_size: int = 10,
) -> Generator[str, None, None]:
    """使用配置中的创作默认模型进行流式调用（B.1 配置驱动）。"""
    yield from call_llm_stream(
        _default_novel_model_id(),
        messages,
        max_new_tokens=max_new_tokens,
        buffer_size=buffer_size,
    )


__all__ = [
    "CHAT_MODELS",
    "chat_model_key",
    "get_llm_fn",
    "call_llm",
    "call_llm_stream",
    "get_default_novel_llm",
    "get_default_novel_llm_stream",
    "call_llm_for_novel",
    "call_llm_for_novel_stream",
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
