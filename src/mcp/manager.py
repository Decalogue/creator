"""
MCP 管理器
管理多个 MCP 服务器和客户端
"""
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

from .server import MCPServer
from .client import MCPClient
from .protocol import MCPTool, MCPResource, MCPPrompt


class MCPManager:
    """
    MCP 管理器
    管理多个 MCP 服务器，提供统一的接口
    """
    
    def __init__(self):
        """初始化 MCP 管理器"""
        self._servers: Dict[str, MCPServer] = {}
        self._clients: Dict[str, MCPClient] = {}
    
    def register_server(self, name: str, server: MCPServer) -> None:
        """
        注册 MCP 服务器
        
        Args:
            name: 服务器名称
            server: 服务器实例
        """
        self._servers[name] = server
        
        ***REMOVED*** 创建对应的客户端
        client = MCPClient(server, client_name=f"mcp-manager-{name}")
        if client.initialize():
            self._clients[name] = client
        else:
            raise RuntimeError(f"Failed to initialize client for server: {name}")
    
    def unregister_server(self, name: str) -> None:
        """
        注销 MCP 服务器
        
        Args:
            name: 服务器名称
        """
        if name in self._servers:
            del self._servers[name]
        if name in self._clients:
            del self._clients[name]
    
    def get_client(self, name: str) -> Optional[MCPClient]:
        """
        获取指定的客户端
        
        Args:
            name: 服务器名称
            
        Returns:
            MCP 客户端实例，如果不存在返回 None
        """
        return self._clients.get(name)
    
    def list_servers(self) -> List[str]:
        """
        列出所有已注册的服务器名称
        
        Returns:
            服务器名称列表
        """
        return list(self._servers.keys())
    
    def get_all_tools(self) -> Dict[str, List[MCPTool]]:
        """
        获取所有服务器的工具
        
        Returns:
            字典，键为服务器名称，值为工具列表
        """
        all_tools = {}
        
        for name, client in self._clients.items():
            try:
                tools = client.list_tools()
                all_tools[name] = tools
            except Exception as e:
                print(f"Warning: Failed to get tools from server {name}: {e}")
        
        return all_tools
    
    def get_all_resources(self) -> Dict[str, List[MCPResource]]:
        """
        获取所有服务器的资源
        
        Returns:
            字典，键为服务器名称，值为资源列表
        """
        all_resources = {}
        
        for name, client in self._clients.items():
            try:
                resources = client.list_resources()
                all_resources[name] = resources
            except Exception as e:
                print(f"Warning: Failed to get resources from server {name}: {e}")
        
        return all_resources
    
    def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        调用指定服务器的工具
        
        Args:
            server_name: 服务器名称
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            执行结果
        """
        client = self.get_client(server_name)
        if not client:
            raise ValueError(f"Server not found: {server_name}")
        
        return client.call_tool(tool_name, arguments)
    
    def read_resource(self, server_name: str, uri: str) -> str:
        """
        从指定服务器读取资源
        
        Args:
            server_name: 服务器名称
            uri: 资源 URI
            
        Returns:
            资源内容
        """
        client = self.get_client(server_name)
        if not client:
            raise ValueError(f"Server not found: {server_name}")
        
        return client.read_resource(uri)
    
    def find_tool(self, tool_name: str) -> Optional[Tuple[str, MCPTool]]:
        """
        在所有服务器中查找工具
        
        Args:
            tool_name: 工具名称
            
        Returns:
            (服务器名称, 工具) 元组，如果未找到返回 None
        """
        for name, client in self._clients.items():
            try:
                tools = client.list_tools()
                for tool in tools:
                    if tool.name == tool_name:
                        return (name, tool)
            except Exception:
                continue
        
        return None
    
    def find_resource(self, uri: str) -> Optional[str]:
        """
        在所有服务器中查找资源
        
        Args:
            uri: 资源 URI
            
        Returns:
            服务器名称，如果未找到返回 None
        """
        for name, client in self._clients.items():
            try:
                resources = client.list_resources()
                for resource in resources:
                    if resource.uri == uri:
                        return name
            except Exception:
                continue
        
        return None


***REMOVED*** 全局 MCP 管理器实例
default_manager = MCPManager()
