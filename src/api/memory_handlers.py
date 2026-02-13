"""
记忆 API 逻辑：实体、图谱、最近检索、节点详情

数据来源：semantic_mesh/mesh.json（按 project_id 即 novel_title 区分项目）
配置启用时（UNIMEM_ENABLED=1）：合并 UniMem 数据；创作成功时 Retain 写入 UniMem（P1 2.3）
EVERMEMOS_ENABLED=1 且配置 EVERMEMOS_API_KEY 时：创作成功同时写入 EverMemOS 云 API（参赛用）

创作记忆抽象（A.3/B.2）：mesh 读写 + UniMem 适配器。
- 主存储：semantic_mesh/mesh.json；read_mesh, write_mesh
- UniMem：UNIMEM_ENABLED=1 时 retain 写入、get_entities/graph 合并 recall
- recall：recall_for_mode(project_id, mode, ...)
- retain：retain_plan, retain_chapter, retain_chapter_entities, retain_polish, retain_chat
"""
import os
import re
import hashlib
import json
import logging
import threading
import queue
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# 创作输出路径与 project_id 规范统一从 config 入口（A.4）
from config import project_dir, normalize_project_id

# 项目 src 目录，用于脚本/日志等路径
_BASE = Path(__file__).resolve().parent.parent

# UniMem 可选后端：环境变量 UNIMEM_ENABLED=1 时启用
_unimem_instance: Optional[Any] = None
_unimem_init_failed: bool = False
_unimem_lock = threading.Lock()


def _unimem_init_timeout() -> float:
    """首次初始化超时（秒），可通过 UNIMEM_INIT_TIMEOUT 设置（默认 30）。"""
    try:
        return max(5.0, float(os.getenv("UNIMEM_INIT_TIMEOUT", "30").strip()))
    except (ValueError, TypeError):
        return 30.0


def _unimem_enabled() -> bool:
    """默认开启；仅当明确设为 0/false/no/off 时关闭。"""
    val = os.getenv("UNIMEM_ENABLED", "1").strip().lower()
    if val in ("0", "false", "no", "off"):
        return False
    return val in ("", "1", "true", "yes")


def _get_unimem() -> Optional[Any]:
    """懒加载 UniMem 实例；不可用时返回 None，不阻塞主流程。首次初始化带超时，避免阻塞 worker。"""
    global _unimem_instance, _unimem_init_failed
    if not _unimem_enabled():
        return None
    if _unimem_instance is not None:
        return _unimem_instance
    if _unimem_init_failed:
        return None
    with _unimem_lock:
        if _unimem_instance is not None:
            return _unimem_instance
        if _unimem_init_failed:
            return None
        result_queue: queue.Queue = queue.Queue()

        def _init():
            try:
                from unimem import UniMem
                # 从环境变量构建 config，使 LayeredStorageAdapter / GraphAdapter / AtomLinkAdapter 使用 Redis / Neo4j / Qdrant
                sb = os.getenv("UNIMEM_STORAGE_BACKEND", "memory").strip().lower()
                gb = os.getenv("UNIMEM_GRAPH_BACKEND", "neo4j").strip().lower()
                vb = os.getenv("UNIMEM_VECTOR_BACKEND", "memory").strip().lower()
                if sb == "memory" and gb == "memory" and vb == "memory":
                    logger.info(
                        "UniMem using memory-only backends; data will not persist to Qdrant/Neo4j. "
                        "Set UNIMEM_STORAGE_BACKEND=redis, UNIMEM_GRAPH_BACKEND=neo4j, UNIMEM_VECTOR_BACKEND=qdrant for persistence."
                    )
                unimem_config = {
                    "storage": {
                        "foa_backend": sb,
                        "da_backend": sb,
                        "ltm_backend": gb,
                    },
                    "graph": {"backend": gb},
                    "vector": {"backend": vb},
                    "network": {
                        "qdrant_host": os.getenv("UNIMEM_QDRANT_HOST", "localhost").strip(),
                        "qdrant_port": int(os.getenv("UNIMEM_QDRANT_PORT", "6333")),
                        "collection_name": os.getenv("UNIMEM_COLLECTION_NAME", "unimem_memories").strip(),
                    },
                }
                inst = UniMem(
                    config=unimem_config,
                    storage_backend=sb,
                    graph_backend=gb,
                    vector_backend=vb,
                )
                result_queue.put(inst)
            except Exception as e:
                logger.warning("UniMem not available, memory API will use semantic_mesh only: %s", e)
                result_queue.put(None)

        t = threading.Thread(target=_init, daemon=True)
        t.start()
        timeout = _unimem_init_timeout()
        try:
            inst = result_queue.get(timeout=timeout)
            if inst is not None:
                _unimem_instance = inst
                return _unimem_instance
            _unimem_init_failed = True
            return None
        except queue.Empty:
            logger.warning(
                "UniMem init timeout (%.1fs), memory API will use semantic_mesh only. "
                "Increase UNIMEM_INIT_TIMEOUT or ensure Redis/Neo4j/Qdrant start before backend.",
                timeout,
            )
            _unimem_init_failed = True
            return None


