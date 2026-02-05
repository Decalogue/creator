"""
适配器注册表

提供适配器的注册、发现和管理功能

工业级特性：
- 线程安全的注册和实例管理
- 完善的错误处理和验证
- 实例缓存和生命周期管理
"""

from typing import Dict, Type, Optional, List
import threading
import logging

from .base import (
    BaseAdapter,
    AdapterError,
    AdapterConfigurationError
)

logger = logging.getLogger(__name__)


class AdapterRegistry:
    """
    适配器注册表（线程安全）
    
    管理所有适配器的注册和发现
    
    Note:
        - 所有操作都是线程安全的
        - 适配器实例会被缓存（基于配置）
        - 支持查询适配器信息和健康检查
    """
    
    _adapters: Dict[str, Type[BaseAdapter]] = {}
    _instances: Dict[str, BaseAdapter] = {}
    _lock = threading.RLock()  # 使用 RLock 支持嵌套锁
    
    @classmethod
    def register(cls, name: str, adapter_class: Type[BaseAdapter]) -> None:
        """
        注册适配器类（线程安全）
        
        Args:
            name: 适配器名称（非空字符串）
            adapter_class: 适配器类（必须是 BaseAdapter 的子类）
        
        Raises:
            ValueError: 如果 name 为空或 adapter_class 无效
            TypeError: 如果 adapter_class 不是 BaseAdapter 的子类
        """
        if not name or not isinstance(name, str) or not name.strip():
            raise ValueError("Adapter name must be a non-empty string")
        
        if not isinstance(adapter_class, type) or not issubclass(adapter_class, BaseAdapter):
            raise TypeError(
                f"adapter_class must be a subclass of BaseAdapter, got {type(adapter_class)}"
            )
        
        with cls._lock:
            cls._adapters[name] = adapter_class
            logger.info(f"Registered adapter: {name} ({adapter_class.__name__})")
    
    @classmethod
    def get_adapter_class(cls, name: str) -> Optional[Type[BaseAdapter]]:
        """
        获取适配器类（线程安全）
        
        Args:
            name: 适配器名称
            
        Returns:
            适配器类，如果不存在则返回 None
        """
        with cls._lock:
            return cls._adapters.get(name)
    
    @classmethod
    def create_adapter(cls, name: str, config: Optional[Dict] = None) -> Optional[BaseAdapter]:
        """
        创建适配器实例（线程安全）
        
        根据适配器名称和配置创建适配器实例。如果已存在相同配置的实例，则返回已存在的实例。
        
        Args:
            name: 适配器名称
            config: 配置字典（可选）
            
        Returns:
            适配器实例，如果适配器不存在或创建失败则返回 None
            
        Note:
            - 实例会被缓存，相同配置的请求会返回同一个实例
            - 实例会立即初始化
            - 使用 id(config) 作为缓存键的一部分（注意：相同内容的字典可能不是同一个实例）
            - 线程安全操作
        """
        if not name:
            logger.warning("Adapter name cannot be empty")
            return None
        
        adapter_class = cls.get_adapter_class(name)
        if adapter_class is None:
            logger.warning(f"Adapter '{name}' not found in registry")
            return None
        
        # 检查是否已有实例（基于配置的 ID）
        # 注意：这不是完美的缓存策略，但对于大多数场景足够
        instance_key = f"{name}_{id(config) if config else 'default'}"
        
        with cls._lock:
            if instance_key in cls._instances:
                logger.debug(f"Returning cached adapter instance: {name}")
                return cls._instances[instance_key]
        
        # 创建新实例（在锁外创建，避免长时间锁定）
        try:
            instance = adapter_class(config=config or {})
            instance.initialize()
            
            with cls._lock:
                # 双重检查，避免重复创建
                if instance_key not in cls._instances:
                    cls._instances[instance_key] = instance
                    logger.debug(f"Created new adapter instance: {name}")
                else:
                    # 另一个线程已经创建了实例，使用已存在的实例
                    logger.debug(f"Adapter instance already created by another thread: {name}")
                    instance = cls._instances[instance_key]
            
            return instance
        except AdapterConfigurationError as e:
            logger.error(f"Adapter configuration error for '{name}': {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Failed to create adapter '{name}': {e}", exc_info=True)
            return None
    
    @classmethod
    def list_adapters(cls) -> List[str]:
        """
        列出所有已注册的适配器（线程安全）
        
        Returns:
            适配器名称列表
        """
        with cls._lock:
            return list(cls._adapters.keys())
    
    @classmethod
    def get_adapter_info(cls, name: str) -> Optional[Dict]:
        """
        获取适配器信息（线程安全）
        
        创建适配器实例并返回其健康检查信息。
        
        Args:
            name: 适配器名称
            
        Returns:
            适配器健康检查信息字典，如果适配器不存在或创建失败则返回 None
            
        Note:
            - 会创建适配器实例（如果尚未创建）
            - 返回的信息包含适配器状态、能力和可用性
            - 使用 get_health_dict() 方法以保持向后兼容
        """
        adapter = cls.create_adapter(name)
        if adapter is None:
            return None
        
        try:
            health_status = adapter.health_check()
            # 转换为字典格式（向后兼容）
            return adapter.get_health_dict() if hasattr(adapter, 'get_health_dict') else {
                "adapter": health_status.adapter,
                "initialized": health_status.initialized,
                "available": health_status.available,
                "capabilities": health_status.capabilities,
                **({"details": health_status.details} if health_status.details else {})
            }
        except Exception as e:
            logger.error(f"Error getting adapter info for '{name}': {e}", exc_info=True)
            return None
    
    @classmethod
    def clear_instances(cls) -> None:
        """
        清空所有适配器实例缓存（线程安全）
        
        用于测试或重置场景。注意：这不会销毁已创建的实例，只是从缓存中移除引用。
        """
        with cls._lock:
            count = len(cls._instances)
            cls._instances.clear()
            logger.info(f"Cleared {count} adapter instances from cache")


