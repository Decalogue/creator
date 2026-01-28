"""
记忆 API 逻辑：实体、图谱、最近检索、节点详情

数据来源：semantic_mesh/mesh.json（按 project_id 即 novel_title 区分项目）
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import json
import logging

logger = logging.getLogger(__name__)

_BASE = Path(__file__).resolve().parent.parent
_OUTPUTS = _BASE / "novel_creation" / "outputs"

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
    """GET /api/memory/entities 返回列表."""
    mesh = _load_mesh(project_id or "完美之墙")
    if not mesh:
        return []
    entities = mesh.get("entities") or {}
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
    return out


def get_graph(project_id: Optional[str] = None, max_nodes: int = 80) -> Dict[str, Any]:
    """GET /api/memory/graph 返回 { nodes, links }，与前端 memoryGraphData 结构兼容."""
    mesh = _load_mesh(project_id or "完美之墙")
    nodes: List[Dict[str, Any]] = []
    links: List[Dict[str, Any]] = []
    if not mesh:
        return {"nodes": nodes, "links": links}

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

    def add_node(eid: str, e: Dict[str, Any]) -> None:
        node_type = _TYPE_MAP.get(e.get("type", "entity"), "entity")
        name = e.get("name") or str(eid)
        content = (e.get("content") or "")[:300]
        id_to_node[eid] = {
            "id": e.get("id") or eid,
            "label": name,
            "type": node_type,
            "brief": content or None,
            "source": f"第{e.get('metadata', {}).get('chapter', '?')}章" if node_type == "atom" and isinstance(e.get("metadata"), dict) else None,
            "body": content if node_type == "atom" and content else None,
        }

    id_to_node = {}
    ***REMOVED*** 先选少量 chapter，再按 order 填满，以保留 chapter–实体 边
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

    nodes = list(id_to_node.values())
    return {"nodes": nodes, "links": links}


def get_recents(project_id: Optional[str] = None, limit: int = 5) -> List[str]:
    """GET /api/memory/recents 返回最近检索描述（当前用最近若干实体名模拟）."""
    entities = get_entities(project_id)
    names = [e["name"] for e in entities[:limit] if e.get("name")]
    if not names:
        return []
    return [f"记忆检索: {', '.join(names)}"]


def get_note(node_id: str, project_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """GET /api/memory/note/<id> 返回单节点详情，供前端抽屉展示."""
    mesh = _load_mesh(project_id or "完美之墙")
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