def retain_plan_to_unimem(project_id: str, plan_summary: str) -> None:
    """创作大纲成功后写入 UniMem（P1 2.3）。失败仅打日志，不抛错。"""
    u = _get_unimem()
    if not u:
        if not _unimem_enabled():
            logger.warning(
                "UniMem disabled (UNIMEM_ENABLED=0 or false), skipping retain plan (project_id=%s). "
                "Set UNIMEM_ENABLED=1 to enable.",
                project_id,
            )
        elif _unimem_init_failed:
            logger.warning(
                "UniMem init failed earlier (timeout or connection error), skipping retain plan (project_id=%s). "
                "Restart the backend after Redis/Neo4j/Qdrant are up; or set UNIMEM_INIT_TIMEOUT=60. "
                "Check startup logs for 'UniMem not available' or 'init timeout'.",
                project_id,
            )
        else:
            logger.warning(
                "UniMem not available, skipping retain plan (project_id=%s). "
                "Set UNIMEM_ENABLED=1 and UNIMEM_*_BACKEND for Qdrant/Neo4j.",
                project_id,
            )
        return
    try:
        from unimem.memory_types import Experience
        logger.info("Retaining plan to UniMem for project_id=%s ...", project_id)
        u.retain_for_agent(
            Experience(content=plan_summary[:8000], timestamp=datetime.now()),
            task_id=project_id,
            role="creator",
            session_id=project_id,
            **{"source": "creator_plan", "project_id": project_id},
        )
        logger.info("Retained plan summary to UniMem for project_id=%s", project_id)
    except Exception as e:
        logger.warning("Failed to retain plan to UniMem (project_id=%s): %s", project_id, e, exc_info=True)


def retain_chapter_to_unimem(project_id: str, chapter_number: int, content: str) -> None:
    """续写章节成功后写入 UniMem（P1 2.3）。失败仅打日志，不抛错。"""
    u = _get_unimem()
    if not u:
        if not _unimem_enabled():
            logger.warning(
                "UniMem disabled (UNIMEM_ENABLED=0 or false), skipping retain chapter (project_id=%s ch=%s). Set UNIMEM_ENABLED=1 to enable.",
                project_id,
                chapter_number,
            )
        elif _unimem_init_failed:
            logger.warning(
                "UniMem init failed earlier, skipping retain chapter (project_id=%s ch=%s). Restart backend after Redis/Neo4j/Qdrant are up, or set UNIMEM_INIT_TIMEOUT=60.",
                project_id,
                chapter_number,
            )
        else:
            logger.warning(
                "UniMem not available, skipping retain chapter (project_id=%s ch=%s). Set UNIMEM_ENABLED=1 and UNIMEM_*_BACKEND for Qdrant/Neo4j.",
                project_id,
                chapter_number,
            )
        return
    try:
        from unimem.memory_types import Experience
        summary = (content[:500] + "…") if len(content) > 500 else content
        u.retain_for_agent(
            Experience(content=summary, timestamp=datetime.now()),
            task_id=project_id,
            role="writer",
            session_id=project_id,
            **{"source": "creator_chapter", "project_id": project_id, "chapter_number": chapter_number},
        )
        logger.info("Retained chapter %s to UniMem for project_id=%s", chapter_number, project_id)
    except Exception as e:
        logger.warning("Failed to retain chapter to UniMem (project_id=%s ch=%s): %s", project_id, chapter_number, e, exc_info=True)


# EverMemOS 创作助手身份：与 api_EverMemOS.CREATOR_SENDER / CREATOR_USER_ID 一致
try:
    from api_EverMemOS import CREATOR_SENDER, CREATOR_USER_ID
except Exception:
    CREATOR_SENDER = "creator"
    CREATOR_USER_ID = "creator"


def _evermemos_group_id(project_id: str) -> str:
    """将 project_id 转为 EverMemOS 可用的稳定 ASCII group_id，避免中文进 URL 导致 404。"""
    pid = (project_id or "").strip() or "default"
    return "grp_" + hashlib.sha256(pid.encode("utf-8")).hexdigest()[:24]


# 每个项目目录下的 evermemos 写入记录，清空时按此列表逐条 delete，无需 get_memory
EVERMEMOS_IDS_FILENAME = "evermemos_ids.json"


def _evermemos_ids_path(project_id: str) -> Path:
    """当前作品目录下的 evermemos 记录文件路径。"""
    return project_dir(normalize_project_id(project_id)) / EVERMEMOS_IDS_FILENAME


def _load_evermemos_ids(project_id: str) -> List[str]:
    """读取该项目已写入云端的 message_id 列表。"""
    path = _evermemos_ids_path(project_id)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return [str(x) for x in data] if isinstance(data, list) else []
    except Exception as e:
        logger.warning("load evermemos_ids failed: %s", e)
        return []


def _append_evermemos_ids(project_id: str, message_ids: List[str]) -> None:
    """追加本次 add_memory 使用的 message_id，写入项目目录下的 evermemos_ids.json。"""
    if not message_ids:
        return
    pid = normalize_project_id(project_id)
    root = project_dir(pid)
    root.mkdir(parents=True, exist_ok=True)
    path = root / EVERMEMOS_IDS_FILENAME
    existing = _load_evermemos_ids(project_id)
    existing.extend(message_ids)
    try:
        path.write_text(json.dumps(existing, ensure_ascii=False, indent=0), encoding="utf-8")
    except Exception as e:
        logger.warning("append evermemos_ids failed: %s", e)


