import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class BaseAdapter(ABC):
    """适配器基类"""
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化适配器
        
        Args:
            config: 配置字典，包含实现相关的配置项
        """
        self.config = config or {}
        self._initialized = False
        self._available = False
    
    def initialize(self):
        """初始化适配器（公共方法）"""
        if not self._initialized:
            try:
                self._do_initialize()
                self._initialized = True
                self._available = True
                logger.info(f"{self.__class__.__name__} initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize {self.__class__.__name__}: {e}")
                self._available = False
                self._initialized = True
    
    @abstractmethod
    def _do_initialize(self):
        """
        子类实现具体的初始化逻辑
        
        注意：
        - 如果底层实现不可用（如未安装），应设置 self._available = False
        - 不应抛出异常，而是优雅降级到 mock 实现
        """
        pass
    
    def is_available(self) -> bool:
        """检查适配器是否可用"""
        if not self._initialized:
            self.initialize()
        return self._available
    
    def get_capabilities(self) -> Dict[str, bool]:
        """获取适配器支持的能力"""
        return {
            "available": self.is_available(),
        }
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "adapter": self.__class__.__name__,
            "initialized": self._initialized,
            "available": self._available,
            "capabilities": self.get_capabilities(),
        }
