***REMOVED*** UniMem: 统一记忆系统

UniMem 是一个统一记忆系统，整合了当前最先进的记忆架构的核心优势，采用"分层存储 + 多维检索 + 涟漪更新 + 操作驱动"的混合架构。

***REMOVED******REMOVED*** 核心设计

***REMOVED******REMOVED******REMOVED*** 功能适配器架构

UniMem 采用**功能导向的适配器设计**，按照功能需求而非架构名称组织：

| 功能模块 | 适配器 | 参考架构 | 功能 |
|---------|--------|---------|------|
| 操作接口 | `OperationAdapter` | HindSight | Retain/Recall/Reflect 三大操作 |
| 分层存储 | `LayeredStorageAdapter` | CogMem | FoA/DA/LTM 三层存储 |
| 记忆分类 | `MemoryTypeAdapter` | MemMachine | 多类型记忆分类 |
| 图结构 | `GraphAdapter` | LightRAG | 实体-关系建模和图结构 |
| 网络链接 | `NetworkLinkAdapter` | A-Mem | 原子笔记网络和动态链接 |
| 检索引擎 | `RetrievalAdapter` | 各架构 | 多维检索和结果融合 |
| 更新机制 | `UpdateAdapter` | LightMem + A-Mem | 涟漪效应和睡眠更新 |

***REMOVED******REMOVED******REMOVED*** 设计优势

1. **功能导向**：适配器按照 UniMem 的功能需求命名，清晰表达用途
2. **思路吸收**：从各大架构学习优秀思路，但接口统一为 UniMem 的需求
3. **易于扩展**：新增功能只需实现适配器接口
4. **解耦设计**：各适配器独立，易于维护和测试

***REMOVED******REMOVED*** 快速开始

***REMOVED******REMOVED******REMOVED*** 安装依赖

```bash
pip install -r requirements.txt
```

***REMOVED******REMOVED******REMOVED*** 基本使用

```python
import logging
from datetime import datetime
from unimem import UniMem, Experience, Context, Task

***REMOVED*** 配置日志（可选，用于查看系统运行状态）
logging.basicConfig(level=logging.INFO)

***REMOVED*** 初始化系统
***REMOVED*** 注意：实际使用时需要配置相应的后端服务（Redis、Neo4j、Qdrant）
memory = UniMem(
    config={
        "network": {
            "local_model_path": "/path/to/all-MiniLM-L6-v2",  ***REMOVED*** 本地嵌入模型路径
            "qdrant_host": "localhost",
            "qdrant_port": 6333,
        }
    },
    storage_backend="redis",  ***REMOVED*** 可选：redis, mongodb, postgresql
    graph_backend="neo4j",     ***REMOVED*** 可选：neo4j, networkx
    vector_backend="qdrant"   ***REMOVED*** 可选：qdrant, faiss, milvus
)

***REMOVED*** ============================================
***REMOVED*** 1. RETAIN: 存储新记忆
***REMOVED*** ============================================
experience = Experience(
    content="用户喜欢在早上喝咖啡，并且偏爱深度烘焙的豆子。",
    timestamp=datetime.now(),
    context="早餐偏好讨论"
)
context = Context(
    session_id="session_001",
    user_id="user_123"
)

try:
    memory_obj = memory.retain(experience, context)
    print(f"✓ 记忆已存储: ID={memory_obj.id}")
    print(f"  内容: {memory_obj.content}")
    print(f"  类型: {memory_obj.memory_type}")
    print(f"  关键词: {memory_obj.keywords}")
except Exception as e:
    print(f"✗ 存储失败: {e}")

***REMOVED*** ============================================
***REMOVED*** 2. RECALL: 检索相关记忆
***REMOVED*** ============================================
query = "用户的早餐偏好是什么？"
try:
    results = memory.recall(
        query=query,
        context=context,
        top_k=5  ***REMOVED*** 返回前5个最相关的记忆
    )
    
    print(f"\n✓ 检索到 {len(results)} 条相关记忆:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. 相似度: {result.score:.3f} | "
              f"方法: {result.retrieval_method}")
        print(f"     内容: {result.memory.content[:60]}...")
except Exception as e:
    print(f"✗ 检索失败: {e}")

***REMOVED*** ============================================
***REMOVED*** 3. REFLECT: 更新和优化记忆
***REMOVED*** ============================================
task = Task(
    id="task_001",
    description="更新用户画像",
    context="根据最新交互更新用户对咖啡的偏好"
)

try:
    ***REMOVED*** 选择需要演化的记忆（通常选择检索结果中的前几条）
    memories_to_reflect = [result.memory for result in results[:3]] if results else [memory_obj]
    
    evolved_memories = memory.reflect(memories_to_reflect, task)
    print(f"\n✓ 已演化 {len(evolved_memories)} 条记忆")
    for mem in evolved_memories:
        print(f"  - {mem.id}: 标签={mem.tags}, 链接数={len(mem.links)}")
except Exception as e:
    print(f"✗ 演化失败: {e}")

***REMOVED*** ============================================
***REMOVED*** 4. 睡眠更新：批量优化记忆网络
***REMOVED*** ============================================
try:
    count = memory.run_sleep_update()
    print(f"\n✓ 睡眠更新完成: 处理了 {count} 条记忆")
except Exception as e:
    print(f"✗ 睡眠更新失败: {e}")

***REMOVED*** ============================================
***REMOVED*** 5. 查看系统状态（可选）
***REMOVED*** ============================================
status = memory.get_adapter_status()
print("\n系统适配器状态:")
for name, info in status.items():
    status_icon = "✓" if info.get("available") else "✗"
    print(f"  {status_icon} {name}: {info.get('adapter', 'N/A')}")
```

