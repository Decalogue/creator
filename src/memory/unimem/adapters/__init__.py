"""
适配器层：按照 UniMem 的功能需求定义接口

设计理念：
1. 按照 UniMem 的功能模块需求命名适配器，而非架构名称
2. 从各大架构吸收精华思路，但接口统一为 UniMem 的需求
3. 各适配器解耦，易于扩展和维护
"""

from .base import BaseAdapter

***REMOVED*** 功能适配器（基类和实现都在同一个文件中）
from .operation_adapter import OperationAdapter
from .layered_storage_adapter import LayeredStorageAdapter
from .memory_type_adapter import MemoryTypeAdapter
from .graph_adapter import GraphAdapter
from .network_link_adapter import NetworkLinkAdapter
from .retrieval_adapter import RetrievalAdapter
from .update_adapter import UpdateAdapter

__all__ = [
    ***REMOVED*** 基类
    "BaseAdapter",
    ***REMOVED*** 功能适配器
    "OperationAdapter",
    "LayeredStorageAdapter",
    "MemoryTypeAdapter",
    "GraphAdapter",
    "NetworkLinkAdapter",
    "RetrievalAdapter",
    "UpdateAdapter",
]
