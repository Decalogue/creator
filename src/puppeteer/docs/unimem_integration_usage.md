***REMOVED*** Puppeteer 与 UniMem 集成使用指南

***REMOVED******REMOVED*** 概述

本文档介绍如何在 Puppeteer 中使用集成的 UniMem 记忆系统。集成设计遵循 Puppeteer 架构，通过工具系统调用 UniMem，实现无缝的记忆管理。

***REMOVED******REMOVED*** 架构设计

***REMOVED******REMOVED******REMOVED*** 集成方式

```
GraphReasoningWithMemory
  ├─ 任务开始时：检索相关记忆
  ├─ 注入记忆到 GlobalInfo
  └─ 任务完成时：存储最终结果

Reasoning_Agent_With_Memory
  ├─ 激活时：注入记忆上下文到 system_prompt
  ├─ 执行时：支持调用 UniMem 工具
  └─ 完成后：自动存储重要内容

提示词增强
  ├─ system_prompt_with_memory.json：记忆使用指南
  ├─ actions_reasoning_with_memory.jsonl：记忆使用建议
  └─ actions_external_tools_with_memory.jsonl：UniMem 工具说明
```

***REMOVED******REMOVED*** 使用方法

***REMOVED******REMOVED******REMOVED*** 方式 1：使用增强的组件（推荐）

***REMOVED******REMOVED******REMOVED******REMOVED*** 1.1 修改任务文件

将 `tasks/novel.py` 中的：
```python
from inference.reasoning.reasoning import GraphReasoning

reasoning = GraphReasoning(task, graph)
```

改为：
```python
from inference.reasoning.reasoning_with_memory import GraphReasoningWithMemory

reasoning = GraphReasoningWithMemory(task, graph, unimem_enabled=True)
```

***REMOVED******REMOVED******REMOVED******REMOVED*** 1.2 修改 Agent 注册（可选）

如果需要使用带记忆的 Agent，可以修改 Agent 注册逻辑，使用 `Reasoning_Agent_With_Memory`。

或者，直接使用原有的 `Reasoning_Agent`，它也能通过工具系统调用 UniMem。

***REMOVED******REMOVED******REMOVED*** 方式 2：使用带记忆的提示词

***REMOVED******REMOVED******REMOVED******REMOVED*** 2.1 更新提示词文件

将原有的提示词文件替换为带记忆版本：
- `prompts/general/system_prompt.json` → `system_prompt_with_memory.json`
- `prompts/general/actions_reasoning.jsonl` → `actions_reasoning_with_memory.jsonl`
- `prompts/general/actions_external_tools.jsonl` → `actions_external_tools_with_memory.jsonl`

***REMOVED******REMOVED******REMOVED******REMOVED*** 2.2 确保 UniMem 工具已注册

确保 `tools/unimem_tool.py` 中的工具已自动注册。通常导入时就会自动注册：

```python
from tools.unimem_tool import UniMemRetainTool, UniMemRecallTool, UniMemReflectTool
```

***REMOVED******REMOVED******REMOVED*** 方式 3：直接使用任务文件

使用已集成的任务文件 `tasks/novel_with_memory.py`：

```python
from tasks.novel_with_memory import run

run(runner, evaluator, results_dir, mode, data_limit=20, unimem_enabled=True)
```

***REMOVED******REMOVED*** 记忆使用流程

***REMOVED******REMOVED******REMOVED*** 1. 任务开始时

`GraphReasoningWithMemory.start()` 会自动：
- 检索任务相关记忆（基于任务简介和问题）
- 将记忆注入到 `GlobalInfo.retrieved_memories`
- 格式化记忆为文本，存储在 `GlobalInfo.memory_context`

***REMOVED******REMOVED******REMOVED*** 2. Agent 执行时

***REMOVED******REMOVED******REMOVED******REMOVED*** 2.1 自动注入记忆上下文

`Reasoning_Agent_With_Memory.activate()` 会自动：
- 从 `GlobalInfo.memory_context` 获取记忆
- 注入到 `system_prompt` 中

***REMOVED******REMOVED******REMOVED******REMOVED*** 2.2 Agent 主动使用记忆

Agent 可以通过提示词指导，主动调用 UniMem 工具：

```json
{"action": "unimem_recall", "parameter": "角色设定 主角性格"}
```

```json
{"action": "unimem_retain", "parameter": "{\"content\": \"主角性格：坚毅果敢\", \"context\": {\"category\": \"character\"}}"}
```

