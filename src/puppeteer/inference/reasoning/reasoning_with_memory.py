"""
增强的 GraphReasoning，集成 UniMem 记忆系统

在原有 GraphReasoning 基础上，添加：
1. 任务开始时检索相关记忆
2. 将记忆注入到 GlobalInfo
3. 在推理完成后存储重要记忆
"""

import os
import json
import yaml
import copy
import logging
from typing import List
from datetime import datetime

from inference.reasoning.reasoning import GraphReasoning, ReasoningState, GraphReasoningPath
from inference.graph.agent_graph import AgentGraph
from inference.graph.action_graph import ActionGraph
from inference.policy.REINFORCE_continuous import ContinuousREINFORCE

from utils.logging import LogManager

from agent.register.register import agent_global_registry
from agent.agent_info.global_info import GlobalInfo

from tasks.evaluator import BenchmarkEvaluator

from tools.base.register import global_tool_registry
***REMOVED*** 确保 UniMem 工具被导入和注册
try:
    from tools.unimem_tool import UniMemRetainTool, UniMemRecallTool, UniMemReflectTool
    main_logger = logging.getLogger('global')
    main_logger.debug("UniMem 工具已导入并注册")
except ImportError as e:
    main_logger = logging.getLogger('global')
    main_logger.warning(f"无法导入 UniMem 工具: {e}")

global_config = yaml.safe_load(open("./config/global.yaml", "r"))


