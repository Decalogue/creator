"""
创作任务中使用 UniMem 的完整示例

展示如何在 Puppeteer 的小说创作任务中集成 UniMem 记忆系统：
1. 任务开始时检索相关记忆
2. Agent 执行时使用记忆增强上下文
3. Agent 执行后存储创作记忆
4. 任务完成后优化记忆
"""

import os
import json
import yaml
from datetime import datetime
from pathlib import Path

***REMOVED*** 添加项目路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tasks.base.base_task import BaseTask
from agent.register.register import agent_global_registry
from inference.graph.agent_graph import AgentGraph
from inference.reasoning.reasoning import GraphReasoning
from agent.agent_info.global_info import GlobalInfo
from tools.base.register import global_tool_registry

***REMOVED*** 导入 UniMem 工具
from tools.unimem_tool import UniMemRetainTool, UniMemRecallTool, UniMemReflectTool


class NovelTaskWithUniMem(BaseTask):
    """
    集成 UniMem 的小说创作任务
    
    特点：
    - 任务开始时检索相关记忆（角色、情节、世界观等）
    - Agent 执行时自动检索和使用记忆
    - 创作内容自动存储到 UniMem
    - 任务完成后优化和整合记忆
    """
    
    def __init__(self, unimem_enabled=True):
        """
        初始化
        
        Args:
            unimem_enabled: 是否启用 UniMem（默认启用）
        """
        super().__init__()
        self.unimem_enabled = unimem_enabled
        
        ***REMOVED*** 确保 UniMem 工具已注册
        if self.unimem_enabled:
            self._ensure_unimem_tools()
    
    def _ensure_unimem_tools(self):
        """确保 UniMem 工具已注册"""
        try:
            ***REMOVED*** 工具会在导入时自动注册，这里只是检查
            recall_tool = global_tool_registry.get_tool("unimem_recall")
            retain_tool = global_tool_registry.get_tool("unimem_retain")
            
            if not recall_tool or not retain_tool:
                print("警告: UniMem 工具未注册，将创建新实例")
                ***REMOVED*** 如果未注册，手动注册
                UniMemRecallTool("unimem_recall")
                UniMemRetainTool("unimem_retain")
                UniMemReflectTool("unimem_reflect")
            
            print("✓ UniMem 工具已就绪")
        except Exception as e:
            print(f"⚠️ UniMem 工具初始化失败: {e}")
            self.unimem_enabled = False
    
    def retrieve_task_memories(self, task):
        """
        检索任务相关的记忆
        
        Args:
            task: 任务信息
            
        Returns:
            检索到的记忆列表
        """
        if not self.unimem_enabled:
            return []
        
        try:
            recall_tool = global_tool_registry.get_tool("unimem_recall")
            if not recall_tool:
                return []
            
            ***REMOVED*** 构建查询
            query_parts = []
            if task.get("Introduction"):
                query_parts.append(task["Introduction"])
            if task.get("Question"):
                query_parts.append(task["Question"])
            query = " ".join(query_parts)
            
            ***REMOVED*** 检索记忆
            success, memories = recall_tool.execute(
                query=query,
                context={
                    "task_type": "novel_creation",
                    "task_id": task.get("id")
                },
                top_k=10
            )
            
            if success and memories:
                print(f"✓ 检索到 {len(memories)} 条相关记忆")
                return memories
            else:
                print("ℹ️ 未检索到相关记忆")
                return []
                
        except Exception as e:
            print(f"⚠️ 记忆检索失败: {e}")
            return []
    
    def store_creation_memory(self, content, agent_role, context=None):
        """
        存储创作记忆
        
        Args:
            content: 创作内容
            agent_role: Agent 角色
            context: 上下文信息
        """
        if not self.unimem_enabled:
            return
        
        try:
            retain_tool = global_tool_registry.get_tool("unimem_retain")
            if not retain_tool:
                return
            
            ***REMOVED*** 构建记忆
            experience = {
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "agent_role": agent_role,
                    "task_type": "novel_creation",
                    **(context or {})
                }
            }
            
            ***REMOVED*** 存储记忆
            success, memory = retain_tool.execute(
                experience=experience,
                context={
                    "agent": agent_role,
                    "task_type": "novel_creation",
                    **(context or {})
                }
            )
            
            if success:
                print(f"✓ 已存储记忆: {agent_role} 的创作内容")
            else:
                print(f"⚠️ 记忆存储失败: {memory}")
                
        except Exception as e:
            print(f"⚠️ 记忆存储异常: {e}")
    
    def enhance_global_info_with_memories(self, global_info, memories):
        """
        将记忆注入到 GlobalInfo
        
        Args:
            global_info: GlobalInfo 对象
            memories: 记忆列表
        """
        if not memories:
            return
        
        ***REMOVED*** 将记忆添加到 global_info 的元数据中
        if not hasattr(global_info, 'retrieved_memories'):
            global_info.retrieved_memories = []
        
        global_info.retrieved_memories.extend(memories)
        
        ***REMOVED*** 格式化记忆为文本，便于 Agent 使用
        memory_text = self._format_memories_for_prompt(memories)
        global_info.memory_context = memory_text
    
    def _format_memories_for_prompt(self, memories):
        """格式化记忆为提示文本"""
        if not memories:
            return ""
        
        formatted = ["=== 相关记忆 ==="]
        for i, mem in enumerate(memories[:5], 1):  ***REMOVED*** 只取前5条
            content = mem.get("content", "") if isinstance(mem, dict) else getattr(mem, "content", "")
            formatted.append(f"{i}. {content}")
        
        formatted.append("=== 记忆结束 ===\n")
        return "\n".join(formatted)
    
    def optimize_memories_after_task(self, task, all_creations):
        """
        任务完成后优化记忆
        
        Args:
            task: 任务信息
            all_creations: 所有创作内容
        """
        if not self.unimem_enabled:
            return
        
        try:
            reflect_tool = global_tool_registry.get_tool("unimem_reflect")
            if not reflect_tool:
                return
            
            ***REMOVED*** 收集所有创作记忆
            memories = []
            for creation in all_creations:
                if isinstance(creation, dict) and creation.get("content"):
                    memories.append({
                        "id": creation.get("id", f"memory_{len(memories)}"),
                        "content": creation.get("content"),
                        "timestamp": creation.get("timestamp", datetime.now().isoformat()),
                        "metadata": creation.get("metadata", {})
                    })
            
            if not memories:
                return
            
            ***REMOVED*** 优化记忆
            success, updated = reflect_tool.execute(
                memories=memories,
                task={
                    "id": task.get("id", "unknown"),
                    "description": task.get("Question", ""),
                    "context": task.get("Introduction", "")
                },
                context={
                    "task_type": "novel_creation"
                }
            )
            
            if success:
                print(f"✓ 已优化 {len(updated)} 条记忆")
            else:
                print(f"⚠️ 记忆优化失败: {updated}")
                
        except Exception as e:
            print(f"⚠️ 记忆优化异常: {e}")


