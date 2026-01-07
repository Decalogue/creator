***REMOVED*** UniMem Tools for Puppeteer

Puppeteer 的 UniMem 工具集成，提供三个工具用于调用 UniMem HTTP 服务。

***REMOVED******REMOVED*** 工具列表

***REMOVED******REMOVED******REMOVED*** 1. unimem_retain - 存储记忆

将经验数据存储为记忆。

**参数**：
- `experience` (dict, 必需): 经验数据，包含 `content`, `timestamp`, `context`, `metadata`
- `context` (dict, 可选): 上下文信息，包含 `session_id`, `user_id`, `metadata`
- `operation_id` (str, 可选): 操作ID（用于幂等性检查）

**返回**：
- `(success: bool, memory: dict)`: 成功时返回记忆对象，失败时返回错误信息

**示例**：
```python
tool = UniMemRetainTool("unimem_retain")
success, memory = tool.execute(
    experience={
        "content": "用户喜欢喝咖啡",
        "timestamp": "2024-01-01T12:00:00",
        "context": "对话上下文",
        "metadata": {}
    },
    context={
        "session_id": "session_123",
        "user_id": "user_456"
    }
)
```

***REMOVED******REMOVED******REMOVED*** 2. unimem_recall - 检索记忆

从 UniMem 系统检索相关记忆。

**参数**：
- `query` (str, 必需): 查询字符串
- `context` (dict, 可选): 上下文信息
- `memory_type` (str, 可选): 记忆类型过滤（episodic/semantic/world/experience/observation/opinion）
- `top_k` (int, 可选): 返回结果数量，默认10

**返回**：
- `(success: bool, results: list)`: 成功时返回检索结果列表，失败时返回错误信息

**示例**：
```python
tool = UniMemRecallTool("unimem_recall")
success, results = tool.execute(
    query="用户喜欢什么饮料",
    context={"session_id": "session_123"},
    memory_type="episodic",
    top_k=10
)
```

***REMOVED******REMOVED******REMOVED*** 3. unimem_reflect - 优化记忆

基于任务上下文更新和优化记忆。

**参数**：
- `memories` (list, 必需): 需要优化的记忆列表
- `task` (dict, 必需): 任务上下文，包含 `id`, `description`, `context`, `metadata`
- `context` (dict, 可选): 上下文信息

**返回**：
- `(success: bool, updated_memories: list)`: 成功时返回优化后的记忆列表，失败时返回错误信息

**示例**：
```python
tool = UniMemReflectTool("unimem_reflect")
success, updated_memories = tool.execute(
    memories=[
        {
            "id": "mem_001",
            "content": "用户喜欢咖啡",
            ...
        }
    ],
    task={
        "id": "task_001",
        "description": "总结用户偏好",
        "context": "任务上下文",
        "metadata": {}
    },
    context={"session_id": "session_123"}
)
```

***REMOVED******REMOVED*** 配置

工具通过环境变量配置 UniMem 服务地址：

```bash
export UNIMEM_API_URL="http://localhost:9622"
```

默认值为 `http://localhost:9622`。

***REMOVED******REMOVED*** 使用前提

1. **启动 UniMem 服务**：
   ```bash
   python -m src.unimem.service.server
   ```

2. **确保服务可访问**：
   - 检查服务健康状态：`curl http://localhost:9622/unimem/health`
   - 确保网络连通性

3. **工具自动注册**：
   - 工具使用 `@global_tool_registry` 装饰器自动注册
   - 导入工具模块后即可使用

***REMOVED******REMOVED*** 错误处理

所有工具都包含：
- **重试机制**：使用 `tenacity` 库实现自动重试（retain/recall: 3次，reflect: 2次）
- **超时处理**：retain/recall 30秒，reflect 60秒
- **错误日志**：使用 logging 记录详细错误信息
- **友好错误信息**：返回可读的错误消息

***REMOVED******REMOVED*** 集成到 Puppeteer

工具已经通过 `@global_tool_registry` 装饰器注册到全局工具注册表。在 Puppeteer 中使用时，工具会被自动发现和使用。

***REMOVED******REMOVED*** 注意事项

1. 确保 UniMem 服务已启动并运行正常
2. 确保网络连接正常（工具与服务在同一网络或可访问）
3. reflect 操作可能较慢（60秒超时），请耐心等待
4. 生产环境建议配置服务发现或负载均衡