def _clear_evermemos_ids_file(project_id: str) -> None:
    """清空该项目本地的 evermemos 记录文件。"""
    path = _evermemos_ids_path(project_id)
    if path.exists():
        try:
            path.write_text("[]", encoding="utf-8")
        except Exception as e:
            logger.warning("clear evermemos_ids file failed: %s", e)


def delete_project_evermemos_by_local_record(project_id: str) -> int:
    """根据本地 evermemos_ids.json 逐条调用 delete，并清空本地记录。返回删除条数。无本地记录时返回 0。"""
    ids = _load_evermemos_ids(project_id)
    if not ids:
        return 0
    try:
        from api_EverMemOS import CREATOR_USER_ID, delete_memory
        for mid in ids:
            try:
                delete_memory(CREATOR_USER_ID, mid)
            except Exception as e:
                logger.warning("delete_memory failed for %s: %s", mid, e)
        _clear_evermemos_ids_file(project_id)
        return len(ids)
    except Exception as e:
        logger.warning("delete_project_evermemos_by_local_record failed: %s", e)
        return 0


def delete_all_evermemos_by_local_records() -> int:
    """遍历所有项目目录，按各项目 evermemos_ids.json 逐条 delete 并清空本地记录。返回总删除条数。"""
    from config import list_projects
    total = 0
    for pid in list_projects():
        total += delete_project_evermemos_by_local_record(pid)
    return total


def retain_plan_to_evermemos(project_id: str, plan_summary: str) -> None:
    """创作大纲成功后写入 EverMemOS 云 API（参赛用）。失败仅打日志，不抛错。"""
    try:
        from api_EverMemOS import is_available, add_memory
        if not is_available():
            return
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        msg_id = "msg_" + uuid.uuid4().hex
        raw = (plan_summary[:8000] + "…") if len(plan_summary) > 8000 else plan_summary
        content = f"【大纲】{raw}" if raw.strip() else raw
        add_memory([{"message_id": msg_id, "create_time": ts, "sender": CREATOR_SENDER, "content": content, "group_id": _evermemos_group_id(project_id)}])
        _append_evermemos_ids(project_id, [msg_id])
        logger.info("Retained plan to EverMemOS for project_id=%s", project_id)
    except Exception as e:
        logger.warning("Failed to retain plan to EverMemOS (project_id=%s): %s", project_id, e, exc_info=True)


def _extract_key_detail_sentences(content: str, max_sentences: int = 5, max_total: int = 600) -> str:
    """提取包含关键细节的句子（数字、百分比、编号、技术相关词），便于长程召回精确回指。"""
    parts = re.split(r'([。！？])', content)
    sentences = []
    buf = ""
    for i, p in enumerate(parts):
        if p in ("。", "！", "？"):
            buf += p
            if buf.strip():
                sentences.append(buf.strip())
            buf = ""
        else:
            buf += p
    if buf.strip():
        sentences.append(buf.strip())
    out = []
    total = 0
    for s in sentences:
        if len(s) < 10:
            continue
        if re.search(r'\d+%|第\d+[号章节]|\d+\.\d+|实验体|傅里叶|量子|维度|播种|遗迹|核心意识|保留率', s):
            out.append(s)
            total += len(s)
            if len(out) >= max_sentences or total >= max_total:
                break
    if not out:
        return ""
    return " ".join(out)[:max_total]


def retain_chapter_to_evermemos(
    project_id: str,
    chapter_number: int,
    content: str,
    chapter_summary: Optional[str] = None,
) -> None:
    """续写章节成功后写入 EverMemOS。优先使用章节摘要，无摘要时用正文前 500 字；另写入关键细节点（数字、术语、一次性事件）便于长程召回。"""
    try:
        from api_EverMemOS import is_available, add_memory
        if not is_available():
            return
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        msg_id = "msg_" + uuid.uuid4().hex
        summary_text = (chapter_summary or "").strip()
        if not summary_text:
            summary_text = (content[:500] + "…") if len(content) > 500 else content
        else:
            summary_text = (summary_text[:800] + "…") if len(summary_text) > 800 else summary_text
        add_memory([{"message_id": msg_id, "create_time": ts, "sender": CREATOR_SENDER, "content": f"【第{chapter_number}章】{summary_text}", "group_id": _evermemos_group_id(project_id)}])
        _append_evermemos_ids(project_id, [msg_id])
        details = _extract_key_detail_sentences(content)
        if details:
            msg_id2 = "msg_" + uuid.uuid4().hex
            add_memory([{"message_id": msg_id2, "create_time": ts, "sender": CREATOR_SENDER, "content": f"【第{chapter_number}章细节点】{details}", "group_id": _evermemos_group_id(project_id)}])
            _append_evermemos_ids(project_id, [msg_id2])
        logger.info("Retained chapter %s to EverMemOS for project_id=%s", chapter_number, project_id)
    except Exception as e:
        logger.warning(
            "Failed to retain chapter to EverMemOS (project_id=%s ch=%s): %s",
            project_id, chapter_number, e, exc_info=True
        )


