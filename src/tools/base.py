"""
Function Calling 基类定义
提供统一的函数调用接口，支持 OpenAI Function Calling 格式

注意：虽然类名使用 "Skill"，但这是一个标准的 Function Calling 系统，
完全兼容 OpenAI 的 Function Calling API。
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import json


class Skill(ABC):
    """
    Function Calling 基类
    所有可调用函数都需要继承此类并实现相应方法
    
    注意：虽然类名是 Skill，但实际对应 Function Calling 中的 Function。
    这个命名是为了保持代码的简洁性，实际功能是标准的 Function Calling。
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def get_function_schema(self) -> Dict[str, Any]:
        """
        返回 OpenAI Function Calling 格式的函数定义
        
        Returns:
            Dict: 包含 name, description, parameters 的字典
        """
        pass
    
    @abstractmethod
    def execute(self, arguments: Dict[str, Any]) -> Any:
        """
        执行技能
        
        Args:
            arguments: 函数参数（JSON 格式解析后的字典）
        
        Returns:
            执行结果（可以是字符串、字典等）
        """
        pass
    
    def validate_arguments(self, arguments: Dict[str, Any]) -> bool:
        """
        验证参数是否有效（可选，子类可以重写）
        
        Args:
            arguments: 函数参数
        
        Returns:
            bool: 参数是否有效
        """
        return True


class SkillRegistry:
    """
    Function Calling 注册表
    管理所有可用的函数调用
    
    注意：虽然类名使用 "Skill"，但实际管理的是 Function Calling 中的 Function。
    """
    
    def __init__(self):
        self._skills: Dict[str, Skill] = {}
    
    def register(self, skill: Skill):
        """注册一个函数（Skill 是内部命名，实际是 Function）"""
        self._skills[skill.name] = skill
    
    def get_skill(self, name: str) -> Optional[Skill]:
        """根据名称获取函数"""
        return self._skills.get(name)
    
    def get_all_functions(self) -> list[Dict[str, Any]]:
        """获取所有函数的定义（OpenAI Function Calling 格式）"""
        return [skill.get_function_schema() for skill in self._skills.values()]
    
    def execute_skill(self, name: str, arguments: Dict[str, Any]) -> Any:
        """
        执行指定的函数调用
        
        Args:
            name: 函数名称
            arguments: 函数参数（JSON 字符串或字典）
        
        Returns:
            执行结果
        """
        skill = self.get_skill(name)
        if skill is None:
            raise ValueError(f"Function '{name}' not found")
        
        ***REMOVED*** 如果 arguments 是字符串，解析为字典
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON arguments: {arguments}")
        
        ***REMOVED*** 验证参数
        if not skill.validate_arguments(arguments):
            raise ValueError(f"Invalid arguments for function '{name}': {arguments}")
        
        ***REMOVED*** 执行函数
        return skill.execute(arguments)
    
    def list_skills(self) -> list[str]:
        """列出所有已注册的函数名称"""
        return list(self._skills.keys())


***REMOVED*** 全局函数注册表
default_registry = SkillRegistry()
