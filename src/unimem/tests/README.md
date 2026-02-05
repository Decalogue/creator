# UniMem 测试说明

## 环境要求

### 1. Conda 环境

运行测试前需要激活 `seeme` 环境：

```bash
conda activate seeme
```

### 2. Qdrant 向量数据库

**Qdrant 不需要注册账号！** 可以使用以下方式：

#### 方式一：本地运行（推荐，无需注册）

使用 Docker 运行 Qdrant：

```bash
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

或者使用 Python 客户端（内存模式，仅用于测试）：

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# 使用内存模式（不需要实际服务）
client = QdrantClient(":memory:")
```

#### 方式二：Qdrant Cloud（可选，需要注册）

如果需要使用云端服务，可以注册 [Qdrant Cloud](https://cloud.qdrant.io/) 账号，但这不是必需的。

**对于测试，推荐使用本地 Docker 方式，无需注册任何账号。**

## 运行测试

### 方式一：自动运行脚本（推荐）

#### 使用 Bash 脚本

```bash
# 给脚本添加执行权限
chmod +x tests/run_tests.sh

# 运行测试（会自动激活 seeme 环境）
./tests/run_tests.sh
```

#### 使用 Python 脚本

```bash
# 给脚本添加执行权限
chmod +x tests/run_tests.py

# 运行测试
python tests/run_tests.py
```

### 方式二：手动运行

```bash
# 1. 激活 seeme 环境
conda activate seeme

# 2. 运行所有测试
python -m pytest unimem/tests/ -v

# 或使用 unittest
python -m unittest discover -s unimem/tests -p "test_*.py" -v
```

### 运行特定测试

```bash
# 测试网络链接适配器
python -m pytest unimem/tests/test_atom_link_adapter.py -v

# 运行特定测试类
python -m pytest unimem/tests/test_atom_link_adapter.py::TestAtomLinkAdapter -v

# 运行特定测试方法
python -m pytest unimem/tests/test_atom_link_adapter.py::TestAtomLinkAdapter::test_construct_atomic_note -v
```

### 运行集成测试

集成测试需要实际的 Qdrant 和 LLM 服务：

```bash
# 1. 确保 Qdrant 服务运行
docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant

# 2. 设置环境变量启用集成测试
export RUN_INTEGRATION_TESTS=1

# 3. 运行集成测试
python -m pytest unimem/tests/test_atom_link_adapter.py::TestAtomLinkAdapterIntegration -v
```

## 测试分类

### 单元测试

使用 Mock 对象，不依赖外部服务：
- ✅ 快速执行
- ✅ 不依赖 Qdrant、LLM 等服务
- ✅ 测试核心逻辑
- ✅ 可以随时运行

### 集成测试

需要实际的外部服务：
- ⚠️ 需要 Qdrant 服务运行（本地 Docker 即可）
- ⚠️ 需要 LLM API 可用（使用 deepseek-v3.2）
- ⚠️ 需要设置 `RUN_INTEGRATION_TESTS=1` 环境变量
- ⚠️ 默认跳过，避免意外运行

## 测试覆盖

### 核心模块测试
- ✅ **test_types.py**: 类型系统测试
  - Experience、Memory、Task、Context 数据类
  - 数据验证（空值、范围检查）
  - 序列化/反序列化
  - Entity、Relation 验证

- ✅ **test_config.py**: 配置管理测试
  - 默认配置加载
  - 文件配置加载
  - 环境变量支持
  - 配置验证（后端类型、范围检查）
  - Neo4j、Redis 配置

- ✅ **test_core.py**: 核心功能测试
  - UniMem 初始化
  - RETAIN 操作（存储记忆）
  - RECALL 操作（检索记忆）
  - REFLECT 操作（优化记忆）
  - 健康检查和指标
  - 线程安全测试

### 适配器测试
- ✅ **test_atom_link_adapter.py**: 原子链接适配器
  - ✅ 原子笔记构建
  - ✅ 内容分析和元数据提取
  - ✅ 向量存储操作（添加、更新、删除）
  - ✅ 语义检索
  - ✅ 子图链接检索
  - ✅ 记忆链接生成
  - ✅ 记忆演化
  - ✅ 错误处理和边界情况
  - ✅ JSON 解析（支持 markdown 代码块）

- ✅ **test_graph_adapter.py**: 图结构适配器测试
  - RequestMetrics 指标测试
  - 实体搜索测试
  - 实体添加测试
  - 关系添加测试
  - API 错误处理
  - 健康检查测试

- ✅ **test_operation_adapter.py**: 操作适配器测试
  - RETAIN 操作测试
  - RECALL 操作测试
  - REFLECT 操作测试
  - 参数验证测试
  - Budget 枚举测试
  - 错误处理测试

### 集成测试
- ✅ **test_integration.py**: 端到端集成测试
  - UniMem 完整工作流（RETAIN -> RECALL -> REFLECT）
  - 存储和检索集成测试
  - 适配器协同工作测试
  - 健康检查和指标收集测试

### 存储层测试
- ✅ **test_storage_manager.py**: 存储管理器测试
  - OperationStats 统计功能
  - 三层存储操作（FoA/DA/LTM）
  - 记忆添加、更新、搜索
  - 健康检查和指标获取
  - 适配器不可用处理

- ✅ **test_hierarchical_storage.py**: 分层存储测试
  - 多层级存储（work/outline/chapter/scene）
  - 层级检索
  - 跨层级检索
  - 一致性检查
  - 记忆删除
  - ConsistencyReport 验证

- ✅ **test_neo4j_ltm.py**: Neo4j LTM 测试

### 检索层测试
- ✅ **test_retrieval_engine.py**: 检索引擎测试
  - 多维检索（实体、抽象、语义、子图）
  - RRF 融合测试
  - 错误处理和降级
  - 参数验证
  - 并行检索测试

- ✅ **test_retrieval_cache.py**: 检索缓存测试
  - CacheEntry 缓存条目测试
  - LRU 淘汰策略测试
  - TTL 过期策略测试
  - 缓存统计和监控
  - 线程安全测试

### 更新层测试
- ✅ **test_update_manager.py**: 更新管理器测试
  - 涟漪效应触发
  - 睡眠更新队列
  - 参数验证
  - 错误处理

### 上下文管理测试
- ✅ **test_context_manager.py**: 上下文管理器测试
  - 上下文压缩
  - 上下文融合
  - 上下文检索
  - 缓存管理
  - 参数验证

## Qdrant 使用说明

### 本地运行（推荐）

**无需注册账号**，使用 Docker 运行：

```bash
# 启动 Qdrant
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -v $(pwd)/local_storage/qdrant:/qdrant/storage \
  qdrant/qdrant

# 检查服务状态
curl http://localhost:6333/health

# 停止服务
docker stop qdrant

# 删除容器（可选）
docker rm qdrant
```

### 配置说明

在 `unimem/config.py` 或初始化时配置：

```python
config = {
    "network": {
        "qdrant_host": "localhost",  # 本地运行
        "qdrant_port": 6333,
        "collection_name": "unimem_memories",
    }
}
```

### 内存模式（仅测试）

对于测试，可以使用内存模式（不需要 Docker）：

```python
# 在测试中使用内存模式
from qdrant_client import QdrantClient

client = QdrantClient(":memory:")  # 内存模式，不持久化
```

## 注意事项

1. **环境依赖**：确保已激活 `seeme` 环境
2. **Qdrant 服务**：
   - 单元测试不需要 Qdrant（使用 Mock）
   - 集成测试需要 Qdrant（本地 Docker 即可，无需注册）
3. **Mock 使用**：单元测试使用 Mock，不会实际调用外部服务
4. **测试隔离**：每个测试方法都会重置状态
5. **清理数据**：集成测试会自动清理测试数据

## 故障排查

### 问题：无法激活 seeme 环境

```bash
# 检查 conda 是否已初始化
conda --version

# 手动激活
conda activate seeme

# 检查环境
echo $CONDA_DEFAULT_ENV
```

### 问题：Qdrant 连接失败

```bash
# 检查 Qdrant 是否运行
curl http://localhost:6333/health

# 如果未运行，启动 Qdrant
docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

### 问题：测试导入失败

```bash
# 确保在项目根目录
cd /root/data/AI/creator/src/memory

# 检查 Python 路径
python -c "import sys; print(sys.path)"

# 确保 unimem 在路径中
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```