def retain_chapter_entities_to_evermemos(project_id: str, chapter_number: int) -> None:
    """将本章在 mesh 中的主要实体写入 EverMemOS，便于跨章节检索与长跨度关联。失败仅打日志。"""
    try:
        from api_EverMemOS import is_available, add_memory
        if not is_available():
            return
        mesh = _load_mesh(project_id)
        if not mesh:
            return
        entities = mesh.get("entities") or {}
        by_type: Dict[str, List[str]] = {}
        for eid, e in entities.items():
            if not isinstance(e, dict):
                continue
            meta = e.get("metadata") or {}
            ch = meta.get("chapter") or meta.get("last_appearance_chapter")
            if ch is None or int(ch) != int(chapter_number):
                continue
            name = (e.get("name") or str(eid)).strip()
            if not name:
                continue
            brief = (e.get("content") or "").strip()[:80]
            label = f"{name}({brief})" if brief else name
            t = (e.get("type") or "entity").strip().lower()
            by_type.setdefault(t, []).append(label)
        if not by_type:
            return
        type_order = ("character", "person", "location", "organization", "item", "concept", "creature", "setting", "entity")
        parts = []
        for t in type_order:
            if t not in by_type:
                continue
            names = by_type[t][:15]
            type_label = {"character": "人物", "person": "人物", "location": "地点", "organization": "组织", "item": "物品", "concept": "概念", "creature": "生物", "setting": "场景", "entity": "实体"}.get(t, t)
            parts.append(f"{type_label}：{'、'.join(names)}")
        if not parts:
            return
        content = f"【第{chapter_number}章实体】" + "；".join(parts)
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        msg_id = "msg_" + uuid.uuid4().hex
        add_memory([{"message_id": msg_id, "create_time": ts, "sender": CREATOR_SENDER, "content": content[:2000], "group_id": _evermemos_group_id(project_id)}])
        _append_evermemos_ids(project_id, [msg_id])
        logger.info("Retained chapter %s entities to EverMemOS for project_id=%s", chapter_number, project_id)
    except Exception as e:
        logger.warning("Failed to retain chapter entities to EverMemOS (project_id=%s ch=%s): %s", project_id, chapter_number, e)


def retain_polish_to_evermemos(project_id: str, original_snippet: str, polished_snippet: str) -> None:
    """润色成功后写入 EverMemOS，便于后续润色/续写时保持风格一致。失败仅打日志。"""
    try:
        from api_EverMemOS import is_available, add_memory
        if not is_available():
            return
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        content = f"润色前：{original_snippet[:500]}{'…' if len(original_snippet) > 500 else ''}\n润色后：{polished_snippet[:500]}{'…' if len(polished_snippet) > 500 else ''}"
        msg_id = "msg_" + uuid.uuid4().hex
        add_memory([{"message_id": msg_id, "create_time": ts, "sender": CREATOR_SENDER, "content": content, "group_id": _evermemos_group_id(project_id)}])
        _append_evermemos_ids(project_id, [msg_id])
        logger.info("Retained polish to EverMemOS for project_id=%s", project_id)
    except Exception as e:
        logger.warning("Failed to retain polish to EverMemOS (project_id=%s): %s", project_id, e)


def retain_chat_to_evermemos(project_id: str, user_message: str, assistant_reply: str) -> None:
    """对话成功后写入 EverMemOS，便于后续规划/续写/对话时利用用户偏好与设定。失败仅打日志。"""
    try:
        from api_EverMemOS import is_available, add_memory
        if not is_available():
            return
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        content = f"用户：{user_message[:800]}{'…' if len(user_message) > 800 else ''}\n助手：{assistant_reply[:800]}{'…' if len(assistant_reply) > 800 else ''}"
        msg_id = "msg_" + uuid.uuid4().hex
        add_memory([{"message_id": msg_id, "create_time": ts, "sender": CREATOR_SENDER, "content": content, "group_id": _evermemos_group_id(project_id)}])
        _append_evermemos_ids(project_id, [msg_id])
        logger.info("Retained chat to EverMemOS for project_id=%s", project_id)
    except Exception as e:
        logger.warning("Failed to retain chat to EverMemOS (project_id=%s): %s", project_id, e)


def _content_from_evermemos_memory(m: Any) -> Optional[str]:
    """从 EverMemOS 单条记忆（EpisodeMemory/EventLog 等）提取展示用文本。优先 summary/episode/content。"""
    if m is None:
        return None
    if isinstance(m, dict):
        for key in ("summary", "episode", "content", "memory_content", "foresight", "atomic_fact"):
            val = m.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()
            if isinstance(val, list) and val:
                return " ".join(str(x) for x in val[:5] if x).strip() or None
        return None
    for key in ("summary", "episode", "content", "memory_content", "foresight", "atomic_fact"):
        val = getattr(m, key, None)
        if isinstance(val, str) and val.strip():
            return val.strip()
        if isinstance(val, list) and val:
            return " ".join(str(x) for x in val[:5] if x).strip() or None
    return None


def delete_from_evermemos(memory_id: str) -> bool:
    """删除一条云端记忆（创作助手写入的用 CREATOR_AGENT user_id 删除）。成功返回 True。"""
    if not memory_id or not memory_id.strip():
        return False
    try:
        from api_EverMemOS import is_available, delete_memory
        if not is_available():
            return False
        delete_memory(user_id=CREATOR_USER_ID, memory_id=memory_id.strip())
        return True
    except Exception as e:
        logger.warning("delete_from_evermemos failed: %s", e)
        return False


