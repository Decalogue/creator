***REMOVED*** UniMem 测试说明

***REMOVED******REMOVED*** 环境要求

***REMOVED******REMOVED******REMOVED*** 1. Conda 环境

运行测试前需要激活 `seeme` 环境：

```bash
conda activate seeme
```

***REMOVED******REMOVED******REMOVED*** 2. Qdrant 向量数据库

**Qdrant 不需要注册账号！** 可以使用以下方式：

***REMOVED******REMOVED******REMOVED******REMOVED*** 方式一：本地运行（推荐，无需注册）

使用 Docker 运行 Qdrant：

```bash
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

或者使用 Python 客户端（内存模式，仅用于测试）：

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

***REMOVED*** 使用内存模式（不需要实际服务）
client = QdrantClient(":memory:")
```

***REMOVED******REMOVED******REMOVED******REMOVED*** 方式二：Qdrant Cloud（可选，需要注册）

如果需要使用云端服务，可以注册 [Qdrant Cloud](https://cloud.qdrant.io/) 账号，但这不是必需的。

**对于测试，推荐使用本地 Docker 方式，无需注册任何账号。**

***REMOVED******REMOVED*** 运行测试

***REMOVED******REMOVED******REMOVED*** 方式一：自动运行脚本（推荐）

***REMOVED******REMOVED******REMOVED******REMOVED*** 使用 Bash 脚本

```bash
***REMOVED*** 给脚本添加执行权限
chmod +x tests/run_tests.sh

***REMOVED*** 运行测试（会自动激活 seeme 环境）
./tests/run_tests.sh
```

***REMOVED******REMOVED******REMOVED******REMOVED*** 使用 Python 脚本

```bash
***REMOVED*** 给脚本添加执行权限
chmod +x tests/run_tests.py

***REMOVED*** 运行测试
python tests/run_tests.py
```

***REMOVED******REMOVED******REMOVED*** 方式二：手动运行

```bash
***REMOVED*** 1. 激活 seeme 环境
conda activate seeme

***REMOVED*** 2. 运行所有测试
python -m pytest unimem/tests/ -v

***REMOVED*** 或使用 unittest
python -m unittest discover -s unimem/tests -p "test_*.py" -v
```

***REMOVED******REMOVED******REMOVED*** 运行特定测试

```bash
***REMOVED*** 测试网络链接适配器
python -m pytest unimem/tests/test_network_link_adapter.py -v

***REMOVED*** 运行特定测试类
python -m pytest unimem/tests/test_network_link_adapter.py::TestNetworkLinkAdapter -v

***REMOVED*** 运行特定测试方法
python -m pytest unimem/tests/test_network_link_adapter.py::TestNetworkLinkAdapter::test_construct_atomic_note -v
```

***REMOVED******REMOVED******REMOVED*** 运行集成测试

集成测试需要实际的 Qdrant 和 LLM 服务：

```bash
***REMOVED*** 1. 确保 Qdrant 服务运行
docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant

***REMOVED*** 2. 设置环境变量启用集成测试
export RUN_INTEGRATION_TESTS=1

***REMOVED*** 3. 运行集成测试
python -m pytest unimem/tests/test_network_link_adapter.py::TestNetworkLinkAdapterIntegration -v
```

***REMOVED******REMOVED*** 测试分类

***REMOVED******REMOVED******REMOVED*** 单元测试

使用 Mock 对象，不依赖外部服务：
- ✅ 快速执行
- ✅ 不依赖 Qdrant、LLM 等服务
- ✅ 测试核心逻辑
- ✅ 可以随时运行

***REMOVED******REMOVED******REMOVED*** 集成测试

需要实际的外部服务：
- ⚠️ 需要 Qdrant 服务运行（本地 Docker 即可）
- ⚠️ 需要 LLM API 可用（使用 deepseek-v3.2）
- ⚠️ 需要设置 `RUN_INTEGRATION_TESTS=1` 环境变量
- ⚠️ 默认跳过，避免意外运行

***REMOVED******REMOVED*** 测试覆盖

- ✅ 原子笔记构建
- ✅ 内容分析和元数据提取
- ✅ 向量存储操作（添加、更新、删除）
- ✅ 语义检索
- ✅ 子图链接检索
- ✅ 记忆链接生成
- ✅ 记忆演化
- ✅ 错误处理和边界情况
- ✅ JSON 解析（支持 markdown 代码块）

***REMOVED******REMOVED*** Qdrant 使用说明

***REMOVED******REMOVED******REMOVED*** 本地运行（推荐）

**无需注册账号**，使用 Docker 运行：

```bash
***REMOVED*** 启动 Qdrant
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant

***REMOVED*** 检查服务状态
curl http://localhost:6333/health

***REMOVED*** 停止服务
docker stop qdrant

***REMOVED*** 删除容器（可选）
docker rm qdrant
```

***REMOVED******REMOVED******REMOVED*** 配置说明

在 `unimem/config.py` 或初始化时配置：

```python
config = {
    "network": {
        "qdrant_host": "localhost",  ***REMOVED*** 本地运行
        "qdrant_port": 6333,
        "collection_name": "unimem_memories",
    }
}
```

***REMOVED******REMOVED******REMOVED*** 内存模式（仅测试）

对于测试，可以使用内存模式（不需要 Docker）：

```python
***REMOVED*** 在测试中使用内存模式
from qdrant_client import QdrantClient

client = QdrantClient(":memory:")  ***REMOVED*** 内存模式，不持久化
```

***REMOVED******REMOVED*** 注意事项

1. **环境依赖**：确保已激活 `seeme` 环境
2. **Qdrant 服务**：
   - 单元测试不需要 Qdrant（使用 Mock）
   - 集成测试需要 Qdrant（本地 Docker 即可，无需注册）
3. **Mock 使用**：单元测试使用 Mock，不会实际调用外部服务
4. **测试隔离**：每个测试方法都会重置状态
5. **清理数据**：集成测试会自动清理测试数据

***REMOVED******REMOVED*** 故障排查

***REMOVED******REMOVED******REMOVED*** 问题：无法激活 seeme 环境

```bash
***REMOVED*** 检查 conda 是否已初始化
conda --version

***REMOVED*** 手动激活
conda activate seeme

***REMOVED*** 检查环境
echo $CONDA_DEFAULT_ENV
```

***REMOVED******REMOVED******REMOVED*** 问题：Qdrant 连接失败

```bash
***REMOVED*** 检查 Qdrant 是否运行
curl http://localhost:6333/health

***REMOVED*** 如果未运行，启动 Qdrant
docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

***REMOVED******REMOVED******REMOVED*** 问题：测试导入失败

```bash
***REMOVED*** 确保在项目根目录
cd /root/data/AI/creator/src/memory

***REMOVED*** 检查 Python 路径
python -c "import sys; print(sys.path)"

***REMOVED*** 确保 unimem 在路径中
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```
