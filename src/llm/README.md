# LLM 层

创作与对话使用的 LLM 统一入口与注册表，配置驱动模型选择。

## 入口

- **chat.py**：门面与注册表
  - `CHAT_MODELS`：模型 ID（小写）→ `(同步函数, 流式函数)`
  - `chat_model_key(name)`：请求里的 model 转成注册表 key
  - `get_llm_fn(model_id)`：取 `(sync_fn, stream_fn)`，未注册抛 `ValueError`
  - **call_llm(model_id, messages, max_new_tokens=8192)**：统一同步调用，返回 `(reasoning_content, content)`
  - **call_llm_stream(model_id, messages, ...)**：统一流式调用，yield 文本块
  - **配置驱动（B.1）**：`get_default_novel_llm()` / `get_default_novel_llm_stream()` 返回 config.NOVEL_LLM_MODEL 对应函数；`call_llm_for_novel(messages, ...)` / `call_llm_for_novel_stream(...)` 直接用默认模型调用，统一输入（messages, max_tokens）与输出（reasoning_content, content）

## 已注册模型

| model_id | 同步/流式 |
|----------|-----------|
| deepseek-v3-2 | deepseek_v3_2 / deepseek_v3_2_stream |
| kimi-k2, kimi-k2-5 | kimi_k2 / kimi_k2_stream 等 |
| glm-4-7 | glm / glm_stream |
| gemini-3-flash | gemini_3_flash / gemini_3_flash_stream |
| claude-opus-4-5 | claude_opus_4_5 / claude_opus_4_5_stream |

## 各厂商模块

- deepseek.py、kimi.py、glm.py、gemini.py、claude.py：各提供 `fn(messages, max_new_tokens=...)` 与 `fn_stream(messages, ...)`，返回约定一致（同步返回 `(reasoning_content, content)`，流式 yield 字符串）。

## 调用点

| 模块 | 用法 |
|------|------|
| api_flask | `CHAT_MODELS` + `chat_model_key`，/api/chat 路由 |
| api/creator_handlers | `get_default_novel_llm()` 取配置驱动的创作默认模型 |
| task/novel/react_novel_creator | 直接 `from llm.chat import kimi_k2, deepseek_v3_2` 等按场景选模型 |
| task/novel/full_novel_quality_agent | 同上 |
| scripts/novel/create_100_chapters_novel.py | `from llm.chat import kimi_k2` |

新增调用建议：优先用 **call_llm** / **call_llm_stream** + 配置中的 model_id，避免散落写死具体模型函数。
