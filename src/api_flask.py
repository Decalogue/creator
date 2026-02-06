"""
Flask 主入口：/api/chat、创作与记忆 API。
配置从 config 与 .env 读取，见 config/__init__.py 与 .env.example。
"""
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


try:
    from api.creator_handlers import (
        run as creator_run,
        list_projects as creator_list_projects,
        get_project_chapters as creator_get_chapters,
    )
    from api.memory_handlers import (
        get_entities as memory_get_entities,
        get_graph as memory_get_graph,
        get_recents as memory_get_recents,
        get_note as memory_get_note,
        recall_from_evermemos as memory_recall_from_evermemos,
    )
    _CREATOR_MEMORY_AVAILABLE = True
except Exception as e:
    app.logger.warning("Creator/Memory API handlers not available: %s", e)
    _CREATOR_MEMORY_AVAILABLE = False

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
    if _CREATOR_MEMORY_AVAILABLE:
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
    if not _CREATOR_MEMORY_AVAILABLE:
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
    if not _CREATOR_MEMORY_AVAILABLE:
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
    if not _CREATOR_MEMORY_AVAILABLE:
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
    if not _CREATOR_MEMORY_AVAILABLE:
        return jsonify([])
    try:
        return jsonify(creator_list_projects())
    except Exception as e:
        app.logger.exception("List projects error")
        return jsonify([])


@app.route("/api/creator/chapters", methods=["GET"])
def creator_chapters():
    if not _CREATOR_MEMORY_AVAILABLE:
        return jsonify({"chapters": [], "total": 0})
    project_id = request.args.get("project_id")
    try:
        code, chapters = creator_get_chapters(project_id)
        lst = chapters if code == 0 and chapters else []
        return jsonify({"chapters": lst, "total": len(lst)})
    except Exception as e:
        app.logger.exception("Chapters list error")
        return jsonify({"chapters": [], "total": 0})


@app.route("/api/memory/entities", methods=["GET"])
def memory_entities():
    if not _CREATOR_MEMORY_AVAILABLE:
        return jsonify([])
    return jsonify(memory_get_entities(request.args.get("project_id")))


@app.route("/api/memory/graph", methods=["GET"])
def memory_graph():
    if not _CREATOR_MEMORY_AVAILABLE:
        return jsonify({"nodes": [], "links": []})
    project_id = request.args.get("project_id")
    max_nodes = request.args.get("max_nodes", type=int) or 80
    return jsonify(memory_get_graph(project_id, max_nodes=max_nodes))


@app.route("/api/memory/recents", methods=["GET"])
def memory_recents():
    if not _CREATOR_MEMORY_AVAILABLE:
        return jsonify([])
    project_id = request.args.get("project_id")
    limit = request.args.get("limit", type=int) or 5
    return jsonify(memory_get_recents(project_id, limit=limit))


@app.route("/api/memory/note/<node_id>", methods=["GET"])
def memory_note(node_id):
    if not _CREATOR_MEMORY_AVAILABLE:
        return jsonify(None), 404
    note = memory_get_note(node_id, request.args.get("project_id"))
    if note is None:
        return jsonify(None), 404
    return jsonify(note)


@app.route("/api/memory/evermemos", methods=["GET"])
def memory_evermemos():
    if not _CREATOR_MEMORY_AVAILABLE:
        return jsonify([])
    project_id = request.args.get("project_id") or "完美之墙"
    query = request.args.get("query", "").strip() or "创作 大纲 章节"
    top_k = request.args.get("top_k", type=int) or 10
    return jsonify(memory_recall_from_evermemos(project_id, query, top_k=top_k))


def start(host=None, port=None, ssl_context=None):
    host = host or FLASK_HOST
    port = port or FLASK_PORT
    if ssl_context is not None:
        app.run(host=host, port=port, processes=True, debug=False, ssl_context=ssl_context)
    else:
        app.run(host=host, port=port, processes=True, debug=False)


if __name__ == "__main__":
    start()
