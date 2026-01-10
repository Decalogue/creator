import time
import requests
from typing import Optional, List, Dict, Any

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(debug=True)

***REMOVED*** FastAPI 配置 CORS（跨源资源共享）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  ***REMOVED*** 生产环境应该指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from llm.glm import glm, glm_stream
from llm.deepseek import deepseek_v3_2, deepseek_v3_2_stream
from llm.gemini import gemini_3_flash, gemini_3_flash_stream
from llm.claude import claude_opus_4_5, claude_opus_4_5_stream

***REMOVED*** 请求模型定义
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    stream: bool
    model: Optional[str] = 'DeepSeek-v3-2'

***REMOVED*** 响应模型定义
class ChatResponse(BaseModel):
    code: int
    message: str
    content: str = ''


def get_current_time(format_string="%Y-%m-%d-%H-%M-%S"):
    return time.strftime(format_string, time.localtime())


def url2file(url, savepath=None):
    assert savepath is not None, 'The savepath should not be None'
    with open(savepath, 'wb') as f:
        f.write(requests.get(url).content)


@app.post('/api/chat', response_model=ChatResponse)
async def chat(request: ChatRequest):
    state = {
        'code': 1,
        'message': "回复失败",
        'content': '',
    }
    
    try:
        ***REMOVED*** 检查请求数据
        if not request.messages:
            state['message'] = '请求数据格式错误：缺少 messages 字段'
            return JSONResponse(content=state, status_code=400)
        
        messages = request.messages[-10:]  ***REMOVED*** 选最近的10轮对话
        ***REMOVED*** 转换为字典格式，因为 chat.py 中的函数期望字典列表
        messages_dict = [{'role': msg.role, 'content': msg.content} for msg in messages]
        stream = request.stream
        model = request.model or 'DeepSeek-v3-2'  ***REMOVED*** 默认使用 DeepSeek-v3-2

        ***REMOVED*** 根据模型类型选择对应的函数
        if model == 'DeepSeek-v3-2' or model == 'deepseek-v3-2':
            if stream:  ***REMOVED*** 流式数据请求
                def stream_data():
                    for t in deepseek_v3_2_stream(messages_dict):
                        yield t
                return StreamingResponse(
                    stream_data(),
                    media_type="text/plain;charset=utf-8"
                )
            else:
                reasoning_content, content = deepseek_v3_2(messages_dict)
        elif model == 'GLM-4-7' or model == 'glm-4-7':
            if stream:  ***REMOVED*** 流式数据请求
                def stream_data():
                    for t in glm_stream(messages_dict):
                        yield t
                return StreamingResponse(
                    stream_data(),
                    media_type="text/plain;charset=utf-8"
                )
            else:
                reasoning_content, content = glm(messages_dict)
        elif model == 'Gemini-3-flash' or model == 'gemini-3-flash':
            if stream:  ***REMOVED*** 流式数据请求
                def stream_data():
                    for t in gemini_3_flash_stream(messages_dict):
                        yield t
                return StreamingResponse(
                    stream_data(),
                    media_type="text/plain;charset=utf-8"
                )
            else:
                reasoning_content, content = gemini_3_flash(messages_dict)
        elif model == 'Claude-Opus-4-5' or model == 'claude-opus-4-5':
            if stream:  ***REMOVED*** 流式数据请求
                def stream_data():
                    for t in claude_opus_4_5_stream(messages_dict):
                        yield t
                return StreamingResponse(
                    stream_data(),
                    media_type="text/plain;charset=utf-8"
                )
            else:
                reasoning_content, content = claude_opus_4_5(messages_dict)
        else:
            state['message'] = f'请求异常：模型不存在 ({model})'
            return JSONResponse(content=state, status_code=400)

        ***REMOVED*** 非流式响应才需要返回 JSON
        if content != '':
            state['code'] = 0
            state['message'] = '回复成功'
            state['content'] = content
        else:
            state['message'] = '请求异常：模型返回空内容'
        
        return JSONResponse(content=state)
    except Exception as e:
        state['message'] = f'服务器错误：{str(e)}'
        return JSONResponse(content=state, status_code=500)


def start(host='0.0.0.0', port=5200, ssl_context=None):
    if ssl_context is not None:  ***REMOVED*** https
        uvicorn.run(
            app,
            host=host,
            port=port,
            ssl_keyfile=ssl_context.get('keyfile'),
            ssl_certfile=ssl_context.get('certfile'),
        )
    else:
        uvicorn.run(app, host=host, port=port)


if __name__ == '__main__':
    start()
