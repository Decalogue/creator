"""
编排事件：P1 编排可观测

创作 pipeline 各步骤（plan / memory / write / polish / qa）在开始/结束/失败时
通过 on_event 回调发出事件，便于 SSE/WebSocket 推送，驱动前端工作流面板。
"""

from typing import Any, Callable, Dict, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

# 步骤名：与前端编排区展示一致
CREATOR_STEPS = ("plan", "memory", "write", "polish", "qa")

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
    """步骤开始"""
    _emit("step_start", step, data, on_event)


def emit_step_done(step: str, data: Optional[Dict[str, Any]] = None, on_event: OnEventCallback = None) -> None:
    """步骤完成"""
    _emit("step_done", step, data, on_event)


def emit_step_error(step: str, error: Any, on_event: OnEventCallback = None) -> None:
    """步骤失败"""
    _emit("step_error", step, {"error": str(error)}, on_event)
