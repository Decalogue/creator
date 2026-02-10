"""
EverMemOS 官方云 API 封装，供 Creator 参赛整合使用。
本模块按官方 SDK 调用 v1.memories（add/get/search/delete）。

官方文档：https://docs.evermind.ai/api-reference/introduction
- Base URL: https://api.evermind.ai，认证：Bearer token
- EVERMEMOS_API_KEY 已配置且 EVERMEMOS_ENABLED=1 时可用，否则 no-op 或返回空。
"""
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

TOP_K_MIN, TOP_K_MAX = 1, 100
CREATOR_USER_ID = "creator"
CREATOR_SENDER = "creator"

def _init_client() -> Any:
    try:
        from config import EVERMEMOS_API_KEY, EVERMEMOS_ENABLED
        if not EVERMEMOS_ENABLED or not (EVERMEMOS_API_KEY or "").strip():
            return None
        from evermemos import EverMemOS
        return EverMemOS(api_key=EVERMEMOS_API_KEY.strip()).v0.memories
    except Exception as e:
        logger.debug("EverMemOS client not available: %s", e)
        return None


_memory_client: Any = _init_client()


def _memories_from_response(response: Any) -> List[Any]:
    result = getattr(response, "result", None)
    return getattr(result, "memories", None) or []


def is_available() -> bool:
    return _memory_client is not None


def add_memory(messages: List[dict]) -> None:
    """写入记忆。每项需 message_id, create_time(ISO8601), sender, content；可选 group_id。未传 sender 用 CREATOR_SENDER。"""
    if not _memory_client or not messages:
        return
    for message in messages:
        if not isinstance(message, dict) or not message.get("message_id") or message.get("content") is None:
            continue
        sender = (message.get("sender") or "").strip() or CREATOR_SENDER
        try:
            _memory_client.add(
                message_id=message.get("message_id"),
                create_time=message.get("create_time"),
                sender=sender,
                content=message.get("content"),
                group_id=message.get("group_id"),
            )
            logger.info("EverMemOS add_memory success: message_id=%s group_id=%s", message.get("message_id"), message.get("group_id"))
        except Exception as e:
            logger.warning(f"EverMemOS add_memory failed: {e} | message_id={message.get('message_id')}")


def get_memory(user_id: Optional[str] = None, group_id: Optional[str] = None) -> List[Any]:
    """按 user_id 或 group_id 拉取记忆（至少其一）。"""
    if not _memory_client or (not user_id and not group_id):
        return []
    try:
        q = {}
        if user_id:
            q["user_id"] = user_id
        if group_id:
            q["group_id"] = group_id
        r = _memory_client.get(extra_query=q)
        logger.info("EverMemOS get_memory success: user_id=%s group_id=%s", user_id, group_id)
        return _memories_from_response(r)
    except Exception as e:
        logger.warning("EverMemOS get_memory failed: %s | user_id=%s group_id=%s", e, user_id, group_id)
        return []


def search_memory(
    query: str,
    user_id: Optional[str] = None,
    group_id: Optional[str] = None,
    top_k: int = 40,
) -> List[Any]:
    """按 query + user_id/group_id 检索（至少其一）。"""
    if not _memory_client or (not user_id and not group_id):
        return []
    try:
        q: dict = {"query": query, "top_k": min(max(TOP_K_MIN, top_k), TOP_K_MAX)}
        if user_id:
            q["user_id"] = user_id
        if group_id:
            q["group_id"] = group_id
        r = _memory_client.search(extra_query=q)
        logger.info("EverMemOS search_memory success: query=%s user_id=%s group_id=%s top_k=%s", query, user_id, group_id, top_k)
        return _memories_from_response(r)
    except Exception as e:
        logger.warning("EverMemOS search_memory failed: %s | query=%r user_id=%s group_id=%s top_k=%s", e, query, user_id, group_id, top_k)
        return []


