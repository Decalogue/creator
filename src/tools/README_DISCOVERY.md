***REMOVED*** 工具动态发现系统（创作相关）

***REMOVED******REMOVED*** 概述

实现 Cursor 风格的 **Index Layer + Discovery Layer** 架构，**主要服务于 Creator 编排层**：ReActAgent 等仅将工具索引注入系统提示词，按需通过本发现层获取详细文档，显著减少 Token 消耗（预期 40-50%）。

***REMOVED******REMOVED*** 核心思想

***REMOVED******REMOVED******REMOVED*** Index Layer（索引层）
- 系统提示词中只包含工具名称列表（轻量级）
- 对 KV Cache 友好
- 减少 Token 消耗

***REMOVED******REMOVED******REMOVED*** Discovery Layer（发现层）
- 所有工具的详细描述、参数定义、使用方法同步到 `tools/docs/` 目录
- Agent 需要时主动查找（使用 `search_tool_docs` 工具）
- 动态发现，不是静态注入

***REMOVED******REMOVED*** 使用方法

***REMOVED******REMOVED******REMOVED*** 1. 自动初始化

工具发现系统会在导入时自动初始化：

```python
from tools import default_registry, get_discovery

***REMOVED*** 自动同步工具文档
discovery = get_discovery()
```

***REMOVED******REMOVED******REMOVED*** 2. 获取 Index Layer 内容

```python
***REMOVED*** 获取轻量级工具列表（用于系统提示词）
index_content = discovery.get_index_layer()
print(index_content)
```

输出示例：
```
可用工具列表：

- search_tool_docs: 按关键词搜索工具文档...
- read_tool_doc: 读取指定工具的完整文档...

注意：如需查看工具的详细描述、参数定义和使用方法，请使用 `search_tool_docs` 工具搜索工具文档。
```

***REMOVED******REMOVED******REMOVED*** 3. Agent 主动搜索工具

Agent 可以使用以下工具主动查找工具文档：

***REMOVED******REMOVED******REMOVED******REMOVED*** `search_tool_docs`
在工具文档中搜索相关工具。

```python
***REMOVED*** Agent 可以这样调用
result = discovery.search_tool_docs("计算", max_results=3)
```

***REMOVED******REMOVED******REMOVED******REMOVED*** `read_tool_doc`
读取指定工具的完整文档。

```python
***REMOVED*** Agent 可以这样调用
doc = discovery.get_tool_doc("calculator")
```

***REMOVED******REMOVED*** 在 ReActAgent 中的应用

`orchestrator/react.py` 中的 `ReActAgent` 已经集成了工具发现系统：

1. **系统提示词**：只包含工具名称列表（Index Layer）
2. **Agent 能力**：可以使用 `search_tool_docs` 和 `read_tool_doc` 主动查找工具文档

***REMOVED******REMOVED*** 工具文档格式

每个工具文档（`tools/docs/{tool_name}.md`）包含：

- 工具名称和描述
- 参数定义（类型、是否必需、描述）
- 使用示例

***REMOVED******REMOVED*** 预期效果

- **Token 消耗减少**：40-50%（参考 Cursor 的 46.9%）
- **上下文质量提升**：Agent 只加载需要的工具信息
- **工具使用更精准**：减少 Context Confusion

***REMOVED******REMOVED*** 扩展性

***REMOVED******REMOVED******REMOVED*** 添加新工具

1. 创建工具类（继承 `Tool`）
2. 注册到 `default_registry`
3. 工具发现系统会自动同步文档

***REMOVED******REMOVED******REMOVED*** 自定义文档目录

```python
from pathlib import Path
from tools.discovery import ToolDiscovery

custom_docs_dir = Path("/path/to/custom/docs")
discovery = ToolDiscovery(default_registry, docs_dir=custom_docs_dir)
```

***REMOVED******REMOVED*** 与创作流程的关系

- **编排层**：`orchestrator/react.py` 的 ReActAgent 已集成本发现系统；系统提示词使用 Index Layer，Agent 通过 `search_tool_docs`、`read_tool_doc` 按需拉取 Discovery Layer。
- **与 Skills**：未来可扩展 Skills 的文档同步与发现，与 tools 统一为创作可用的能力层。