***REMOVED******REMOVED******REMOVED*** 快速示例（最小化配置）

如果只需要快速体验核心功能，可以使用默认配置：

```python
from unimem import UniMem, Experience, Context
from datetime import datetime

***REMOVED*** 使用默认配置初始化（无需外部服务）
memory = UniMem()

***REMOVED*** 存储记忆
experience = Experience(
    content="Python 是一种高级编程语言",
    timestamp=datetime.now()
)
memory_obj = memory.retain(experience, Context())

***REMOVED*** 检索记忆
results = memory.recall("编程语言", top_k=3)
for result in results:
    print(f"{result.score:.3f}: {result.memory.content}")
```

***REMOVED******REMOVED*** 系统架构

***REMOVED******REMOVED******REMOVED*** 总体架构图

UniMem 采用五层架构设计，从用户操作到数据存储的完整流程：

```mermaid
flowchart TD
    A[UniMem: 统一记忆系统<br/>分层存储 + 多维检索 + 涟漪更新 + 操作驱动] 
    
    A --> Layer1[第一层: 操作接口层<br/>OperationAdapter]
    Layer1 --> Retain[Retain<br/>记忆存储]
    Layer1 --> Recall[Recall<br/>记忆检索]
    Layer1 --> Reflect[Reflect<br/>记忆更新]
    
    Layer1 --> Layer2[第二层: 存储管理层]
    Layer2 --> FoA[FoA<br/>工作记忆<br/>~100 tokens]
    Layer2 --> DA[DA<br/>快速访问<br/>~10K tokens]
    Layer2 --> LTM[LTM<br/>长期存储<br/>无限制]
    
    FoA --> MemoryType[多类型记忆分类<br/>情景记忆、语义记忆、用户画像记忆]
    DA --> MemoryType
    LTM --> MemoryType
    
    Layer2 --> Layer3[第三层: 网络组织层]
    Layer3 --> GraphLayer[图结构层<br/>GraphAdapter<br/>实体节点、关系边、双层索引]
    Layer3 --> NetworkLayer[原子笔记网络层<br/>NetworkLinkAdapter<br/>原子笔记、动态链接、记忆演化]
    NetworkLayer -.->|映射关系| GraphLayer
    
    Layer3 --> Layer4[第四层: 检索引擎层<br/>RetrievalAdapter]
    Layer4 --> EntityRet[实体检索]
    Layer4 --> AbstractRet[抽象检索]
    Layer4 --> SemanticRet[语义检索]
    Layer4 --> GraphRet[子图链接检索]
    Layer4 --> TemporalRet[时间检索]
    
    EntityRet --> Fusion[智能融合<br/>RRF + 重排序]
    AbstractRet --> Fusion
    SemanticRet --> Fusion
    GraphRet --> Fusion
    TemporalRet --> Fusion
    
    Layer4 --> Layer5[第五层: 更新机制层<br/>UpdateAdapter]
    Layer5 --> Ripple[实时涟漪更新<br/>新记忆触发->直接相关节点->多级传播->图结构增量更新]
    Layer5 --> Sleep[批量睡眠更新<br/>定期触发->批量处理->压缩去重->长期记忆固化]
    
    style A fill:***REMOVED***e1f5ff
    style Layer1 fill:***REMOVED***fff4e6
    style Layer2 fill:***REMOVED***e8f5e9
    style Layer3 fill:***REMOVED***f3e5f5
    style Layer4 fill:***REMOVED***fff3e0
    style Layer5 fill:***REMOVED***fce4ec
```

