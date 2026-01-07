"""
资源管理器

管理并行执行时的资源分配，包括线程池、内存、API 调用等。
"""

import logging
import threading
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class ResourceLimits:
    """资源限制"""
    max_workers: int = 5  ***REMOVED*** 最大并发工作线程数
    max_memory_mb: int = 4096  ***REMOVED*** 最大内存（MB）
    max_api_calls_per_minute: int = 60  ***REMOVED*** 每分钟最大 API 调用数
    max_api_calls_per_hour: int = 1000  ***REMOVED*** 每小时最大 API 调用数


@dataclass
class ResourceUsage:
    """资源使用情况"""
    active_workers: int = 0
    memory_usage_mb: float = 0.0
    api_calls_last_minute: int = 0
    api_calls_last_hour: int = 0
    api_call_timestamps: List[datetime] = field(default_factory=list)


class ResourceManager:
    """资源管理器
    
    管理并行执行时的资源分配，包括：
    - 线程池管理
    - 内存监控
    - API 调用限流
    - 资源使用统计
    """
    
    def __init__(self, limits: Optional[ResourceLimits] = None):
        """
        初始化资源管理器
        
        Args:
            limits: 资源限制配置
        """
        self.limits = limits or ResourceLimits()
        self.usage = ResourceUsage()
        self._lock = threading.Lock()
        
        logger.info(f"ResourceManager initialized: max_workers={self.limits.max_workers}")
    
    def can_acquire_worker(self) -> bool:
        """
        检查是否可以获取工作线程
        
        Returns:
            是否可以获取
        """
        with self._lock:
            return self.usage.active_workers < self.limits.max_workers
    
    def acquire_worker(self) -> bool:
        """
        获取工作线程
        
        Returns:
            是否成功获取
        """
        with self._lock:
            if self.usage.active_workers >= self.limits.max_workers:
                logger.debug("Cannot acquire worker: max workers reached")
                return False
            
            self.usage.active_workers += 1
            logger.debug(f"Worker acquired: {self.usage.active_workers}/{self.limits.max_workers}")
            return True
    
    def release_worker(self) -> None:
        """释放工作线程"""
        with self._lock:
            if self.usage.active_workers > 0:
                self.usage.active_workers -= 1
                logger.debug(f"Worker released: {self.usage.active_workers}/{self.limits.max_workers}")
    
    def can_make_api_call(self) -> bool:
        """
        检查是否可以发起 API 调用
        
        Returns:
            是否可以发起
        """
        with self._lock:
            self._update_api_call_stats()
            
            if (self.usage.api_calls_last_minute >= self.limits.max_api_calls_per_minute or
                self.usage.api_calls_last_hour >= self.limits.max_api_calls_per_hour):
                return False
            
            return True
    
    def record_api_call(self) -> None:
        """记录 API 调用"""
        with self._lock:
            now = datetime.now()
            self.usage.api_call_timestamps.append(now)
            self._update_api_call_stats()
            logger.debug(f"API call recorded: {self.usage.api_calls_last_minute}/{self.limits.max_api_calls_per_minute} per minute")
    
    def _update_api_call_stats(self) -> None:
        """更新 API 调用统计"""
        now = datetime.now()
        
        ***REMOVED*** 清理过期的调用记录
        one_minute_ago = now - timedelta(minutes=1)
        one_hour_ago = now - timedelta(hours=1)
        
        self.usage.api_call_timestamps = [
            ts for ts in self.usage.api_call_timestamps
            if ts > one_hour_ago
        ]
        
        ***REMOVED*** 统计最近一分钟的调用数
        self.usage.api_calls_last_minute = sum(
            1 for ts in self.usage.api_call_timestamps
            if ts > one_minute_ago
        )
        
        ***REMOVED*** 统计最近一小时的调用数
        self.usage.api_calls_last_hour = len(self.usage.api_call_timestamps)
    
    def get_available_workers(self) -> int:
        """获取可用工作线程数"""
        with self._lock:
            return max(0, self.limits.max_workers - self.usage.active_workers)
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """获取资源使用统计"""
        with self._lock:
            self._update_api_call_stats()
            
            return {
                "active_workers": self.usage.active_workers,
                "max_workers": self.limits.max_workers,
                "available_workers": self.get_available_workers(),
                "api_calls_last_minute": self.usage.api_calls_last_minute,
                "max_api_calls_per_minute": self.limits.max_api_calls_per_minute,
                "api_calls_last_hour": self.usage.api_calls_last_hour,
                "max_api_calls_per_hour": self.limits.max_api_calls_per_hour,
                "memory_usage_mb": self.usage.memory_usage_mb,
                "max_memory_mb": self.limits.max_memory_mb
            }
    
    def wait_for_resource(self, resource_type: str = "worker", timeout: float = 60.0) -> bool:
        """
        等待资源可用
        
        Args:
            resource_type: 资源类型（worker 或 api）
            timeout: 超时时间（秒）
            
        Returns:
            是否成功获取资源
        """
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if resource_type == "worker":
                if self.can_acquire_worker():
                    return True
            elif resource_type == "api":
                if self.can_make_api_call():
                    return True
            
            time.sleep(0.1)  ***REMOVED*** 等待 100ms 后重试
        
        logger.warning(f"Timeout waiting for {resource_type} resource")
        return False

