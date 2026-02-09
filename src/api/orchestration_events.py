"""
编排事件：P1 编排可观测（B.4 编排事件契约）

创作 pipeline 各步骤在开始/结束/失败时通过 on_event 回调发出事件，
便于 SSE/WebSocket 推送，驱动前端工作流面板。

step 类型与 payload 稳定契约（B.4）：
- 步骤名：CREATOR_STEPS（plan, memory, write, polish, qa），与前端编排区一致
- 事件类型：step_start | step_done | step_error
- payload 结构：{ type, step, data?, ts }；step_error 时 data.error 必填
- stream_end（由 api_flask 发出）：{ type: "stream_end", code, message, content?, ... }
"""

from typing import Any, Callable, Dict, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

# 步骤名：与前端编排区展示一致，稳定契约（B.4）
CREATOR_STEPS = ("plan", "memory", "write", "polish", "qa")

# 事件类型：稳定契约（B.4）
EVENT_STEP_START = "step_start"
EVENT_STEP_DONE = "step_done"
EVENT_STEP_ERROR = "step_error"
EVENT_STREAM_END = "stream_end"

EventPayload = Dict[str, Any]
OnEventCallback = Optional[Callable[[EventPayload], None]]


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _emit(
    event_type: str,
    step: str,
    data: Optional[Dict[str, Any]] = None,
    on_event: OnEventCallback = None,
) -> None:
    if not callable(on_event):
        return
    payload: EventPayload = {
        "type": event_type,
        "step": step,
        "data": data or {},
        "ts": _ts(),
    }
    try:
        on_event(payload)
    except Exception as e:
        logger.warning("orchestration on_event callback failed: %s", e)


def emit_step_start(step: str, data: Optional[Dict[str, Any]] = None, on_event: OnEventCallback = None) -> None:
    """步骤开始。payload: { type: "step_start", step, data, ts }"""
    _emit(EVENT_STEP_START, step, data, on_event)


def emit_step_done(step: str, data: Optional[Dict[str, Any]] = None, on_event: OnEventCallback = None) -> None:
    """步骤完成。payload: { type: "step_done", step, data, ts }"""
    _emit(EVENT_STEP_DONE, step, data, on_event)


def emit_step_error(step: str, error: Any, on_event: OnEventCallback = None) -> None:
    """步骤失败。payload: { type: "step_error", step, data: { error }, ts }"""
    _emit(EVENT_STEP_ERROR, step, {"error": str(error)}, on_event)