***REMOVED******REMOVED******REMOVED*** 架构图分解（便于制作 PPT）

***REMOVED******REMOVED******REMOVED******REMOVED*** 部分 1：操作接口层

```mermaid
flowchart TD
    A[操作接口层<br/>OperationAdapter] 
    
    A --> B[Retain<br/>记忆存储接口]
    A --> C[Recall<br/>记忆检索接口]
    A --> D[Reflect<br/>记忆更新接口]
    
    B --> B1[• 接收新记忆]
    B --> B2[• 内容增强]
    B --> B3[• 存储分配]
    B --> B4[• 触发更新]
    
    C --> C1[• 查询解析]
    C --> C2[• 多维检索]
    C --> C3[• 结果融合]
    C --> C4[• 重排序]
    
    D --> D1[• 记忆分析]
    D --> D2[• 关联发现]
    D --> D3[• 内容演化]
    D --> D4[• 网络更新]
    
    style A fill:***REMOVED***fff4e6
    style B fill:***REMOVED***e3f2fd
    style C fill:***REMOVED***e8f5e9
    style D fill:***REMOVED***fce4ec
```

***REMOVED******REMOVED******REMOVED******REMOVED*** 部分 2：存储管理层

```mermaid
flowchart TD
    A[存储管理层<br/>LayeredStorageAdapter] 
    
    A --> FoA[FoA<br/>工作记忆]
    A --> DA[DA<br/>快速访问]
    A --> LTM[LTM<br/>长期存储]
    
    FoA --> FoA1[• ~100 tokens]
    FoA --> FoA2[• 当前会话]
    FoA --> FoA3[• 快速检索]
    
    DA --> DA1[• ~10K tokens]
    DA --> DA2[• 频繁访问]
    DA --> DA3[• 关键记忆]
    
    LTM --> LTM1[• 无限制]
    LTM --> LTM2[• 持久化存储]
    LTM --> LTM3[• 完整历史]
    
    FoA --> MemoryType[多类型记忆分类<br/>MemoryTypeAdapter]
    DA --> MemoryType
    LTM --> MemoryType
    
    MemoryType --> Type1[情景记忆]
    MemoryType --> Type2[语义记忆]
    MemoryType --> Type3[用户画像记忆]
    
    style A fill:***REMOVED***e8f5e9
    style FoA fill:***REMOVED***c8e6c9
    style DA fill:***REMOVED***a5d6a7
    style LTM fill:***REMOVED***81c784
    style MemoryType fill:***REMOVED***fff9c4
```

***REMOVED******REMOVED******REMOVED******REMOVED*** 部分 3：网络组织层

```mermaid
flowchart TD
    A[网络组织层] 
    
    A --> GraphLayer[图结构层<br/>GraphAdapter]
    A --> NetworkLayer[原子笔记网络层<br/>NetworkLinkAdapter]
    
    GraphLayer --> Entity[实体节点<br/>Entity Nodes]
    GraphLayer --> Relation[关系边<br/>Relation Edges]
    Entity --> Index[双层索引<br/>实体索引 + 抽象概念索引]
    Relation --> Index
    
    NetworkLayer --> Atomic[原子笔记<br/>Atomic Notes]
    NetworkLayer --> Dynamic[动态链接<br/>Dynamic Links]
    Atomic --> Evolution[记忆演化<br/>内容增强、关联发现、网络优化]
    Dynamic --> Evolution
    
    NetworkLayer -.->|映射关系| GraphLayer
    
    style A fill:***REMOVED***f3e5f5
    style GraphLayer fill:***REMOVED***e1bee7
    style NetworkLayer fill:***REMOVED***ce93d8
    style Index fill:***REMOVED***fff9c4
    style Evolution fill:***REMOVED***fff9c4
```

