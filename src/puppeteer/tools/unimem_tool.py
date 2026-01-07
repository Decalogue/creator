"""
UniMem 工具

提供三个工具用于调用 UniMem HTTP 服务：
- unimem_retain: 存储记忆
- unimem_recall: 检索记忆
- unimem_reflect: 优化记忆
"""

import os
import requests
import logging
from typing import Dict, Any, Optional
from tools.base.register import global_tool_registry
from tools.base.base_tool import Tool
from tenacity import retry, stop_after_attempt, wait_fixed

logger = logging.getLogger(__name__)


def get_unimem_api_url() -> str:
    """获取 UniMem API 基础URL"""
    return os.getenv("UNIMEM_API_URL", "http://localhost:9622")


@global_tool_registry("unimem_retain")
class UniMemRetainTool(Tool):
    """
    存储记忆到 UniMem 系统
    
    用法：
        retain_result, memory = tool.execute(
            experience={"content": "用户喜欢喝咖啡", ...},
            context={"session_id": "session_123", ...},
            operation_id="op_789"  ***REMOVED*** 可选
        )
    """
    
    def __init__(self, name):
        super().__init__(
            name=name,
            description="Store memory in UniMem system. Store new experiences as memories with context information.",
            execute_function=self.execute,
            timeout_duration=30  ***REMOVED*** 30秒超时
        )
        self.api_base_url = get_unimem_api_url()
    
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def execute(self, *args, **kwargs):
        """执行 retain 操作"""
        try:
            experience = kwargs.get("experience", {})
            context = kwargs.get("context", {})
            operation_id = kwargs.get("operation_id")
            
            if not experience or not isinstance(experience, dict):
                return False, "experience parameter is required and must be a dict"
            
            ***REMOVED*** 构建请求
            url = f"{self.api_base_url}/unimem/retain"
            payload = {
                "experience": experience,
            }
            if context:
                payload["context"] = context
            if operation_id:
                payload["operation_id"] = operation_id
            
            ***REMOVED*** 发送请求
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            ***REMOVED*** 检查响应
            if result.get("success"):
                memory = result.get("memory", {})
                return True, memory
            else:
                error_msg = result.get("error", "Unknown error")
                logger.error(f"UniMem retain failed: {error_msg}")
                return False, error_msg
                
        except requests.exceptions.RequestException as e:
            logger.error(f"UniMem retain request failed: {e}", exc_info=True)
            return False, f"Request failed: {str(e)}"
        except Exception as e:
            logger.error(f"UniMem retain failed: {e}", exc_info=True)
            return False, f"Unexpected error: {str(e)}"


@global_tool_registry("unimem_recall")
class UniMemRecallTool(Tool):
    """
    从 UniMem 系统检索记忆
    
    用法：
        recall_result, results = tool.execute(
            query="用户喜欢什么饮料",
            context={"session_id": "session_123", ...},  ***REMOVED*** 可选
            memory_type="episodic",  ***REMOVED*** 可选：episodic/semantic/world/experience/observation/opinion
            top_k=10  ***REMOVED*** 可选，默认10
        )
    """
    
    def __init__(self, name):
        super().__init__(
            name=name,
            description="Recall memories from UniMem system. Search and retrieve relevant memories based on query.",
            execute_function=self.execute,
            timeout_duration=30  ***REMOVED*** 30秒超时
        )
        self.api_base_url = get_unimem_api_url()
    
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def execute(self, *args, **kwargs):
        """执行 recall 操作"""
        try:
            query = kwargs.get("query", "")
            context = kwargs.get("context", {})
            memory_type = kwargs.get("memory_type")
            top_k = kwargs.get("top_k", 10)
            
            if not query:
                return False, "query parameter is required"
            
            ***REMOVED*** 构建请求
            url = f"{self.api_base_url}/unimem/recall"
            payload = {
                "query": query,
                "top_k": top_k,
            }
            if context:
                payload["context"] = context
            if memory_type:
                payload["memory_type"] = memory_type
            
            ***REMOVED*** 发送请求
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            ***REMOVED*** 检查响应
            if result.get("success"):
                results = result.get("results", [])
                return True, results
            else:
                error_msg = result.get("error", "Unknown error")
                logger.error(f"UniMem recall failed: {error_msg}")
                return False, error_msg
                
        except requests.exceptions.RequestException as e:
            logger.error(f"UniMem recall request failed: {e}", exc_info=True)
            return False, f"Request failed: {str(e)}"
        except Exception as e:
            logger.error(f"UniMem recall failed: {e}", exc_info=True)
            return False, f"Unexpected error: {str(e)}"


