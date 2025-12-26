import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class Tool(ABC):
    """
    Function Calling 基类
    所有可调用函数都需要继承此类并实现相应方法
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
        执行工具
        
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


class ToolRegistry:
    """
    Function Calling 注册表
    管理所有可用的工具调用
    """
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool) -> None:
        """注册一个工具（Tool 对应 Function Calling 中的 Function）"""
        if not isinstance(tool, Tool):
            raise TypeError(f"Expected Tool instance, got {type(tool).__name__}")
        self._tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """根据名称获取函数"""
        return self._tools.get(name)
    
    def get_all_functions(self) -> List[Dict[str, Any]]:
        """获取所有函数的定义（OpenAI Function Calling 格式）"""
        return [tool.get_function_schema() for tool in self._tools.values()]
    
    def execute_tool(self, name: str, arguments: Union[Dict[str, Any], str]) -> Any:
        """
        执行指定的函数调用
        
        Args:
            name: 函数名称
            arguments: 函数参数（JSON 字符串或字典）
        
        Returns:
            执行结果
        """
        tool = self.get_tool(name)
        if tool is None:
            raise ValueError(f"Function '{name}' not found")
        
        ***REMOVED*** 如果 arguments 是字符串，解析为字典
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON arguments: {arguments}")
        
        ***REMOVED*** 验证参数
        if not tool.validate_arguments(arguments):
            raise ValueError(f"Invalid arguments for function '{name}': {arguments}")
        
        ***REMOVED*** 执行函数
        return tool.execute(arguments)
    
    def list_tools(self) -> List[str]:
        """列出所有已注册的函数名称"""
        return list(self._tools.keys())


***REMOVED*** 全局函数注册表
default_registry = ToolRegistry()