def recall_from_evermemos(
    project_id: str,
    query: str,
    top_k: int = 10,
) -> List[Dict[str, Any]]:
    """从 EverMemOS 按 group_id（由 project_id 派生的 ASCII）与 query 检索，供 prompt 或前端展示。"""
    try:
        from api_EverMemOS import is_available, search_memory
        if not is_available():
            return []
        raw = search_memory(query, user_id=CREATOR_USER_ID, group_id=_evermemos_group_id(project_id), top_k=top_k)
        if not raw:
            return []
        seen_ids: set = set()
        seen_content_prefix: set = set()
        out: List[Dict[str, Any]] = []
        for m in raw:
            mem_id = getattr(m, "id", None) or getattr(m, "memory_id", None) or (m.get("id") or m.get("memory_id") if isinstance(m, dict) else None)
            if mem_id and mem_id in seen_ids:
                continue
            content = _content_from_evermemos_memory(m)
            if not content:
                continue
            content_trim = content[:2000] if len(content) > 2000 else content
            content_key = content_trim[:80].strip()
            if content_key and content_key in seen_content_prefix and not mem_id:
                continue
            if mem_id:
                seen_ids.add(mem_id)
            if content_key:
                seen_content_prefix.add(content_key)
            out.append({"content": content_trim, "id": mem_id})
        return out
    except Exception as e:
        logger.warning("recall_from_evermemos failed: %s", e)
        return []


