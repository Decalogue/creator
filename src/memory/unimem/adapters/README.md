***REMOVED*** 适配器层设计文档

***REMOVED******REMOVED*** 设计理念

适配器的主要目的是**从各大架构吸收精华，将思路实现到 UniMem**，而不是简单地照搬架构接口。

***REMOVED******REMOVED******REMOVED*** 核心原则

1. **按功能需求命名**：适配器按照 UniMem 的功能模块需求命名，而非架构名称
2. **吸收精华思路**：从各大架构学习优秀思路，但接口统一为 UniMem 的需求
3. **解耦和扩展**：各适配器独立，易于扩展和维护

***REMOVED******REMOVED*** 功能适配器架构

```
┌─────────────┐
│    UniMem   │
└──────┬──────┘
       │
       ├─── OperationAdapter ────> 参考 HindSight（三操作范式）
       ├─── LayeredStorageAdapter ────> 参考 CogMem（三层架构）
       ├─── MemoryTypeAdapter ────> 参考 MemMachine（多类型）
       ├─── GraphAdapter ────> 参考 LightRAG（图结构）
       ├─── AtomLinkAdapter ────> 参考 A-Mem（原子笔记网络）
       ├─── RetrievalAdapter ────> 参考各架构（多维检索）
       └─── UpdateAdapter ────> 参考 LightMem + A-Mem（更新机制）
```

***REMOVED******REMOVED*** 功能适配器说明

***REMOVED******REMOVED******REMOVED*** 1. OperationAdapter（操作接口适配器）

**功能需求**：实现 Retain/Recall/Reflect 三大操作  
**参考架构**：HindSight（三操作范式）

```python
class OperationAdapterImpl(OperationAdapter):
    def retain(self, experience, context) -> Memory:
        """存储新记忆 - 参考 HindSight 的 retain 思路"""
        pass
    
    def recall(self, query, context, top_k) -> List[Memory]:
        """检索相关记忆 - 参考 HindSight 的 recall 思路"""
        pass
    
    def reflect(self, memories, task) -> List[Memory]:
        """更新和优化记忆 - 参考 HindSight 的 reflect 思路"""
        pass
```

***REMOVED******REMOVED******REMOVED*** 2. LayeredStorageAdapter（分层存储适配器）

**功能需求**：实现 FoA/DA/LTM 三层存储  
**参考架构**：CogMem（三层记忆架构）

```python
class LayeredStorageAdapterImpl(LayeredStorageAdapter):
    def add_to_foa(self, memory) -> bool:
        """添加到 FoA - 参考 CogMem 的 FoA 思路"""
        pass
    
    def add_to_da(self, memory) -> bool:
        """添加到 DA - 参考 CogMem 的 DA 思路"""
        pass
    
    def add_to_ltm(self, memory, memory_type) -> bool:
        """添加到 LTM - 参考 CogMem 的 LTM 思路"""
        pass
```

***REMOVED******REMOVED******REMOVED*** 3. MemoryTypeAdapter（记忆分类适配器）

**功能需求**：对记忆进行类型分类  
**参考架构**：MemMachine（多类型记忆）

```python
class MemoryTypeAdapterImpl(MemoryTypeAdapter):
    def classify(self, memory) -> MemoryType:
        """分类记忆类型 - 参考 MemMachine 的分类思路"""
        pass
```

***REMOVED******REMOVED******REMOVED*** 4. GraphAdapter（图结构适配器）

**功能需求**：实体-关系建模和图结构管理  
**参考架构**：LightRAG（图结构 + 双层检索）

```python
class GraphAdapterImpl(GraphAdapter):
    def extract_entities_relations(self, text) -> Tuple[List[Entity], List[Relation]]:
        """提取实体和关系 - 参考 LightRAG 的抽取思路"""
        pass
    
    def entity_retrieval(self, query, top_k) -> List[Memory]:
        """实体级检索 - 参考 LightRAG 的低级别检索"""
        pass
    
    def abstract_retrieval(self, query, top_k) -> List[Memory]:
        """抽象概念检索 - 参考 LightRAG 的高级检索"""
        pass
```

***REMOVED******REMOVED******REMOVED*** 5. AtomLinkAdapter（原子链接适配器）

**功能需求**：原子笔记网络和动态链接生成  
**参考架构**：A-Mem（原子笔记网络 + 记忆演化）

```python
class AtomLinkAdapterImpl(AtomLinkAdapter):
    def construct_atomic_note(self, content, timestamp, entities) -> Memory:
        """构建原子笔记 - 参考 A-Mem 的原子笔记思路"""
        pass
    
    def generate_links(self, new_note, top_k) -> Set[str]:
        """生成动态链接 - 参考 A-Mem 的链接生成思路"""
        pass
    
    def evolve_memory(self, memory, related, new_context) -> Memory:
        """演化记忆 - 参考 A-Mem 的记忆演化思路"""
        pass
```

***REMOVED******REMOVED******REMOVED*** 6. RetrievalAdapter（检索引擎适配器）

**功能需求**：多维检索和结果融合  
**参考架构**：各架构的检索思路

```python
class RetrievalAdapterImpl(RetrievalAdapter):
    def temporal_retrieval(self, query, top_k) -> List[Memory]:
        """时间检索 - 参考 CogMem 的时间检索思路"""
        pass
    
    def rrf_fusion(self, results_list, k) -> List[Memory]:
        """RRF 融合 - 参考各架构的融合思路"""
        pass
    
    def rerank(self, query, results) -> List[Memory]:
        """重排序 - 参考各架构的重排序思路"""
        pass
```

