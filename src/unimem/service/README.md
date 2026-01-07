# UniMem HTTP Service

UniMem HTTP 服务，提供 REST API 接口，允许外部系统通过 HTTP 调用 UniMem 功能。

## 功能特性

- ✅ REST API 接口（FastAPI）
- ✅ 三个核心操作：retain（存储）、recall（检索）、reflect（优化）
- ✅ 健康检查端点
- ✅ 自动 API 文档（Swagger UI）
- ✅ CORS 支持
- ✅ 类型安全的请求/响应模型（Pydantic）
- ✅ 完善的错误处理

## 快速开始

### 1. 安装依赖

```bash
# 默认工作目录为 src
cd /root/data/AI/creator/src
pip install -r unimem/requirements.txt
```

### 2. 配置环境变量（可选）

```bash
export UNIMEM_HOST="0.0.0.0"
export UNIMEM_PORT="9622"
export UNIMEM_CONFIG_FILE="unimem/config/unimem_service.json"
export UNIMEM_STORAGE_BACKEND="redis"
export UNIMEM_GRAPH_BACKEND="neo4j"
export UNIMEM_VECTOR_BACKEND="qdrant"
export OPENAI_API_KEY="your-api-key"
```

### 3. 启动服务

```bash
# 方式1：使用启动脚本（默认工作目录为 src）
cd /root/data/AI/creator/src
./unimem/scripts/start_unimem_service.sh

# 方式2：直接运行 Python 模块（默认工作目录为 src）
cd /root/data/AI/creator/src
python -m unimem.service.server

# 方式3：指定参数
python -m unimem.service.server --host 0.0.0.0 --port 9622 --config unimem/config/unimem_service.json
```

### 4. 访问服务

- API 文档（Swagger UI）：http://localhost:9622/docs
- API 文档（ReDoc）：http://localhost:9622/redoc
- 健康检查：http://localhost:9622/unimem/health

## API 端点

### POST /unimem/retain

存储新记忆

**请求示例**：
```json
{
  "experience": {
    "content": "用户喜欢喝咖啡",
    "timestamp": "2024-01-01T12:00:00",
    "context": "对话上下文",
    "metadata": {}
  },
  "context": {
    "session_id": "session_123",
    "user_id": "user_456",
    "metadata": {}
  },
  "operation_id": "op_789"
}
```

**响应示例**：
```json
{
  "success": true,
  "memory": {
    "id": "mem_001",
    "content": "用户喜欢喝咖啡",
    "timestamp": "2024-01-01T12:00:00",
    "memory_type": "episodic",
    "layer": "ltm",
    ...
  }
}
```

### POST /unimem/recall

检索记忆

**请求示例**：
```json
{
  "query": "用户喜欢什么饮料",
  "context": {
    "session_id": "session_123",
    "user_id": "user_456"
  },
  "memory_type": "episodic",
  "top_k": 10
}
```

**响应示例**：
```json
{
  "success": true,
  "results": [
    {
      "memory": {...},
      "score": 0.95,
      "retrieval_method": "semantic",
      "metadata": {}
    }
  ]
}
```

### POST /unimem/reflect

优化记忆

**请求示例**：
```json
{
  "memories": [
    {
      "id": "mem_001",
      "content": "...",
      ...
    }
  ],
  "task": {
    "id": "task_001",
    "description": "总结用户偏好",
    "context": "任务上下文",
    "metadata": {}
  },
  "context": {
    "session_id": "session_123"
  }
}
```

**响应示例**：
```json
{
  "success": true,
  "updated_memories": [
    {
      "id": "mem_001",
      "content": "...",
      ...
    }
  ]
}
```

### GET /unimem/health

健康检查

**响应示例**：
```json
{
  "status": "ok",
  "unimem_initialized": true,
  "message": "UniMem service is running"
}
```

## 开发模式

启动开发模式（代码变更时自动重载）：

```bash
python -m src.unimem.service.server --reload
```

## 配置

服务支持通过以下方式配置：

1. **配置文件**（JSON）：通过 `--config` 参数或 `UNIMEM_CONFIG_FILE` 环境变量
2. **环境变量**：覆盖配置文件中的值
3. **命令行参数**：`--host`, `--port` 等

配置文件示例：`src/unimem/config/unimem_service.example.json`

**重要提示**：
- 所有路径都是相对于 `src` 目录的，默认工作目录应为 `src`
- 配置文件位于 `unimem/config/` 目录下
- 启动服务前请确保在 `src` 目录下运行命令

## 集成到 Puppeteer

服务设计为独立运行，可以轻松集成到 Puppeteer 或其他系统中。参考 `unimem/docs/集成指南.md` 了解集成方案。

## 注意事项

1. 确保后端服务（Redis、Neo4j、Qdrant）已启动
2. 确保已配置 LLM API Key（OpenAI API Key）
3. 生产环境建议设置具体的 CORS 域名
4. 建议使用进程管理器（如 systemd、supervisor）管理服务

