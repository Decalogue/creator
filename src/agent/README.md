***REMOVED*** Agent 模块使用指南

***REMOVED******REMOVED*** 概述

Agent 模块实现了基于 ReAct 框架的智能代理系统，集成了以下核心功能：

1. **分层行动空间（Layered Action Space）** - Manus 风格的三层工具架构
2. **上下文管理器（Context Manager）** - Cursor 风格的上下文卸载
3. **Compaction & Summarization** - Manus 风格的上下文缩减系统

这些功能共同解决了 Agent 在长对话和复杂任务中的上下文窗口溢出问题。

---

***REMOVED******REMOVED*** 1. 分层行动空间（Layered Action Space）

***REMOVED******REMOVED******REMOVED*** 概述

实现了 Manus 风格的三层行动空间架构，解决工具系统扁平化的问题：
- **L1**: 原子函数调用（固定、正交，对 KV Cache 友好）
- **L2**: 沙盒工具（预装在系统中，通过 shell 动态交互）
- **L3**: 软件包与 API（编写 Python 脚本调用 API）

***REMOVED******REMOVED******REMOVED*** L1: 原子函数调用（Atomic Function Calling）

***REMOVED******REMOVED******REMOVED******REMOVED*** 核心特点

- **固定、正交**：函数列表固定，不会动态变化
- **对 KV Cache 友好**：始终在系统提示词中，不会重置 KV Cache
- **功能边界清晰**：每个函数职责单一

***REMOVED******REMOVED******REMOVED******REMOVED*** 可用函数

1. **read_file**: 读取文件内容
2. **write_file**: 写入文件内容
3. **execute_shell**: 执行 shell 命令（用于调用 L2 工具）
4. **search_files**: 在文件系统中搜索文件
5. **search_web**: 搜索互联网（需要集成搜索引擎 API）

***REMOVED******REMOVED******REMOVED******REMOVED*** 使用示例

```python
from agent.layered_action_space import get_layered_action_space

las = get_layered_action_space()

***REMOVED*** 读取文件
result = las.execute_l1_function("read_file", {"file_path": "/path/to/file.txt"})

***REMOVED*** 写入文件
result = las.execute_l1_function(
    "write_file",
    {"file_path": "/path/to/file.txt", "content": "文件内容"}
)

***REMOVED*** 执行 shell 命令（调用 L2 工具）
result = las.execute_l1_function("execute_shell", {"command": "grep pattern file.txt"})
```

***REMOVED******REMOVED******REMOVED*** L2: 沙盒工具（Sandbox Tools）

***REMOVED******REMOVED******REMOVED******REMOVED*** 核心特点

- **预装在系统中**：工具作为预装软件放在 Linux VM 沙箱中
- **通过 shell 动态交互**：Agent 通过 L1 的 `execute_shell` 使用
- **动态发现**：可以使用 `which` 和 `man` 命令发现工具

***REMOVED******REMOVED******REMOVED******REMOVED*** 可用工具示例

- `grep`: 在文件中搜索文本模式
- `sed`: 流编辑器，用于文本替换
- `awk`: 文本处理工具
- `curl`: HTTP 客户端
- `wget`: 文件下载工具
- `ffmpeg`: 音视频处理工具
- `imagemagick`: 图像处理工具
- `pandoc`: 文档格式转换工具

***REMOVED******REMOVED******REMOVED******REMOVED*** 使用示例

```python
***REMOVED*** 通过 L1 的 execute_shell 使用 L2 工具
result = las.execute_l1_function(
    "execute_shell",
    {"command": "grep -r 'pattern' /path/to/directory"}
)

***REMOVED*** 发现工具
description = las.discover_l2_tool("grep")
if description:
    print(f"工具信息: {description}")
```

***REMOVED******REMOVED******REMOVED*** L3: 软件包与 API（Packages & APIs）

***REMOVED******REMOVED******REMOVED******REMOVED*** 核心特点

