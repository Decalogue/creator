***REMOVED*** Puppeteer 与 UniMem 集成指南

***REMOVED******REMOVED*** 一、集成方式

***REMOVED******REMOVED******REMOVED*** 方式 1：任务级别集成（推荐用于创作任务）

在任务开始时检索记忆，任务完成后优化记忆。

**适用场景**：
- 小说创作
- 剧本创作
- 需要长期记忆的任务

**实现位置**：
- `tasks/novel.py`
- `tasks/creative_writing.py`

**示例代码**：
```python
from tools.base.register import global_tool_registry
from tools.unimem_tool import UniMemRetainTool, UniMemRecallTool

def run(runner, evaluator, results_dir, mode, data_limit=None):
    ***REMOVED*** 1. 检索任务相关记忆
    recall_tool = global_tool_registry.get_tool("unimem_recall")
    memories = recall_tool.execute(
        query=task["Introduction"],
        context={"task_type": "novel"}
    )
    
    ***REMOVED*** 2. 将记忆注入任务
    task["retrieved_memories"] = memories
    
    ***REMOVED*** 3. 创建推理系统（Agent 可以使用记忆）
    reasoning = GraphReasoning(task, graph)
    reasoning.start()
    result = reasoning.n_step(max_steps)
    
    ***REMOVED*** 4. 存储结果
    retain_tool = global_tool_registry.get_tool("unimem_retain")
    retain_tool.execute(
        experience={"content": result, ...},
        context={"task_id": task["id"]}
    )
```

***REMOVED******REMOVED******REMOVED*** 方式 2：Agent 级别集成（推荐用于专业 Agent）

在特定 Agent 中集成记忆功能。

**适用场景**：
- CharacterAgent（角色 Agent）
- PlotAgent（情节 Agent）
- WorldBuildingAgent（世界观 Agent）

**实现位置**：
- 创建新的 Agent 类继承 `Reasoning_Agent`
- 或修改现有 Agent 的 `take_action()` 方法

**示例代码**：
```python
class CharacterAgentWithMemory(Reasoning_Agent):
    def take_action(self, global_info):
        ***REMOVED*** 1. 检索角色记忆
        recall_tool = global_tool_registry.get_tool("unimem_recall")
        memories = recall_tool.execute(
            query="角色设定",
            context={"agent": "CharacterAgent"}
        )
        
        ***REMOVED*** 2. 使用记忆
        if memories:
            character_context = format_memories(memories)
            ***REMOVED*** 添加到 system prompt
        
        ***REMOVED*** 3. 执行任务
        action = super().take_action(global_info)
        
        ***REMOVED*** 4. 存储创作结果
        retain_tool = global_tool_registry.get_tool("unimem_retain")
        retain_tool.execute(
            experience={"content": action.answer, ...},
            context={"agent": "CharacterAgent"}
        )
        
        return action
```

***REMOVED******REMOVED******REMOVED*** 方式 3：GraphReasoning 层面集成（统一管理）

在 GraphReasoning 中统一管理记忆。

**适用场景**：
- 需要统一记忆管理的场景
- 跨 Agent 的记忆共享

**实现位置**：
- `inference/reasoning/reasoning.py`
- 修改 `GraphReasoning` 类

**示例代码**：
```python
class GraphReasoning:
    def start(self, save_data):
        ***REMOVED*** ... 原有代码 ...
        
        ***REMOVED*** 检索任务相关记忆
        if unimem_enabled:
            memories = self._retrieve_task_memories()
            ***REMOVED*** 注入到 global_info
            global_info.retrieved_memories = memories
    
    def finalize(self):
        ***REMOVED*** ... 原有代码 ...
        
        ***REMOVED*** 优化记忆
        if unimem_enabled:
            self._optimize_memories()
```

***REMOVED******REMOVED*** 二、集成时机

***REMOVED******REMOVED******REMOVED*** 时机 1：任务开始时

**位置**：`GraphReasoning.start()`

**操作**：检索任务相关记忆

**示例**：
```python
def start(self, save_data):
    ***REMOVED*** 检索记忆
    recall_tool = global_tool_registry.get_tool("unimem_recall")
    success, memories = recall_tool.execute(
        query=self.task.get("Question"),
        context={"task_type": self.task.get("type")},
        top_k=10
    )
    
    ***REMOVED*** 注入到 GlobalInfo
    if success and memories:
        self.global_info.retrieved_memories = memories
```

***REMOVED******REMOVED******REMOVED*** 时机 2：Agent 执行前

**位置**：`Agent.take_action()` 开始

**操作**：检索 Agent 相关记忆

**示例**：
```python
def take_action(self, global_info):
    ***REMOVED*** 检索 Agent 相关记忆
    if self.role == "CharacterAgent":
        recall_tool = global_tool_registry.get_tool("unimem_recall")
        memories = recall_tool.execute(
            query="角色设定",
            context={"agent": self.role},
            top_k=5
        )
        ***REMOVED*** 使用记忆...
```