***REMOVED******REMOVED******REMOVED******REMOVED*** 部分 4：检索引擎层

```mermaid
flowchart TD
    A[检索引擎层<br/>RetrievalAdapter] 
    
    A --> EntityRet[实体检索<br/>Entity Retrieval]
    A --> AbstractRet[抽象检索<br/>Abstract Retrieval]
    A --> SemanticRet[语义检索<br/>Semantic Retrieval]
    A --> GraphRet[子图链接检索<br/>Subgraph Link Retrieval]
    A --> TemporalRet[时间检索<br/>Temporal Retrieval]
    
    EntityRet --> RRF[RRF 融合<br/>Reciprocal Rank Fusion]
    AbstractRet --> RRF
    SemanticRet --> RRF
    GraphRet --> RRF
    TemporalRet --> RRF
    
    RRF --> RRF1[• 多维度结果合并]
    RRF --> RRF2[• 排名加权计算]
    
    RRF --> ReRank[重排序<br/>Re-ranking]
    ReRank --> ReRank1[• 相关性评分]
    ReRank --> ReRank2[• 上下文匹配]
    ReRank --> ReRank3[• 最终结果排序]
    
    style A fill:***REMOVED***fff3e0
    style EntityRet fill:***REMOVED***ffe0b2
    style AbstractRet fill:***REMOVED***ffe0b2
    style SemanticRet fill:***REMOVED***ffe0b2
    style GraphRet fill:***REMOVED***ffe0b2
    style TemporalRet fill:***REMOVED***ffe0b2
    style RRF fill:***REMOVED***ffcc80
    style ReRank fill:***REMOVED***ffb74d
```

***REMOVED******REMOVED******REMOVED******REMOVED*** 部分 5：更新机制层

```mermaid
flowchart TD
    A[更新机制层<br/>UpdateAdapter] 
    
    A --> Ripple[实时涟漪更新<br/>Ripple Effect]
    A --> Sleep[批量睡眠更新<br/>Sleep Update]
    
    Ripple --> NewMem[新记忆]
    NewMem --> DirectNode[直接相关节点]
    DirectNode --> SecondNode[二级相关节点]
    SecondNode --> MoreNode[多级相关节点...]
    
    DirectNode --> Update1[内容更新]
    SecondNode --> Update2[内容更新]
    
    Update1 --> GraphUpdate[图结构增量更新]
    Update2 --> GraphUpdate
    
    Sleep --> Trigger[定期触发]
    Trigger --> Batch[批量处理]
    Batch --> NonCritical[非关键节点]
    Batch --> Compress[压缩去重]
    Batch --> Persist[长期存储]
    
    NonCritical --> Optimize[记忆网络优化]
    Compress --> Optimize
    Persist --> Optimize
    
    style A fill:***REMOVED***fce4ec
    style Ripple fill:***REMOVED***f8bbd0
    style Sleep fill:***REMOVED***f48fb1
    style GraphUpdate fill:***REMOVED***fff9c4
    style Optimize fill:***REMOVED***fff9c4
```

***REMOVED******REMOVED******REMOVED******REMOVED*** 部分 6：数据流图

```mermaid
flowchart TD
    User[用户输入] 
    
    User --> Operation[操作接口层<br/>Retain / Recall / Reflect]
    
    Operation --> Storage[存储层<br/>FoA / DA / LTM]
    Operation --> Network[网络层<br/>图结构 + 原子笔记网络]
    Operation --> Retrieval[检索层<br/>多维检索 + 融合]
    
    Storage --> Update[更新机制层<br/>涟漪更新 + 睡眠更新]
    Network --> Update
    Retrieval --> Update
    
    Update --> Result[结果返回用户]
    
    style User fill:***REMOVED***e3f2fd
    style Operation fill:***REMOVED***fff4e6
    style Storage fill:***REMOVED***e8f5e9
    style Network fill:***REMOVED***f3e5f5
    style Retrieval fill:***REMOVED***fff3e0
    style Update fill:***REMOVED***fce4ec
    style Result fill:***REMOVED***e1f5ff
```

