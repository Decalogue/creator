from openai import OpenAI

ark_client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key="93a67648-c2cd-4a51-99ba-c51114b537ee",
)


def ark_deepseek_v3_2(messages, max_new_tokens=8192):
    response = ark_client.chat.completions.create(
        model="ep-20251209150604-gxb42", ***REMOVED*** deepseek-v3-2-251201
        messages=messages,
        stream=False,
        max_tokens=max_new_tokens,
    )
    content = response.choices[0].message.content
    return '', content


def ark_deepseek_v3_2_stream(messages, max_new_tokens=8192):
    response = ark_client.chat.completions.create(
        model="ep-20251209150604-gxb42", ***REMOVED*** deepseek-v3-2-251201
        messages=messages,
        stream=True,
        max_tokens=max_new_tokens,
    )
    reasoning_content = ''
    content = ''
    for chunk in response:
        if not chunk.choices:
            continue
        if 'reasoning_content' in chunk.choices[0].delta:
            text = chunk.choices[0].delta.reasoning_content
            reasoning_content += text
            yield text
        else:
            text = chunk.choices[0].delta.content
            content += text
            yield text


if __name__ == "__main__":
    prompt = '小说《倚天屠龙记》的作者是谁？'
    messages = [
        {'role': 'user', 'content': prompt}
    ]
    
    print("=== 测试非流式 ===")
    reasoning_content, content = ark_deepseek_v3_2(messages)
    print(f'reasoning_content:\n{reasoning_content}\ncontent:\n{content}')

    print("\n=== 测试流式 ===")
    stream_res = ark_deepseek_v3_2_stream(messages)
    full_content = ''
    for chunk in stream_res:
        full_content += chunk
        print(chunk, end='', flush=True)