@global_tool_registry("unimem_reflect")
class UniMemReflectTool(Tool):
    """
    优化 UniMem 系统中的记忆
    
    用法：
        reflect_result, updated_memories = tool.execute(
            memories=[{"id": "mem_001", "content": "...", ...}, ...],
            task={"id": "task_001", "description": "...", "context": "...", ...},
            context={"session_id": "session_123", ...}  ***REMOVED*** 可选
        )
    """
    
    def __init__(self, name):
        super().__init__(
            name=name,
            description="Reflect and optimize memories in UniMem system. Update and improve memories based on task context.",
            execute_function=self.execute,
            timeout_duration=60  ***REMOVED*** 60秒超时（reflect操作可能较慢）
        )
        self.api_base_url = get_unimem_api_url()
    
    @retry(stop=stop_after_attempt(2), wait=wait_fixed(2))  ***REMOVED*** reflect操作减少重试次数
    def execute(self, *args, **kwargs):
        """执行 reflect 操作"""
        try:
            memories = kwargs.get("memories", [])
            task = kwargs.get("task", {})
            context = kwargs.get("context", {})
            
            if not memories or not isinstance(memories, list):
                return False, "memories parameter is required and must be a list"
            if not task or not isinstance(task, dict):
                return False, "task parameter is required and must be a dict"
            
            ***REMOVED*** 构建请求
            url = f"{self.api_base_url}/unimem/reflect"
            payload = {
                "memories": memories,
                "task": task,
            }
            if context:
                payload["context"] = context
            
            ***REMOVED*** 发送请求
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            ***REMOVED*** 检查响应
            if result.get("success"):
                updated_memories = result.get("updated_memories", [])
                return True, updated_memories
            else:
                error_msg = result.get("error", "Unknown error")
                logger.error(f"UniMem reflect failed: {error_msg}")
                return False, error_msg
                
        except requests.exceptions.RequestException as e:
            logger.error(f"UniMem reflect request failed: {e}", exc_info=True)
            return False, f"Request failed: {str(e)}"
        except Exception as e:
            logger.error(f"UniMem reflect failed: {e}", exc_info=True)
            return False, f"Unexpected error: {str(e)}"


@global_tool_registry("unimem_update")
class UniMemUpdateTool(Tool):
    """
    更新 UniMem 系统中的记忆
    
    参考 AgeMem 的 Update 工具：更新已有记忆
    
    用法：
        update_result, updated_memory = tool.execute(
            memory_id="mem_001",
            new_content="更新后的内容",
            context={"session_id": "session_123", ...}  ***REMOVED*** 可选
        )
    """
    
    def __init__(self, name):
        super().__init__(
            name=name,
            description="Update existing memory in UniMem system. Update the content of a stored memory when information changes or is corrected.",
            execute_function=self.execute,
            timeout_duration=30
        )
        self.api_base_url = get_unimem_api_url()
    
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def execute(self, *args, **kwargs):
        """执行 update 操作"""
        try:
            memory_id = kwargs.get("memory_id", "")
            new_content = kwargs.get("new_content", "")
            context = kwargs.get("context", {})
            
            if not memory_id:
                return False, "memory_id parameter is required"
            if not new_content:
                return False, "new_content parameter is required"
            
            ***REMOVED*** 构建请求
            url = f"{self.api_base_url}/unimem/update"
            payload = {
                "memory_id": memory_id,
                "new_content": new_content,
            }
            if context:
                payload["context"] = context
            
            ***REMOVED*** 发送请求
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            ***REMOVED*** 检查响应
            if result.get("success"):
                updated_memory = result.get("memory", {})
                return True, updated_memory
            else:
                error_msg = result.get("error", "Unknown error")
                logger.error(f"UniMem update failed: {error_msg}")
                return False, error_msg
                
        except requests.exceptions.RequestException as e:
            logger.error(f"UniMem update request failed: {e}", exc_info=True)
            return False, f"Request failed: {str(e)}"
        except Exception as e:
            logger.error(f"UniMem update failed: {e}", exc_info=True)
            return False, f"Unexpected error: {str(e)}"


@global_tool_registry("unimem_delete")
class UniMemDeleteTool(Tool):
    """
    从 UniMem 系统中删除记忆
    
    参考 AgeMem 的 Delete 工具：删除过时的记忆
    
    用法：
        delete_result, success = tool.execute(
            memory_id="mem_001",
            context={"session_id": "session_123", ...}  ***REMOVED*** 可选
        )
    """
    
    def __init__(self, name):
        super().__init__(
            name=name,
            description="Delete memory from UniMem system. Remove outdated or incorrect memories that are no longer needed.",
            execute_function=self.execute,
            timeout_duration=30
        )
        self.api_base_url = get_unimem_api_url()
    
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def execute(self, *args, **kwargs):
        """执行 delete 操作"""
        try:
            memory_id = kwargs.get("memory_id", "")
            context = kwargs.get("context", {})
            
            if not memory_id:
                return False, "memory_id parameter is required"
            
            ***REMOVED*** 构建请求
            url = f"{self.api_base_url}/unimem/delete"
            payload = {
                "memory_id": memory_id,
            }
            if context:
                payload["context"] = context
            
            ***REMOVED*** 发送请求
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            ***REMOVED*** 检查响应
            if result.get("success"):
                return True, "Memory deleted successfully"
            else:
                error_msg = result.get("error", "Unknown error")
                logger.error(f"UniMem delete failed: {error_msg}")
                return False, error_msg
                
        except requests.exceptions.RequestException as e:
            logger.error(f"UniMem delete request failed: {e}", exc_info=True)
            return False, f"Request failed: {str(e)}"
        except Exception as e:
            logger.error(f"UniMem delete failed: {e}", exc_info=True)
            return False, f"Unexpected error: {str(e)}"