- **编写 Python 脚本**：Agent 可以编写 Python 脚本执行复杂任务
- **调用预授权 API**：API keys 已预安装
- **使用预安装的 Python 包**：可以导入和使用预安装的包
- **返回摘要结果**：不加载所有原始数据，只返回摘要

***REMOVED******REMOVED******REMOVED******REMOVED*** 使用示例

```python
***REMOVED*** 编写并执行 Python 脚本
script_content = """
import json
from datetime import datetime

data = {
    "timestamp": datetime.now().isoformat(),
    "message": "Hello from L3 script!"
}

print(json.dumps(data, ensure_ascii=False, indent=2))
"""

summary, script_path = las.execute_l3_script(script_content, "my_script.py")
print(summary)  ***REMOVED*** 摘要结果
print(f"脚本路径: {script_path}")
```

***REMOVED******REMOVED******REMOVED*** 在 ReActAgent 中的应用

`orchestrator/react.py` 中的 `ReActAgent` 已经集成了分层行动空间：

1. **系统提示词**：包含 L1/L2/L3 的描述
2. **工具执行**：Agent 可以直接使用 L1 函数
3. **L2 工具**：通过 L1 的 `execute_shell` 使用
4. **L3 脚本**：通过 L1 的 `write_file` 和 `execute_shell` 创建和执行

***REMOVED******REMOVED******REMOVED*** 工作流程

```
Agent 需要执行任务
    ↓
选择行动空间层级
    ↓
L1: 直接调用原子函数
L2: 通过 execute_shell 调用系统工具
L3: 编写 Python 脚本并执行
```

***REMOVED******REMOVED******REMOVED*** 设计优势

***REMOVED******REMOVED******REMOVED******REMOVED*** 1. 对 KV Cache 友好

- L1 函数固定，不会动态变化
- 不会因为动态加载工具定义而重置 KV Cache
- 历史记录中的工具调用不会失效

***REMOVED******REMOVED******REMOVED******REMOVED*** 2. 功能边界清晰

- L1: 核心原子操作
- L2: 系统工具（通过 shell）
- L3: 复杂任务（通过脚本）

***REMOVED******REMOVED******REMOVED******REMOVED*** 3. 可扩展性

- L2 工具可以动态发现（通过 `which` 和 `man`）
- L3 脚本可以调用任何预授权的 API
- 不需要修改系统提示词

***REMOVED******REMOVED******REMOVED*** 与现有工具系统的关系

分层行动空间是对现有工具系统的补充，不是替代：

- **现有工具系统**（`tools/`）：用于特定领域的工具（如 calculator、weather）
- **分层行动空间**：用于通用操作和系统级工具

两者可以共存，Agent 可以根据任务选择合适的工具。

***REMOVED******REMOVED******REMOVED*** 沙箱目录结构

```
agent/sandbox/
├── scripts/          ***REMOVED*** L3 Python 脚本
└── ...              ***REMOVED*** 其他沙箱文件
```

***REMOVED******REMOVED******REMOVED*** 安全考虑

1. **L1 函数**：有基本的参数验证和错误处理
2. **L2 工具**：在沙箱目录中执行，有超时限制（30秒）
3. **L3 脚本**：在沙箱目录中执行，有超时限制（60秒）

未来可以增强：
- 更严格的权限控制
- 资源限制（CPU、内存）
- 网络访问控制

---

***REMOVED******REMOVED*** 2. 上下文管理器（Context Manager）

***REMOVED******REMOVED******REMOVED*** 概述

实现了 Cursor 风格的 **Context Offloading**，将冗长的工具结果、聊天历史、终端会话转化为文件，避免上下文窗口溢出。

***REMOVED******REMOVED******REMOVED*** 核心功能

***REMOVED******REMOVED******REMOVED******REMOVED*** 1. 工具结果卸载（Tool Result Offloading）

当工具返回结果过长时，自动写入文件，只返回文件路径引用。