***REMOVED******REMOVED******REMOVED*** 3. 任务完成时

`GraphReasoningWithMemory.finalize()` 会自动：
- 存储最终结果到记忆系统
- 包含任务ID、类型、简介和大纲

***REMOVED******REMOVED*** 配置选项

***REMOVED******REMOVED******REMOVED*** 启用/禁用 UniMem

```python
***REMOVED*** 启用（默认）
reasoning = GraphReasoningWithMemory(task, graph, unimem_enabled=True)

***REMOVED*** 禁用
reasoning = GraphReasoningWithMemory(task, graph, unimem_enabled=False)
```

***REMOVED******REMOVED******REMOVED*** UniMem 服务配置

确保 UniMem 服务运行：

```bash
cd /root/data/AI/creator/src
python -m unimem.service.server
```

或使用启动脚本：

```bash
./unimem/scripts/start_unimem_service.sh
```

默认地址：`http://localhost:9622`

可以通过环境变量修改：

```bash
export UNIMEM_API_URL="http://localhost:9622"
```

***REMOVED******REMOVED*** 记忆使用策略

***REMOVED******REMOVED******REMOVED*** 检索时机

1. **任务开始**：自动检索任务相关记忆
2. **规划阶段**：Agent 可以检索相似任务的记忆
3. **推理阶段**：检索相关角色、情节、世界观设定
4. **反思阶段**：检索问题模式和解决方案

***REMOVED******REMOVED******REMOVED*** 存储时机

1. **规划阶段**：存储重要的创作决策（世界观、升级体系）
2. **推理阶段**：存储角色设定、情节设计
3. **完成阶段**：自动存储最终大纲
4. **反思阶段**：存储问题模式和解决方案

***REMOVED******REMOVED*** 示例

***REMOVED******REMOVED******REMOVED*** 完整使用示例

```python
from tasks.novel_with_memory import run
from tasks.runner import BenchmarkRunner
from tasks.evaluator import BenchmarkEvaluator

***REMOVED*** 初始化
runner = BenchmarkRunner("personas/personas.jsonl", {})
evaluator = BenchmarkEvaluator()
results_dir = "./results/Novel_with_memory_validation"

***REMOVED*** 运行任务（启用 UniMem）
run(runner, evaluator, results_dir, "validation", 
    data_limit=10, 
    unimem_enabled=True)
```

***REMOVED******REMOVED******REMOVED*** Agent 使用记忆示例

Agent 在推理过程中可以调用：

```python
***REMOVED*** 检索记忆
{"action": "unimem_recall", "parameter": "升级体系 力量等级"}

***REMOVED*** 存储记忆
{"action": "unimem_retain", "parameter": "{\"content\": \"升级体系：炼气、筑基、金丹\", \"context\": {\"category\": \"worldview\"}}"}
```

***REMOVED******REMOVED*** 故障排除

***REMOVED******REMOVED******REMOVED*** UniMem 服务未运行

**错误**：`Connection refused` 或 `无法连接到 UniMem 服务`

**解决**：
1. 启动 UniMem 服务
2. 检查服务地址是否正确
3. 检查网络连接

***REMOVED******REMOVED******REMOVED*** 工具未注册

**错误**：`UniMem 工具未注册`

**解决**：
1. 确保 `tools/unimem_tool.py` 已导入
2. 检查工具注册装饰器是否生效

***REMOVED******REMOVED******REMOVED*** 记忆检索失败

**现象**：检索不到记忆或检索失败

**解决**：
1. 检查 UniMem 服务是否正常
2. 检查后端服务（Redis、Neo4j、Qdrant）是否运行
3. 检查查询参数是否正确

***REMOVED******REMOVED*** 最佳实践

1. **渐进式启用**：先在小数据集上测试，再扩展到完整任务
2. **监控记忆使用**：观察检索和存储的频率，优化查询策略
3. **记忆质量**：只存储有价值的内容，避免噪音
4. **查询优化**：使用具体的查询词，限制检索数量（top_k=5-10）
5. **错误处理**：确保记忆操作失败不影响主流程

***REMOVED******REMOVED*** 性能考虑

- **检索延迟**：HTTP 调用有延迟，考虑批量检索或异步操作
- **存储频率**：避免过度存储，只在关键节点存储
- **记忆数量**：限制检索数量，避免上下文过长

***REMOVED******REMOVED*** 下一步

- 优化记忆检索策略
- 添加记忆重要性评分
- 实现记忆自动清理
- 支持记忆版本管理