def list_from_evermemos(project_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """按 project_id 对应 group_id 拉取该项目下全部云端记忆（不依赖 query），与 recall_from_evermemos 返回格式一致；用于前端「云端记忆」列表、重启后可靠展示。"""
    try:
        from api_EverMemOS import is_available, get_memory
        if not is_available():
            return []
        raw = get_memory(user_id=CREATOR_USER_ID, group_id=_evermemos_group_id(project_id))
        if not raw:
            return []
        seen_ids: set = set()
        seen_content_prefix: set = set()
        out: List[Dict[str, Any]] = []
        for m in raw[: limit * 2]:
            if len(out) >= limit:
                break
            mem_id = getattr(m, "id", None) or getattr(m, "memory_id", None) or (m.get("id") or m.get("memory_id") if isinstance(m, dict) else None)
            if mem_id and mem_id in seen_ids:
                continue
            content = _content_from_evermemos_memory(m)
            if not content:
                continue
            content_trim = content[:2000] if len(content) > 2000 else content
            content_key = content_trim[:80].strip()
            if content_key and content_key in seen_content_prefix and not mem_id:
                continue
            if mem_id:
                seen_ids.add(mem_id)
            if content_key:
                seen_content_prefix.add(content_key)
            out.append({"content": content_trim, "id": mem_id})
        return out
    except Exception as e:
        logger.warning("list_from_evermemos failed: %s", e)
        return []


# 三类检索（跨章人物、伏笔、长线设定），供 run_retrieval_demo/API 与 recall_for_mode(continue) 共用
RETRIEVAL_DEMO_QUERIES = [
    ("跨章人物", "主角 人物 角色 成长 变化 关系"),
    ("伏笔", "伏笔 铺垫 悬念 回收 线索"),
    ("长线设定", "世界观 设定 规则 体系 玄灵 大陆"),
]

# 续写专用：近期情节（章节数>5 时启用，强化前后章衔接）
CONTINUE_QUERY_RECENT = ("近期情节", "近期 情节 发展 剧情 承接 上一章")

# 长程召回（章节>=21 时启用）：针对早期章节的叙事细节（初次相遇、遗迹发现、人物登场、具体数字与术语）
CONTINUE_QUERY_LONGRANGE = ("长程细节", "主角初次相遇 遗迹发现 人物登场 早期情节 具体数字 技术术语")

# 按模式区分的查询策略：(单 query 字符串) 或 (多 (label, query) 的列表)，以及 top_k
MODE_QUERY_CONFIG = {
    "create": {"query": "风格 主题 类型 过往创作 大纲 设定 世界观", "top_k": 8},
    "polish": {"query": "风格 语气 润色偏好 用词 文风", "top_k": 6},
    "chat": {"query": "对话 偏好 设定 大纲 人物 情节", "top_k": 6},
}


def recall_three_types_from_evermemos(
    project_id: str,
    top_k_per_type: int = 5,
    include_recent_plot: bool = False,
    include_longrange: bool = False,
    extra_queries: Optional[List[Tuple[str, str]]] = None,
) -> List[Dict[str, Any]]:
    """按三类（跨章人物、伏笔、长线设定）检索云端记忆并合并去重；可选近期情节、长程细节、额外查询。
    返回格式与 recall_from_evermemos 一致，可直接用于 extra_memory_context。
    include_longrange：章节>=21 时 True，加入长程召回以获取早期章节的叙事细节。"""
    seen_ids: set = set()
    seen_content_prefix: set = set()
    out: List[Dict[str, Any]] = []
    queries = list(RETRIEVAL_DEMO_QUERIES)
    if include_recent_plot:
        queries.append(CONTINUE_QUERY_RECENT)
    if include_longrange:
        queries.append(CONTINUE_QUERY_LONGRANGE)
    if extra_queries:
        queries.extend(extra_queries)
    for _label, query in queries:
        items = recall_from_evermemos(project_id, query, top_k=top_k_per_type)
        for x in items:
            mem_id = x.get("id")
            content = (x.get("content") or "").strip()
            if not content:
                continue
            content_trim = content[:2000] if len(content) > 2000 else content
            content_key = content_trim[:80].strip()
            if mem_id and mem_id in seen_ids:
                continue
            if content_key and content_key in seen_content_prefix and not mem_id:
                continue
            if mem_id:
                seen_ids.add(mem_id)
            if content_key:
                seen_content_prefix.add(content_key)
            out.append({"content": content_trim, "id": mem_id})
    return out


def recall_for_mode(
    project_id: str,
    mode: str,
    chapter_number: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """按创作模式检索云端记忆，供 prompt 注入。mode: create/continue/polish/chat。"""
    try:
        from api_EverMemOS import is_available
        if not is_available():
            return []
    except Exception:
        return []
    if mode == "continue":
        ch = chapter_number or 0
        top_k_per = 5 if ch <= 10 else (6 if ch <= 20 else 7)
        include_recent = ch > 5
        include_longrange = ch >= 21
        return recall_three_types_from_evermemos(
            project_id,
            top_k_per_type=top_k_per,
            include_recent_plot=include_recent,
            include_longrange=include_longrange,
        )
    cfg = MODE_QUERY_CONFIG.get(mode)
    if not cfg:
        return []
    items = recall_from_evermemos(project_id, cfg["query"], top_k=cfg["top_k"])
    return items


RETRIEVAL_DEMO_EXCERPT_MAX = 120
RETRIEVAL_DEMO_EXCERPT_COUNT = 3
DEFAULT_RETRIEVAL_DEMO_LOG_PATH = _BASE / "scripts" / "evermemos_retrieval_log.jsonl"


def run_retrieval_demo(
    project_id: str,
    top_k: int = 8,
    log_path: Optional[Path] = None,
    include_recent_plot: bool = True,
    include_longrange: bool = True,
) -> List[Dict[str, Any]]:
    """跑三类检索（跨章人物、伏笔、长线设定、近期情节、长程细节）并返回摘要；若提供 log_path 则追加到 JSONL 日志。
    与续写流程一致；include_recent_plot 为 True 时加入近期情节；include_longrange 为 True 时加入长程细节（续写 ch≥21 时启用）。"""
    try:
        from api_EverMemOS import is_available
        if not is_available():
            return []
    except Exception:
        return []

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    entries: List[Dict[str, Any]] = []
    queries = list(RETRIEVAL_DEMO_QUERIES)
    if include_recent_plot:
        queries.append(CONTINUE_QUERY_RECENT)
    if include_longrange:
        queries.append(CONTINUE_QUERY_LONGRANGE)
    for query_type, query in queries:
        items = recall_from_evermemos(project_id, query, top_k=top_k)
        count = len(items)
        excerpts: List[str] = []
        for item in items[:RETRIEVAL_DEMO_EXCERPT_COUNT]:
            content = (item.get("content") or "").strip()
            if content:
                excerpts.append(
                    content[:RETRIEVAL_DEMO_EXCERPT_MAX]
                    + ("…" if len(content) > RETRIEVAL_DEMO_EXCERPT_MAX else "")
                )
        record = {
            "query_type": query_type,
            "query": query,
            "top_k": top_k,
            "result_count": count,
            "excerpts": excerpts,
        }
        entries.append(record)

        if log_path:
            log_line = {
                "timestamp": ts,
                "project_id": project_id,
                "query_type": query_type,
                "query": query,
                "top_k": top_k,
                "result_count": count,
                "excerpts": excerpts,
                "note": "",
            }
            try:
                log_path.parent.mkdir(parents=True, exist_ok=True)
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(log_line, ensure_ascii=False) + "\n")
            except Exception as e:
                logger.warning("run_retrieval_demo write log failed: %s", e)

    return entries


_TYPE_MAP = {
    "person": "entity", "character": "entity", "location": "entity", "organization": "entity",
    "item": "entity", "concept": "entity", "creature": "entity", "setting": "entity",
    "chapter": "atom", "plot_point": "atom", "foreshadowing": "atom",
}


def _load_mesh(project_id: str) -> Optional[Dict[str, Any]]:
    d = project_dir(project_id)
    mesh_file = d / "semantic_mesh" / "mesh.json"
    if not mesh_file.exists():
        return None
    try:
        with open(mesh_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning("Failed to load mesh for %s: %s", project_id, e)
        return None


def read_mesh(project_id: str) -> Optional[Dict[str, Any]]:
    """按 project 读取 semantic_mesh（mesh.json）。创作记忆抽象入口。"""
    return _load_mesh(project_id)


def write_mesh(project_id: str, mesh_data: Dict[str, Any]) -> None:
    """按 project 写入 semantic_mesh（mesh.json）。创作记忆抽象入口。失败打日志不抛错。"""
    d = project_dir(project_id)
    mesh_dir = d / "semantic_mesh"
    mesh_dir.mkdir(parents=True, exist_ok=True)
    mesh_file = mesh_dir / "mesh.json"
    try:
        mesh_file.write_text(
            json.dumps(mesh_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.debug("Written mesh for project_id=%s", project_id)
    except Exception as e:
        logger.warning("Failed to write mesh for %s: %s", project_id, e)


def retain_plan(project_id: str, plan_summary: str) -> None:
    """大纲成功后写入 UniMem + EverMemOS（可选）。创作记忆抽象入口。"""
    retain_plan_to_unimem(project_id, plan_summary)
    retain_plan_to_evermemos(project_id, plan_summary)


def retain_chapter(
    project_id: str,
    chapter_number: int,
    content: str,
    chapter_summary: Optional[str] = None,
) -> None:
    """章节成功后写入 UniMem + EverMemOS（可选）。创作记忆抽象入口。"""
    retain_chapter_to_unimem(project_id, chapter_number, content)
    retain_chapter_to_evermemos(
        project_id, chapter_number, content, chapter_summary=chapter_summary
    )


def retain_chapter_entities(project_id: str, chapter_number: int) -> None:
    """章节实体写入 EverMemOS（可选）。创作记忆抽象入口。"""
    retain_chapter_entities_to_evermemos(project_id, chapter_number)


def retain_polish(project_id: str, original_snippet: str, polished_snippet: str) -> None:
    """润色成功后写入 EverMemOS（可选）。创作记忆抽象入口。"""
    retain_polish_to_evermemos(project_id, original_snippet, polished_snippet)


def retain_chat(project_id: str, user_message: str, assistant_reply: str) -> None:
    """对话成功后写入 EverMemOS（可选）。创作记忆抽象入口。"""
    retain_chat_to_evermemos(project_id, user_message, assistant_reply)


def get_entities(project_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """GET /api/memory/entities 返回列表。启用 UniMem 时合并 recall 结果。"""
    pid = normalize_project_id(project_id)
    mesh = _load_mesh(pid)
    entities = mesh.get("entities") or {} if mesh else {}
    out = []
    for eid, e in entities.items():
        if not isinstance(e, dict):
            continue
        out.append({
            "id": e.get("id") or eid,
            "name": e.get("name") or str(eid),
            "type": e.get("type", "entity"),
            "brief": (e.get("content") or "")[:200] if e.get("content") else None,
        })
    u = _get_unimem()
    if u:
        try:
            from unimem.memory_types import Context
            ctx = Context(metadata={"task_id": pid, "project_id": pid})
            results = u.recall_for_agent("实体 角色 情节 项目", context=ctx, top_k=20)
            seen = {x["id"] for x in out}
            for r in results[:20]:
                m = r.memory
                mid = "unimem_" + m.id
                if mid in seen:
                    continue
                seen.add(mid)
                out.append({
                    "id": mid,
                    "name": (m.content or "")[:80] or mid,
                    "type": "entity",
                    "brief": (m.content or "")[:200] if m.content else None,
                })
        except Exception as e:
            logger.debug("UniMem merge entities skip: %s", e)
    return out


def get_graph(project_id: Optional[str] = None, max_nodes: int = 80) -> Dict[str, Any]:
    """GET /api/memory/graph 返回 { nodes, links }。启用 UniMem 时合并 recall 结果为额外节点与边（P1 2.4）。"""
    pid = normalize_project_id(project_id)
    mesh = _load_mesh(pid)
    nodes: List[Dict[str, Any]] = []
    links: List[Dict[str, Any]] = []
    id_to_node: Dict[str, Dict[str, Any]] = {}
    if not mesh:
        mesh = {}

    entities = mesh.get("entities") or {}
    relations = mesh.get("relations") or []

    order = ["character", "concept", "location", "organization", "item", "creature", "setting", "chapter", "plot_point", "foreshadowing"]
    by_type: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {k: [] for k in order}
    for eid, e in entities.items():
        if not isinstance(e, dict):
            continue
        t = e.get("type", "entity")
        k = t if t in by_type else "character"
        by_type.setdefault(k, []).append((eid, e))

    def add_node(eid: str, e: Dict[str, Any], source_label: Optional[str] = None) -> None:
        node_type = _TYPE_MAP.get(e.get("type", "entity"), "entity")
        name = e.get("name") or str(eid)
        content = (e.get("content") or "")[:300]
        id_to_node[eid] = {
            "id": e.get("id") or eid,
            "label": name,
            "type": node_type,
            "brief": content or None,
            "source": source_label or (f"第{e.get('metadata', {}).get('chapter', '?')}章" if node_type == "atom" and isinstance(e.get("metadata"), dict) else None),
            "body": content if node_type == "atom" and content else None,
        }

    # 先选少量 chapter，再按 order 填满
    for eid, e in (by_type.get("chapter") or [])[:12]:
        add_node(eid, e)
    for k in order:
        if k == "chapter":
            continue
        for eid, e in (by_type.get(k) or []):
            if len(id_to_node) >= max_nodes:
                break
            add_node(eid, e)
        if len(id_to_node) >= max_nodes:
            break

    for r in relations:
        if not isinstance(r, dict):
            continue
        src = r.get("source_id")
        tgt = r.get("target_id")
        if src and tgt and src in id_to_node and tgt in id_to_node:
            links.append({
                "source": src,
                "target": tgt,
                "relation": (r.get("relation_type") or "").replace("_", "") or None,
            })

    # UniMem 合并：recall 结果作为节点，links 作为边
    u = _get_unimem()
    if u and len(id_to_node) < max_nodes:
        try:
            from unimem.memory_types import Context
            ctx = Context(metadata={"task_id": pid, "project_id": pid})
            results = u.recall_for_agent("项目 章节 情节", context=ctx, top_k=min(30, max_nodes - len(id_to_node)))
            for r in results:
                if len(id_to_node) >= max_nodes:
                    break
                m = r.memory
                mid = "unimem_" + m.id
                if mid in id_to_node:
                    continue
                id_to_node[mid] = {
                    "id": mid,
                    "label": (m.content or "")[:60] or mid,
                    "type": "entity",
                    "brief": (m.content or "")[:300] if m.content else None,
                    "source": "UniMem",
                    "body": (m.content or "")[:500] if m.content else None,
                }
                for link_id in (getattr(m, "links", None) or [])[:5]:
                    link_mid = "unimem_" + link_id if not str(link_id).startswith("unimem_") else link_id
                    if link_mid in id_to_node and link_mid != mid:
                        links.append({"source": mid, "target": link_mid, "relation": "related"})
        except Exception as e:
            logger.debug("UniMem merge graph skip: %s", e)

    nodes = list(id_to_node.values())
    return {"nodes": nodes, "links": links}


def get_recents(project_id: Optional[str] = None, limit: int = 5) -> List[str]:
    """GET /api/memory/recents 返回最近检索描述。启用 UniMem 时合并 recall 摘要。"""
    entities = get_entities(project_id)
    names = [e["name"] for e in entities[:limit] if e.get("name")]
    out: List[str] = [f"记忆检索: {', '.join(names)}"] if names else []
    u = _get_unimem()
    if u:
        try:
            from unimem.memory_types import Context
            ctx = Context(metadata={"task_id": normalize_project_id(project_id), "project_id": project_id})
            results = u.recall_for_agent("最近 记忆", context=ctx, top_k=limit)
            for r in results[:limit]:
                brief = (r.memory.content or "").strip()
                if brief:
                    out.append(brief[:100] + ("…" if len(brief) > 100 else ""))
        except Exception as e:
            logger.debug("UniMem merge recents skip: %s", e)
    return out[:limit]


def get_note(node_id: str, project_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """GET /api/memory/note/<id> 返回单节点详情。若为 UniMem 节点（unimem_ 前缀）则从 UniMem 取。"""
    pid = normalize_project_id(project_id)

    if node_id.startswith("unimem_"):
        raw_id = node_id.replace("unimem_", "", 1)
        u = _get_unimem()
        if u:
            try:
                from unimem.neo4j import get_memory
                m = get_memory(raw_id)
                if m:
                    related = []
                    for link_id in (getattr(m, "links", None) or [])[:10]:
                        link_mid = "unimem_" + link_id if not str(link_id).startswith("unimem_") else link_id
                        related.append({"node": {"id": link_mid, "label": link_mid}, "relation": "related"})
                    return {
                        "id": node_id,
                        "label": (m.content or "")[:80] or node_id,
                        "type": "entity",
                        "brief": (m.content or "")[:300] if m.content else None,
                        "source": "UniMem",
                        "body": (m.content or "")[:500] if m.content else None,
                        "related": related,
                    }
            except Exception as e:
                logger.debug("UniMem get_note skip: %s", e)
        # Neo4j 中无该节点时（如 LTM 为 memory 或仅写入 Qdrant）返回占位，避免 404
        return {
            "id": node_id,
            "label": node_id,
            "type": "entity",
            "brief": "该记忆未在 Neo4j 中（可能仅存在于向量库或内存）。请确认 UNIMEM_GRAPH_BACKEND=neo4j 且 Neo4j 已写入。",
            "source": "UniMem",
            "body": None,
            "related": [],
        }

    mesh = _load_mesh(pid)
    if not mesh:
        return None
    entities = mesh.get("entities") or {}
    relations = mesh.get("relations") or []
    e = entities.get(node_id) if isinstance(entities, dict) else None
    if not isinstance(e, dict):
        return None

    t = e.get("type", "entity")
    node_type = _TYPE_MAP.get(t, "entity")
    name = e.get("name") or str(node_id)
    content = (e.get("content") or "")[:500]
    related: List[Dict[str, Any]] = []
    for r in relations:
        if not isinstance(r, dict):
            continue
        src, tgt = r.get("source_id"), r.get("target_id")
        other_id = tgt if src == node_id else (src if tgt == node_id else None)
        if not other_id or other_id not in entities:
            continue
        other = entities.get(other_id)
        other_name = other.get("name", other_id) if isinstance(other, dict) else other_id
        related.append({"node": {"id": other_id, "label": other_name}, "relation": (r.get("relation_type") or "").replace("_", "") or None})
    return {
        "id": e.get("id") or node_id,
        "label": name,
        "type": node_type,
        "brief": content or None,
        "source": f"第{e.get('metadata', {}).get('chapter', '?')}章" if isinstance(e.get("metadata"), dict) else None,
        "body": content if node_type == "atom" and content else None,
        "related": related,
    }
