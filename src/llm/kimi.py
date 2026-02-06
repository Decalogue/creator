from openai import OpenAI

def _kimi_client():
    """懒加载，从 config 读取 MOONSHOT 配置，避免硬编码 key。"""
    from config import MOONSHOT_BASE_URL, MOONSHOT_API_KEY
    return OpenAI(
        base_url=(MOONSHOT_BASE_URL or "https://api.moonshot.cn/v1").rstrip("/"),
        api_key=(MOONSHOT_API_KEY or "").strip(),
    )


def kimi_k2_5(messages, max_new_tokens=8192):
    response = _kimi_client().chat.completions.create(
        model="kimi-k2.5",
        messages=messages,
        stream=False,
        max_tokens=max_new_tokens,
        extra_body={
            "thinking": {"type": "disabled"}
        },
    )
    message = response.choices[0].message
    reasoning_content = getattr(message, 'reasoning_content', None) or ''
    content = message.content or ''
    return reasoning_content, content


def kimi_k2_5_stream(messages, max_new_tokens=8192, buffer_size=10):
    response = _kimi_client().chat.completions.create(
        model="kimi-k2.5",
        messages=messages,
        stream=True,
        max_tokens=max_new_tokens,
        extra_body={
            "thinking": {"type": "disabled"}
        },
    )
    buffer = ''  # 缓冲累积的文本
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
            # 当缓冲达到指定大小或遇到换行符时，发送缓冲内容
            if len(buffer) >= buffer_size or '\n' in text:
                yield buffer
                buffer = ''
    
    # 发送剩余的缓冲内容
    if buffer:
        yield buffer


def kimi_k2(messages, max_new_tokens=8192):
    response = _kimi_client().chat.completions.create(
        model="kimi-k2-0905-preview",
        messages=messages,
        stream=False,
        max_tokens=max_new_tokens,
    )
    message = response.choices[0].message
    reasoning_content = getattr(message, 'reasoning_content', None) or ''
    content = message.content or ''
    return reasoning_content, content


def kimi_k2_stream(messages, max_new_tokens=8192, buffer_size=10):
    """
    流式生成响应，支持缓冲以提升前端显示流畅度
    
    Args:
        messages: 对话消息列表
        max_new_tokens: 最大生成token数
        buffer_size: 缓冲大小（字符数），累积到该大小或遇到换行符时发送
    """
    response = _kimi_client().chat.completions.create(
        model="kimi-k2-0905-preview",
        messages=messages,
        stream=True,
        max_tokens=max_new_tokens,
    )

    buffer = ""
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
            # 当缓冲达到指定大小或遇到换行符时，发送缓冲内容
            if len(buffer) >= buffer_size or '\n' in text:
                yield buffer
                buffer = ''
    
    # 发送剩余的缓冲内容
    if buffer:
        yield buffer


if __name__ == "__main__":
    prompt = '小说《倚天屠龙记》的作者是谁？'
    messages = [
        {'role': 'user', 'content': prompt}
    ]
    
    print("=== 测试非流式 ===")
    reasoning_content, content = kimi_k2(messages)
    print(f'reasoning_content:\n{reasoning_content}\ncontent:\n{content}')

    print("\n=== 测试流式 ===")
    stream_res = kimi_k2_stream(messages)
    full_content = ''
    for chunk in stream_res:
        full_content += chunk
        print(chunk, end='', flush=True)
