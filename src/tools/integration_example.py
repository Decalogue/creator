"""
Function Calling 与 API 集成示例
展示如何在 FastAPI/Flask 中使用 Function Calling 系统

注意：虽然内部使用 "Skill" 命名，但这是一个标准的 Function Calling 系统。
"""
import json
from typing import List, Dict, Any, Optional
from skills import default_registry
from llm.chat import ark_deepseek_v3_2, ark_deepseek_v3_2_stream
from openai import OpenAI

***REMOVED*** 初始化 OpenAI 客户端（用于函数调用）
ark_client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key="93a67648-c2cd-4a51-99ba-c51114b537ee",
)


def chat_with_skills(messages: List[Dict[str, str]], stream: bool = False) -> Any:
    """
    带 Function Calling 的对话函数
    
    Args:
        messages: 对话消息列表
        stream: 是否使用流式响应
    
    Returns:
        对话结果（字符串或生成器）
    """
    ***REMOVED*** 1. 获取所有可用的函数定义（OpenAI Function Calling 格式）
    functions = default_registry.get_all_functions()
    
    ***REMOVED*** 2. 调用 LLM，传入函数定义
    if stream:
        ***REMOVED*** 流式调用（简化版，实际需要处理 tool_calls）
        for chunk in ark_deepseek_v3_2_stream(messages):
            yield chunk
    else:
        ***REMOVED*** 非流式调用
        try:
            response = ark_client.chat.completions.create(
                model="ep-20251209150604-gxb42",
                messages=messages,
                tools=functions,
                tool_choice="auto",
                max_tokens=8192,
            )
            
            message = response.choices[0].message
            
            ***REMOVED*** 3. 检查是否有函数调用
            if message.tool_calls:
                ***REMOVED*** 处理函数调用
                tool_results = []
                
                for tool_call in message.tool_calls:
                    func_name = tool_call.function.name
                    func_args_str = tool_call.function.arguments
                    
                    try:
                        ***REMOVED*** 解析参数
                        func_args = json.loads(func_args_str)
                        
                        ***REMOVED*** 执行技能
                        result = default_registry.execute_skill(func_name, func_args)
                        
                        ***REMOVED*** 保存结果
                        tool_results.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "content": str(result)
                        })
                    except Exception as e:
                        tool_results.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "content": f"执行失败：{str(e)}"
                        })
                
                ***REMOVED*** 4. 将函数结果添加到对话中
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in message.tool_calls
                    ]
                })
                
                for tool_result in tool_results:
                    messages.append(tool_result)
                
                ***REMOVED*** 5. 再次调用 LLM，生成最终回复
                response = ark_client.chat.completions.create(
                    model="ep-20251209150604-gxb42",
                    messages=messages,
                    tools=functions,
                    max_tokens=8192,
                )
                
                return response.choices[0].message.content
            else:
                ***REMOVED*** 没有函数调用，直接返回回复
                return message.content
                
        except Exception as e:
            return f"错误：{str(e)}"


def example_chat():
    """示例对话"""
    print("=" * 60)
    print("Function Calling 集成示例：对话演示")
    print("=" * 60)
    
    ***REMOVED*** 示例 1：计算
    print("\n【示例 1】用户：帮我计算 25 * 8 + 100")
    messages = [
        {"role": "user", "content": "帮我计算 25 * 8 + 100"}
    ]
    result = chat_with_skills(messages, stream=False)
    print(f"AI: {result}")
    
    ***REMOVED*** 示例 2：天气查询
    print("\n【示例 2】用户：查询北京的天气")
    messages = [
        {"role": "user", "content": "查询北京的天气"}
    ]
    result = chat_with_skills(messages, stream=False)
    print(f"AI: {result}")
    
    ***REMOVED*** 示例 3：时间查询
    print("\n【示例 3】用户：现在几点了？")
    messages = [
        {"role": "user", "content": "现在几点了？"}
    ]
    result = chat_with_skills(messages, stream=False)
    print(f"AI: {result}")


def example_api_integration():
    """展示如何在 API 中使用"""
    print("\n" + "=" * 60)
    print("API 集成代码示例")
    print("=" * 60)
    
    api_code = '''
***REMOVED*** 在 api_fastapi.py 或 api_flask.py 中使用

from skills import default_registry
import json

@app.post('/api/chat')
async def chat(request: ChatRequest):
    messages = request.messages[-10:]  ***REMOVED*** 最近10轮对话
    messages_dict = [{'role': msg.role, 'content': msg.content} 
                     for msg in messages]
    
    ***REMOVED*** 获取技能函数定义
    functions = default_registry.get_all_functions()
    
    ***REMOVED*** 调用 LLM（带函数定义）
    response = ark_client.chat.completions.create(
        model="your-model",
        messages=messages_dict,
        tools=functions,
        tool_choice="auto"
    )
    
    message = response.choices[0].message
    
    ***REMOVED*** 处理函数调用
    if message.tool_calls:
        ***REMOVED*** 执行所有函数调用
        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)
            result = default_registry.execute_skill(func_name, func_args)
            
            ***REMOVED*** 添加函数结果到对话
            messages_dict.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })
        
        ***REMOVED*** 再次调用 LLM 生成最终回复
        response = ark_client.chat.completions.create(
            model="your-model",
            messages=messages_dict,
            tools=functions
        )
    
    return response.choices[0].message.content
'''
    print(api_code)


if __name__ == "__main__":
    ***REMOVED*** 注意：实际运行需要有效的 API key
    print("注意：此示例需要有效的 API key 才能运行")
    print("这里只展示代码结构，不实际调用 API\n")
    
    example_api_integration()
    
    print("\n" + "=" * 60)
    print("如需实际测试，请取消注释 example_chat() 并配置 API key")
    print("=" * 60)
    
    ***REMOVED*** 取消下面的注释以实际运行（需要 API key）
    ***REMOVED*** example_chat()