***REMOVED******REMOVED******REMOVED*** 时机 3：Agent 执行后

**位置**：`Agent.take_action()` 返回后

**操作**：存储 Agent 输出

**示例**：
```python
def take_action(self, global_info):
    ***REMOVED*** 执行任务
    action = self.execute_task(global_info)
    
    ***REMOVED*** 存储重要结果
    if action.answer:
        retain_tool = global_tool_registry.get_tool("unimem_retain")
        retain_tool.execute(
            experience={
                "content": action.answer,
                "timestamp": datetime.now().isoformat()
            },
            context={
                "agent": self.role,
                "task_id": global_info.task.get("id")
            }
        )
    
    return action
```

***REMOVED******REMOVED******REMOVED*** 时机 4：任务完成时

**位置**：`GraphReasoning.n_step()` 完成后

**操作**：优化和整合记忆

**示例**：
```python
def finalize(self):
    ***REMOVED*** ... 原有逻辑 ...
    
    ***REMOVED*** 收集所有路径的记忆
    all_memories = self._collect_path_memories()
    
    ***REMOVED*** 优化记忆
    reflect_tool = global_tool_registry.get_tool("unimem_reflect")
    reflect_tool.execute(
        memories=all_memories,
        task=self.task
    )
```

***REMOVED******REMOVED*** 三、创作任务集成示例

***REMOVED******REMOVED******REMOVED*** 完整的 Novel 任务集成

```python
***REMOVED*** tasks/novel_with_unimem.py

def run(runner, evaluator, results_dir, mode, data_limit=None):
    ***REMOVED*** 检查 UniMem 服务
    if not check_unimem_service():
        print("警告: UniMem 服务未运行，将不使用记忆功能")
    
    dataset = load_dataset(data_limit)
    
    for task_data in dataset:
        task = format_question(task_data)
        
        ***REMOVED*** ===== 步骤 1: 检索相关记忆 =====
        print("\n[UniMem] 检索任务相关记忆...")
        recall_tool = global_tool_registry.get_tool("unimem_recall")
        success, memories = recall_tool.execute(
            query=task["Introduction"],
            context={"task_type": "novel", "task_id": task["id"]},
            top_k=10
        )
        
        if success and memories:
            print(f"[UniMem] ✓ 检索到 {len(memories)} 条相关记忆")
            ***REMOVED*** 将记忆添加到任务中，Agent 可以使用
            task["retrieved_memories"] = memories
        else:
            print("[UniMem] ℹ️ 未检索到相关记忆")
        
        ***REMOVED*** ===== 步骤 2: 执行推理 =====
        reasoning = GraphReasoning(task, graph)
        reasoning.start(None)
        
        ***REMOVED*** Agent 在执行过程中可以：
        ***REMOVED*** 1. 使用 task["retrieved_memories"] 中的记忆
        ***REMOVED*** 2. 调用 UniMem 工具存储新记忆
        ***REMOVED*** 3. 检索特定领域的记忆
        
        final_result, _ = reasoning.n_step(max_steps)
        
        ***REMOVED*** ===== 步骤 3: 存储最终结果 =====
        print("\n[UniMem] 存储最终结果...")
        retain_tool = global_tool_registry.get_tool("unimem_retain")
        retain_tool.execute(
            experience={
                "content": f"小说大纲：{final_result}",
                "timestamp": datetime.now().isoformat()
            },
            context={
                "task_id": task["id"],
                "task_type": "novel",
                "introduction": task["Introduction"]
            }
        )
        
        ***REMOVED*** ===== 步骤 4: 优化记忆 =====
        print("\n[UniMem] 优化记忆...")
        reflect_tool = global_tool_registry.get_tool("unimem_reflect")
        ***REMOVED*** 收集任务过程中的所有创作内容
        all_creations = collect_creations_from_paths(reasoning.reasoning_paths)
        reflect_tool.execute(
            memories=all_creations,
            task={
                "id": task["id"],
                "description": task["Question"],
                "context": task["Introduction"]
            }
        )
```

***REMOVED******REMOVED******REMOVED*** Agent 中的记忆使用

