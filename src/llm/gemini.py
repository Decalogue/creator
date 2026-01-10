from openai import OpenAI

client = OpenAI(
    base_url="https://sg.uiuiapi.com/v1",
    api_key="sk-y1LF0rYKtvVGgc4ZtBZZRG7NzPnAAtX9llZWHl0HsnvU5r3z",
)


def gemini_3_flash(messages, max_new_tokens=8192):
    response = client.chat.completions.create(
        model="gemini-3-flash-preview-nothinking",
        messages=messages,
        stream=False,
        max_tokens=max_new_tokens,
    )
    content = response.choices[0].message.content
    return '', content


def gemini_3_flash_stream(messages, max_new_tokens=8192, buffer_size=10):
    """
    流式生成响应，支持缓冲以提升前端显示流畅度
    
    Args:
        messages: 对话消息列表
        max_new_tokens: 最大生成token数
        buffer_size: 缓冲大小（字符数），累积到该大小或遇到换行符时发送
    """
    response = client.chat.completions.create(
        model="gemini-3-flash-preview-nothinking",
        messages=messages,
        stream=True,
        max_tokens=max_new_tokens,
    )

    buffer = ''  ***REMOVED*** 缓冲累积的文本
    for chunk in response:
        if not chunk.choices:
            continue
        
        text = ''
        if 'reasoning_content' in chunk.choices[0].delta:
            text = chunk.choices[0].delta.reasoning_content or ''
        else:
            text = chunk.choices[0].delta.content or ''
        
        if text:
            buffer += text
            ***REMOVED*** 当缓冲达到指定大小或遇到换行符时，发送缓冲内容
            if len(buffer) >= buffer_size or '\n' in text:
                yield buffer
                buffer = ''
    
    ***REMOVED*** 发送剩余的缓冲内容
    if buffer:
        yield buffer


if __name__ == "__main__":
    prompt = '小说《倚天屠龙记》的作者是谁？'
    messages = [
        {'role': 'user', 'content': prompt}
    ]
    
    print("=== 测试非流式 ===")
    reasoning_content, content = gemini_3_flash(messages)
    print(f'reasoning_content:\n{reasoning_content}\ncontent:\n{content}')

    print("\n=== 测试流式 ===")
    stream_res = gemini_3_flash_stream(messages)
    full_content = ''
    for chunk in stream_res:
        full_content += chunk
        print(chunk, end='', flush=True)
