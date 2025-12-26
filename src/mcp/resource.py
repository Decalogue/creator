"""
MCP 资源管理
定义和管理 MCP 资源
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from pathlib import Path

from .protocol import MCPResource


class MCPResourceProvider(ABC):
    """
    MCP 资源提供者基类
    子类需要实现具体的资源读取逻辑
    """
    
    @abstractmethod
    def get_resource(self, uri: str) -> str:
        """
        获取资源内容
        
        Args:
            uri: 资源 URI
            
        Returns:
            资源内容
        """
        pass
    
    @abstractmethod
    def list_resources(self) -> List[MCPResource]:
        """
        列出所有可用的资源
        
        Returns:
            资源列表
        """
        pass


class FileSystemResourceProvider(MCPResourceProvider):
    """
    文件系统资源提供者
    从本地文件系统读取资源
    """
    
    def __init__(self, base_path: Path, uri_prefix: str = "file://"):
        """
        初始化文件系统资源提供者
        
        Args:
            base_path: 基础路径
            uri_prefix: URI 前缀
        """
        self.base_path = Path(base_path)
        self.uri_prefix = uri_prefix
        self._resources: Dict[str, MCPResource] = {}
        self._scan_resources()
    
    def _scan_resources(self) -> None:
        """扫描资源文件"""
        if not self.base_path.exists():
            return
        
        for file_path in self.base_path.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith("."):
                relative_path = file_path.relative_to(self.base_path)
                uri = f"{self.uri_prefix}{relative_path.as_posix()}"
                
                self._resources[uri] = MCPResource(
                    uri=uri,
                    name=relative_path.name,
                    description=f"File: {relative_path.as_posix()}",
                    mimeType=self._guess_mime_type(file_path)
                )
    
    def _guess_mime_type(self, file_path: Path) -> str:
        """根据文件扩展名猜测 MIME 类型"""
        suffix = file_path.suffix.lower()
        mime_types = {
            ".txt": "text/plain",
            ".md": "text/markdown",
            ".json": "application/json",
            ".yaml": "application/yaml",
            ".yml": "application/yaml",
            ".py": "text/x-python",
            ".js": "text/javascript",
            ".html": "text/html",
            ".css": "text/css",
        }
        return mime_types.get(suffix, "text/plain")
    
    def get_resource(self, uri: str) -> str:
        """获取资源内容"""
        if not uri.startswith(self.uri_prefix):
            raise ValueError(f"Invalid URI prefix: {uri}")
        
        ***REMOVED*** 移除前缀，获取相对路径
        relative_path = uri[len(self.uri_prefix):]
        file_path = self.base_path / relative_path
        
        if not file_path.exists():
            raise FileNotFoundError(f"Resource not found: {uri}")
        
        return file_path.read_text(encoding='utf-8')
    
    def list_resources(self) -> List[MCPResource]:
        """列出所有资源"""
        return list(self._resources.values())


class MemoryResourceProvider(MCPResourceProvider):
    """
    内存资源提供者
    从内存中管理资源
    """
    
    def __init__(self):
        """初始化内存资源提供者"""
        self._resources: Dict[str, str] = {}  ***REMOVED*** uri -> content
        self._metadata: Dict[str, MCPResource] = {}  ***REMOVED*** uri -> metadata
    
    def register_resource(self, uri: str, name: str, content: str, 
                         description: Optional[str] = None, 
                         mime_type: Optional[str] = None) -> None:
        """
        注册资源
        
        Args:
            uri: 资源 URI
            name: 资源名称
            content: 资源内容
            description: 资源描述
            mime_type: MIME 类型
        """
        self._resources[uri] = content
        self._metadata[uri] = MCPResource(
            uri=uri,
            name=name,
            description=description,
            mimeType=mime_type or "text/plain"
        )
    
    def get_resource(self, uri: str) -> str:
        """获取资源内容"""
        if uri not in self._resources:
            raise FileNotFoundError(f"Resource not found: {uri}")
        return self._resources[uri]
    
    def list_resources(self) -> List[MCPResource]:
        """列出所有资源"""
        return list(self._metadata.values())
