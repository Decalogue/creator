from zai import ZhipuAiClient

client = ZhipuAiClient(api_key="33e71a88085147d1a9721f65401afe92.xkmfzm8HAiwaG1wI")


def glm(messages, thinking='disabled', max_new_tokens=8192):
    response = client.chat.completions.create(
        model="glm-4.7",
        messages=messages,
        thinking={
            "type": thinking,
        },
        stream=False,
        max_tokens=max_new_tokens,
        temperature=1.0
    )
    message = response.choices[0].message
    reasoning_content = getattr(message, 'reasoning_content', None) or ''
    content = message.content or ''
    return reasoning_content, content


def glm_stream(messages, thinking='disabled', max_new_tokens=8192, buffer_size=10):
    response = client.chat.completions.create(
        model="glm-4.7",
        messages=messages,
        thinking={
            "type": thinking,
        },
        stream=True,
        max_tokens=max_new_tokens,
        temperature=1.0
    )

    buffer = ''  ***REMOVED*** 缓冲累积的文本
    for chunk in response:
        if not chunk.choices:
            continue
        
        text = ''
        if chunk.choices[0].delta.reasoning_content:
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
    reasoning_content, content = glm(messages)
    print(f'reasoning_content:\n{reasoning_content}\ncontent:\n{content}')

    print("\n=== 测试流式 ===")
    stream_res = glm_stream(messages)
    full_content = ''
    for chunk in stream_res:
        full_content += chunk
        print(chunk, end='', flush=True)