***REMOVED******REMOVED*** 架构说明

***REMOVED******REMOVED******REMOVED*** 1. 操作接口层（OperationAdapter）

- **Retain**: 存储新记忆
- **Recall**: 检索相关记忆
- **Reflect**: 更新和优化记忆

***REMOVED******REMOVED******REMOVED*** 2. 存储管理层（LayeredStorageAdapter + MemoryTypeAdapter）

- **FoA (Focus of Attention)**: 工作记忆，~100 tokens
- **DA (Direct Access)**: 快速访问，~10K tokens
- **LTM (Long-Term Memory)**: 长期存储，无限制
- **多类型记忆**: 情景记忆、语义记忆、用户画像记忆

***REMOVED******REMOVED******REMOVED*** 3. 网络组织层（GraphAdapter + NetworkLinkAdapter）

- **图结构**: 实体-关系建模，双层检索
- **原子笔记网络**: 动态链接，记忆演化

***REMOVED******REMOVED******REMOVED*** 4. 检索引擎层（RetrievalAdapter）

- **多维检索**: 实体检索、抽象检索、语义检索、子图链接检索、时间检索
- **RRF 融合**: Reciprocal Rank Fusion 算法
- **重排序**: 提升检索准确性

***REMOVED******REMOVED******REMOVED*** 5. 更新机制层（UpdateAdapter）

- **涟漪效应**: 新记忆触发连锁更新
- **睡眠更新**: 批量优化非关键节点

***REMOVED******REMOVED*** 配置

***REMOVED******REMOVED******REMOVED*** 环境变量

```bash
export OPENAI_API_KEY="your-api-key"
export UNIMEM_STORAGE_BACKEND="redis"
export UNIMEM_LTM_BACKEND="postgresql"
export UNIMEM_GRAPH_BACKEND="neo4j"
export UNIMEM_VECTOR_BACKEND="qdrant"
```

***REMOVED******REMOVED******REMOVED*** 配置文件

创建 `config.json`:

```json
{
  "operation": {
    "llm_provider": "openai",
    "llm_model": "gpt-4o-mini"
  },
  "graph": {
    "backend": "neo4j",
    "workspace": "./lightrag_workspace",
    "llm_model": "gpt-4o-mini",
    "embedding_model": "text-embedding-3-small"
  },
  "network": {
    "llm_backend": "openai",
    "llm_model": "gpt-4o-mini",
    "local_model_path": "/root/data/AI/pretrain/all-MiniLM-L6-v2",
    "qdrant_host": "localhost",
    "qdrant_port": 6333,
    "collection_name": "unimem_memories"
  },
  "retrieval": {
    "top_k": 10,
    "rrf_k": 60
  },
  "update": {
    "sleep_interval": 3600
  }
}
```

***REMOVED******REMOVED*** 目录结构