***REMOVED*** 增强的 Agent 基类（示例）
class MemoryAwareAgent:
    """
    支持记忆的 Agent 混入类
    
    可以混入到现有的 Agent 类中，添加记忆功能
    """
    
    def retrieve_agent_memories(self, query, context=None):
        """检索 Agent 相关的记忆"""
        try:
            recall_tool = global_tool_registry.get_tool("unimem_recall")
            if not recall_tool:
                return []
            
            success, memories = recall_tool.execute(
                query=query,
                context={
                    "agent": self.role,
                    **(context or {})
                },
                top_k=5
            )
            
            return memories if success else []
        except Exception as e:
            print(f"⚠️ Agent {self.role} 记忆检索失败: {e}")
            return []
    
    def store_agent_memory(self, content, context=None):
        """存储 Agent 创作记忆"""
        try:
            retain_tool = global_tool_registry.get_tool("unimem_retain")
            if not retain_tool:
                return False
            
            success, memory = retain_tool.execute(
                experience={
                    "content": content,
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {
                        "agent_role": self.role,
                        **(context or {})
                    }
                },
                context={
                    "agent": self.role,
                    **(context or {})
                }
            )
            
            return success
        except Exception as e:
            print(f"⚠️ Agent {self.role} 记忆存储失败: {e}")
            return False


***REMOVED*** 使用示例：增强的推理流程
def run_novel_task_with_unimem(task_data, unimem_enabled=True):
    """
    运行集成 UniMem 的小说创作任务
    
    Args:
        task_data: 任务数据
        unimem_enabled: 是否启用 UniMem
    """
    print("=" * 60)
    print("小说创作任务（集成 UniMem）")
    print("=" * 60)
    
    ***REMOVED*** 1. 初始化任务管理器
    task_manager = NovelTaskWithUniMem(unimem_enabled=unimem_enabled)
    
    ***REMOVED*** 2. 格式化任务
    task = {
        "type": "Novel",
        "Question": f"根据小说简介生成小说大纲。\n***REMOVED******REMOVED*** 小说简介\n{task_data.get('introduction', '')}\n\n输出：",
        "Answer": task_data.get("outline", ""),
        "Introduction": task_data.get("introduction", ""),
        "id": task_data.get("id", "unknown")
    }
    
    ***REMOVED*** 3. 检索相关记忆
    print("\n【步骤 1】检索相关记忆...")
    memories = task_manager.retrieve_task_memories(task)
    print(f"检索到 {len(memories)} 条记忆")
    for i, mem in enumerate(memories[:3], 1):
        content = mem.get("content", "") if isinstance(mem, dict) else getattr(mem, "content", "")
        print(f"  {i}. {content[:60]}...")
    
    ***REMOVED*** 4. 注册 Agent 并创建推理系统
    print("\n【步骤 2】初始化 Agent 和推理系统...")
    agent_global_registry.register_all_agents("personas/personas.jsonl")
    agent_global_registry.reset_all_agents()
    
    graph = AgentGraph()
    reasoning = GraphReasoning(task, graph)
    
    ***REMOVED*** 5. 创建增强的 GlobalInfo（注入记忆）
    ***REMOVED*** 注意：这需要在 GraphReasoning.start() 之后修改
    ***REMOVED*** 或者创建一个自定义的 start 方法
    
    ***REMOVED*** 6. 开始推理
    print("\n【步骤 3】开始推理...")
    reasoning.start(None)
    
    ***REMOVED*** 7. 执行推理（Agent 会自动调用工具，包括 UniMem 工具）
    print("\n【步骤 4】执行推理步骤...")
    max_steps = 5
    final_result, _ = reasoning.n_step(max_steps)
    
    ***REMOVED*** 8. 存储最终结果
    if unimem_enabled and final_result:
        print("\n【步骤 5】存储最终结果到 UniMem...")
        task_manager.store_creation_memory(
            content=f"小说大纲：{final_result}",
            agent_role="FinalResult",
            context={"task_id": task["id"]}
        )
    
    ***REMOVED*** 9. 优化记忆
    if unimem_enabled:
        print("\n【步骤 6】优化记忆...")
        all_creations = [
            {"content": final_result, "id": f"task_{task['id']}_final"}
        ]
        task_manager.optimize_memories_after_task(task, all_creations)
    
    print("\n" + "=" * 60)
    print("任务完成！")
    print("=" * 60)
    
    return final_result


