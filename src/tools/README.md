# tools — 工具调用层（创作相关）

## 简介

基于 OpenAI Function Calling 格式的工具调用框架，**主要服务于 Creator 创作流程**：编排层（如 ReAct）通过本模块发现与执行工具，支撑创作助手完成计算、查询、文档检索等能力。

- 统一接口：定义与执行可被 LLM 调用的函数，兼容 OpenAI Function Calling API。
- 与编排层配合：`orchestrator/react.py` 的 ReActAgent 使用 `default_registry` 与 `get_discovery()`，详见下文「工具发现系统」。

## 目录结构

```
tools/
├── __init__.py          # 模块导出和自动注册
├── base.py              # Tool 基类和注册表
├── discovery.py         # 工具发现（Index + Discovery Layer）
├── search_tool_docs.py  # 工具文档搜索/读取工具
├── docs/                # 各工具说明（供发现层同步）
├── example.py           # 使用示例
├── test.py              # 测试
└── README.md            # 本文档
```

**当前内置工具**（仅创作相关）：`search_tool_docs`、`read_tool_doc`。编排层通过它们按需查找工具文档；新增创作工具时继承 `Tool` 并注册，详见「与创作流程的关系」。

## 快速开始（5 分钟上手）

### 1. 导入模块

```python
from tools import default_registry, get_discovery
```

### 2. 查看可用工具

```python
# 列出所有工具
print(default_registry.list_tools())
# 输出: ['search_tool_docs', 'read_tool_doc']

# 获取工具定义（用于传递给 LLM，OpenAI Function Calling 格式）
functions = default_registry.get_all_functions()

# 获取 Index Layer 内容（供编排层注入系统提示词）
discovery = get_discovery()
index_content = discovery.get_index_layer()
```

### 3. 执行工具调用

```python
# 搜索工具文档（编排层按需调用）
result = default_registry.execute_tool(
    "search_tool_docs",
    {"query": "创作", "max_results": 5}
)

# 读取指定工具文档
doc = default_registry.execute_tool("read_tool_doc", {"tool_name": "search_tool_docs"})
```

### 4. 运行示例

```bash
cd /root/data/AI/creator/src

# 运行完整示例（包括基础使用、LLM 集成和 API 集成）
python -m tools.example

# 或直接运行
python tools/example.py

# 运行测试
python -m tools.test
```

## 详细使用指南

### 1. 基本使用

```python
from tools import default_registry, get_discovery

# 获取所有可用的工具定义（用于传递给 LLM）
functions = default_registry.get_all_functions()

# 获取 Index Layer（供编排层注入系统提示词）
discovery = get_discovery()
index_content = discovery.get_index_layer()

# 执行工具调用（示例：搜索工具文档）
result = default_registry.execute_tool(
    "search_tool_docs",
    {"query": "创作", "max_results": 5}
)
```

### 2. 创建自定义创作相关工具

```python
from tools.base import Tool, default_registry
from typing import Any, Dict

class MyCreationTool(Tool):
    """示例：创作相关自定义工具"""
    def __init__(self):
        super().__init__(name="my_creation_tool", description="创作相关能力描述")

    def get_function_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "my_creation_tool",
                "description": "创作相关能力描述",
                "parameters": {
                    "type": "object",
                    "properties": {"param1": {"type": "string", "description": "参数描述"}},
                    "required": ["param1"],
                },
            },
        }

    def execute(self, arguments: Dict[str, Any]) -> Any:
        return f"处理结果：{arguments.get('param1', '')}"

default_registry.register(MyCreationTool())
```

新增工具后，在 `tools/docs/` 下提供对应 `{tool_name}.md`（或由 discovery 自动同步生成），即可被编排层通过 `search_tool_docs` / `read_tool_doc` 发现。

## 内置工具（创作相关）

当前仅保留与创作编排配合的工具发现能力：

| 工具名 | 功能 |
|--------|------|
| **search_tool_docs** | 按关键词搜索工具文档，供编排层按需查找 |
| **read_tool_doc** | 读取指定工具的完整文档 |

