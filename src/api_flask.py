import time
import uuid
import threading
import requests

from flask import Flask
from flask import request, jsonify, stream_with_context, Response
app = Flask(__name__)
app.debug = True
app.config['WTF_CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = 'you-will-never-guess'

***REMOVED*** Flask 配置 CORS（跨源资源共享）
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
            ***REMOVED*** 检查请求数据
            if not request.json:
                state['message'] = '请求数据格式错误：缺少 JSON 数据'
                return jsonify(state)
            
            if 'messages' not in request.json:
                state['message'] = '请求数据格式错误：缺少 messages 字段'
                return jsonify(state)
            
            messages = request.json['messages'][-10:] ***REMOVED*** 选最近的10轮对话
            stream = request.json['stream']
            model = request.json.get('model', 'DeepSeek-v3-2') ***REMOVED*** 默认使用 DeepSeek-v3-2

            ***REMOVED*** 根据模型类型选择对应的函数
            if model == 'DeepSeek-v3-2' or model == 'deepseek-v3-2':
                if stream:  ***REMOVED*** 流式数据请求
                    @stream_with_context
                    def stream_data():
                        for t in deepseek_v3_2_stream(messages):
                            yield t
                    return Response(stream_data(), mimetype="text/plain;charset=utf-8")
                else:
                    reasoning_content, content = deepseek_v3_2(messages)
            elif model == 'Kimi-k2' or model == 'kimi-k2':
                if stream:  ***REMOVED*** 流式数据请求
                    @stream_with_context
                    def stream_data():
                        for t in kimi_k2_stream(messages):
                            yield t
                    return Response(stream_data(), mimetype="text/plain;charset=utf-8")
                else:
                    reasoning_content, content = kimi_k2(messages)
            elif model == 'GLM-4-7' or model == 'glm-4-7':
                if stream:  ***REMOVED*** 流式数据请求
                    @stream_with_context
                    def stream_data():
                        for t in glm_stream(messages):
                            yield t
                    return Response(stream_data(), mimetype="text/plain;charset=utf-8")
                else:
                    reasoning_content, content = glm(messages)
            elif model == 'Gemini-3-flash' or model == 'gemini-3-flash':
                if stream:  ***REMOVED*** 流式数据请求
                    @stream_with_context
                    def stream_data():
                        for t in gemini_3_flash_stream(messages):
                            yield t
                    return Response(stream_data(), mimetype="text/plain;charset=utf-8")
                else:
                    reasoning_content, content = gemini_3_flash(messages)
            elif model == 'Claude-Opus-4-5' or model == 'claude-opus-4-5':
                if stream:  ***REMOVED*** 流式数据请求
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

            ***REMOVED*** 非流式响应才需要返回 JSON
            if content != '':
                state['code'] = 0
                state['message'] = '回复成功'
                state['content'] = content
                ***REMOVED*** 如果有 reasoning_content，也一并返回（推理模型的思考过程）
                if reasoning_content:
                    state['reasoning_content'] = reasoning_content
            else:
                state['message'] = '请求异常：模型返回空内容'
            
            return jsonify(state)
    except Exception as e:
        state['message'] = f'服务器错误：{str(e)}'
        app.logger.error(f'Chat API error: {str(e)}', exc_info=True)
        return jsonify(state)


***REMOVED*** ---------- P0 创作与记忆 API ----------

try:
    from api.creator_handlers import run as creator_run
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

***REMOVED*** 异步任务存储：task_id -> { status: pending|running|done|failed, ... }
_creator_tasks = {}
_creator_tasks_lock = threading.Lock()
_CREATOR_TASKS_MAX = 200
***REMOVED*** 续写（写章节）串行锁：同一时刻只允许一个续写任务执行，避免「写3章」时多任务同时看到 0 个文件都写第 1 章
_continue_lock = threading.Lock()


def _run_creator_task(task_id, mode, raw, project_id):
    try:
        with _creator_tasks_lock:
            _creator_tasks[task_id]['status'] = 'running'
        if mode == 'continue':
            _continue_lock.acquire()
        try:
            code, msg, extra = creator_run(mode, raw, project_id)
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


@app.route('/api/creator/run', methods=['POST'])
def creator_run_endpoint():
    """POST /api/creator/run  body: { mode, input, project_id? } 立即返回 task_id，结果通过轮询 GET /api/creator/task/<task_id> 获取"""
    if not _CREATOR_MEMORY_AVAILABLE:
        return jsonify({'code': 1, 'message': '创作服务未就绪', 'content': ''})
    try:
        data = request.json or {}
        mode = data.get('mode', 'chat')
        raw = data.get('input', '')
        project_id = data.get('project_id')
        task_id = str(uuid.uuid4())
        with _creator_tasks_lock:
            if len(_creator_tasks) >= _CREATOR_TASKS_MAX:
                ***REMOVED*** 简单清理：删掉最早的一批
                keys = list(_creator_tasks.keys())[:_CREATOR_TASKS_MAX // 2]
                for k in keys:
                    del _creator_tasks[k]
            _creator_tasks[task_id] = {'status': 'pending'}
        t = threading.Thread(target=_run_creator_task, args=(task_id, mode, raw, project_id), daemon=True)
        t.start()
        return jsonify({'code': 0, 'task_id': task_id, 'message': '任务已提交，请轮询状态'})
    except Exception as e:
        app.logger.exception('Creator run error')
        return jsonify({'code': 1, 'message': str(e), 'content': ''})


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
    """GET /api/config 返回后端配置（如 backend_url），供前端或调试使用"""
    return jsonify({'backend_url': backend_url})


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
    if ssl_contex != None: ***REMOVED*** https
        app.run(host=host, port=port, processes=True, debug=False, ssl_context=ssl_contex)
    else:
        app.run(host=host, port=port, processes=True, debug=False)


if __name__ == '__main__':
    start()