```python
from agent.context_manager import get_context_manager

manager = get_context_manager()

***REMOVED*** 工具结果过长时自动卸载
result, file_path = manager.offload_tool_result(
    tool_name="get_weather",
    tool_input={"city": "北京"},
    tool_output="很长的输出结果...",
    max_length=500  ***REMOVED*** 超过500字符则写入文件
)

if file_path:
    print(f"结果已保存到: {file_path}")
    ***REMOVED*** 在上下文中只返回文件引用
else:
    print(f"结果: {result}")  ***REMOVED*** 短结果直接返回
```

***REMOVED******REMOVED******REMOVED******REMOVED*** 2. 聊天历史卸载（Chat History Offloading）

当上下文接近限制时，将完整历史转储到文件，提供摘要+文件引用。

```python
***REMOVED*** 检查是否需要缩减
estimated_tokens, needs_reduction = manager.estimate_context_length(
    conversation_history,
    threshold=128000  ***REMOVED*** Pre-rot threshold: 128K tokens
)

if needs_reduction:
    ***REMOVED*** 卸载历史
    summary_ref, history_file = manager.offload_chat_history(
        conversation_history
    )
    ***REMOVED*** summary_ref 包含摘要和文件引用
```

***REMOVED******REMOVED******REMOVED******REMOVED*** 3. 终端会话卸载（Terminal Session Offloading）

自动同步终端输出到文件系统。

```python
file_ref, file_path = manager.offload_terminal_output(
    command="ls -la",
    output="很长的终端输出...",
    exit_code=0
)
```

***REMOVED******REMOVED******REMOVED******REMOVED*** 4. 工具调用紧凑化（Compaction）

移除可从外部状态重建的信息，只保留路径。

```python
compact_record = manager.compact_tool_call(
    tool_name="test_tool",
    tool_input={"param": "value"},
    tool_output="很长的输出...",
    file_path=Path("/path/to/output.txt")
)

***REMOVED*** compact_record 只包含：
***REMOVED*** - tool: 工具名称
***REMOVED*** - input: 输入参数
***REMOVED*** - output_file: 文件路径（而不是完整输出）
***REMOVED*** - output_length: 输出长度
***REMOVED*** - output_preview: 输出预览（前100字符）
```

***REMOVED******REMOVED******REMOVED*** 在 ReActAgent 中的应用

`orchestrator/react.py` 中的 `ReActAgent` 已经集成了上下文管理器：

1. **自动卸载工具结果**：结果超过500字符时自动写入文件
2. **自动检查上下文长度**：每轮迭代检查，超过128K tokens时卸载历史
3. **保留最近消息**：卸载历史时保留最近3条消息作为 Few-shot Examples

***REMOVED******REMOVED******REMOVED******REMOVED*** 使用示例

```python
from orchestrator import ReActAgent

***REMOVED*** 启用上下文卸载（默认启用）
agent = ReActAgent(
    max_iterations=10,
    enable_context_offloading=True
)

***REMOVED*** 运行任务
result = agent.run("查询北京的天气")
```

***REMOVED******REMOVED******REMOVED*** 输出目录结构

```
agent/context_outputs/
├── tool_results/          ***REMOVED*** 工具结果文件
│   ├── calculator_xxx.txt
│   └── get_weather_xxx.txt
├── chat_history/          ***REMOVED*** 聊天历史文件
│   └── chat_history_xxx.json
└── terminal_sessions/      ***REMOVED*** 终端会话文件
    └── terminal_xxx.log
```

***REMOVED******REMOVED******REMOVED*** 设计原则

***REMOVED******REMOVED******REMOVED******REMOVED*** Cursor 风格：万物皆可文件化
- 工具结果 → 文件
- 聊天历史 → 文件
- 终端会话 → 文件

***REMOVED******REMOVED******REMOVED******REMOVED*** Manus 风格：可逆、结构化
- **Compaction**：无损、可逆，信息被"外部化"但可通过路径重建
- **Summarization**：有损但带保险，先转储完整上下文再生成摘要