```python
***REMOVED*** agent/character_agent.py (示例)

class CharacterAgent(Reasoning_Agent):
    def take_action(self, global_info):
        ***REMOVED*** 1. 检索角色相关记忆
        if hasattr(global_info, 'retrieved_memories'):
            character_memories = [
                m for m in global_info.retrieved_memories
                if "角色" in m.get("content", "") or "character" in m.get("content", "").lower()
            ]
        else:
            ***REMOVED*** 主动检索
            recall_tool = global_tool_registry.get_tool("unimem_recall")
            success, character_memories = recall_tool.execute(
                query="角色设定 人物",
                context={"agent": "CharacterAgent"},
                top_k=5
            )
            character_memories = character_memories if success else []
        
        ***REMOVED*** 2. 使用记忆增强上下文
        memory_context = ""
        if character_memories:
            memory_context = "\n".join([
                f"- {m.get('content', '')}" for m in character_memories[:3]
            ])
            ***REMOVED*** 添加到 system prompt
            enhanced_prompt = f"{self.system_prompt}\n\n相关角色记忆：\n{memory_context}"
            self.dialog_history[0]["content"] = enhanced_prompt
        
        ***REMOVED*** 3. 执行任务（调用父类方法）
        action, terminated = super().take_action(global_info)
        
        ***REMOVED*** 4. 存储创作结果
        if action and hasattr(action, 'answer') and action.answer:
            ***REMOVED*** 提取角色信息（从 answer 中解析）
            character_info = self._extract_character_info(action.answer)
            
            if character_info:
                retain_tool = global_tool_registry.get_tool("unimem_retain")
                retain_tool.execute(
                    experience={
                        "content": character_info,
                        "timestamp": datetime.now().isoformat()
                    },
                    context={
                        "agent": "CharacterAgent",
                        "task_id": global_info.task.get("id")
                    }
                )
        
        return action, terminated
```

***REMOVED******REMOVED*** 四、最佳实践

***REMOVED******REMOVED******REMOVED*** 1. 记忆检索策略

**按需检索**：
- 任务开始时检索全局记忆
- Agent 执行时检索专业记忆
- 避免重复检索

**查询优化**：
- 使用具体的查询词（如"角色设定"、"情节发展"）
- 结合上下文信息（task_type, agent_role）
- 限制 top_k（通常 5-10 条足够）

***REMOVED******REMOVED******REMOVED*** 2. 记忆存储策略

**重要性过滤**：
- 只存储重要的创作内容
- 避免存储中间过程或调试信息
- 区分核心记忆和临时记忆

**结构化存储**：
- 使用清晰的 content 格式
- 添加丰富的 metadata（agent, task_id, category）
- 关联相关实体（如果有）

***REMOVED******REMOVED******REMOVED*** 3. 错误处理

**优雅降级**：
```python
def safe_recall(query, context=None):
    try:
        recall_tool = global_tool_registry.get_tool("unimem_recall")
        if not recall_tool:
            return []
        success, memories = recall_tool.execute(query=query, context=context)
        return memories if success else []
    except Exception as e:
        print(f"记忆检索失败，继续执行: {e}")
        return []  ***REMOVED*** 返回空列表，不影响主流程
```

***REMOVED******REMOVED******REMOVED*** 4. 性能优化

**批量操作**：
- 任务开始时批量检索所有需要的记忆
- 在 GlobalInfo 中缓存记忆
- 避免在循环中重复检索

**异步存储**：
- 非关键记忆可以异步存储
- 使用后台任务存储记忆

***REMOVED******REMOVED*** 五、调试和监控

***REMOVED******REMOVED******REMOVED*** 检查 UniMem 服务

```python
import requests

def check_unimem_service():
    try:
        response = requests.get("http://localhost:9622/unimem/health", timeout=2)
        return response.status_code == 200
    except:
        return False
```

***REMOVED******REMOVED******REMOVED*** 查看记忆使用情况

```python
***REMOVED*** 在任务执行过程中打印记忆使用情况
def log_memory_usage(operation, memories):
    print(f"[UniMem] {operation}: {len(memories)} 条记忆")
    for i, mem in enumerate(memories[:3], 1):
        content = mem.get("content", "") if isinstance(mem, dict) else getattr(mem, "content", "")
        print(f"  {i}. {content[:50]}...")
```

***REMOVED******REMOVED*** 六、完整工作流示例

```
1. 启动 UniMem 服务
   ↓
2. 加载任务
   ↓
3. 检索任务相关记忆（角色、情节、世界观等）
   ↓
4. 创建推理系统，注入记忆到 GlobalInfo
   ↓
5. Agent 执行：
   ├─ CharacterAgent: 检索角色记忆 → 创建角色 → 存储角色记忆
   ├─ PlotAgent: 检索情节记忆 → 设计情节 → 存储情节记忆
   └─ WorldBuildingAgent: 检索世界观记忆 → 构建世界观 → 存储世界观记忆
   ↓
6. 任务完成，收集所有创作内容
   ↓
7. 优化和整合记忆
   ↓
8. 下次任务可以复用这些记忆
```

***REMOVED******REMOVED*** 七、注意事项

1. **服务可用性**：确保 UniMem 服务运行
2. **性能影响**：HTTP 调用有延迟，考虑异步或批量操作
3. **错误处理**：记忆操作失败不应影响主流程
4. **记忆质量**：存储高质量的记忆，避免噪音
5. **查询优化**：使用合适的查询词和上下文

