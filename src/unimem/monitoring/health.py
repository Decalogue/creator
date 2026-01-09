"""
健康监控模块

提供系统健康状态监控和报告功能
"""

import time
import threading
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """健康状态"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """健康检查结果"""
    name: str
    status: HealthStatus
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    duration_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp,
            "duration_ms": self.duration_ms
        }


class HealthMonitor:
    """健康监控器
    
    管理多个健康检查，定期执行并报告系统健康状态
    """
    
    def __init__(self):
        """初始化健康监控器"""
        self._lock = threading.RLock()
        self._checks: Dict[str, Callable[[], HealthCheckResult]] = {}
        self._results: Dict[str, HealthCheckResult] = {}
        self._last_check_time: float = 0.0
        logger.info("HealthMonitor initialized")
    
    def register_check(self, name: str, check_func: Callable[[], HealthCheckResult]):
        """
        注册健康检查
        
        Args:
            name: 检查名称
            check_func: 检查函数，返回 HealthCheckResult
        """
        with self._lock:
            self._checks[name] = check_func
            logger.info(f"Registered health check: {name}")
    
    def unregister_check(self, name: str):
        """
        取消注册健康检查
        
        Args:
            name: 检查名称
        """
        with self._lock:
            if name in self._checks:
                del self._checks[name]
                if name in self._results:
                    del self._results[name]
                logger.info(f"Unregistered health check: {name}")
    
    def run_check(self, name: str) -> Optional[HealthCheckResult]:
        """
        运行指定的健康检查
        
        Args:
            name: 检查名称
            
        Returns:
            健康检查结果，如果检查不存在则返回 None
        """
        with self._lock:
            if name not in self._checks:
                return None
            
            check_func = self._checks[name]
        
        # 在锁外执行检查（避免阻塞）
        start_time = time.time()
        try:
            result = check_func()
            result.duration_ms = (time.time() - start_time) * 1000
        except Exception as e:
            logger.error(f"Health check {name} failed with exception: {e}", exc_info=True)
            result = HealthCheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Check failed with exception: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000
            )
        
        with self._lock:
            self._results[name] = result
        
        return result
    
    def run_all_checks(self) -> Dict[str, HealthCheckResult]:
        """
        运行所有健康检查
        
        Returns:
            所有检查结果的字典
        """
        with self._lock:
            check_names = list(self._checks.keys())
        
        results = {}
        for name in check_names:
            result = self.run_check(name)
            if result:
                results[name] = result
        
        with self._lock:
            self._last_check_time = time.time()
        
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取整体健康状态
        
        Returns:
            包含所有检查结果的健康状态报告
        """
        with self._lock:
            results = list(self._results.values())
        
        if not results:
            overall_status = HealthStatus.UNKNOWN
        else:
            # 判断整体状态：如果有任何 UNHEALTHY 则为 UNHEALTHY
            # 如果有任何 DEGRADED 则为 DEGRADED，否则为 HEALTHY
            statuses = [r.status for r in results]
            if HealthStatus.UNHEALTHY in statuses:
                overall_status = HealthStatus.UNHEALTHY
            elif HealthStatus.DEGRADED in statuses:
                overall_status = HealthStatus.DEGRADED
            elif all(s == HealthStatus.HEALTHY for s in statuses):
                overall_status = HealthStatus.HEALTHY
            else:
                overall_status = HealthStatus.UNKNOWN
        
        return {
            "status": overall_status.value,
            "checks": {name: result.to_dict() for name, result in self._results.items()},
            "last_check_time": self._last_check_time,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def get_check_result(self, name: str) -> Optional[HealthCheckResult]:
        """
        获取指定检查的结果
        
        Args:
            name: 检查名称
            
        Returns:
            健康检查结果，如果不存在则返回 None
        """
        with self._lock:
            return self._results.get(name)

