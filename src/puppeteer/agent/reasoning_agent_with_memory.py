"""
增强的 Reasoning_Agent，集成 UniMem 记忆系统

在原有 Reasoning_Agent 基础上，添加：
1. 在 system_prompt 中注入记忆上下文
2. 支持 Agent 主动调用 UniMem 工具
3. 在推理完成后自动存储重要内容
"""

import os
import re
import json
import yaml
from copy import deepcopy
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential

from tools.base.register import global_tool_registry
from tools.web_search import Web_Search
from tools.code_interpreter import CodeInterpreter
from tools.file_read import FileRead

from agent.reasoning_agent import Reasoning_Agent
from agent.agent_info.global_info import GlobalInfo
from agent.agent_info.workflow import Action
from agent.agent_info.actions import REASONING_ACTION_LIST, TOOL_ACTION_LIST, TERMINATION_ACTION_LIST

from utils.file_utils import format_code_with_prints, extract_code_from_text, write_code, write_text, read_code

global_config = yaml.safe_load(open("./config/global.yaml", "r"))


class Reasoning_Agent_With_Memory(Reasoning_Agent):
    """
    集成 UniMem 的 Reasoning_Agent
    
    特点：
    - 在 system_prompt 中自动注入记忆上下文
    - 支持调用 UniMem 工具（unimem_recall, unimem_retain）
    - 在推理完成后自动存储重要创作内容
    """
    
    def __init__(self, role, role_prompt, index, model="gpt", actions=[], policy=None, global_info=None, initial_dialog_history=None, unimem_enabled=True):
        """
        初始化
        
        Args:
            unimem_enabled: 是否启用 UniMem（默认启用）
        """
        super().__init__(role, role_prompt, index, model, actions, policy, global_info, initial_dialog_history)
        self.unimem_enabled = unimem_enabled
        
        if self.unimem_enabled:
            self._ensure_unimem_tools()
    
    def _ensure_unimem_tools(self):
        """确保 UniMem 工具已注册"""
        try:
            recall_tool = global_tool_registry.get_tool("unimem_recall")
            retain_tool = global_tool_registry.get_tool("unimem_retain")
            
            if not recall_tool or not retain_tool:
                self.unimem_enabled = False
        except Exception:
            self.unimem_enabled = False
    
    def activate(self, global_info: GlobalInfo, initial_dialog_history=None):
        """
        激活 Agent，注入记忆上下文
        
        Args:
            global_info: 全局信息（可能包含记忆）
            initial_dialog_history: 初始对话历史
        """
        ***REMOVED*** 调用父类方法
        super().activate(global_info, initial_dialog_history)
        
        ***REMOVED*** 注入记忆上下文到 system_prompt
        if self.unimem_enabled and hasattr(global_info, 'memory_context'):
            memory_context = global_info.memory_context or "暂无相关记忆。"
            
            ***REMOVED*** 检查是否已经包含记忆上下文（避免重复注入）
            if "【记忆上下文】" not in self.system_prompt:
                ***REMOVED*** 替换 system_prompt 中的记忆上下文占位符
                ***REMOVED*** 使用带记忆的 system_prompt 模板
                prompt_filepath = "prompts/general/system_prompt_with_memory.json"
                if os.path.exists(prompt_filepath):
                    with open(prompt_filepath, "r", encoding="utf-8") as f:
                        system_prompt_template = json.load(f)
                    
                    ***REMOVED*** 格式化 system_prompt
                    memory_formatted = memory_context
                    system_step_data = [self._compress_data(d) for d in global_info.workflow.valid_tool_results]
                    
                    ***REMOVED*** 使用 replace() 方法逐个替换占位符，避免 JSON 示例中的花括号问题
                    system_prompt_str = "\n".join(system_prompt_template['system_prompt'])
                    
                    ***REMOVED*** 按照顺序替换4个占位符 {}
                    ***REMOVED*** 注意：必须按顺序替换，因为后面的占位符可能在内容中出现
                    replacements = [
                        self.role_prompt,
                        str(global_info.task.get("Question", "")),
                        str(system_step_data),
                        memory_formatted
                    ]
                    
                    for value in replacements:
                        ***REMOVED*** 查找第一个 {} 并替换
                        idx = system_prompt_str.find("{}")
                        if idx != -1:
                            system_prompt_str = system_prompt_str[:idx] + value + system_prompt_str[idx+2:]
                        else:
                            ***REMOVED*** 如果没有找到占位符，说明已经全部替换完成或模板有问题
                            main_logger.warning(f"未找到占位符，可能模板格式不正确")
                            break
                    
                    self.system_prompt = system_prompt_str
                    
                    ***REMOVED*** 更新 dialog_history
                    if self.dialog_history and len(self.dialog_history) > 0:
                        self.dialog_history[0] = {"role": "system", "content": self.system_prompt}
    
    def _tool_operation(self, action, global_info):
        """
        执行工具操作，支持 UniMem 工具
        
        Args:
            action: 动作信息
            global_info: 全局信息
            
        Returns:
            (flag, step_data) 元组
        """
        name = action.get("action")
        parameter = action.get("parameter", "")
        
        ***REMOVED*** 处理 UniMem 工具
        if name == "unimem_recall":
            return self._handle_unimem_recall(parameter, global_info)
        elif name == "unimem_retain":
            return self._handle_unimem_retain(parameter, global_info)
        elif name == "unimem_update":
            return self._handle_unimem_update(parameter, global_info)
        elif name == "unimem_delete":
            return self._handle_unimem_delete(parameter, global_info)
        elif name == "unimem_summary":
            return self._handle_unimem_summary(parameter, global_info)
        elif name == "unimem_filter":
            return self._handle_unimem_filter(parameter, global_info)
        
        ***REMOVED*** 其他工具调用父类方法
        ***REMOVED*** 注意：需要检查是否有带记忆的工具提示词文件
        return super()._tool_operation(action, global_info)
    
    def _handle_unimem_recall(self, parameter, global_info):
        """
        处理 UniMem 检索操作
        
        Args:
            parameter: 查询参数
            global_info: 全局信息
            
        Returns:
            (flag, step_data) 元组
        """
        try:
            recall_tool = global_tool_registry.get_tool("unimem_recall")
            if not recall_tool:
                return False, "UniMem recall 工具未注册"
            
            ***REMOVED*** 执行检索
            ***REMOVED*** Context 只接受 session_id, user_id, metadata
            success, memories = recall_tool.execute(
                query=parameter,
                context={
                    "session_id": f"task_{global_info.task.get('id', 'unknown')}",
                    "user_id": "creative_assistant",
                    "metadata": {
                        "agent": self.role,
                        "task_id": str(global_info.task.get("id", "unknown")),
                        "task_type": global_info.task.get("type", "unknown")
                    }
                },
                top_k=5
            )
            
            if success:
                if memories:
                    ***REMOVED*** 格式化记忆结果
                    formatted_memories = []
                    for mem in memories:
                        if isinstance(mem, dict):
                            content = mem.get("content", "")
                            metadata = mem.get("metadata", {})
                            category = metadata.get("category", "其他")
                        else:
                            content = getattr(mem, "content", "")
                            category = "其他"
                        
                        formatted_memories.append(f"[{category}] {content}")
                    
                    result_text = f"检索到 {len(memories)} 条相关记忆：\n\n" + "\n\n".join(formatted_memories)
                else:
                    result_text = "未检索到相关记忆。"
                
                global_info.logger.info(f"[UniMem Recall] 查询: {parameter}\n结果: {len(memories) if memories else 0} 条记忆")
                return True, result_text
            else:
                global_info.logger.warning(f"[UniMem Recall] 检索失败: {memories}")
                return False, f"检索失败: {memories}"
                
        except Exception as e:
            global_info.logger.error(f"[UniMem Recall] 异常: {e}", exc_info=True)
            return False, f"检索异常: {str(e)}"
    
    def _handle_unimem_retain(self, parameter, global_info):
        """
        处理 UniMem 存储操作
        
        Args:
            parameter: 存储参数（JSON字符串）
            global_info: 全局信息
            
        Returns:
            (flag, step_data) 元组
        """
        try:
            retain_tool = global_tool_registry.get_tool("unimem_retain")
            if not retain_tool:
                return False, "UniMem retain 工具未注册"
            
            ***REMOVED*** 解析参数
            try:
                param_dict = json.loads(parameter) if isinstance(parameter, str) else parameter
                content = param_dict.get("content", "")
                context = param_dict.get("context", {})
            except json.JSONDecodeError:
                ***REMOVED*** 如果参数不是 JSON，直接作为内容
                content = parameter
                context = {}
            
            if not content:
                return False, "存储内容不能为空"
            
            ***REMOVED*** 添加默认上下文
            context.setdefault("agent", self.role)
            context.setdefault("task_id", str(global_info.task.get("id", "unknown")))
            context.setdefault("task_type", global_info.task.get("type", "unknown"))
            
            ***REMOVED*** 执行存储
            success, memory = retain_tool.execute(
                experience={
                    "content": content,
                    "timestamp": datetime.now().isoformat(),
                    "metadata": context
                },
                context=context
            )
            
            if success:
                memory_id = memory.get("id", "unknown") if isinstance(memory, dict) else getattr(memory, "id", "unknown")
                global_info.logger.info(f"[UniMem Retain] 已存储记忆: {memory_id[:20]}...")
                return True, f"已成功存储记忆: {content[:100]}{'...' if len(content) > 100 else ''}"
            else:
                global_info.logger.warning(f"[UniMem Retain] 存储失败: {memory}")
                return False, f"存储失败: {memory}"
                
        except Exception as e:
            global_info.logger.error(f"[UniMem Retain] 异常: {e}", exc_info=True)
            return False, f"存储异常: {str(e)}"
    
    def _reasoning_operation(self, action, global_info) -> str:
        """
        执行推理操作，使用带记忆的提示词
        
        Args:
            action: 动作信息
            global_info: 全局信息
            
        Returns:
            推理结果
        """
        ***REMOVED*** 使用带记忆的提示词文件（如果存在）
        prompt_filepath = "prompts/general/actions_reasoning_with_memory.jsonl"
        if not os.path.exists(prompt_filepath):
            ***REMOVED*** 如果不存在，使用原来的文件
            prompt_filepath = "prompts/general/actions_reasoning.jsonl"
        
        code_generated_type = True if global_info.task.get("req") == "code" else False
        text_generated_type = True if global_info.task.get("req") == "text" else False
        prompt = ""
        
        with open(prompt_filepath, "r", encoding="utf-8") as f:
            for line in f:
                json_obj = json.loads(line)
                if json_obj.get("action") == action.get("action"):
                    prompt = json_obj.get("prompt")
                    break
        
        ***REMOVED*** 使用 replace() 方法替换占位符，避免 JSON 示例中的花括号问题
        if code_generated_type or text_generated_type:
            previous_content = read_code(global_info.code_path)
        else:
            previous_content = global_info.workflow.valid_reasoning_results
        
        ***REMOVED*** 查找并替换占位符 *你之前的推理是：{}*
        placeholder_pattern = "*你之前的推理是：{}*"
        if placeholder_pattern in prompt:
            query_prompt = prompt.replace(placeholder_pattern, f"*你之前的推理是：{previous_content}*")
        else:
            ***REMOVED*** 如果没有找到完整占位符，尝试只替换 {}
            query_prompt = prompt.replace("{}", str(previous_content), 1)  ***REMOVED*** 只替换第一个 {}
        
        global_info.logger.info(f"[System Prompt] {self.system_prompt}\n[Query] {query_prompt}\n")
        
        raw_response, total_tokens = self._query(query_prompt)
        global_info.logger.info(f"[Reasoning]: {raw_response}")
        
        if code_generated_type:
            answer = extract_code_from_text(raw_response)
        else:
            ***REMOVED*** 对于文本类型或其他类型，直接使用原始响应
            answer = raw_response
        
        return answer, total_tokens
    
    def _handle_unimem_update(self, parameter, global_info):
        """处理 UniMem 更新操作"""
        try:
            update_tool = global_tool_registry.get_tool("unimem_update")
            if not update_tool:
                return False, "UniMem update 工具未注册"
            
            ***REMOVED*** 解析参数
            try:
                param_dict = json.loads(parameter) if isinstance(parameter, str) else parameter
                memory_id = param_dict.get("memory_id", "")
                new_content = param_dict.get("new_content", "")
                context = param_dict.get("context", {})
            except json.JSONDecodeError:
                return False, "参数格式错误，应为JSON格式：{\"memory_id\": \"...\", \"new_content\": \"...\"}"
            
            if not memory_id or not new_content:
                return False, "memory_id 和 new_content 不能为空"
            
            ***REMOVED*** 添加默认上下文
            context.setdefault("agent", self.role)
            context.setdefault("task_id", str(global_info.task.get("id", "unknown")))
            
            ***REMOVED*** 执行更新
            success, memory = update_tool.execute(
                memory_id=memory_id,
                new_content=new_content,
                context={
                    "session_id": f"task_{global_info.task.get('id', 'unknown')}",
                    "user_id": "creative_assistant",
                    "metadata": context
                }
            )
            
            if success:
                global_info.logger.info(f"[UniMem Update] 记忆 {memory_id} 更新成功")
                return True, f"记忆 {memory_id} 已更新"
            else:
                global_info.logger.warning(f"[UniMem Update] 更新失败: {memory}")
                return False, f"更新失败: {memory}"
                
        except Exception as e:
            global_info.logger.error(f"[UniMem Update] 异常: {e}", exc_info=True)
            return False, f"更新异常: {str(e)}"
    
    def _handle_unimem_delete(self, parameter, global_info):
        """处理 UniMem 删除操作"""
        try:
            delete_tool = global_tool_registry.get_tool("unimem_delete")
            if not delete_tool:
                return False, "UniMem delete 工具未注册"
            
            ***REMOVED*** 解析参数
            try:
                param_dict = json.loads(parameter) if isinstance(parameter, str) else parameter
                memory_id = param_dict.get("memory_id", "")
                context = param_dict.get("context", {})
            except json.JSONDecodeError:
                ***REMOVED*** 如果不是JSON，直接作为memory_id
                memory_id = parameter
                context = {}
            
            if not memory_id:
                return False, "memory_id 不能为空"
            
            ***REMOVED*** 添加默认上下文
            context.setdefault("agent", self.role)
            context.setdefault("task_id", str(global_info.task.get("id", "unknown")))
            
            ***REMOVED*** 执行删除
            success, result = delete_tool.execute(
                memory_id=memory_id,
                context={
                    "session_id": f"task_{global_info.task.get('id', 'unknown')}",
                    "user_id": "creative_assistant",
                    "metadata": context
                }
            )
            
            if success:
                global_info.logger.info(f"[UniMem Delete] 记忆 {memory_id} 删除成功")
                return True, f"记忆 {memory_id} 已删除"
            else:
                global_info.logger.warning(f"[UniMem Delete] 删除失败: {result}")
                return False, f"删除失败: {result}"
                
        except Exception as e:
            global_info.logger.error(f"[UniMem Delete] 异常: {e}", exc_info=True)
            return False, f"删除异常: {str(e)}"
    
    def _handle_unimem_summary(self, parameter, global_info):
        """处理 UniMem 总结操作（STM管理）"""
        try:
            summary_tool = global_tool_registry.get_tool("unimem_summary")
            if not summary_tool:
                return False, "UniMem summary 工具未注册"
            
            ***REMOVED*** 解析参数
            try:
                param_dict = json.loads(parameter) if isinstance(parameter, str) else parameter
                context = param_dict.get("context", {})
                max_tokens = param_dict.get("max_tokens", 1000)
                preserve_key_info = param_dict.get("preserve_key_info", True)
            except json.JSONDecodeError:
                ***REMOVED*** 如果没有context，使用当前对话历史
                context = {
                    "dialog_history": getattr(global_info, "dialog_history", [])
                }
                max_tokens = 1000
                preserve_key_info = True
            
            ***REMOVED*** 如果没有dialog_history，尝试从global_info获取
            if "dialog_history" not in context and hasattr(global_info, "dialog_history"):
                context["dialog_history"] = global_info.dialog_history
            
            ***REMOVED*** 执行总结
            success, summary = summary_tool.execute(
                context=context,
                max_tokens=max_tokens,
                preserve_key_info=preserve_key_info
            )
            
            if success:
                global_info.logger.info(f"[UniMem Summary] 上下文已总结，长度: {len(summary)} 字符")
                return True, f"上下文总结完成：\n\n{summary}"
            else:
                global_info.logger.warning(f"[UniMem Summary] 总结失败: {summary}")
                return False, f"总结失败: {summary}"
                
        except Exception as e:
            global_info.logger.error(f"[UniMem Summary] 异常: {e}", exc_info=True)
            return False, f"总结异常: {str(e)}"
    
    def _handle_unimem_filter(self, parameter, global_info):
        """处理 UniMem 过滤操作（STM管理）"""
        try:
            filter_tool = global_tool_registry.get_tool("unimem_filter")
            if not filter_tool:
                return False, "UniMem filter 工具未注册"
            
            ***REMOVED*** 解析参数
            try:
                param_dict = json.loads(parameter) if isinstance(parameter, str) else parameter
                context = param_dict.get("context", {})
                filter_criteria = param_dict.get("filter_criteria", "irrelevant")
                preserve_recent = param_dict.get("preserve_recent", 3)
            except json.JSONDecodeError:
                ***REMOVED*** 如果没有context，使用当前对话历史
                context = {
                    "dialog_history": getattr(global_info, "dialog_history", [])
                }
                filter_criteria = "irrelevant"
                preserve_recent = 3
            
            ***REMOVED*** 如果没有dialog_history，尝试从global_info获取
            if "dialog_history" not in context and hasattr(global_info, "dialog_history"):
                context["dialog_history"] = global_info.dialog_history
            
            ***REMOVED*** 执行过滤
            success, filtered_context = filter_tool.execute(
                context=context,
                filter_criteria=filter_criteria,
                preserve_recent=preserve_recent
            )
            
            if success:
                original_count = len(context.get("dialog_history", []))
                filtered_count = len(filtered_context.get("dialog_history", []))
                global_info.logger.info(f"[UniMem Filter] 上下文已过滤：{original_count} -> {filtered_count} 条消息")
                return True, f"上下文已过滤：{original_count} -> {filtered_count} 条消息"
            else:
                global_info.logger.warning(f"[UniMem Filter] 过滤失败: {filtered_context}")
                return False, f"过滤失败: {filtered_context}"
                
        except Exception as e:
            global_info.logger.error(f"[UniMem Filter] 异常: {e}", exc_info=True)
            return False, f"过滤异常: {str(e)}"

