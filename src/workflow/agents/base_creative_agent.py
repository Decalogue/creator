"""
创作专用 Agent 基类

定义创作 Agent 的统一接口，继承自 Puppeteer 的 Agent 基类。
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

***REMOVED*** 导入 Puppeteer 的 Agent 基类
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
from agent.puppeteer.agent.agent import Agent

logger = logging.getLogger(__name__)


class BaseCreativeAgent(Agent, ABC):
    """创作专用 Agent 基类
    
    所有创作相关的 Agent 都继承此类，提供统一的创作接口。
    """
    
    def __init__(
        self,
        role: str,
        role_prompt: str,
        index: int,
        model: str = "gpt",
        actions: List = None,
        policy=None,
        global_info=None,
        initial_dialog_history=None
    ):
        """
        初始化创作 Agent
        
        Args:
            role: Agent 角色名称
            role_prompt: 角色提示词
            index: Agent 索引
            model: 使用的模型
            actions: 可用动作列表
            policy: 策略对象
            global_info: 全局信息
            initial_dialog_history: 初始对话历史
        """
        super().__init__(
            role=role,
            role_prompt=role_prompt,
            index=index,
            model=model,
            actions=actions or [],
            policy=policy,
            global_info=global_info,
            initial_dialog_history=initial_dialog_history
        )
        logger.info(f"CreativeAgent {role} initialized")
    
    @abstractmethod
    def generate_content(
        self,
        context: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        生成创作内容
        
        Args:
            context: 上下文信息（包含记忆、前文等）
            constraints: 约束条件（风格、长度等）
            
        Returns:
            生成结果字典，包含：
            - content: 生成的内容
            - metadata: 元数据（角色、场景等）
            - confidence: 置信度
        """
        pass
    
    @abstractmethod
    def validate_content(
        self,
        content: str,
        requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        验证生成的内容
        
        Args:
            content: 要验证的内容
            requirements: 验证要求
            
        Returns:
            验证结果字典，包含：
            - is_valid: 是否通过验证
            - issues: 问题列表
            - suggestions: 改进建议
        """
        pass
    
    def activate(self, global_info, initial_dialog_history=None):
        """激活 Agent"""
        super().activate(global_info, initial_dialog_history)
        logger.debug(f"CreativeAgent {self.role} activated")
    
    def deactivate(self):
        """停用 Agent"""
        super().deactivate()
        logger.debug(f"CreativeAgent {self.role} deactivated")

