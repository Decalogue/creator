***REMOVED*** Compaction 和 Summarization 使用指南

***REMOVED******REMOVED*** 概述

实现了 Manus 风格的完整上下文缩减系统：
- **Compaction（紧凑化）**: 无损、可逆的缩减
- **Summarization（摘要化）**: 有损但带保险的压缩

***REMOVED******REMOVED*** Compaction（紧凑化）

***REMOVED******REMOVED******REMOVED*** 核心思想

**无损、可逆**：剥离可从外部状态重建的信息，信息被"外部化"到文件系统，但可通过路径重建。

***REMOVED******REMOVED******REMOVED*** 使用场景

当工具返回结果过长时，将冗长的 `content` 字段移除，只保留 `path` 或 `file_path`。

***REMOVED******REMOVED******REMOVED*** 示例

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

***REMOVED******REMOVED******REMOVED*** 对话历史紧凑化

```python
***REMOVED*** 对早期历史进行紧凑化，保留最近的完整记录
compacted_history, removed_records = manager.compact_conversation_history(
    conversation_history,
    keep_recent=3  ***REMOVED*** 保留最近3条作为 Few-shot Examples
)
```

***REMOVED******REMOVED*** Summarization（摘要化）

***REMOVED******REMOVED******REMOVED*** 核心思想

**有损但带保险**：在生成摘要前，将完整上下文转储到日志文件（保险），然后生成摘要。

***REMOVED******REMOVED******REMOVED*** 使用场景

当上下文超过 Pre-rot Threshold（默认128K tokens）时，触发 Summarization。

***REMOVED******REMOVED******REMOVED*** 示例

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

***REMOVED******REMOVED******REMOVED*** LLM 摘要生成

如果提供了 `llm_func`，系统会使用 LLM 生成高质量摘要：

```python
from llm.deepseek import deepseek_v3_2

***REMOVED*** 初始化时提供 LLM 函数
manager = get_context_manager(llm_func=deepseek_v3_2)

***REMOVED*** 自动使用 LLM 生成摘要
summary = manager._generate_summary(conversation_history, use_llm=True)
```

如果没有 LLM 函数或生成失败，会回退到简单统计摘要。

***REMOVED******REMOVED*** 在 ReActAgent 中的应用

`react.py` 中的 `ReActAgent` 已经集成了完整的 Compaction + Summarization：

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

***REMOVED******REMOVED*** 设计原则

***REMOVED******REMOVED******REMOVED*** Manus 风格

1. **Compaction**: 无损、可逆
   - 信息被"外部化"到文件系统
   - 可通过路径重建
   - 保留元数据（长度、预览等）

2. **Summarization**: 有损但带保险
   - 先转储完整上下文（保险）
   - 再生成摘要（有损）
   - 保留最近记录作为 Few-shot Examples

***REMOVED******REMOVED******REMOVED*** Pre-rot Threshold

默认设置为 128K tokens（Manus 的建议），可以在初始化时自定义：

```python
manager = get_context_manager(pre_rot_threshold=100000)  ***REMOVED*** 100K tokens
```

***REMOVED******REMOVED*** 输出文件

***REMOVED******REMOVED******REMOVED*** Compaction 输出

- `agent/context_outputs/tool_results/` - 紧凑化的工具结果文件

***REMOVED******REMOVED******REMOVED*** Summarization 输出

- `agent/context_outputs/chat_history/full_context_dump_*.json` - 完整上下文转储文件

***REMOVED******REMOVED*** 与 UniMem 的集成

未来可以扩展支持：
- 将转储的完整上下文同步到 UniMem
- 使用 UniMem 的检索能力查找历史文件
- 在 Summarization 时利用 UniMem 的知识增强摘要质量
