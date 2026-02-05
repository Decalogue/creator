import time
import uuid
import threading
import queue
import json
import requests

from flask import Flask
from flask import request, jsonify, stream_with_context, Response
app = Flask(__name__)
app.debug = True
app.config['WTF_CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = 'you-will-never-guess'

# Flask 配置 CORS（跨源资源共享）
from flask_cors import CORS
CORS(app)

from llm.glm import glm, glm_stream
from llm.kimi import kimi_k2, kimi_k2_stream
from llm.deepseek import deepseek_v3_2, deepseek_v3_2_stream
from llm.gemini import gemini_3_flash, gemini_3_flash_stream
from llm.claude import claude_opus_4_5, claude_opus_4_5_stream

from config import backend_url


def get_current_time(format_string="%Y-%m-%d-%H-%M-%S"):
    return time.strftime(format_string, time.localtime())


def url2file(url, savepath=None):
    assert savepath is not None, 'The savepath should not be None'
    with open(savepath, 'wb') as f:
        f.write(requests.get(url).content)


@app.route('/api/chat', methods=['POST'])
def chat():
    state = {
        'code': 1,
        'message': "回复失败",
        'content': '',
    }
    
    try:
        if request.method == 'POST':
            # 检查请求数据
            if not request.json:
                state['message'] = '请求数据格式错误：缺少 JSON 数据'
                return jsonify(state)
            
            if 'messages' not in request.json:
                state['message'] = '请求数据格式错误：缺少 messages 字段'
                return jsonify(state)
            
            messages = request.json['messages'][-10:] # 选最近的10轮对话
            stream = request.json['stream']
            model = request.json.get('model', 'DeepSeek-v3-2') # 默认使用 DeepSeek-v3-2

            # 根据模型类型选择对应的函数
            if model == 'DeepSeek-v3-2' or model == 'deepseek-v3-2':
                if stream:  # 流式数据请求
                    @stream_with_context
                    def stream_data():
                        for t in deepseek_v3_2_stream(messages):
                            yield t
                    return Response(stream_data(), mimetype="text/plain;charset=utf-8")
                else:
                    reasoning_content, content = deepseek_v3_2(messages)
            elif model == 'Kimi-k2' or model == 'kimi-k2':
                if stream:  # 流式数据请求
                    @stream_with_context
                    def stream_data():
                        for t in kimi_k2_stream(messages):
                            yield t
                    return Response(stream_data(), mimetype="text/plain;charset=utf-8")
                else:
                    reasoning_content, content = kimi_k2(messages)
            elif model == 'GLM-4-7' or model == 'glm-4-7':
                if stream:  # 流式数据请求
                    @stream_with_context
                    def stream_data():
                        for t in glm_stream(messages):
                            yield t
                    return Response(stream_data(), mimetype="text/plain;charset=utf-8")
                else:
                    reasoning_content, content = glm(messages)
            elif model == 'Gemini-3-flash' or model == 'gemini-3-flash':
                if stream:  # 流式数据请求
                    @stream_with_context
                    def stream_data():
                        for t in gemini_3_flash_stream(messages):
                            yield t
                    return Response(stream_data(), mimetype="text/plain;charset=utf-8")
                else:
                    reasoning_content, content = gemini_3_flash(messages)
            elif model == 'Claude-Opus-4-5' or model == 'claude-opus-4-5':
                if stream:  # 流式数据请求
                    @stream_with_context
                    def stream_data():
                        for t in claude_opus_4_5_stream(messages):
                            yield t
                    return Response(stream_data(), mimetype="text/plain;charset=utf-8")
                else:
                    reasoning_content, content = claude_opus_4_5(messages)
            else:
                state['message'] = '请求异常：模型不存在'
                return jsonify(state)

            # 非流式响应才需要返回 JSON
            if content != '':
                state['code'] = 0
                state['message'] = '回复成功'
                state['content'] = content
                # 如果有 reasoning_content，也一并返回（推理模型的思考过程）
                if reasoning_content:
                    state['reasoning_content'] = reasoning_content
            else:
                state['message'] = '请求异常：模型返回空内容'
            
            return jsonify(state)
    except Exception as e:
        state['message'] = f'服务器错误：{str(e)}'
        app.logger.error(f'Chat API error: {str(e)}', exc_info=True)
        return jsonify(state)


# ---------- P0 创作与记忆 API ----------

try:
    from api.creator_handlers import run as creator_run, list_projects as creator_list_projects, get_project_chapters as creator_get_chapters
    from api.memory_handlers import (
        get_entities as memory_get_entities,
        get_graph as memory_get_graph,
        get_recents as memory_get_recents,
        get_note as memory_get_note,
    )
    _CREATOR_MEMORY_AVAILABLE = True
except Exception as e:
    app.logger.warning('Creator/Memory API handlers not available: %s', e)
    _CREATOR_MEMORY_AVAILABLE = False

# 异步任务存储：task_id -> { status: pending|running|done|failed, ... }
_creator_tasks = {}
_creator_tasks_lock = threading.Lock()
_CREATOR_TASKS_MAX = 200
# 续写（写章节）串行锁：同一时刻只允许一个续写任务执行，避免「写3章」时多任务同时看到 0 个文件都写第 1 章
_continue_lock = threading.Lock()


def _run_creator_task(task_id, mode, raw, project_id, options=None):
    options = options or {}
    try:
        with _creator_tasks_lock:
            _creator_tasks[task_id]['status'] = 'running'
        if mode == 'continue':
            _continue_lock.acquire()
        try:
            code, msg, extra = creator_run(
                mode, raw, project_id,
                previous_project_id=options.get('previous_project_id'),
                start_chapter=options.get('start_chapter'),
                target_chapters=options.get('target_chapters'),
            )
        finally:
            if mode == 'continue':
                _continue_lock.release()
        with _creator_tasks_lock:
            _creator_tasks[task_id] = {
                'status': 'done',
                'code': code,
                'message': msg,
                'content': (extra or {}).get('content', ''),
                **(extra or {}),
            }
    except Exception as e:
        app.logger.exception('Creator task failed: %s', e)
        with _creator_tasks_lock:
            _creator_tasks[task_id] = {'status': 'failed', 'error': str(e)}


def _run_creator_stream_task(ev_queue, mode, raw, project_id, options=None):
    """在后台线程中执行创作，将编排事件放入 ev_queue，最后放入 stream_end 与 None。"""
    options = options or {}
    try:
        if mode == 'continue':
            _continue_lock.acquire()
        try:
            code, msg, extra = creator_run(
                mode, raw, project_id,
                previous_project_id=options.get('previous_project_id'),
                start_chapter=options.get('start_chapter'),
                target_chapters=options.get('target_chapters'),
                on_event=ev_queue.put,
            )
            ev_queue.put({
                'type': 'stream_end',
                'code': code,
                'message': msg,
                'content': (extra or {}).get('content', ''),
                **(extra or {}),
            })
        finally:
            if mode == 'continue':
                _continue_lock.release()
    except Exception as e:
        app.logger.exception('Creator stream task failed: %s', e)
        ev_queue.put({'type': 'stream_end', 'code': 1, 'message': str(e), 'content': ''})
    ev_queue.put(None)


@app.route('/api/creator/run', methods=['POST'])
def creator_run_endpoint():
    """POST /api/creator/run  body: { mode, input, project_id?, previous_project_id?, start_chapter?, target_chapters? } 立即返回 task_id"""
    if not _CREATOR_MEMORY_AVAILABLE:
        return jsonify({'code': 1, 'message': '创作服务未就绪', 'content': ''})
    try:
        data = request.json or {}
        mode = data.get('mode', 'chat')
        raw = data.get('input', '')
        project_id = data.get('project_id')
        options = {
            'previous_project_id': data.get('previous_project_id'),
            'start_chapter': data.get('start_chapter'),
            'target_chapters': data.get('target_chapters'),
        }
        task_id = str(uuid.uuid4())
        with _creator_tasks_lock:
            if len(_creator_tasks) >= _CREATOR_TASKS_MAX:
                keys = list(_creator_tasks.keys())[:_CREATOR_TASKS_MAX // 2]
                for k in keys:
                    del _creator_tasks[k]
            _creator_tasks[task_id] = {'status': 'pending'}
        t = threading.Thread(target=_run_creator_task, args=(task_id, mode, raw, project_id, options), daemon=True)
        t.start()
        return jsonify({'code': 0, 'task_id': task_id, 'message': '任务已提交，请轮询状态'})
    except Exception as e:
        app.logger.exception('Creator run error')
        return jsonify({'code': 1, 'message': str(e), 'content': ''})


@app.route('/api/creator/stream', methods=['POST'])
def creator_stream_endpoint():
    """POST /api/creator/stream  body 同 /api/creator/run，返回 SSE：编排事件（step_start/step_done/step_error） + 最后一条 stream_end。"""
    if not _CREATOR_MEMORY_AVAILABLE:
        return jsonify({'code': 1, 'message': '创作服务未就绪', 'content': ''}), 503
    try:
        data = request.json or {}
        mode = data.get('mode', 'chat')
        raw = data.get('input', '')
        project_id = data.get('project_id')
        options = {
            'previous_project_id': data.get('previous_project_id'),
            'start_chapter': data.get('start_chapter'),
            'target_chapters': data.get('target_chapters'),
        }
        if mode not in ('create', 'continue'):
            return jsonify({'code': 1, 'message': 'stream 仅支持 mode=create 或 continue'}), 400
        ev_queue = queue.Queue()
        t = threading.Thread(target=_run_creator_stream_task, args=(ev_queue, mode, raw, project_id, options), daemon=True)
        t.start()

        @stream_with_context
        def sse_gen():
            _SSE_KEEPALIVE_SEC = 30  # 每 30s 无事件时发心跳，避免代理因“空闲”断开；代理读超时建议 >= 300s
            while True:
                try:
                    ev = ev_queue.get(timeout=_SSE_KEEPALIVE_SEC)
                except queue.Empty:
                    yield ': keepalive\n\n'
                    continue
                if ev is None:
                    break
                yield 'data: ' + json.dumps(ev, ensure_ascii=False) + '\n\n'

        return Response(sse_gen(), mimetype='text/event-stream')
    except Exception as e:
        app.logger.exception('Creator stream error')
        return jsonify({'code': 1, 'message': str(e), 'content': ''}), 500


@app.route('/api/creator/task/<task_id>', methods=['GET'])
def creator_task_status(task_id):
    """GET /api/creator/task/<task_id> 轮询任务状态。status: pending|running|done|failed"""
    with _creator_tasks_lock:
        t = _creator_tasks.get(task_id)
    if t is None:
        return jsonify({'status': 'unknown', 'message': '任务不存在或已过期'}), 404
    out = {'status': t['status']}
    if t['status'] == 'done':
        out['code'] = t.get('code', 0)
        out['message'] = t.get('message', '')
        out['content'] = t.get('content', '')
        for k in ('project_id', 'chapter_number'):
            if k in t:
                out[k] = t[k]
    elif t['status'] == 'failed':
        out['error'] = t.get('error', '')
    return jsonify(out)


@app.route('/api/config', methods=['GET'])
def api_config():
    """GET /api/config 返回后端配置（如 backend_url、unimem_enabled），供前端或调试使用"""
    unimem_enabled = False
    if _CREATOR_MEMORY_AVAILABLE:
        try:
            from api.memory_handlers import _unimem_enabled
            unimem_enabled = _unimem_enabled()
        except Exception:
            pass
    return jsonify({'backend_url': backend_url, 'unimem_enabled': unimem_enabled})


@app.route('/api/memory/neo4j/health', methods=['GET'])
def memory_neo4j_health():
    """GET /api/memory/neo4j/health 检查 Neo4j 连接是否正常（用于 LTM Memory 节点写入）"""
    out = {'ok': False, 'uri': None, 'error': None}
    if not _CREATOR_MEMORY_AVAILABLE:
        out['error'] = 'memory module not available'
        return jsonify(out), 200
    try:
        from unimem.neo4j import get_graph, NEO4J_AVAILABLE
        import os
        uri = os.getenv('NEO4J_URI', 'bolt://localhost:7680')
        out['uri'] = uri
        if not NEO4J_AVAILABLE:
            out['error'] = 'py2neo not installed'
            return jsonify(out), 200
        g = get_graph()
        if g:
            g.run('RETURN 1').data()
            out['ok'] = True
    except Exception as e:
        out['error'] = str(e)
    return jsonify(out), 200


@app.route('/api/creator/projects', methods=['GET'])
def creator_projects():
    """GET /api/creator/projects 返回已创作小说列表（project_id 数组），用于前端选择/加载项目"""
    if not _CREATOR_MEMORY_AVAILABLE:
        return jsonify([])
    try:
        return jsonify(creator_list_projects())
    except Exception as e:
        app.logger.exception('List projects error')
        return jsonify([])


@app.route('/api/creator/chapters', methods=['GET'])
def creator_chapters():
    """GET /api/creator/chapters?project_id= 返回当前作品章节列表（number, title, summary, has_file）"""
    if not _CREATOR_MEMORY_AVAILABLE:
        return jsonify({'chapters': [], 'total': 0})
    project_id = request.args.get('project_id')
    try:
        code, chapters = creator_get_chapters(project_id)
        lst = chapters if code == 0 and chapters is not None else []
        return jsonify({'chapters': lst, 'total': len(lst)})
    except Exception as e:
        app.logger.exception('Chapters list error')
        return jsonify({'chapters': [], 'total': 0})


@app.route('/api/memory/entities', methods=['GET'])
def memory_entities():
    """GET /api/memory/entities?project_id="""
    if not _CREATOR_MEMORY_AVAILABLE:
        return jsonify([])
    project_id = request.args.get('project_id')
    return jsonify(memory_get_entities(project_id))


@app.route('/api/memory/graph', methods=['GET'])
def memory_graph():
    """GET /api/memory/graph?project_id=&max_nodes=80"""
    if not _CREATOR_MEMORY_AVAILABLE:
        return jsonify({'nodes': [], 'links': []})
    project_id = request.args.get('project_id')
    max_nodes = request.args.get('max_nodes', type=int) or 80
    return jsonify(memory_get_graph(project_id, max_nodes=max_nodes))


@app.route('/api/memory/recents', methods=['GET'])
def memory_recents():
    """GET /api/memory/recents?project_id="""
    if not _CREATOR_MEMORY_AVAILABLE:
        return jsonify([])
    project_id = request.args.get('project_id')
    limit = request.args.get('limit', type=int) or 5
    return jsonify(memory_get_recents(project_id, limit=limit))


@app.route('/api/memory/note/<node_id>', methods=['GET'])
def memory_note(node_id):
    """GET /api/memory/note/<id>?project_id="""
    if not _CREATOR_MEMORY_AVAILABLE:
        return jsonify(None), 404
    project_id = request.args.get('project_id')
    note = memory_get_note(node_id, project_id)
    if note is None:
        return jsonify(None), 404
    return jsonify(note)


def start(host='0.0.0.0', port=5200, ssl_contex=None):
    if ssl_contex != None: # https
        app.run(host=host, port=port, processes=True, debug=False, ssl_context=ssl_contex)
    else:
        app.run(host=host, port=port, processes=True, debug=False)


if __name__ == '__main__':
    start()