def delete_memory(user_id: str, memory_id: str, group_id: Optional[str] = None) -> None:
    """删除指定记忆。使用 SDK 命名参数；同时传 query（含 id/memory_id/event_id）以防服务端忽略 DELETE body；可选 group_id。"""
    if not _memory_client:
        return
    try:
        # 部分网关忽略 DELETE body，故 query 中传齐 id / memory_id / event_id（API 中均为删除条件）
        q = {"user_id": user_id, "memory_id": memory_id, "id": memory_id, "event_id": memory_id}
        if group_id:
            q["group_id"] = group_id
        _memory_client.delete(
            user_id=user_id,
            memory_id=memory_id,
            group_id=group_id,
            extra_query=q,
        )
        logger.info("EverMemOS delete_memory success: user_id=%s memory_id=%s", user_id, memory_id)
    except Exception as e:
        logger.warning("EverMemOS delete_memory failed: %s | user_id=%s memory_id=%s", e, user_id, memory_id)


def _memory_id_from_item(m: Any) -> Optional[str]:
    """从 get 返回的单项中取出 memory_id。"""
    if m is None:
        return None
    mid = getattr(m, "id", None) or getattr(m, "memory_id", None)
    if mid:
        return str(mid)
    if isinstance(m, dict):
        return str(m.get("id") or m.get("memory_id") or "")
    return None


def delete_all_memories_for_user(user_id: str) -> int:
    """删除该用户下全部云端记忆（如清空实验数据）。使用「仅 user_id」的批量删除，返回删除前条数。"""
    if not _memory_client or not user_id:
        return 0
    try:
        raw = get_memory(user_id=user_id)
        count = len(raw or [])
        if count == 0:
            return 0
        # 服务端逐条按 memory_id 删除不生效，需用「仅 user_id」的批量删除
        _memory_client.delete(
            user_id=user_id,
            extra_query={"user_id": user_id},
        )
        logger.info("EverMemOS delete_all_memories_for_user: user_id=%s deleted=%s", user_id, count)
        return count
    except Exception as e:
        logger.warning("EverMemOS delete_all_memories_for_user failed: %s | user_id=%s", e, user_id)
        return 0


def delete_all_memories_for_group(user_id: str, group_id: str) -> int:
    """删除该用户下指定 group_id 的全部记忆（即清空某一作品的云端记忆）。使用「仅 user_id+group_id」的批量删除，返回删除前该组条数。"""
    if not _memory_client or not user_id or not group_id:
        return 0
    try:
        raw = get_memory(user_id=user_id, group_id=group_id)
        count = len(raw or [])
        if count == 0:
            return 0
        # 服务端按 memory_id 逐条删除不生效，需用「仅 user_id + group_id」的批量删除
        _memory_client.delete(
            user_id=user_id,
            group_id=group_id,
            extra_query={"user_id": user_id, "group_id": group_id},
        )
        logger.info("EverMemOS delete_all_memories_for_group: user_id=%s group_id=%s deleted=%s", user_id, group_id, count)
        return count
    except Exception as e:
        logger.warning("EverMemOS delete_all_memories_for_group failed: %s | user_id=%s group_id=%s", e, user_id, group_id)
        return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    iso8601_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    msg_id = "msg_" + uuid.uuid4().hex[:16]
    grp_id = "group_" + uuid.uuid4().hex[:16]

    messages = [{
        "message_id": msg_id,
        "create_time": iso8601_time,
        "sender": CREATOR_SENDER,
        "content": "【大纲】玄灵大陆是一个充满灵气的异世界，五大域与七境界；地球科学家林墨穿越到玄灵大陆。",
        "group_id": grp_id,
    }]
    add_memory(messages)
    print('-' * 100)

    get_memory(user_id=CREATOR_USER_ID, group_id=grp_id)
    print('-' * 100)

    q = "前文 情节 人物 大纲"
    r1 = search_memory(q, user_id=CREATOR_USER_ID, group_id=grp_id, top_k=10)
    print('-' * 100)

    delete_memory(CREATOR_USER_ID, msg_id)
    print('-' * 100)
