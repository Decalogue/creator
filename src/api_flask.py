import time
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
from llm.deepseek import deepseek_v3_2, deepseek_v3_2_stream
from llm.gemini import gemini_3_flash, gemini_3_flash_stream
from llm.claude import claude_opus_4_5, claude_opus_4_5_stream


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


def start(host='0.0.0.0', port=5200, ssl_contex=None):
    if ssl_contex != None: ***REMOVED*** https
        app.run(host=host, port=port, processes=True, debug=False, ssl_context=ssl_contex)
    else:
        app.run(host=host, port=port, processes=True, debug=False)


if __name__ == '__main__':
    start()
