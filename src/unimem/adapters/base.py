"""
适配器基类模块

提供所有适配器的基类 BaseAdapter，定义了适配器的基本接口和通用功能。
所有具体的适配器实现都应该继承自 BaseAdapter。

工业级特性：
- 自定义异常体系（AdapterError 及其子类）
- 线程安全支持（RLock）
- 完善的类型提示和数据类
- 上下文管理器支持
- 统一的错误处理和日志记录
"""

import logging
import threading
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, ContextManager
from dataclasses import dataclass
from contextlib import contextmanager

logger = logging.getLogger(__name__)


***REMOVED*** ==================== 自定义异常类 ====================

class AdapterError(Exception):
    """适配器基础异常类"""
    
    def __init__(
        self,
        message: str,
        adapter_name: Optional[str] = None,
        cause: Optional[Exception] = None
    ) -> None:
        """
        初始化适配器异常
        
        Args:
            message: 错误消息
            adapter_name: 适配器名称（可选）
            cause: 原始异常（可选）
        """
        self.message = message
        self.adapter_name = adapter_name
        self.cause = cause
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        """格式化错误消息"""
        parts = []
        if self.adapter_name:
            parts.append(f"[{self.adapter_name}]")
        parts.append(self.message)
        if self.cause:
            parts.append(f"Caused by: {type(self.cause).__name__}: {self.cause}")
        return " ".join(parts)


class AdapterInitializationError(AdapterError):
    """适配器初始化错误"""
    pass


class AdapterNotAvailableError(AdapterError):
    """适配器不可用错误"""
    pass


class AdapterConfigurationError(AdapterError):
    """适配器配置错误"""
    pass


@dataclass
class AdapterHealthStatus:
    """适配器健康状态数据类"""
    adapter: str
    initialized: bool
    available: bool
    capabilities: Dict[str, bool]
    details: Optional[Dict[str, Any]] = None


