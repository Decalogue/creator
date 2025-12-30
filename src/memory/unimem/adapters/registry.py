"""
适配器注册表

提供适配器的注册、发现和管理功能
"""

from typing import Dict, Type, Optional, List
from .base import BaseAdapter
import logging

logger = logging.getLogger(__name__)


class AdapterRegistry:
    """
    适配器注册表
    
    管理所有适配器的注册和发现
    """
    
    _adapters: Dict[str, Type[BaseAdapter]] = {}
    _instances: Dict[str, BaseAdapter] = {}
    
    @classmethod
    def register(cls, name: str, adapter_class: Type[BaseAdapter]):
        """
        注册适配器类
        
        Args:
            name: 适配器名称
            adapter_class: 适配器类
        """
        cls._adapters[name] = adapter_class
        logger.info(f"Registered adapter: {name}")
    
    @classmethod
    def get_adapter_class(cls, name: str) -> Optional[Type[BaseAdapter]]:
        """
        获取适配器类
        
        Args:
            name: 适配器名称
            
        Returns:
            适配器类，如果不存在则返回 None
        """
        return cls._adapters.get(name)
    
    @classmethod
    def create_adapter(cls, name: str, config: Optional[Dict] = None) -> Optional[BaseAdapter]:
        """
        创建适配器实例
        
        Args:
            name: 适配器名称
            config: 配置字典
            
        Returns:
            适配器实例，如果不存在则返回 None
        """
        adapter_class = cls.get_adapter_class(name)
        if adapter_class is None:
            logger.warning(f"Adapter {name} not found")
            return None
        
        ***REMOVED*** 检查是否已有实例
        instance_key = f"{name}_{id(config) if config else 'default'}"
        if instance_key in cls._instances:
            return cls._instances[instance_key]
        
        ***REMOVED*** 创建新实例
        instance = adapter_class(config=config)
        instance.initialize()
        cls._instances[instance_key] = instance
        return instance
    
    @classmethod
    def list_adapters(cls) -> List[str]:
        """
        列出所有已注册的适配器
        
        Returns:
            适配器名称列表
        """
        return list(cls._adapters.keys())
    
    @classmethod
    def get_adapter_info(cls, name: str) -> Optional[Dict]:
        """
        获取适配器信息
        
        Args:
            name: 适配器名称
            
        Returns:
            适配器信息字典
        """
        adapter = cls.create_adapter(name)
        if adapter is None:
            return None
        
        return adapter.health_check()


***REMOVED*** 自动注册所有适配器
def _auto_register():
    """自动注册所有功能适配器"""
    from .operation_adapter import OperationAdapter
    from .layered_storage_adapter import LayeredStorageAdapter
    from .memory_type_adapter import MemoryTypeAdapter
    from .graph_adapter import GraphAdapter
    from .atom_link_adapter import AtomLinkAdapter
    from .retrieval_adapter import RetrievalAdapter
    from .update_adapter import UpdateAdapter
    
    AdapterRegistry.register("operation", OperationAdapter)
    AdapterRegistry.register("layered_storage", LayeredStorageAdapter)
    AdapterRegistry.register("memory_type", MemoryTypeAdapter)
    AdapterRegistry.register("graph", GraphAdapter)
    AdapterRegistry.register("atom_link", AtomLinkAdapter)
    AdapterRegistry.register("retrieval", RetrievalAdapter)
    AdapterRegistry.register("update", UpdateAdapter)
    
    logger.info("All adapters registered successfully")

***REMOVED*** 执行自动注册
_auto_register()