***REMOVED******REMOVED******REMOVED*** 与 UniMem 的集成

未来可以扩展支持：
- 将卸载的文件内容同步到 UniMem
- 使用 UniMem 的检索能力查找历史文件
- 在 Summarization 时利用 UniMem 的知识

---

***REMOVED******REMOVED*** 3. Compaction 和 Summarization

***REMOVED******REMOVED******REMOVED*** 概述

实现了 Manus 风格的完整上下文缩减系统：
- **Compaction（紧凑化）**: 无损、可逆的缩减
- **Summarization（摘要化）**: 有损但带保险的压缩

***REMOVED******REMOVED******REMOVED*** Compaction（紧凑化）

***REMOVED******REMOVED******REMOVED******REMOVED*** 核心思想

**无损、可逆**：剥离可从外部状态重建的信息，信息被"外部化"到文件系统，但可通过路径重建。

***REMOVED******REMOVED******REMOVED******REMOVED*** 使用场景

当工具返回结果过长时，将冗长的 `content` 字段移除，只保留 `path` 或 `file_path`。

***REMOVED******REMOVED******REMOVED******REMOVED*** 示例

```python
from agent.context_manager import get_context_manager

manager = get_context_manager()

***REMOVED*** 紧凑化工具调用
compact_record = manager.compact_tool_call(
    tool_name="get_weather",
    tool_input={"city": "北京"},
    tool_output="很长的输出结果...",
    file_path=Path("/path/to/output.txt")
)

***REMOVED*** compact_record 只包含：
***REMOVED*** - tool: 工具名称
***REMOVED*** - input: 输入参数
***REMOVED*** - output_file: 文件路径（而不是完整输出）
***REMOVED*** - output_length: 输出长度
***REMOVED*** - output_preview: 输出预览（前100字符）
***REMOVED*** - compacted: True（标记为已紧凑化）
```

***REMOVED******REMOVED******REMOVED******REMOVED*** 对话历史紧凑化

```python
***REMOVED*** 对早期历史进行紧凑化，保留最近的完整记录
compacted_history, removed_records = manager.compact_conversation_history(
    conversation_history,
    keep_recent=3  ***REMOVED*** 保留最近3条作为 Few-shot Examples
)
```

***REMOVED******REMOVED******REMOVED*** Summarization（摘要化）

***REMOVED******REMOVED******REMOVED******REMOVED*** 核心思想

**有损但带保险**：在生成摘要前，将完整上下文转储到日志文件（保险），然后生成摘要。

***REMOVED******REMOVED******REMOVED******REMOVED*** 使用场景

当上下文超过 Pre-rot Threshold（默认128K tokens）时，触发 Summarization。

***REMOVED******REMOVED******REMOVED******REMOVED*** 示例

```python
***REMOVED*** 摘要化对话历史（带转储）
summary_ref, dump_file, recent_history = manager.summarize_with_dump(
    conversation_history,
    keep_recent=3  ***REMOVED*** 保留最近3条完整记录
)

***REMOVED*** summary_ref 包含：
***REMOVED*** - 对话历史摘要（使用 LLM 生成，如果可用）
***REMOVED*** - 完整上下文转储文件路径
***REMOVED*** - 消息数量统计
***REMOVED*** - 保留的最近记录数量
```

***REMOVED******REMOVED******REMOVED******REMOVED*** LLM 摘要生成

如果提供了 `llm_func`，系统会使用 LLM 生成高质量摘要：

```python
from llm.deepseek import deepseek_v3_2

***REMOVED*** 初始化时提供 LLM 函数
manager = get_context_manager(llm_func=deepseek_v3_2)

***REMOVED*** 自动使用 LLM 生成摘要
summary = manager._generate_summary(conversation_history, use_llm=True)
```

如果没有 LLM 函数或生成失败，会回退到简单统计摘要。

