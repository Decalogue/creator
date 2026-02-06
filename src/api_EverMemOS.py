"""
EverMemOS 官方云 API 封装，供 Creator 参赛整合使用。

官方文档：https://docs.evermind.ai/api-reference/introduction
Search 接口定义：https://docs.evermind.ai/api-reference/memory-controller/search-memories
- Base URL: https://api.evermind.ai
- 认证：Bearer token (Authorization header)
- 核心：POST/GET /api/v1/memories（add/get）、GET /api/v1/memories/search（RetrieveMemRequest）、DELETE 删除

调用方式与官方样例一致：memory.get(extra_query={...}) / memory.search(extra_query={...})。
仅在 EVERMEMOS_API_KEY 已配置且 EVERMEMOS_ENABLED=1 时可用；
否则各函数为 no-op 或返回空，不抛错。

创作场景推荐（助力规划/续写/润色/对话）：
- 规划前检索：query="风格 主题 类型 过往创作 大纲", memory_types=["episodic_memory"], top_k=5~10
- 续写前检索：query="前文 情节 人物 大纲 本章摘要 角色", memory_types=["episodic_memory"], top_k=5~10
- 润色前检索：query="风格 语气 润色偏好 用词", group_id=project_id, top_k=3~5
- 对话前检索：query="对话 偏好 设定 大纲 人物", group_id=project_id, top_k=5
- 可选用 search_memory_result() 获取 scores/total_count，按分数过滤低相关记忆。
"""
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_memory_client: Optional[Any] = None

TOP_K_MIN, TOP_K_MAX = 1, 100
RADIUS_MIN, RADIUS_MAX = 0.0, 1.0


def _client() -> Optional[Any]:
    """懒加载 EverMemOS 客户端；无 key 或未启用时返回 None。"""
    global _memory_client
    if _memory_client is not None:
        return _memory_client
    try:
        from config import EVERMEMOS_API_KEY, EVERMEMOS_ENABLED
        if not EVERMEMOS_ENABLED or not (EVERMEMOS_API_KEY or "").strip():
            return None
        from evermemos import EverMemOS
        _memory_client = EverMemOS(api_key=EVERMEMOS_API_KEY.strip()).v1.memories
        return _memory_client
    except Exception as e:
        logger.debug("EverMemOS client not available: %s", e)
        return None


def _result_from_response(response: Any) -> Any:
    """从 SearchMemoriesResponse 解析 result 对象；无则返回 None。"""
    return getattr(response, "result", None)


def _memories_from_response(response: Any) -> List[Any]:
    """从 SearchMemoriesResponse / Get 响应中解析 result.memories，失败返回 []。"""
    result = _result_from_response(response)
    return getattr(result, "memories", None) or []


def is_available() -> bool:
    """是否已配置并可调用 EverMemOS API。"""
    return _client() is not None


def add_memory(messages: List[dict]) -> None:
    """写入记忆。messages 每项需含 message_id, create_time, sender, content；可选 sender_name, group_id。"""
    client = _client()
    if not client:
        return
    for message in messages:
        try:
            response = client.add(**message)
            logger.debug(
                "EverMemOS add status=%s message=%s request_id=%s",
                getattr(response, "status", None),
                getattr(response, "message", None),
                getattr(response, "request_id", None),
            )
        except Exception as e:
            logger.warning("EverMemOS add_memory failed: %s", e)


def get_memory(user_id: Optional[str] = None, group_id: Optional[str] = None) -> List[Any]:
    """按 user_id 或 group_id 拉取记忆（API 要求至少其一）。user_id 与 message.sender 对应，表示「谁的记忆」。"""
    client = _client()
    if not client:
        return []
    if not user_id and not group_id:
        return []
    try:
        q = {}
        if user_id:
            q["user_id"] = user_id
        if group_id:
            q["group_id"] = group_id
        response = client.get(extra_query=q)
        memories = _memories_from_response(response)
        logger.debug("EverMemOS get_memory %s count=%s", q, len(memories))
        return memories
    except Exception as e:
        logger.warning("EverMemOS get_memory failed: %s", e)
        return []


