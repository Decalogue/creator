"""
MCP 客户端
用于连接和管理 MCP 服务器
"""
from typing import Any, Dict, List, Optional, Callable
from pathlib import Path
import json

from .protocol import MCPRequest, MCPResponse, MCPTool, MCPResource, MCPPrompt
from .server import MCPServer


class MCPClient:
    """
    MCP 客户端
    管理与 MCP 服务器的连接和通信
    """
    
    def __init__(self, server: MCPServer, client_name: str = "mcp-client", client_version: str = "1.0.0"):
        """
        初始化 MCP 客户端
        
        Args:
            server: MCP 服务器实例
            client_name: 客户端名称
            client_version: 客户端版本
        """
        self.server = server
        self.client_name = client_name
        self.client_version = client_version
        self._initialized = False
        self._request_id = 0
    
    def initialize(self) -> bool:
        """
        初始化与服务器的连接
        
        Returns:
            是否初始化成功
        """
        request = MCPRequest(
            id=self._next_request_id(),
            method="initialize",
            params={
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "prompts": {}
                },
                "clientInfo": {
                    "name": self.client_name,
                    "version": self.client_version
                }
            }
        )
        
        response = self.server.handle_request(request)
        
        ***REMOVED*** 检查响应是否有错误（直接使用 _error 字段）
        if response._error is None:
            self._initialized = True
            ***REMOVED*** 发送 initialized 通知
            self._send_notification("initialized", {})
            return True
        else:
            return False
    
    def list_tools(self) -> List[MCPTool]:
        """
        获取所有可用的工具
        
        Returns:
            工具列表
        """
        if not self._initialized:
            raise RuntimeError("Client not initialized")
        
        request = MCPRequest(
            id=self._next_request_id(),
            method="tools/list"
        )
        
        response = self.server.handle_request(request)
        
        if response._error is not None:
            raise RuntimeError(f"Error listing tools: {response._error.get('message', 'Unknown error')}")
        
        tools_data = response.result.get("tools", []) if response.result else []
        return [MCPTool(**tool) for tool in tools_data]
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """
        调用指定的工具
        
        Args:
            name: 工具名称
            arguments: 工具参数
            
        Returns:
            工具执行结果
        """
        if not self._initialized:
            raise RuntimeError("Client not initialized")
        
        request = MCPRequest(
            id=self._next_request_id(),
            method="tools/call",
            params={
                "name": name,
                "arguments": arguments
            }
        )
        
        response = self.server.handle_request(request)
        
        if response._error is not None:
            raise RuntimeError(f"Error calling tool: {response._error.get('message', 'Unknown error')}")
        
        ***REMOVED*** 提取文本内容
        content = response.result.get("content", [])
        if content and len(content) > 0:
            return content[0].get("text", "")
        return response.result
    
    def list_resources(self) -> List[MCPResource]:
        """
        获取所有可用的资源
        
        Returns:
            资源列表
        """
        if not self._initialized:
            raise RuntimeError("Client not initialized")
        
        request = MCPRequest(
            id=self._next_request_id(),
            method="resources/list"
        )
        
        response = self.server.handle_request(request)
        
        if response._error is not None:
            raise RuntimeError(f"Error listing resources: {response._error.get('message', 'Unknown error')}")
        
        resources_data = response.result.get("resources", [])
        return [MCPResource(**resource) for resource in resources_data]
    
    def read_resource(self, uri: str) -> str:
        """
        读取指定的资源
        
        Args:
            uri: 资源 URI
            
        Returns:
            资源内容
        """
        if not self._initialized:
            raise RuntimeError("Client not initialized")
        
        request = MCPRequest(
            id=self._next_request_id(),
            method="resources/read",
            params={"uri": uri}
        )
        
        response = self.server.handle_request(request)
        
        if response._error is not None:
            raise RuntimeError(f"Error reading resource: {response._error.get('message', 'Unknown error')}")
        
        ***REMOVED*** 提取文本内容
        contents = response.result.get("contents", [])
        if contents and len(contents) > 0:
            return contents[0].get("text", "")
        return ""
    
    def list_prompts(self) -> List[MCPPrompt]:
        """
        获取所有可用的提示
        
        Returns:
            提示列表
        """
        if not self._initialized:
            raise RuntimeError("Client not initialized")
        
        request = MCPRequest(
            id=self._next_request_id(),
            method="prompts/list"
        )
        
        response = self.server.handle_request(request)
        
        if response._error is not None:
            raise RuntimeError(f"Error listing prompts: {response._error.get('message', 'Unknown error')}")
        
        prompts_data = response.result.get("prompts", [])
        return [MCPPrompt(**prompt) for prompt in prompts_data]
    
    def get_prompt(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        获取指定的提示
        
        Args:
            name: 提示名称
            arguments: 提示参数
            
        Returns:
            提示内容
        """
        if not self._initialized:
            raise RuntimeError("Client not initialized")
        
        request = MCPRequest(
            id=self._next_request_id(),
            method="prompts/get",
            params={
                "name": name,
                "arguments": arguments or {}
            }
        )
        
        response = self.server.handle_request(request)
        
        if response._error is not None:
            raise RuntimeError(f"Error getting prompt: {response._error.get('message', 'Unknown error')}")
        
        return response.result
    
    def _next_request_id(self) -> int:
        """获取下一个请求 ID"""
        self._request_id += 1
        return self._request_id
    
    def _send_notification(self, method: str, params: Dict[str, Any]) -> None:
        """发送通知（无响应）"""
        request = MCPRequest(
            id=None,  ***REMOVED*** 通知没有 ID
            method=method,
            params=params
        )
        ***REMOVED*** 通知不需要响应
        self.server.handle_request(request)
    
    @property
    def is_initialized(self) -> bool:
        """是否已初始化"""
        return self._initialized
