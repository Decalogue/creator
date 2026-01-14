"""
Multi-Agent 协作系统
基于 ReAct 的 Multi-Agent 编排

实现两种协作模式：
1. 任务委托（Task Delegation）- 通过通信实现隔离
2. 信息同步（Information Synchronization）- 通过共享上下文实现协作
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Callable
from datetime import datetime
from enum import Enum
import logging

try:
    from react import ReActAgent
except ImportError:
    ***REMOVED*** 如果 react 模块不可用，定义占位类
    class ReActAgent:
        def __init__(self, *args, **kwargs):
            pass
        def run(self, *args, **kwargs):
            return "ReActAgent not available"

from agent.context_manager import get_context_manager
from agent.layered_action_space import get_layered_action_space

logger = logging.getLogger(__name__)


class CollaborationMode(Enum):
    """协作模式"""
    TASK_DELEGATION = "TASK_DELEGATION"  ***REMOVED*** 任务委托
    INFO_SYNC = "INFO_SYNC"  ***REMOVED*** 信息同步


class SubAgent:
    """
    Sub-Agent（子代理）
    
    由 Master Agent 创建，执行特定任务
    """
    
    def __init__(
        self,
        agent_id: str,
        task_description: str,
        output_schema: Optional[Dict[str, Any]] = None,
        shared_context: Optional[List[Dict[str, Any]]] = None,
        sandbox_dir: Optional[Path] = None,
        mode: CollaborationMode = CollaborationMode.TASK_DELEGATION
    ):
        """
        初始化 Sub-Agent
        
        Args:
            agent_id: Agent 唯一标识
            task_description: 任务描述
            output_schema: 输出 Schema（用于任务委托模式）
            shared_context: 共享上下文（用于信息同步模式）
            sandbox_dir: 沙箱目录（共享沙箱）
            mode: 协作模式
        """
        self.agent_id = agent_id
        self.task_description = task_description
        self.output_schema = output_schema
        self.shared_context = shared_context or []
        self.sandbox_dir = sandbox_dir
        self.mode = mode
        
        ***REMOVED*** 创建独立的 ReActAgent
        self.agent = ReActAgent(
            max_iterations=10,
            enable_context_offloading=True
        )
        
        ***REMOVED*** 设置共享沙箱
        if sandbox_dir:
            self.agent.layered_action_space = get_layered_action_space(sandbox_dir)
        
        ***REMOVED*** 构建系统提示词
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        if self.mode == CollaborationMode.TASK_DELEGATION:
            ***REMOVED*** 任务委托模式：简短指令，独立上下文
            prompt = f"""你是一个 Sub-Agent，负责执行以下任务：

任务描述：
{self.task_description}

"""
            if self.output_schema:
                prompt += f"""
输出要求：
你必须按照以下 Schema 返回结果：
{json.dumps(self.output_schema, ensure_ascii=False, indent=2)}

使用 `submit_result` 工具提交结果，确保结果严格符合 Schema。
"""
        else:
            ***REMOVED*** 信息同步模式：完整历史上下文
            prompt = f"""你是一个 Sub-Agent，负责执行以下任务：

任务描述：
{self.task_description}

你拥有 Master Agent 的完整历史上下文，可以基于这些信息进行综合分析。
"""
        
        prompt += """