```
unimem/
├── __init__.py              ***REMOVED*** 主入口
├── core.py                   ***REMOVED*** 核心实现（UniMem 类）
├── types.py                  ***REMOVED*** 数据类型定义
├── config.py                 ***REMOVED*** 配置管理
├── chat.py                   ***REMOVED*** LLM 聊天接口
├── adapters/                 ***REMOVED*** 功能适配器层
│   ├── __init__.py
│   ├── base.py               ***REMOVED*** 适配器基类
│   ├── operation_adapter.py  ***REMOVED*** 操作接口适配器
│   ├── layered_storage_adapter.py  ***REMOVED*** 分层存储适配器
│   ├── memory_type_adapter.py  ***REMOVED*** 记忆分类适配器
│   ├── graph_adapter.py      ***REMOVED*** 图结构适配器
│   ├── network_link_adapter.py  ***REMOVED*** 网络链接适配器
│   ├── retrieval_adapter.py  ***REMOVED*** 检索引擎适配器
│   ├── update_adapter.py    ***REMOVED*** 更新机制适配器
│   ├── registry.py          ***REMOVED*** 适配器注册表
│   └── README.md            ***REMOVED*** 适配器设计文档
├── storage/                  ***REMOVED*** 存储管理模块
│   ├── __init__.py
│   └── storage_manager.py    ***REMOVED*** 存储管理器
├── network/                  ***REMOVED*** 网络管理模块
│   ├── __init__.py
│   └── network_manager.py    ***REMOVED*** 网络管理器
├── retrieval/               ***REMOVED*** 检索引擎模块
│   ├── __init__.py
│   └── retrieval_engine.py  ***REMOVED*** 检索引擎
├── update/                  ***REMOVED*** 更新管理模块
│   ├── __init__.py
│   ├── update_manager.py    ***REMOVED*** 更新管理器
│   └── ripple_effect.py     ***REMOVED*** 涟漪效应实现
├── orchestration/           ***REMOVED*** 编排管理模块
│   ├── __init__.py
│   ├── orchestrator.py      ***REMOVED*** 编排器
│   ├── workflow.py          ***REMOVED*** 工作流定义
│   └── examples.py          ***REMOVED*** 编排示例
├── tests/                   ***REMOVED*** 测试模块
│   ├── __init__.py
│   ├── conftest.py          ***REMOVED*** 测试配置
│   ├── test_network_link_adapter.py  ***REMOVED*** 网络链接适配器测试
│   └── README.md            ***REMOVED*** 测试文档
├── examples/                ***REMOVED*** 使用示例
│   └── basic_usage.py       ***REMOVED*** 基本使用示例
├── requirements.txt        ***REMOVED*** 项目依赖
├── README.md               ***REMOVED*** 本文档
├── ARCHITECTURE.md         ***REMOVED*** 架构设计文档
├── IMPLEMENTATION.md       ***REMOVED*** 实现文档
└── IMPROVEMENTS.md         ***REMOVED*** 改进记录
```

***REMOVED******REMOVED*** 设计理念

***REMOVED******REMOVED******REMOVED*** 适配器模式

适配器的主要目的是**从各大架构吸收精华，将思路实现到 UniMem**，而不是简单地照搬架构接口。

- **功能导向**：按照 UniMem 的功能需求命名适配器
- **思路吸收**：从各大架构学习优秀思路
- **统一接口**：接口按照 UniMem 的需求定义
- **易于扩展**：新增功能只需实现适配器

***REMOVED******REMOVED******REMOVED*** 信息交互、操作、叠加

适配器之间可以按照整体架构进行：

1. **顺序交互**：前一个适配器的输出作为后一个的输入
2. **并行交互**：多个适配器并行执行，结果合并
3. **叠加交互**：多个适配器操作叠加，形成完整流程

***REMOVED******REMOVED*** 测试

运行测试前需要激活 `seeme` 环境：

```bash
***REMOVED*** 方式一：使用自动测试脚本
python tests/run_tests.py

***REMOVED*** 方式二：手动激活环境
conda activate seeme
python -m pytest tests/ -v
```

更多测试信息请参考 [tests/README.md](tests/README.md)。

***REMOVED******REMOVED*** 相关文档

- [ARCHITECTURE.md](ARCHITECTURE.md) - 详细的架构设计文档
- [IMPLEMENTATION.md](IMPLEMENTATION.md) - 实现细节和进度
- [IMPROVEMENTS.md](IMPROVEMENTS.md) - 改进记录
- [adapters/README.md](adapters/README.md) - 适配器设计文档
- [tests/README.md](tests/README.md) - 测试文档

***REMOVED******REMOVED*** 后续工作

1. **完善适配器实现**：集成各架构的实际 API
2. **集成实际存储后端**：Redis、PostgreSQL、Neo4j、Qdrant
3. **实现各检索方法**：向量相似度、图遍历、关键词匹配
4. **测试覆盖**：增加更多单元测试和集成测试
5. **性能优化**：异步处理、缓存机制、分布式部署
6. **编排功能**：完善工作流编排和任务调度
