from openai import OpenAI

client = OpenAI(
    base_url="https://sg.uiuiapi.com/v1",
    api_key="sk-y1LF0rYKtvVGgc4ZtBZZRG7NzPnAAtX9llZWHl0HsnvU5r3z",
)


def claude_opus_4_5(messages, max_new_tokens=8192):
    response = client.chat.completions.create(
        model="claude-opus-4-5-20251101",
        messages=messages,
        stream=False,
        max_tokens=max_new_tokens,
    )
    content = response.choices[0].message.content
    return '', content


if __name__ == "__main__":
    messages = [
        {"role": "user", "content": "你是谁？"}
    ]
    reasoning_content, content = claude_opus_4_5(messages)
    print(content)