你可以使用所有可用的工具来完成任务。
完成后，使用 `submit_result` 工具提交结果。
"""
        
        return prompt
    
    def run(self, verbose: bool = False) -> Tuple[bool, Any]:
        """
        运行 Sub-Agent
        
        Args:
            verbose: 是否打印详细过程
        
        Returns:
            (是否成功, 结果)
        """
        ***REMOVED*** 构建初始消息
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        ***REMOVED*** 如果是信息同步模式，添加共享上下文
        if self.mode == CollaborationMode.INFO_SYNC and self.shared_context:
            messages.append({
                "role": "user",
                "content": f"以下是 Master Agent 的完整历史上下文：\n{json.dumps(self.shared_context, ensure_ascii=False, indent=2)}"
            })
        
        ***REMOVED*** 添加任务描述
        messages.append({
            "role": "user",
            "content": f"请执行任务：{self.task_description}"
        })
        
        ***REMOVED*** 运行 Agent
        try:
            result = self.agent.run(
                query=f"执行任务：{self.task_description}",
                verbose=verbose
            )
            
            ***REMOVED*** 验证输出 Schema（如果指定）
            if self.output_schema and self.mode == CollaborationMode.TASK_DELEGATION:
                ***REMOVED*** 尝试解析结果
                try:
                    parsed_result = json.loads(result) if isinstance(result, str) else result
                    ***REMOVED*** 简单验证：检查是否包含必需的字段
                    if isinstance(parsed_result, dict) and isinstance(self.output_schema, dict):
                        required_fields = self.output_schema.get("required", [])
                        for field in required_fields:
                            if field not in parsed_result:
                                logger.warning(f"结果缺少必需字段: {field}")
                                return False, f"结果不符合 Schema：缺少字段 {field}"
                except json.JSONDecodeError:
                    logger.warning("结果不是有效的 JSON")
            
            return True, result
        except Exception as e:
            logger.error(f"Sub-Agent 执行失败: {e}")
            return False, str(e)


class MasterAgent:
    """
    Master Agent（主代理）
    
    负责创建和管理 Sub-Agent，协调多 Agent 协作
    """
    
    def __init__(
        self,
        master_id: str = "master",
        sandbox_dir: Optional[Path] = None
    ):
        """
        初始化 Master Agent
        
        Args:
            master_id: Master Agent 标识
            sandbox_dir: 共享沙箱目录
        """
        self.master_id = master_id
        self.sandbox_dir = sandbox_dir or Path("agent/sandbox")
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
        
        ***REMOVED*** 创建 Master Agent 的 ReActAgent
        self.agent = ReActAgent(
            max_iterations=10,
            enable_context_offloading=True
        )
        
        ***REMOVED*** 设置共享沙箱
        self.agent.layered_action_space = get_layered_action_space(self.sandbox_dir)
        
        ***REMOVED*** Sub-Agent 列表
        self.sub_agents: Dict[str, SubAgent] = {}
        
        ***REMOVED*** 对话历史（用于信息同步）
        self.conversation_history: List[Dict[str, Any]] = []
    
    def create_sub_agent(
        self,
        task_description: str,
        output_schema: Optional[Dict[str, Any]] = None,
        mode: CollaborationMode = CollaborationMode.TASK_DELEGATION,
        agent_id: Optional[str] = None
    ) -> SubAgent:
        """
        创建 Sub-Agent
        
        Args:
            task_description: 任务描述
            output_schema: 输出 Schema（用于任务委托模式）
            mode: 协作模式
            agent_id: Agent ID（可选，自动生成）
        
        Returns:
            SubAgent 实例
        """
        if not agent_id:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            agent_id = f"sub_{timestamp}"
        
        ***REMOVED*** 准备共享上下文（用于信息同步模式）
        shared_context = None
        if mode == CollaborationMode.INFO_SYNC:
            shared_context = self.conversation_history.copy()
        
        ***REMOVED*** 创建 Sub-Agent
        sub_agent = SubAgent(
            agent_id=agent_id,
            task_description=task_description,
            output_schema=output_schema,
            shared_context=shared_context,
            sandbox_dir=self.sandbox_dir,
            mode=mode
        )
        
        self.sub_agents[agent_id] = sub_agent
        
        logger.info(f"创建 Sub-Agent: {agent_id}, 模式: {mode.value}, 任务: {task_description[:50]}...")
        
        return sub_agent
    
    def delegate_task(
        self,
        task_description: str,
        output_schema: Dict[str, Any],
        verbose: bool = False
    ) -> Tuple[bool, Any]:
        """
        任务委托（Task Delegation）
        
        Master Agent 封装任务为简短指令，发送给 Sub-agent。
        Sub-agent 的上下文完全独立。
        
        Args:
            task_description: 任务描述
            output_schema: 输出 Schema（强制 API 契约）
            verbose: 是否打印详细过程
        
        Returns:
            (是否成功, 结果)
        """
        ***REMOVED*** 创建 Sub-Agent（任务委托模式）
        sub_agent = self.create_sub_agent(
            task_description=task_description,
            output_schema=output_schema,
            mode=CollaborationMode.TASK_DELEGATION
        )
        
        ***REMOVED*** 运行 Sub-Agent
        success, result = sub_agent.run(verbose=verbose)
        
        ***REMOVED*** 记录结果
        if success:
            logger.info(f"任务委托成功: {sub_agent.agent_id}")
        else:
            logger.warning(f"任务委托失败: {sub_agent.agent_id}, 错误: {result}")
        
        return success, result
    
    def sync_info_task(
        self,
        task_description: str,
        verbose: bool = False
    ) -> Tuple[bool, Any]:
        """
        信息同步任务（Information Synchronization）
        
        Sub-agent 创建时获得 Master Agent 的完整历史上下文，
        但保持独立的系统提示词和行动空间。
        
        Args:
            task_description: 任务描述
            verbose: 是否打印详细过程
        
        Returns:
            (是否成功, 结果)
        """
        ***REMOVED*** 创建 Sub-Agent（信息同步模式）
        sub_agent = self.create_sub_agent(
            task_description=task_description,
            output_schema=None,  ***REMOVED*** 信息同步模式不需要严格的 Schema
            mode=CollaborationMode.INFO_SYNC
        )
        
        ***REMOVED*** 运行 Sub-Agent
        success, result = sub_agent.run(verbose=verbose)
        
        ***REMOVED*** 记录结果
        if success:
            logger.info(f"信息同步任务成功: {sub_agent.agent_id}")
        else:
            logger.warning(f"信息同步任务失败: {sub_agent.agent_id}, 错误: {result}")
        
        return success, result
    
    def run(self, query: str, verbose: bool = True) -> str:
        """
        运行 Master Agent
        
        Args:
            query: 用户查询
            verbose: 是否打印详细过程
        
        Returns:
            最终答案
        """
        ***REMOVED*** 运行 Master Agent
        result = self.agent.run(query=query, verbose=verbose)
        
        ***REMOVED*** 更新对话历史
        self.conversation_history.extend(self.agent.conversation_history)
        
        return result


***REMOVED*** 全局 Master Agent 实例（延迟初始化）
_master_agent_instance: Optional[MasterAgent] = None


def get_master_agent(sandbox_dir: Optional[Path] = None) -> MasterAgent:
    """
    获取全局 Master Agent 实例
    
    Args:
        sandbox_dir: 沙箱目录，如果为 None 则使用默认目录
    
    Returns:
        MasterAgent 实例
    """
    global _master_agent_instance
    
    if _master_agent_instance is None:
        _master_agent_instance = MasterAgent(sandbox_dir=sandbox_dir)
    
    return _master_agent_instance
