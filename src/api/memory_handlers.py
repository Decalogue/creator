"""
记忆 API 逻辑：实体、图谱、最近检索、节点详情

数据来源：semantic_mesh/mesh.json（按 project_id 即 novel_title 区分项目）
配置启用时（UNIMEM_ENABLED=1）：合并 UniMem 数据；创作成功时 Retain 写入 UniMem（P1 2.3）
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import json
import logging
import os
import threading
import queue

logger = logging.getLogger(__name__)

_BASE = Path(__file__).resolve().parent.parent
_OUTPUTS = _BASE / "novel_creation" / "outputs"

***REMOVED*** UniMem 可选后端：环境变量 UNIMEM_ENABLED=1 时启用
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
                ***REMOVED*** 从环境变量构建 config，使 LayeredStorageAdapter / GraphAdapter / AtomLinkAdapter 使用 Redis / Neo4j / Qdrant
                sb = os.getenv("UNIMEM_STORAGE_BACKEND", "memory").strip().lower()
                gb = os.getenv("UNIMEM_GRAPH_BACKEND", "neo4j").strip().lower()
                vb = os.getenv("UNIMEM_VECTOR_BACKEND", "memory").strip().lower()
                if sb == "memory" and gb == "memory" and vb == "memory":
                    logger.info(
                        "UniMem using memory-only backends; data will not persist to Qdrant/Neo4j. "
                        "Set UNIMEM_STORAGE_BACKEND=redis, UNIMEM_GRAPH_BACKEND=neo4j, UNIMEM_VECTOR_BACKEND=qdrant for persistence."
                    )
                ***REMOVED*** 未设置 UNIMEM_LIGHTRAG_URL 时不连 LightRAG（避免 POST /query 到 localhost:9621 报错）
                lightrag_url = (os.getenv("UNIMEM_LIGHTRAG_URL") or "").strip()
                unimem_config = {
                    "storage": {
                        "foa_backend": sb,
                        "da_backend": sb,
                        "ltm_backend": gb,
                    },
                    "graph": {"backend": gb, "api_base_url": lightrag_url},
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

_TYPE_MAP = {
    "person": "entity", "character": "entity", "location": "entity", "organization": "entity",
    "item": "entity", "concept": "entity", "creature": "entity", "setting": "entity",
    "chapter": "atom", "plot_point": "atom", "foreshadowing": "atom",
}


def _project_dir(project_id: str) -> Path:
    pid = (project_id or "完美之墙").strip() or "完美之墙"
    return _OUTPUTS / pid


def _load_mesh(project_id: str) -> Optional[Dict[str, Any]]:
    d = _project_dir(project_id)
    mesh_file = d / "semantic_mesh" / "mesh.json"
    if not mesh_file.exists():
        return None
    try:
        with open(mesh_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning("Failed to load mesh for %s: %s", project_id, e)
        return None


def get_entities(project_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """GET /api/memory/entities 返回列表。启用 UniMem 时合并 recall 结果。"""
    pid = project_id or "完美之墙"
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
    pid = project_id or "完美之墙"
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

    ***REMOVED*** 先选少量 chapter，再按 order 填满
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

    ***REMOVED*** UniMem 合并：recall 结果作为节点，links 作为边
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
            ctx = Context(metadata={"task_id": project_id or "完美之墙", "project_id": project_id})
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
    pid = project_id or "完美之墙"

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
        ***REMOVED*** Neo4j 中无该节点时（如 LTM 为 memory 或仅写入 Qdrant）返回占位，避免 404
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