def search_memory(
    query: str,
    user_id: Optional[str] = None,
    group_id: Optional[str] = None,
    top_k: int = 40,
    retrieve_method: str = "hybrid",
    memory_types: Optional[List[str]] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    radius: Optional[float] = None,
) -> List[Any]:
    """按 query + user_id/group_id 检索记忆（至少提供 user_id 或 group_id 其一）。

    请求体遵循官方 RetrieveMemRequest：
    https://docs.evermind.ai/api-reference/memory-controller/search-memories
    - query: 检索文本（必填）
    - user_id / group_id: 至少其一
    - top_k: 1–100，默认 40
    - retrieve_method: keyword | vector | hybrid | rrf | agentic，默认 hybrid
    - memory_types: 可选，如 ["episodic_memory","foresight","event_log"]，search 不支持 profile
    - start_time / end_time: 可选，ISO 8601 带时区
    - radius: 可选，0–1，vector/hybrid 时 COSINE 相似度阈值，默认 0.6
    """
    client = _client()
    if not client:
        return []
    if not user_id and not group_id:
        return []
    try:
        q = {"query": query}
        if user_id:
            q["user_id"] = user_id
        if group_id:
            q["group_id"] = group_id
        q["top_k"] = min(max(TOP_K_MIN, top_k), TOP_K_MAX)
        q["retrieve_method"] = retrieve_method
        if memory_types is not None:
            q["memory_types"] = memory_types
        if start_time is not None:
            q["start_time"] = start_time
        if end_time is not None:
            q["end_time"] = end_time
        if radius is not None:
            q["radius"] = min(max(RADIUS_MIN, radius), RADIUS_MAX)
        response = client.search(extra_query=q)
        memories = _memories_from_response(response)
        logger.debug("EverMemOS search_memory %s count=%s", q, len(memories))
        return memories
    except Exception as e:
        logger.warning("EverMemOS search_memory failed: %s", e)
        return []


def search_memory_result(
    query: str,
    user_id: Optional[str] = None,
    group_id: Optional[str] = None,
    top_k: int = 40,
    retrieve_method: str = "hybrid",
    memory_types: Optional[List[str]] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    radius: Optional[float] = None,
) -> Dict[str, Any]:
    """与 search_memory 参数一致，但返回完整检索结果，便于按 scores 过滤或分页。

    返回：{"memories": [...], "scores": [...], "total_count": int, "has_more": bool}；
    scores 可能与 memories 一一对应（依服务端实现），缺失时为 []。
    """
    client = _client()
    empty: Dict[str, Any] = {"memories": [], "scores": [], "total_count": 0, "has_more": False}
    if not client or (not user_id and not group_id):
        return empty
    try:
        q: dict = {"query": query}
        if user_id:
            q["user_id"] = user_id
        if group_id:
            q["group_id"] = group_id
        q["top_k"] = min(max(TOP_K_MIN, top_k), TOP_K_MAX)
        q["retrieve_method"] = retrieve_method
        if memory_types is not None:
            q["memory_types"] = memory_types
        if start_time is not None:
            q["start_time"] = start_time
        if end_time is not None:
            q["end_time"] = end_time
        if radius is not None:
            q["radius"] = min(max(RADIUS_MIN, radius), RADIUS_MAX)
        response = client.search(extra_query=q)
        result = _result_from_response(response)
        if result is None:
            return empty
        memories = getattr(result, "memories", None) or []
        scores = getattr(result, "scores", None) or []
        total_count = getattr(result, "total_count", 0) or 0
        has_more = getattr(result, "has_more", False) or False
        logger.debug("EverMemOS search_memory_result %s count=%s", q, len(memories))
        return {
            "memories": memories,
            "scores": scores,
            "total_count": total_count,
            "has_more": has_more,
        }
    except Exception as e:
        logger.warning("EverMemOS search_memory_result failed: %s", e)
        return empty


def delete_memory(user_id: str, memory_id: str) -> None:
    """删除指定记忆。"""
    client = _client()
    if not client:
        return
    try:
        response = client.delete(
            extra_query={"user_id": user_id, "memory_id": memory_id}
        )
        logger.debug("EverMemOS delete status=%s", getattr(response, "status", None))
    except Exception as e:
        logger.warning("EverMemOS delete_memory failed: %s", e)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    messages = [
        {
            "message_id": "msg_001",
            "create_time": "2026-02-06T10:00:00Z",
            "sender": "user_demo_001",
            "sender_name": "Demo User",
            "group_id": "group_001",
            "content": "I like black Americano, no sugar, the stronger the better!",
        }
    ]
    add_memory(messages)
    print(get_memory(user_id="user_demo_001"))
    print(search_memory("coffee preference", user_id="user_demo_001"))