class BaseAdapter(ABC):
    """
    适配器基类
    
    所有适配器的抽象基类，定义了适配器的基本接口和通用功能。
    
    核心功能：
    1. 初始化管理：统一的初始化流程和状态管理
    2. 可用性检查：检查适配器是否可用
    3. 能力查询：获取适配器支持的能力
    4. 健康检查：检查适配器的健康状态
    
    使用方式：
    ```python
    class MyAdapter(BaseAdapter):
        def _do_initialize(self) -> None:
            ***REMOVED*** 实现具体的初始化逻辑
            pass
    ```
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化适配器
        
        Args:
            config: 配置字典，包含实现相关的配置项
                - 如果为 None，将使用空字典作为默认配置
                - 子类可以定义特定的配置项要求
        
        Note:
            - 初始化时不会立即执行 `_do_initialize()`，需要调用 `initialize()` 方法
            - 这样可以支持延迟初始化，避免在构造时执行耗时操作
            - 使用 RLock 确保线程安全
        """
        self.config: Dict[str, Any] = config or {}
        self._initialized: bool = False
        self._available: bool = False
        ***REMOVED*** 线程安全锁（使用 RLock 支持嵌套锁）
        self._lock = threading.RLock()
    
    def initialize(self) -> None:
        """
        初始化适配器（公共方法，线程安全）
        
        执行适配器的初始化流程：
        1. 检查是否已经初始化（避免重复初始化）
        2. 调用子类实现的 `_do_initialize()` 方法
        3. 更新初始化状态和可用性状态
        4. 记录初始化结果
        
        Note:
            - 如果初始化失败，会记录错误但不会抛出异常
            - 适配器会标记为不可用（`_available = False`）
            - 即使初始化失败，也会标记为已初始化（`_initialized = True`），避免重复尝试
            - 使用锁确保线程安全
        """
        with self._lock:
            if not self._initialized:
                try:
                    self._do_initialize()
                    self._initialized = True
                    self._available = True
                    logger.info(f"{self.__class__.__name__} initialized successfully")
                except AdapterConfigurationError:
                    ***REMOVED*** 配置错误需要重新抛出，让调用者知道
                    raise
                except Exception as e:
                    logger.error(
                        f"Failed to initialize {self.__class__.__name__}: {e}",
                        exc_info=True
                    )
                    self._available = False
                    self._initialized = True
                    ***REMOVED*** 即使初始化失败，也标记为已初始化，避免重复尝试
    
    @abstractmethod
    def _do_initialize(self) -> None:
        """
        子类实现具体的初始化逻辑
        
        这是抽象方法，子类必须实现。用于执行适配器特定的初始化操作，
        如连接数据库、加载模型、初始化资源等。
        
        实现要求：
        - 如果底层实现不可用（如依赖未安装），应设置 `self._available = False`
        - 不应抛出异常，而是优雅降级到 mock 实现或标记为不可用
        - 如果初始化成功，应设置 `self._available = True`（虽然父类也会设置）
        
        Raises:
            Exception: 如果初始化过程中发生严重错误，可以抛出异常
                （父类的 `initialize()` 方法会捕获并处理）
        """
        pass
    
    def is_available(self) -> bool:
        """
        检查适配器是否可用（线程安全）
        
        检查适配器是否已初始化且可用。如果未初始化，会自动调用 `initialize()`。
        
        Returns:
            bool: 如果适配器已初始化且可用返回 True，否则返回 False
            
        Note:
            - 如果适配器未初始化，会自动触发初始化
            - 初始化失败不会抛出异常，而是返回 False
        """
        with self._lock:
            if not self._initialized:
                try:
                    self.initialize()
                except AdapterConfigurationError:
                    ***REMOVED*** 配置错误：标记为不可用但不抛出异常
                    return False
                except Exception:
                    ***REMOVED*** 其他初始化错误已在 initialize() 中处理
                    return False
            return self._available
    
    def get_capabilities(self) -> Dict[str, bool]:
        """
        获取适配器支持的能力
        
        返回适配器支持的各种能力的字典。子类可以重写此方法以提供更详细的能力信息。
        
        Returns:
            Dict[str, bool]: 能力字典，至少包含 "available" 键
                - "available": bool - 适配器是否可用
                - 子类可以添加其他能力键，如 "vector_search", "text_generation" 等
        
        Example:
            ```python
            {
                "available": True,
                "vector_search": True,
                "text_generation": False
            }
            ```
        """
        return {
            "available": self.is_available(),
        }
    
    def health_check(self) -> AdapterHealthStatus:
        """
        健康检查（返回数据类）
        
        检查适配器的健康状态，返回详细的状态信息。用于监控和诊断。
        
        Returns:
            AdapterHealthStatus: 健康状态数据类
            
        Example:
            ```python
            status = adapter.health_check()
            print(status.adapter)  ***REMOVED*** "AtomLinkAdapter"
            print(status.available)  ***REMOVED*** True
            ```
        """
        with self._lock:
            return AdapterHealthStatus(
                adapter=self.__class__.__name__,
                initialized=self._initialized,
                available=self._available,
                capabilities=self.get_capabilities(),
            )
    
    def get_health_dict(self) -> Dict[str, Any]:
        """
        获取健康状态字典（向后兼容）
        
        Returns:
            Dict[str, Any]: 健康状态字典
        """
        status = self.health_check()
        result = {
            "adapter": status.adapter,
            "initialized": status.initialized,
            "available": status.available,
            "capabilities": status.capabilities,
        }
        if status.details:
            result["details"] = status.details
        return result
    
    def reset(self) -> None:
        """
        重置适配器状态
        
        重置适配器的初始化状态，允许重新初始化。主要用于测试和调试。
        
        Note:
            - 重置后需要重新调用 `initialize()` 才能使用适配器
            - 不会清理已创建的资源（如数据库连接、模型等），子类可以重写以添加清理逻辑
        """
        self._initialized = False
        self._available = False
        logger.debug(f"{self.__class__.__name__} reset")
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        获取配置项（线程安全）
        
        从配置字典中获取指定键的值，如果不存在则返回默认值。
        
        Args:
            key: 配置键
            default: 默认值，如果键不存在则返回此值
            
        Returns:
            Any: 配置值或默认值
        """
        with self._lock:
            return self.config.get(key, default)
    
    def set_config(self, key: str, value: Any) -> None:
        """
        设置配置项（线程安全）
        
        在配置字典中设置指定键的值。
        
        Args:
            key: 配置键
            value: 配置值
        
        Note:
            - 修改配置后不会自动重新初始化适配器
            - 如果需要应用新配置，应调用 `reset()` 然后重新 `initialize()`
        """
        with self._lock:
            self.config[key] = value
    
    @contextmanager
    def _operation_context(self, operation_name: str) -> ContextManager[None]:
        """
        操作上下文管理器（用于统一日志记录和错误处理）
        
        Args:
            operation_name: 操作名称（用于日志）
        
        Example:
            ```python
            with self._operation_context("search"):
                ***REMOVED*** 执行搜索操作
                pass
            ```
        """
        logger.debug(f"{self.__class__.__name__}: Starting {operation_name}")
        try:
            yield
            logger.debug(f"{self.__class__.__name__}: Completed {operation_name}")
        except Exception as e:
            logger.error(
                f"{self.__class__.__name__}: Failed {operation_name}: {e}",
                exc_info=True
            )
            raise