@global_tool_registry("unimem_summary")
class UniMemSummaryTool(Tool):
    """
    总结压缩当前上下文（STM管理）
    
    参考 AgeMem 的 Summary 工具：总结要点，节省空间
    
    用法：
        summary_result, summary_text = tool.execute(
            context={"dialog_history": [...], ...},
            max_tokens=1000,  ***REMOVED*** 可选
            preserve_key_info=True  ***REMOVED*** 可选
        )
    """
    
    def __init__(self, name):
        super().__init__(
            name=name,
            description="Summarize and compress current context to save space. Extract key points from conversation history while preserving important information.",
            execute_function=self.execute,
            timeout_duration=60  ***REMOVED*** 总结可能较慢
        )
        self.api_base_url = get_unimem_api_url()
    
    @retry(stop=stop_after_attempt(2), wait=wait_fixed(2))
    def execute(self, *args, **kwargs):
        """执行 summary 操作"""
        try:
            context = kwargs.get("context", {})
            max_tokens = kwargs.get("max_tokens", 1000)
            preserve_key_info = kwargs.get("preserve_key_info", True)
            
            if not context:
                return False, "context parameter is required"
            
            ***REMOVED*** 构建请求
            url = f"{self.api_base_url}/unimem/summary"
            payload = {
                "context": context,
                "max_tokens": max_tokens,
                "preserve_key_info": preserve_key_info,
            }
            
            ***REMOVED*** 发送请求
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            ***REMOVED*** 检查响应
            if result.get("success"):
                summary_text = result.get("summary", "")
                return True, summary_text
            else:
                error_msg = result.get("error", "Unknown error")
                logger.error(f"UniMem summary failed: {error_msg}")
                return False, error_msg
                
        except requests.exceptions.RequestException as e:
            logger.error(f"UniMem summary request failed: {e}", exc_info=True)
            return False, f"Request failed: {str(e)}"
        except Exception as e:
            logger.error(f"UniMem summary failed: {e}", exc_info=True)
            return False, f"Unexpected error: {str(e)}"


@global_tool_registry("unimem_filter")
class UniMemFilterTool(Tool):
    """
    过滤掉无用的对话内容（STM管理）
    
    参考 AgeMem 的 Filter 工具：过滤废话
    
    用法：
        filter_result, filtered_context = tool.execute(
            context={"dialog_history": [...], ...},
            filter_criteria="irrelevant",  ***REMOVED*** 可选：irrelevant/redundant/noise
            preserve_recent=3  ***REMOVED*** 可选：保留最近N条消息
        )
    """
    
    def __init__(self, name):
        super().__init__(
            name=name,
            description="Filter out irrelevant or redundant content from conversation history. Remove noise while preserving recent and important messages.",
            execute_function=self.execute,
            timeout_duration=30
        )
        self.api_base_url = get_unimem_api_url()
    
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def execute(self, *args, **kwargs):
        """执行 filter 操作"""
        try:
            context = kwargs.get("context", {})
            filter_criteria = kwargs.get("filter_criteria", "irrelevant")
            preserve_recent = kwargs.get("preserve_recent", 3)
            
            if not context:
                return False, "context parameter is required"
            
            ***REMOVED*** 构建请求
            url = f"{self.api_base_url}/unimem/filter"
            payload = {
                "context": context,
                "filter_criteria": filter_criteria,
                "preserve_recent": preserve_recent,
            }
            
            ***REMOVED*** 发送请求
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            ***REMOVED*** 检查响应
            if result.get("success"):
                filtered_context = result.get("context", {})
                return True, filtered_context
            else:
                error_msg = result.get("error", "Unknown error")
                logger.error(f"UniMem filter failed: {error_msg}")
                return False, error_msg
                
        except requests.exceptions.RequestException as e:
            logger.error(f"UniMem filter request failed: {e}", exc_info=True)
            return False, f"Request failed: {str(e)}"
        except Exception as e:
            logger.error(f"UniMem filter failed: {e}", exc_info=True)
            return False, f"Unexpected error: {str(e)}"