class GraphReasoningWithMemory(GraphReasoning):
    """
    集成 UniMem 的 GraphReasoning
    
    在原有功能基础上，增加记忆系统的集成：
    - 任务开始时检索相关记忆
    - 将记忆注入到 GlobalInfo，供 Agent 使用
    - 任务完成后存储重要创作内容到记忆
    """
    
    def __init__(self, task: json, graph: AgentGraph, env=None, env_name=None, unimem_enabled=True):
        """
        初始化
        
        Args:
            task: 任务数据
            graph: AgentGraph 实例
            env: 环境（可选）
            env_name: 环境名称（可选）
            unimem_enabled: 是否启用 UniMem（默认启用）
        """
        super().__init__(task, graph, env, env_name)
        self.unimem_enabled = unimem_enabled
        self.retrieved_memories = []  ***REMOVED*** 存储检索到的记忆
        self.stored_memories = []     ***REMOVED*** 存储已存储的记忆
        
        if self.unimem_enabled:
            self._ensure_unimem_tools()
    
    def _ensure_unimem_tools(self):
        """确保 UniMem 工具已注册"""
        try:
            recall_tool = global_tool_registry.get_tool("unimem_recall")
            retain_tool = global_tool_registry.get_tool("unimem_retain")
            
            if not recall_tool or not retain_tool:
                main_logger.warning("UniMem 工具未注册，记忆功能将不可用")
                self.unimem_enabled = False
            else:
                main_logger.info("UniMem 工具已就绪")
        except Exception as e:
            main_logger.warning(f"UniMem 工具检查失败: {e}，记忆功能将不可用")
            self.unimem_enabled = False
    
    def _retrieve_task_memories(self):
        """
        检索任务相关记忆
        
        Returns:
            记忆列表
        """
        if not self.unimem_enabled:
            return []
        
        try:
            recall_tool = global_tool_registry.get_tool("unimem_recall")
            if not recall_tool:
                return []
            
            ***REMOVED*** 构建查询
            query_parts = []
            if self.task.get("Introduction"):
                query_parts.append(self.task["Introduction"])
            if self.task.get("Question"):
                query_parts.append(self.task["Question"])
            query = " ".join(query_parts[:100])  ***REMOVED*** 限制查询长度
            
            ***REMOVED*** 检索记忆
            ***REMOVED*** Context 只接受 session_id, user_id, metadata
            success, memories = recall_tool.execute(
                query=query,
                context={
                    "session_id": f"task_{self.task.get('id', 'unknown')}",
                    "user_id": "creative_assistant",
                    "metadata": {
                        "task_type": self.task.get("type", "unknown"),
                        "task_id": str(self.task.get("id", "unknown"))
                    }
                },
                top_k=10
            )
            
            if success and memories:
                main_logger.info(f"检索到 {len(memories)} 条相关记忆")
                return memories
            else:
                main_logger.debug("未检索到相关记忆")
                return []
                
        except Exception as e:
            main_logger.warning(f"记忆检索失败: {e}")
            return []
    
    def _format_memories_for_prompt(self, memories):
        """
        格式化记忆为提示文本
        
        Args:
            memories: 记忆列表
            
        Returns:
            格式化后的文本
        """
        if not memories:
            return "暂无相关记忆。"
        
        formatted = ["【相关记忆】"]
        for i, mem in enumerate(memories[:5], 1):  ***REMOVED*** 只取前5条
            if isinstance(mem, dict):
                content = mem.get("content", "")
                metadata = mem.get("metadata", {})
                category = metadata.get("category", "其他")
            else:
                content = getattr(mem, "content", "")
                category = getattr(mem, "category", "其他")
            
            formatted.append(f"{i}. [{category}] {content[:100]}{'...' if len(content) > 100 else ''}")
        
        formatted.append("")
        return "\n".join(formatted)
    
    def start(self, save_data):
        """
        启动推理，集成记忆检索
        
        Args:
            save_data: 保存数据（用于checkpoint）
        """
        ***REMOVED*** 调用父类方法
        super().start(save_data)
        
        ***REMOVED*** 检索任务相关记忆
        if self.unimem_enabled:
            main_logger.info("检索任务相关记忆...")
            self.retrieved_memories = self._retrieve_task_memories()
            
            ***REMOVED*** 将记忆注入到所有路径的 GlobalInfo
            memory_context = self._format_memories_for_prompt(self.retrieved_memories)
            
            for path in self.reasoning_paths:
                ***REMOVED*** 将记忆添加到 global_info
                if not hasattr(path.global_info, 'retrieved_memories'):
                    path.global_info.retrieved_memories = []
                path.global_info.retrieved_memories = self.retrieved_memories
                path.global_info.memory_context = memory_context
                
                main_logger.debug(f"Path {path.index}: 已注入 {len(self.retrieved_memories)} 条记忆")
    
    def finalize(self):
        """
        完成推理，存储重要记忆
        
        Returns:
            最终答案
        """
        ***REMOVED*** 调用父类方法获取最终答案
        final_answer = super().finalize()
        
        ***REMOVED*** 存储重要创作内容到记忆
        if self.unimem_enabled and final_answer:
            self._store_final_result(final_answer)
        
        return final_answer
    
    def _store_final_result(self, final_answer):
        """
        存储最终结果到记忆系统
        
        Args:
            final_answer: 最终答案
        """
        try:
            retain_tool = global_tool_registry.get_tool("unimem_retain")
            if not retain_tool:
                return
            
            ***REMOVED*** 提取任务信息
            task_id = str(self.task.get("id", "unknown"))
            task_type = self.task.get("type", "unknown")
            introduction = self.task.get("Introduction", "")
            
            ***REMOVED*** 构建记忆内容
            memory_content = f"任务ID: {task_id}\n类型: {task_type}\n小说简介: {introduction[:200]}...\n\n最终大纲:\n{final_answer[:1000]}"
            
            ***REMOVED*** 存储记忆
            ***REMOVED*** Context 只接受 session_id, user_id, metadata
            success, memory = retain_tool.execute(
                experience={
                    "content": memory_content,
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {
                        "task_id": task_id,
                        "task_type": task_type,
                        "category": "final_outline"
                    }
                },
                context={
                    "session_id": f"task_{task_id}",
                    "user_id": "creative_assistant",
                    "metadata": {
                        "task_id": task_id,
                        "task_type": task_type,
                        "category": "final_outline"
                    }
                }
            )
            
            if success:
                main_logger.info(f"已存储最终结果到记忆系统 (任务ID: {task_id})")
                self.stored_memories.append(memory)
            else:
                main_logger.warning(f"存储最终结果失败: {memory}")
                
        except Exception as e:
            main_logger.warning(f"存储最终结果异常: {e}")

