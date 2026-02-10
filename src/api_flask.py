"""
Flask 主入口：/api/chat、创作与记忆 API。
配置从 config 与 .env 读取，见 config/__init__.py 与 .env.example。
"""
import hashlib
import os
import time
import uuid
import queue
import json
import threading

from flask import Flask, request, jsonify, stream_with_context, Response
from flask_cors import CORS

from config import (
    backend_url,
    FLASK_DEBUG,
    FLASK_SECRET_KEY,
    FLASK_HOST,
    FLASK_PORT,
    CHAT_DEFAULT_MODEL,
    CHAT_MESSAGES_MAX_HISTORY,
    CREATOR_TASKS_MAX,
    SSE_KEEPALIVE_SEC,
    normalize_project_id,
    list_projects as config_list_projects,
    project_dir,
)

app = Flask(__name__)
app.debug = FLASK_DEBUG
app.config["WTF_CSRF_ENABLED"] = True
app.config["SECRET_KEY"] = FLASK_SECRET_KEY
CORS(app)

from llm.chat import CHAT_MODELS, chat_model_key


@app.route("/api/chat", methods=["POST"])
def chat():
    state = {"code": 1, "message": "回复失败", "content": ""}
    try:
        if not request.json:
            state["message"] = "请求数据格式错误：缺少 JSON 数据"
            return jsonify(state)
        if "messages" not in request.json:
            state["message"] = "请求数据格式错误：缺少 messages 字段"
            return jsonify(state)

        messages = request.json["messages"][-CHAT_MESSAGES_MAX_HISTORY:]
        stream = request.json.get("stream", False)
        model_raw = request.json.get("model", CHAT_DEFAULT_MODEL)
        model_key = chat_model_key(model_raw)

        if model_key not in CHAT_MODELS:
            state["message"] = "请求异常：模型不存在"
            return jsonify(state)

        llm_fn, stream_fn = CHAT_MODELS[model_key]
        if stream:
            def gen():
                for t in stream_fn(messages):
                    yield t
            return Response(stream_with_context(gen()), mimetype="text/plain;charset=utf-8")

        reasoning_content, content = llm_fn(messages)
        if content:
            state["code"] = 0
            state["message"] = "回复成功"
            state["content"] = content
            if reasoning_content:
                state["reasoning_content"] = reasoning_content
        else:
            state["message"] = "请求异常：模型返回空内容"
        return jsonify(state)
    except Exception as e:
        state["message"] = f"服务器错误：{str(e)}"
        app.logger.error("Chat API error: %s", e, exc_info=True)
        return jsonify(state)


# 创作与记忆拆分导入：仅创作 (creator_handlers) 失败时续写不可用；记忆 (memory_handlers) 失败时用 fallback，续写仍可进行
creator_run = None
creator_get_chapters = None
try:
    from api.creator_handlers import (
        run as creator_run,
        get_project_chapters as creator_get_chapters,
    )
    _CREATOR_AVAILABLE = True
except Exception as e:
    app.logger.warning("Creator handlers not available: %s", e)
    _CREATOR_AVAILABLE = False

try:
    from api.memory_handlers import (
        get_entities as memory_get_entities,
        get_graph as memory_get_graph,
        get_recents as memory_get_recents,
        get_note as memory_get_note,
        recall_from_evermemos as memory_recall_from_evermemos,
    )
    _MEMORY_AVAILABLE = True
except Exception as e:
    app.logger.warning("Memory handlers not available: %s", e)
    _MEMORY_AVAILABLE = False
    memory_get_entities = None
    memory_get_graph = None
    memory_get_recents = None
    memory_get_note = None
    memory_recall_from_evermemos = None

# 续写/stream 仅依赖创作就绪；记忆为可选（失败时 creator_handlers 内已 try/except 跳过）
_CREATOR_MEMORY_AVAILABLE = _CREATOR_AVAILABLE

# 记忆只读 fallback：仅依赖 config + 本地 mesh.json，在 creator/memory 未加载时仍能展示实体/图谱
_TYPE_MAP_FALLBACK = {
    "person": "entity", "character": "entity", "location": "entity", "organization": "entity",
    "item": "entity", "concept": "entity", "creature": "entity", "setting": "entity",
    "chapter": "atom", "plot_point": "atom", "foreshadowing": "atom",
}