***REMOVED******REMOVED******REMOVED*** 7. UpdateAdapter（更新机制适配器）

**功能需求**：涟漪效应更新和睡眠更新  
**参考架构**：LightMem（睡眠更新）+ A-Mem（涟漪效应）

```python
class UpdateAdapterImpl(UpdateAdapter):
    def add_to_sleep_queue(self, memories) -> bool:
        """添加到睡眠更新队列 - 参考 LightMem 的睡眠更新思路"""
        pass
    
    def run_sleep_update(self) -> int:
        """执行睡眠更新 - 参考 LightMem 的批量更新思路"""
        pass
```

***REMOVED******REMOVED*** 适配器交互模式

***REMOVED******REMOVED******REMOVED*** 顺序交互

适配器按顺序执行，前一个的输出作为后一个的输入：

```python
***REMOVED*** retain 操作中的顺序交互
def retain(self, experience, context):
    ***REMOVED*** 1. 图结构适配器提取实体（参考 LightRAG）
    entities = self.graph_adapter.extract_entities_relations(text)
    
    ***REMOVED*** 2. 网络链接适配器构建笔记（参考 A-Mem，使用图结构适配器的输出）
    note = self.network_adapter.construct_atomic_note(..., entities=entities)
    
    ***REMOVED*** 3. 记忆分类适配器分类（参考 MemMachine，使用网络链接适配器的输出）
    type = self.memory_type_adapter.classify(note)
    
    ***REMOVED*** 4. 分层存储适配器存储（参考 CogMem）
    self.storage_adapter.add_to_foa(note)
```

***REMOVED******REMOVED******REMOVED*** 并行交互

多个适配器并行执行，结果合并：

```python
***REMOVED*** recall 操作中的并行交互
def recall(self, query, context):
    ***REMOVED*** 并行检索
    entity_results = self.graph_adapter.entity_retrieval(query)  ***REMOVED*** 参考 LightRAG
    semantic_results = self.network_adapter.semantic_retrieval(query)  ***REMOVED*** 参考 A-Mem
    temporal_results = self.retrieval_adapter.temporal_retrieval(query)  ***REMOVED*** 参考 CogMem
    
    ***REMOVED*** 融合结果
    fused = self.retrieval_adapter.rrf_fusion([entity_results, semantic_results, temporal_results])
```

***REMOVED******REMOVED******REMOVED*** 叠加交互

适配器操作叠加，形成完整的处理流程：

```python
***REMOVED*** 完整的 retain 流程
retain() 
  -> extract_entities()      ***REMOVED*** 图结构适配器（参考 LightRAG）
  -> construct_note()        ***REMOVED*** 网络链接适配器（参考 A-Mem）
  -> classify()              ***REMOVED*** 记忆分类适配器（参考 MemMachine）
  -> add_to_foa/da/ltm()     ***REMOVED*** 分层存储适配器（参考 CogMem）
  -> generate_links()        ***REMOVED*** 网络链接适配器（参考 A-Mem）
  -> trigger_ripple()        ***REMOVED*** 更新适配器（参考 LightMem + A-Mem）
```

***REMOVED******REMOVED*** 优势总结

***REMOVED******REMOVED******REMOVED*** 1. 功能导向

- 适配器按照 UniMem 的功能需求命名，清晰表达用途
- 不依赖具体架构，易于理解和维护

***REMOVED******REMOVED******REMOVED*** 2. 思路吸收

- 从各大架构学习优秀思路，但接口统一为 UniMem 的需求
- 可以灵活切换底层实现，而不影响上层接口

***REMOVED******REMOVED******REMOVED*** 3. 易于扩展

- 新增功能只需实现对应的适配器接口
- 可以同时参考多个架构的思路，融合最佳实践

***REMOVED******REMOVED******REMOVED*** 4. 解耦设计

- 各适配器独立，可以单独开发、测试、替换
- 适配器之间通过统一接口交互，不直接依赖

***REMOVED******REMOVED*** 实现指南

***REMOVED******REMOVED******REMOVED*** 创建新适配器

1. 确定功能需求（如：新的检索方式）
2. 定义适配器接口（继承相应的基类）
3. 参考相关架构的实现思路
4. 实现适配器（将架构思路转换为 UniMem 接口）
5. 在 `UniMem` 中注册适配器

***REMOVED******REMOVED******REMOVED*** 参考架构实现

在适配器实现中，可以：

```python
***REMOVED*** 参考 LightRAG 的实现思路
from lightrag import LightRAG  ***REMOVED*** 导入参考架构

class GraphAdapterImpl(GraphAdapter):
    def _do_initialize(self):
        ***REMOVED*** 参考 LightRAG 的初始化思路
        self.lightrag = LightRAG(...)  ***REMOVED*** 但接口按照 UniMem 的需求定义
    
    def extract_entities_relations(self, text):
        ***REMOVED*** 调用 LightRAG 的方法，但转换为 UniMem 的类型
        lightrag_entities = self.lightrag.extract(text)
        return [self._convert_to_unimem_entity(e) for e in lightrag_entities]
```

***REMOVED******REMOVED*** 总结

适配器层按照 **UniMem 的功能需求** 命名，从各大架构**吸收精华思路**，实现了：

- ✅ 功能导向：清晰表达适配器的用途
- ✅ 思路吸收：学习各架构的优秀实践
- ✅ 统一接口：接口按照 UniMem 的需求定义
- ✅ 易于扩展：新增功能只需实现适配器
- ✅ 解耦设计：各适配器独立，易于维护
