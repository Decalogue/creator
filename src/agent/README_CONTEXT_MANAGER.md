# 上下文管理器使用指南

## 概述

实现了 Cursor 风格的 **Context Offloading**，将冗长的工具结果、聊天历史、终端会话转化为文件，避免上下文窗口溢出。

## 核心功能

### 1. 工具结果卸载（Tool Result Offloading）

当工具返回结果过长时，自动写入文件，只返回文件路径引用。

```python
from agent.context_manager import get_context_manager

manager = get_context_manager()

# 工具结果过长时自动卸载
result, file_path = manager.offload_tool_result(
    tool_name="get_weather",
    tool_input={"city": "北京"},
    tool_output="很长的输出结果...",
    max_length=500  # 超过500字符则写入文件
)

if file_path:
    print(f"结果已保存到: {file_path}")
    # 在上下文中只返回文件引用
else:
    print(f"结果: {result}")  # 短结果直接返回
```

### 2. 聊天历史卸载（Chat History Offloading）

当上下文接近限制时，将完整历史转储到文件，提供摘要+文件引用。

```python
# 检查是否需要缩减
estimated_tokens, needs_reduction = manager.estimate_context_length(
    conversation_history,
    threshold=128000  # Pre-rot threshold: 128K tokens
)

if needs_reduction:
    # 卸载历史
    summary_ref, history_file = manager.offload_chat_history(
        conversation_history
    )
    # summary_ref 包含摘要和文件引用
```

### 3. 终端会话卸载（Terminal Session Offloading）

自动同步终端输出到文件系统。

```python
file_ref, file_path = manager.offload_terminal_output(
    command="ls -la",
    output="很长的终端输出...",
    exit_code=0
)
```

### 4. 工具调用紧凑化（Compaction）

移除可从外部状态重建的信息，只保留路径。

```python
compact_record = manager.compact_tool_call(
    tool_name="test_tool",
    tool_input={"param": "value"},
    tool_output="很长的输出...",
    file_path=Path("/path/to/output.txt")
)

# compact_record 只包含：
# - tool: 工具名称
# - input: 输入参数
# - output_file: 文件路径（而不是完整输出）
# - output_length: 输出长度
# - output_preview: 输出预览（前100字符）
```

## 在 ReActAgent 中的应用

`react.py` 中的 `ReActAgent` 已经集成了上下文管理器：

1. **自动卸载工具结果**：结果超过500字符时自动写入文件
2. **自动检查上下文长度**：每轮迭代检查，超过128K tokens时卸载历史
3. **保留最近消息**：卸载历史时保留最近3条消息作为 Few-shot Examples

### 使用示例

```python
from react import ReActAgent

# 启用上下文卸载（默认启用）
agent = ReActAgent(
    max_iterations=10,
    enable_context_offloading=True
)

# 运行任务
result = agent.run("查询北京的天气")
```

## 输出目录结构

```
agent/context_outputs/
├── tool_results/          # 工具结果文件
│   ├── calculator_xxx.txt
│   └── get_weather_xxx.txt
├── chat_history/          # 聊天历史文件
│   └── chat_history_xxx.json
└── terminal_sessions/      # 终端会话文件
    └── terminal_xxx.log
```

## 设计原则

### Cursor 风格：万物皆可文件化
- 工具结果 → 文件
- 聊天历史 → 文件
- 终端会话 → 文件

### Manus 风格：可逆、结构化
- **Compaction**：无损、可逆，信息被"外部化"但可通过路径重建
- **Summarization**：有损但带保险，先转储完整上下文再生成摘要

## 与 UniMem 的集成

未来可以扩展支持：
- 将卸载的文件内容同步到 UniMem
- 使用 UniMem 的检索能力查找历史文件
- 在 Summarization 时利用 UniMem 的知识