编排层（如 ReActAgent）在系统提示词中只注入工具索引（Index Layer），通过上述两个工具按需拉取 Discovery Layer，减少 token。详见「工具发现系统」。

## 工具发现系统（Index + Discovery Layer）

实现 Cursor 风格的 **Index Layer + Discovery Layer** 架构：ReActAgent 等仅将工具索引注入系统提示词，按需通过发现层获取详细文档，显著减少 Token 消耗（预期 40-50%）。

### Index Layer（索引层）

- 系统提示词中只包含工具名称列表（轻量级，对 KV Cache 友好）
- Agent 知道有哪些工具可用，但不预加载详细描述

### Discovery Layer（发现层）

- 所有工具的详细描述、参数定义、使用方法同步到 `tools/docs/` 目录
- Agent 需要时主动查找：使用 `search_tool_docs` 搜索、`read_tool_doc` 读取指定工具文档
- 动态发现，不是静态注入

### 在 ReActAgent 中的应用

`orchestrator/react.py` 的 ReActAgent 已集成：系统提示词使用 Index Layer；Agent 通过 `search_tool_docs`、`read_tool_doc` 按需拉取 Discovery Layer。

### 添加新工具与文档

1. 创建工具类（继承 `Tool`），注册到 `default_registry`
2. 在 `tools/docs/` 下提供对应 `{tool_name}.md`（或由 discovery 自动同步生成）
3. 发现系统会自动同步，编排层即可通过 search/read 发现与调用

### 自定义文档目录

```python
from pathlib import Path
from tools.discovery import ToolDiscovery

custom_docs_dir = Path("/path/to/custom/docs")
discovery = ToolDiscovery(default_registry, docs_dir=custom_docs_dir)
```

## API 参考

### ToolRegistry（工具注册表）

- `register(tool: Tool) -> None`: 注册工具（Tool 对应 Function Calling 中的 Function）
- `get_tool(name: str) -> Optional[Tool]`: 根据名称获取工具
- `get_all_functions() -> List[Dict[str, Any]]`: 获取所有工具定义（OpenAI Function Calling 格式）
- `execute_tool(name: str, arguments: Union[Dict[str, Any], str]) -> Any`: 执行工具调用
- `list_tools() -> List[str]`: 列出所有已注册的工具名称

### Tool 基类（Function 基类）

所有可调用工具需要继承 `Tool` 并实现：

- `get_function_schema() -> Dict[str, Any]`: 返回 OpenAI Function Calling 格式的工具定义
- `execute(arguments: Dict[str, Any]) -> Any`: 执行工具逻辑
- `validate_arguments(arguments: Dict[str, Any]) -> bool`: 验证参数（可选，默认返回 True）

**注意**：`Tool` 对应 Function Calling 中的 Function。

## 注意事项

1. **命名说明**: 完全兼容 OpenAI Function Calling API；当前内置工具仅保留创作相关（工具发现）。
2. **错误处理**: 所有工具应有适当错误处理，返回友好错误信息。
3. **路径处理**: 运行示例时工作目录需包含 `src` 或已配置 PYTHONPATH；可直接运行 `python tools/example.py`。

## 与创作流程的关系

- **编排层**：`orchestrator/react.py` 的 ReActAgent 使用 `default_registry` 与 `get_discovery()`，系统提示词中只注入工具索引（Index Layer），Agent 通过 `search_tool_docs` / `read_tool_doc` 按需查找工具文档（Discovery Layer），减少 token 消耗。
- **扩展**：新增创作相关工具（如大纲辅助、风格检查等）时，继承 `Tool`、注册到 `default_registry`，并在 `tools/docs/` 下提供对应 `.md`，即可被发现与调用。

## 下一步

1. 查看 `example.py` 学习更多用法
2. 运行 `python -m tools.example` 查看示例
3. 运行 `python -m tools.test` 验证功能
4. 参考「工具发现系统」了解 Index + Discovery Layer 与创作编排的配合