# 自动注册所有适配器
def _auto_register() -> None:
    """
    自动注册所有功能适配器
    
    在模块加载时自动注册所有可用的适配器类。
    
    Note:
        - 这会在模块导入时执行
        - 如果某个适配器导入失败，会记录错误但不会中断注册过程
    """
    try:
        from .operation_adapter import OperationAdapter
        AdapterRegistry.register("operation", OperationAdapter)
    except ImportError as e:
        logger.warning(f"Failed to import OperationAdapter: {e}")
    
    try:
        from .layered_storage_adapter import LayeredStorageAdapter
        AdapterRegistry.register("layered_storage", LayeredStorageAdapter)
    except ImportError as e:
        logger.warning(f"Failed to import LayeredStorageAdapter: {e}")
    
    try:
        from .memory_type_adapter import MemoryTypeAdapter
        AdapterRegistry.register("memory_type", MemoryTypeAdapter)
    except ImportError as e:
        logger.warning(f"Failed to import MemoryTypeAdapter: {e}")
    
    try:
        from .graph_adapter import GraphAdapter
        AdapterRegistry.register("graph", GraphAdapter)
    except ImportError as e:
        logger.warning(f"Failed to import GraphAdapter: {e}")
    
    try:
        from .atom_link_adapter import AtomLinkAdapter
        AdapterRegistry.register("atom_link", AtomLinkAdapter)
    except ImportError as e:
        logger.warning(f"Failed to import AtomLinkAdapter: {e}")
    
    try:
        from .retrieval_adapter import RetrievalAdapter
        AdapterRegistry.register("retrieval", RetrievalAdapter)
    except ImportError as e:
        logger.warning(f"Failed to import RetrievalAdapter: {e}")
    
    try:
        from .update_adapter import UpdateAdapter
        AdapterRegistry.register("update", UpdateAdapter)
    except ImportError as e:
        logger.warning(f"Failed to import UpdateAdapter: {e}")
    
    logger.info(f"Adapter registration completed: {len(AdapterRegistry.list_adapters())} adapters registered")

# 执行自动注册
_auto_register()
