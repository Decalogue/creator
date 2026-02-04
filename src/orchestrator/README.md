***REMOVED*** orchestrator — 编排层

多种 Agentic 推理/编排方式，统一放在此目录，便于扩展与切换。

***REMOVED******REMOVED*** 当前编排方式

| 模块 | 说明 |
|------|------|
| **react** | ReAct (Reasoning + Acting)：思考-行动-观察循环，工具发现 + 上下文卸载 + 分层行动空间。 |

***REMOVED******REMOVED*** 使用

```python
from orchestrator import ReActAgent
***REMOVED*** 或
from orchestrator.react import ReActAgent

agent = ReActAgent(max_iterations=10, enable_context_offloading=True)
result = agent.run("你的任务描述")
```

***REMOVED******REMOVED*** 后续规划

- 增加基座原生 Agentic 推理（如 OpenAI/DeepSeek 等最新 Agent API）
- 其他推理模型按需加入本目录，通过 `orchestrator` 包统一导出

***REMOVED******REMOVED*** 依赖

- tools、agent、llm 等 src 下兄弟包；运行示例时工作目录需包含 `src`（或已配置 PYTHONPATH）。
- llm 依赖（如 zai 等）需在项目虚拟环境中安装，例如：`conda activate seeme`。