***REMOVED******REMOVED******REMOVED*** 在 ReActAgent 中的应用

`orchestrator/react.py` 中的 `ReActAgent` 已经集成了完整的 Compaction + Summarization：

1. **自动检查上下文长度**：每轮迭代检查，超过128K tokens时触发缩减
2. **第一步：Compaction**：对早期历史进行紧凑化，保留最近3条完整记录
3. **第二步：Summarization**：如果 Compaction 后仍超过阈值，进行摘要化（带转储）

***REMOVED******REMOVED******REMOVED*** 工作流程

```
上下文长度检查
    ↓
超过阈值？
    ↓ 是
Compaction（紧凑化）
    ↓
仍超过阈值？
    ↓ 是
Summarization（摘要化 + 转储）
    ↓
替换对话历史为摘要+文件引用+最近记录
```

***REMOVED******REMOVED******REMOVED*** 设计原则

***REMOVED******REMOVED******REMOVED******REMOVED*** Manus 风格

1. **Compaction**: 无损、可逆
   - 信息被"外部化"到文件系统
   - 可通过路径重建
   - 保留元数据（长度、预览等）

2. **Summarization**: 有损但带保险
   - 先转储完整上下文（保险）
   - 再生成摘要（有损）
   - 保留最近记录作为 Few-shot Examples

***REMOVED******REMOVED******REMOVED******REMOVED*** Pre-rot Threshold

默认设置为 128K tokens（Manus 的建议），可以在初始化时自定义：

```python
manager = get_context_manager(pre_rot_threshold=100000)  ***REMOVED*** 100K tokens
```

***REMOVED******REMOVED******REMOVED*** 输出文件

***REMOVED******REMOVED******REMOVED******REMOVED*** Compaction 输出

- `agent/context_outputs/tool_results/` - 紧凑化的工具结果文件

***REMOVED******REMOVED******REMOVED******REMOVED*** Summarization 输出

- `agent/context_outputs/chat_history/full_context_dump_*.json` - 完整上下文转储文件

***REMOVED******REMOVED******REMOVED*** 与 UniMem 的集成

未来可以扩展支持：
- 将转储的完整上下文同步到 UniMem
- 使用 UniMem 的检索能力查找历史文件
- 在 Summarization 时利用 UniMem 的知识增强摘要质量

---

***REMOVED******REMOVED*** 完整使用示例

***REMOVED******REMOVED******REMOVED*** 创建启用所有功能的 ReActAgent

```python
from orchestrator import ReActAgent
from agent.layered_action_space import get_layered_action_space
from agent.context_manager import get_context_manager

***REMOVED*** 获取分层行动空间
las = get_layered_action_space()

***REMOVED*** 获取上下文管理器
context_manager = get_context_manager()

***REMOVED*** 创建 Agent（自动集成所有功能）
agent = ReActAgent(
    max_iterations=20,
    enable_context_offloading=True  ***REMOVED*** 启用上下文卸载
)

***REMOVED*** 运行任务
result = agent.run("分析这个项目的代码结构，并生成一份报告")
```

***REMOVED******REMOVED******REMOVED*** 工作流程

1. **Agent 接收任务**
2. **选择工具层级**（L1/L2/L3）
3. **执行工具调用**
4. **自动卸载长结果**（如果超过阈值）
5. **检查上下文长度**（每轮迭代）
6. **自动缩减上下文**（Compaction → Summarization）
7. **继续执行直到完成**

---

***REMOVED******REMOVED*** 总结

Agent 模块提供了完整的工具系统和上下文管理能力：

- **分层行动空间**：解决工具系统扁平化问题，对 KV Cache 友好
- **上下文卸载**：Cursor 风格，万物皆可文件化
- **Compaction & Summarization**：Manus 风格，无损可逆 + 有损带保险

这些功能共同确保了 Agent 能够在长对话和复杂任务中稳定运行，避免上下文窗口溢出问题。