***REMOVED*** 增强的 Agent 示例：CharacterAgent with UniMem
class CharacterAgentWithMemory:
    """
    支持记忆的角色 Agent 示例
    
    展示如何在特定 Agent 中集成 UniMem
    """
    
    def __init__(self, base_agent):
        """
        初始化
        
        Args:
            base_agent: 基础的 Reasoning_Agent 实例
        """
        self.base_agent = base_agent
        self.role = base_agent.role
    
    def take_action_with_memory(self, global_info):
        """
        执行带记忆的动作
        
        流程：
        1. 检索角色相关记忆
        2. 使用记忆增强上下文
        3. 执行任务
        4. 存储新记忆
        """
        ***REMOVED*** 1. 检索相关记忆
        print(f"[{self.role}] 检索角色相关记忆...")
        memories = self.retrieve_character_memories(global_info)
        
        ***REMOVED*** 2. 增强上下文
        if memories:
            memory_context = self._format_memories(memories)
            ***REMOVED*** 将记忆添加到 system prompt 或 dialog history
            if hasattr(global_info, 'retrieved_memories'):
                global_info.retrieved_memories = memories
            print(f"[{self.role}] 使用 {len(memories)} 条记忆增强上下文")
        
        ***REMOVED*** 3. 执行任务（调用原始 Agent）
        action, terminated = self.base_agent.take_action(global_info)
        
        ***REMOVED*** 4. 存储创作结果
        if action and hasattr(action, 'answer') and action.answer:
            self.store_character_creation(
                content=action.answer,
                context={
                    "task_id": global_info.task.get("id"),
                    "path_id": global_info.path_id
                }
            )
        
        return action, terminated
    
    def retrieve_character_memories(self, global_info):
        """检索角色相关记忆"""
        try:
            recall_tool = global_tool_registry.get_tool("unimem_recall")
            if not recall_tool:
                return []
            
            ***REMOVED*** 构建查询（从任务中提取角色相关信息）
            task_text = global_info.task.get("Question", "") + " " + global_info.task.get("Introduction", "")
            query = f"角色 {task_text}"
            
            success, memories = recall_tool.execute(
                query=query,
                context={
                    "agent": "CharacterAgent",
                    "task_type": "character_creation"
                },
                top_k=5
            )
            
            return memories if success else []
        except Exception as e:
            print(f"⚠️ 角色记忆检索失败: {e}")
            return []
    
    def store_character_creation(self, content, context=None):
        """存储角色创作记忆"""
        try:
            retain_tool = global_tool_registry.get_tool("unimem_retain")
            if not retain_tool:
                return False
            
            ***REMOVED*** 提取角色信息（简单示例，实际应该从 content 中解析）
            experience = {
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "agent_role": "CharacterAgent",
                    "memory_type": "character_creation",
                    **(context or {})
                }
            }
            
            success, memory = retain_tool.execute(
                experience=experience,
                context={
                    "agent": "CharacterAgent",
                    "task_type": "character_creation",
                    **(context or {})
                }
            )
            
            if success:
                print(f"[{self.role}] ✓ 已存储角色创作记忆")
            
            return success
        except Exception as e:
            print(f"⚠️ 角色记忆存储失败: {e}")
            return False
    
    def _format_memories(self, memories):
        """格式化记忆"""
        if not memories:
            return ""
        
        formatted = ["相关角色记忆："]
        for i, mem in enumerate(memories, 1):
            content = mem.get("content", "") if isinstance(mem, dict) else getattr(mem, "content", "")
            formatted.append(f"{i}. {content}")
        
        return "\n".join(formatted)


***REMOVED*** 实际使用示例
if __name__ == "__main__":
    ***REMOVED*** 示例任务数据
    example_task = {
        "id": "novel_001",
        "introduction": "一个关于时间旅行的科幻小说",
        "outline": "..."
    }
    
    ***REMOVED*** 运行任务
    result = run_novel_task_with_unimem(example_task, unimem_enabled=True)
    print(f"\n最终结果:\n{result}")