def _fallback_load_mesh(project_id):
    pid = normalize_project_id(project_id)
    mesh_file = project_dir(pid) / "semantic_mesh" / "mesh.json"
    if not mesh_file.exists():
        return None
    try:
        with open(mesh_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _fallback_entities(project_id):
    mesh = _fallback_load_mesh(project_id)
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
    return out


def _fallback_graph(project_id, max_nodes=80):
    mesh = _fallback_load_mesh(project_id) or {}
    entities = mesh.get("entities") or {}
    relations = mesh.get("relations") or []
    order = ["character", "concept", "location", "organization", "item", "creature", "setting", "chapter", "plot_point", "foreshadowing"]
    by_type = {k: [] for k in order}
    for eid, e in entities.items():
        if not isinstance(e, dict):
            continue
        t = e.get("type", "entity")
        k = t if t in by_type else "character"
        by_type.setdefault(k, []).append((eid, e))
    id_to_node = {}
    for eid, e in (by_type.get("chapter") or [])[:12]:
        _add_node(id_to_node, eid, e)
    for k in order:
        if k == "chapter":
            continue
        for eid, e in (by_type.get(k) or []):
            if len(id_to_node) >= max_nodes:
                break
            _add_node(id_to_node, eid, e)
        if len(id_to_node) >= max_nodes:
            break
    links = []
    for r in relations:
        if not isinstance(r, dict):
            continue
        src, tgt = r.get("source_id"), r.get("target_id")
        if src and tgt and src in id_to_node and tgt in id_to_node:
            links.append({"source": src, "target": tgt, "relation": (r.get("relation_type") or "").replace("_", "") or None})
    return {"nodes": list(id_to_node.values()), "links": links}


def _add_node(id_to_node, eid, e):
    node_type = _TYPE_MAP_FALLBACK.get(e.get("type", "entity"), "entity")
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


def _fallback_recents(project_id, limit=5):
    entities = _fallback_entities(project_id)
    names = [e["name"] for e in entities[:limit] if e.get("name")]
    return [f"记忆检索: {', '.join(names)}"] if names else []


def _fallback_chapters(project_id):
    """仅依赖 config + 本地 novel_plan.json / chapters 目录，返回与 get_project_chapters 相同结构。(code, list|None)"""
    pid = normalize_project_id(project_id)
    root = project_dir(pid)
    plan_file = root / "novel_plan.json"
    chapters_dir = root / "chapters"
    if not plan_file.exists():
        # 无大纲时仅从 chapters 目录推断：共 N 章、已写 M 章
        existing = []
        if chapters_dir.exists():
            for f in chapters_dir.glob("chapter_*.txt"):
                try:
                    suffix = f.stem.replace("chapter_", "").strip()
                    if suffix.isdigit():
                        existing.append(int(suffix))
                except Exception:
                    pass
        if not existing:
            return 1, None
        existing.sort()
        out = [{"number": n, "title": f"第{n}章", "summary": "", "has_file": True} for n in existing]
        return 0, out
    try:
        with open(plan_file, "r", encoding="utf-8") as f:
            plan = json.load(f)
    except Exception:
        return 1, None
    co = plan.get("chapter_outline") or (plan.get("plan") or {}).get("chapter_outline")
    if not isinstance(co, list) or not co:
        # 渐进式大纲：从 phases[].chapters 合并
        phases = plan.get("phases") or []
        co = []
        for p in phases:
            if isinstance(p, dict):
                co.extend(p.get("chapters") or [])
    if not isinstance(co, list):
        co = []
    existing_files = set()
    if chapters_dir.exists():
        for f in chapters_dir.glob("chapter_*.txt"):
            try:
                suffix = f.stem.replace("chapter_", "").strip()
                if suffix.isdigit():
                    existing_files.add(int(suffix))
            except Exception:
                pass
    out = []
    for i, ch in enumerate(co):
        if not isinstance(ch, dict):
            continue
        num = ch.get("chapter_number", i + 1)
        title = ch.get("title") or f"第{num}章"
        summary = ch.get("summary") or ""
        out.append({
            "number": num,
            "title": title,
            "summary": summary[:200] if summary else "",
            "has_file": num in existing_files,
        })
    # 若大纲条数少于 target_chapters（如渐进式只生成了首阶段），补齐到 target_chapters
    target = plan.get("target_chapters")
    if isinstance(target, int) and target > 0:
        max_num = max((x["number"] for x in out), default=0)
        if max_num < target:
            for n in range(max_num + 1, target + 1):
                out.append({
                    "number": n,
                    "title": f"第{n}章",
                    "summary": "",
                    "has_file": n in existing_files,
                })
    return 0, out


def _fallback_note(node_id, project_id):
    mesh = _fallback_load_mesh(project_id)
    if not mesh:
        return None
    entities = mesh.get("entities") or {}
    relations = mesh.get("relations") or []
    e = entities.get(node_id) if isinstance(entities, dict) else None
    if not isinstance(e, dict):
        return None
    node_type = _TYPE_MAP_FALLBACK.get(e.get("type", "entity"), "entity")
    name = e.get("name") or str(node_id)
    content = (e.get("content") or "")[:500]
    related = []
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


_creator_tasks = {}
_creator_tasks_lock = threading.Lock()
_continue_lock = threading.Lock()


def _run_creator_task(task_id, mode, raw, project_id, options=None):
    options = options or {}
    try:
        with _creator_tasks_lock:
            _creator_tasks[task_id]["status"] = "running"
        if mode == "continue":
            _continue_lock.acquire()
        try:
            code, msg, extra = creator_run(
                mode, raw, project_id,
                previous_project_id=options.get("previous_project_id"),
                start_chapter=options.get("start_chapter"),
                target_chapters=options.get("target_chapters"),
                use_evermemos_context=options.get("use_evermemos_context", True),
                use_progressive=options.get("use_progressive"),
            )
        finally:
            if mode == "continue":
                _continue_lock.release()
        with _creator_tasks_lock:
            _creator_tasks[task_id] = {
                "status": "done",
                "code": code,
                "message": msg,
                "content": (extra or {}).get("content", ""),
                **(extra or {}),
            }
    except Exception as e:
        app.logger.exception("Creator task failed: %s", e)
        with _creator_tasks_lock:
            _creator_tasks[task_id] = {"status": "failed", "error": str(e)}


def _run_creator_stream_task(ev_queue, mode, raw, project_id, options=None):
    options = options or {}
    try:
        if mode == "continue":
            _continue_lock.acquire()
        try:
            code, msg, extra = creator_run(
                mode, raw, project_id,
                previous_project_id=options.get("previous_project_id"),
                start_chapter=options.get("start_chapter"),
                target_chapters=options.get("target_chapters"),
                on_event=ev_queue.put,
                use_evermemos_context=options.get("use_evermemos_context", True),
                use_progressive=options.get("use_progressive"),
            )
            ev_queue.put({
                "type": "stream_end",
                "code": code,
                "message": msg,
                "content": (extra or {}).get("content", ""),
                **(extra or {}),
            })
        finally:
            if mode == "continue":
                _continue_lock.release()
    except Exception as e:
        app.logger.exception("Creator stream task failed: %s", e)
        ev_queue.put({"type": "stream_end", "code": 1, "message": str(e), "content": ""})
    ev_queue.put(None)


@app.route("/api/config", methods=["GET"])
def api_config():
    """GET /api/config 返回后端配置（含 EverMemOS 是否可用）"""
    unimem_enabled = False
    evermemos_available = False
    if _MEMORY_AVAILABLE:
        try:
            from api.memory_handlers import _unimem_enabled
            unimem_enabled = _unimem_enabled()
        except Exception:
            pass
    try:
        from api_EverMemOS import is_available
        evermemos_available = is_available()
    except Exception:
        pass
    return jsonify({
        "backend_url": backend_url,
        "unimem_enabled": unimem_enabled,
        "evermemos_available": evermemos_available,
    })


@app.route("/api/creator/run", methods=["POST"])
def creator_run_endpoint():
    """POST /api/creator/run  body: { mode, input, project_id?, ... } 立即返回 task_id"""
    if not _CREATOR_AVAILABLE or creator_run is None:
        return jsonify({"code": 1, "message": "创作服务未就绪", "content": ""})
    try:
        data = request.json or {}
        mode = data.get("mode", "chat")
        raw = data.get("input", "")
        project_id = data.get("project_id")
        options = {
            "previous_project_id": data.get("previous_project_id"),
            "start_chapter": data.get("start_chapter"),
            "target_chapters": data.get("target_chapters"),
            "use_evermemos_context": data.get("use_evermemos_context", True),
            "use_progressive": data.get("use_progressive"),
        }
        task_id = str(uuid.uuid4())
        with _creator_tasks_lock:
            if len(_creator_tasks) >= CREATOR_TASKS_MAX:
                keys = list(_creator_tasks.keys())[: CREATOR_TASKS_MAX // 2]
                for k in keys:
                    del _creator_tasks[k]
            _creator_tasks[task_id] = {"status": "pending"}
        threading.Thread(
            target=_run_creator_task,
            args=(task_id, mode, raw, project_id, options),
            daemon=True,
        ).start()
        return jsonify({"code": 0, "task_id": task_id, "message": "任务已提交，请轮询状态"})
    except Exception as e:
        app.logger.exception("Creator run error")
        return jsonify({"code": 1, "message": str(e), "content": ""})


@app.route("/api/creator/stream", methods=["POST"])
def creator_stream_endpoint():
    """POST /api/creator/stream  body 同 run，返回 SSE 编排事件 + stream_end"""
    if not _CREATOR_AVAILABLE or creator_run is None:
        return jsonify({"code": 1, "message": "创作服务未就绪", "content": ""}), 503
    try:
        data = request.json or {}
        mode = data.get("mode", "chat")
        raw = data.get("input", "")
        project_id = data.get("project_id")
        options = {
            "previous_project_id": data.get("previous_project_id"),
            "start_chapter": data.get("start_chapter"),
            "target_chapters": data.get("target_chapters"),
            "use_evermemos_context": data.get("use_evermemos_context", True),
            "use_progressive": data.get("use_progressive"),
        }
        if mode not in ("create", "continue"):
            return jsonify({"code": 1, "message": "stream 仅支持 mode=create 或 continue"}), 400
        ev_queue = queue.Queue()
        threading.Thread(
            target=_run_creator_stream_task,
            args=(ev_queue, mode, raw, project_id, options),
            daemon=True,
        ).start()

        @stream_with_context
        def sse_gen():
            while True:
                try:
                    ev = ev_queue.get(timeout=SSE_KEEPALIVE_SEC)
                except queue.Empty:
                    yield ": keepalive\n\n"
                    continue
                if ev is None:
                    break
                yield "data: " + json.dumps(ev, ensure_ascii=False) + "\n\n"

        return Response(sse_gen(), mimetype="text/event-stream")
    except Exception as e:
        app.logger.exception("Creator stream error")
        return jsonify({"code": 1, "message": str(e), "content": ""}), 500


@app.route("/api/creator/task/<task_id>", methods=["GET"])
def creator_task_status(task_id):
    """GET /api/creator/task/<task_id> 轮询任务状态"""
    with _creator_tasks_lock:
        t = _creator_tasks.get(task_id)
    if t is None:
        return jsonify({"status": "unknown", "message": "任务不存在或已过期"}), 404
    out = {"status": t["status"]}
    if t["status"] == "done":
        out["code"] = t.get("code", 0)
        out["message"] = t.get("message", "")
        out["content"] = t.get("content", "")
        for k in ("project_id", "chapter_number"):
            if k in t:
                out[k] = t[k]
    elif t["status"] == "failed":
        out["error"] = t.get("error", "")
    return jsonify(out)


@app.route("/api/memory/neo4j/health", methods=["GET"])
def memory_neo4j_health():
    """GET /api/memory/neo4j/health 检查 Neo4j 连接"""
    out = {"ok": False, "uri": None, "error": None}
    if not _MEMORY_AVAILABLE:
        out["error"] = "memory module not available"
        return jsonify(out), 200
    try:
        from unimem.neo4j import get_graph, NEO4J_AVAILABLE
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7680")
        out["uri"] = uri
        if not NEO4J_AVAILABLE:
            out["error"] = "py2neo not installed"
            return jsonify(out), 200
        g = get_graph()
        if g:
            g.run("RETURN 1").data()
            out["ok"] = True
    except Exception as e:
        out["error"] = str(e)
    return jsonify(out), 200


@app.route("/api/creator/projects", methods=["GET"])
def creator_projects():
    """作品列表：直接读 config.list_projects（outputs 下含 novel_plan.json 的目录），不依赖 creator/memory 是否加载成功。"""
    try:
        return jsonify(config_list_projects())
    except Exception as e:
        app.logger.exception("List projects error")
        return jsonify([])


@app.route("/api/creator/chapters", methods=["GET"])
def creator_chapters():
    """章节列表：CREATOR 就绪时用 creator_handlers，否则用本地 novel_plan.json + chapters 目录 fallback。"""
    project_id = normalize_project_id(request.args.get("project_id"))
    try:
        if _CREATOR_AVAILABLE and creator_get_chapters:
            code, chapters = creator_get_chapters(project_id)
        else:
            code, chapters = _fallback_chapters(project_id)
        lst = chapters if code == 0 and chapters else []
        if not lst:
            code2, chapters2 = _fallback_chapters(project_id)
            lst = chapters2 if code2 == 0 and chapters2 else lst
        return jsonify({"chapters": lst, "total": len(lst)})
    except Exception as e:
        app.logger.exception("Chapters list error")
        try:
            code, chapters = _fallback_chapters(project_id)
            lst = chapters if code == 0 and chapters else []
            return jsonify({"chapters": lst, "total": len(lst)})
        except Exception:
            return jsonify({"chapters": [], "total": 0})


@app.route("/api/memory/entities", methods=["GET"])
def memory_entities():
    project_id = normalize_project_id(request.args.get("project_id"))
    if _MEMORY_AVAILABLE and memory_get_entities:
        return jsonify(memory_get_entities(project_id))
    return jsonify(_fallback_entities(project_id))


@app.route("/api/memory/graph", methods=["GET"])
def memory_graph():
    project_id = normalize_project_id(request.args.get("project_id"))
    max_nodes = request.args.get("max_nodes", type=int) or 80
    if _MEMORY_AVAILABLE and memory_get_graph:
        return jsonify(memory_get_graph(project_id, max_nodes=max_nodes))
    return jsonify(_fallback_graph(project_id, max_nodes=max_nodes))


@app.route("/api/memory/recents", methods=["GET"])
def memory_recents():
    project_id = normalize_project_id(request.args.get("project_id"))
    limit = request.args.get("limit", type=int) or 5
    if _MEMORY_AVAILABLE and memory_get_recents:
        return jsonify(memory_get_recents(project_id, limit=limit))
    return jsonify(_fallback_recents(project_id, limit=limit))


@app.route("/api/memory/note/<node_id>", methods=["GET"])
def memory_note(node_id):
    project_id = normalize_project_id(request.args.get("project_id"))
    if _MEMORY_AVAILABLE and memory_get_note:
        note = memory_get_note(node_id, project_id)
    else:
        note = _fallback_note(node_id, project_id)
    if note is None:
        return jsonify(None), 404
    return jsonify(note)


def _evermemos_group_id(project_id: str) -> str:
    """与 memory_handlers._evermemos_group_id 一致，供 fallback 用。"""
    pid = (project_id or "").strip() or "default"
    return "grp_" + hashlib.sha256(pid.encode("utf-8")).hexdigest()[:24]


# 与 memory_handlers 一致，供 retrieval-demo fallback 使用
_RETRIEVAL_DEMO_QUERIES = [
    ("跨章人物", "主角 人物 角色 成长 变化 关系"),
    ("伏笔", "伏笔 铺垫 悬念 回收 线索"),
    ("长线设定", "世界观 设定 规则 体系 玄灵 大陆"),
    ("近期情节", "近期 情节 发展 剧情 承接 上一章"),
]
_RETRIEVAL_DEMO_EXCERPT_MAX = 120
_RETRIEVAL_DEMO_EXCERPT_COUNT = 3


def _content_from_evermemos_raw(m):
    """从 EverMemOS 单条原始结果提取展示文本。"""
    if m is None:
        return None
    for key in ("summary", "episode", "content", "memory_content", "foresight", "atomic_fact"):
        val = m.get(key) if isinstance(m, dict) else getattr(m, key, None)
        if isinstance(val, str) and val.strip():
            return val.strip()
        if isinstance(val, list) and val:
            return " ".join(str(x) for x in val[:5] if x).strip() or None
    return None


def _fallback_retrieval_demo(project_id: str, top_k: int = 8):
    """当 memory_handlers 未加载时，用 api_EverMemOS.search_memory 跑三类检索，返回与 run_retrieval_demo 相同结构。"""
    try:
        from api_EverMemOS import is_available, search_memory
        if not is_available():
            return []
        grp = _evermemos_group_id(project_id)
        entries = []
        for query_type, query in _RETRIEVAL_DEMO_QUERIES:
            raw = search_memory(query, user_id="creator", group_id=grp, top_k=top_k)
            if not raw:
                raw = search_memory(query, group_id=grp, top_k=top_k)
            items = []
            seen = set()
            for m in raw:
                content = _content_from_evermemos_raw(m)
                if not content:
                    continue
                content_trim = content[:2000] if len(content) > 2000 else content
                key = content_trim[:80].strip()
                if key and key in seen:
                    continue
                if key:
                    seen.add(key)
                mem_id = getattr(m, "id", None) or getattr(m, "memory_id", None) or (m.get("id") or m.get("memory_id") if isinstance(m, dict) else None)
                items.append({"content": content_trim, "id": mem_id})
            excerpts = []
            for item in items[:_RETRIEVAL_DEMO_EXCERPT_COUNT]:
                c = (item.get("content") or "").strip()
                if c:
                    excerpts.append(c[:_RETRIEVAL_DEMO_EXCERPT_MAX] + ("…" if len(c) > _RETRIEVAL_DEMO_EXCERPT_MAX else ""))
            entries.append({
                "query_type": query_type,
                "query": query,
                "top_k": top_k,
                "result_count": len(items),
                "excerpts": excerpts,
            })
        return entries
    except Exception:
        return []


def _fallback_evermemos_list(project_id: str, limit: int = 50):
    """当 memory_handlers 未加载时，仅用 api_EverMemOS 按 group_id 拉列表。"""
    try:
        from api_EverMemOS import is_available, get_memory
        if not is_available():
            return []
        grp = _evermemos_group_id(project_id)
        raw = get_memory(group_id=grp)
        if not raw:
            raw = get_memory(user_id="creator", group_id=grp)
        out = []
        seen = set()
        for m in raw[: limit * 2]:
            if len(out) >= limit:
                break
            mem_id = getattr(m, "id", None) or getattr(m, "memory_id", None) or (m.get("id") or m.get("memory_id") if isinstance(m, dict) else None)
            content = None
            if isinstance(m, dict):
                for key in ("summary", "episode", "content", "memory_content", "foresight", "atomic_fact"):
                    val = m.get(key)
                    if isinstance(val, str) and val.strip():
                        content = val.strip()
                        break
            else:
                for key in ("summary", "episode", "content", "memory_content", "foresight", "atomic_fact"):
                    val = getattr(m, key, None)
                    if isinstance(val, str) and val.strip():
                        content = val.strip()
                        break
            if not content:
                continue
            content_trim = content[:2000] if len(content) > 2000 else content
            key = content_trim[:80].strip()
            if key and key in seen and not mem_id:
                continue
            if key:
                seen.add(key)
            out.append({"content": content_trim, "id": mem_id})
        return out
    except Exception:
        return []


@app.route("/api/memory/evermemos", methods=["POST", "DELETE"])
def memory_evermemos():
    """云端记忆：POST 检索（JSON body），DELETE 删除（JSON body 含 memory_id）。"""
    if request.method == "DELETE":
        if not _MEMORY_AVAILABLE:
            return jsonify({"ok": False, "message": "云端记忆未配置"}), 400
        body = request.get_json(silent=True) or {}
        memory_id = body.get("memory_id") or request.args.get("memory_id")
        if not memory_id or not str(memory_id).strip():
            return jsonify({"ok": False, "message": "缺少 memory_id"}), 400
        from api.memory_handlers import delete_from_evermemos
        ok = delete_from_evermemos(str(memory_id).strip())
        return jsonify({"ok": ok})
    # POST：检索或按项目拉列表。body 为 JSON；project_id 与创作/续写侧一致（经 normalize_project_id）。
    body = request.get_json(silent=True) or {}
    project_id = normalize_project_id(body.get("project_id"))
    query = (body.get("query") or "").strip()
    top_k = body.get("top_k")
    if top_k is None:
        top_k = 10
    try:
        top_k = int(top_k)
    except (TypeError, ValueError):
        top_k = 10
    if not query:
        if _MEMORY_AVAILABLE:
            try:
                from api.memory_handlers import list_from_evermemos
                return jsonify(list_from_evermemos(project_id, limit=top_k))
            except Exception:
                pass
        return jsonify(_fallback_evermemos_list(project_id, limit=top_k))
    if not _MEMORY_AVAILABLE or not memory_recall_from_evermemos:
        return jsonify([])
    return jsonify(memory_recall_from_evermemos(project_id, query or "创作 大纲 章节", top_k=top_k))


@app.route("/api/memory/evermemos/clear", methods=["POST", "DELETE"])
def memory_evermemos_clear():
    """清空云端记忆：POST/DELETE body 含 scope。优先按各项目目录下的 evermemos_ids.json 逐条 delete。
    - scope=all：按所有项目本地记录逐条删除，再按 user 拉取并删除剩余（无本地记录的历史数据）。
    - scope=project 且 project_id=xxx：按该项目 evermemos_ids.json 逐条删除；无本地记录时回退为按 group_id 拉取后删除。
    返回 { "ok": true, "deleted": N } 或 { "ok": false, "message": "..." }。"""
    try:
        from api_EverMemOS import is_available, CREATOR_USER_ID, delete_all_memories_for_user, delete_all_memories_for_group
        from api.memory_handlers import delete_project_evermemos_by_local_record, delete_all_evermemos_by_local_records
    except Exception as e:
        app.logger.warning("EverMemOS clear not available: %s", e)
        return jsonify({"ok": False, "message": "云端记忆服务不可用", "deleted": 0}), 400
    if not is_available():
        return jsonify({"ok": False, "message": "EverMemOS 未配置或不可用", "deleted": 0}), 400
    body = request.get_json(silent=True) or {}
    scope = (body.get("scope") or request.args.get("scope") or "").strip().lower()
    if scope == "all":
        deleted = delete_all_evermemos_by_local_records()
        remaining = delete_all_memories_for_user(CREATOR_USER_ID)
        return jsonify({"ok": True, "deleted": deleted + remaining})
    if scope == "project":
        project_id = normalize_project_id(body.get("project_id") or request.args.get("project_id"))
        if not project_id:
            return jsonify({"ok": False, "message": "scope=project 时需提供 project_id", "deleted": 0}), 400
        group_id = _evermemos_group_id(project_id)
        deleted = delete_all_memories_for_group(CREATOR_USER_ID, group_id)
        from api.memory_handlers import _clear_evermemos_ids_file
        try:
            _clear_evermemos_ids_file(project_id)
        except Exception:
            pass
        return jsonify({"ok": True, "deleted": deleted})
    return jsonify({"ok": False, "message": "请传 scope=all 或 scope=project 及 project_id", "deleted": 0}), 400


@app.route("/api/memory/evermemos/retrieval-demo", methods=["POST"])
def memory_evermemos_retrieval_demo():
    """跑三类检索（跨章人物、伏笔、长线设定、近期情节）并返回本次结果供前端展示；可选写 JSONL 日志。POST JSON: project_id?, top_k?"""
    body = request.get_json(silent=True) or {}
    project_id = normalize_project_id(body.get("project_id"))
    top_k = body.get("top_k")
    if top_k is None:
        top_k = 8
    try:
        top_k = int(top_k)
    except (TypeError, ValueError):
        top_k = 8
    if not _MEMORY_AVAILABLE:
        entries = _fallback_retrieval_demo(project_id, top_k=top_k)
        return jsonify({"ok": True, "entries": entries})
    try:
        from api.memory_handlers import run_retrieval_demo, DEFAULT_RETRIEVAL_DEMO_LOG_PATH
        entries = run_retrieval_demo(project_id, top_k=top_k, log_path=DEFAULT_RETRIEVAL_DEMO_LOG_PATH)
        return jsonify({"ok": True, "entries": entries})
    except Exception as e:
        app.logger.warning("retrieval-demo failed: %s", e, exc_info=True)
        return jsonify({"ok": False, "message": str(e), "entries": []})


def start(host=None, port=None, ssl_context=None):
    host = host or FLASK_HOST
    port = port or FLASK_PORT
    if ssl_context is not None:
        app.run(host=host, port=port, processes=True, debug=False, ssl_context=ssl_context)
    else:
        app.run(host=host, port=port, processes=True, debug=False)


if __name__ == "__main__":
    start()
