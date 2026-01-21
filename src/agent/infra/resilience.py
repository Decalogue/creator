"""
容错和恢复机制

提供 Circuit Breaker、重试策略、优雅降级等功能
"""
import time
import threading
from typing import Callable, TypeVar, Optional, Any, Dict
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CircuitState(Enum):
    """熔断器状态"""
    CLOSED = "closed"  ***REMOVED*** 关闭（正常）
    OPEN = "open"  ***REMOVED*** 打开（熔断）
    HALF_OPEN = "half_open"  ***REMOVED*** 半开（测试中）


class CircuitBreaker:
    """
    熔断器实现
    
    当错误率超过阈值时，自动熔断，避免级联故障
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max_calls: int = 3
    ):
        """
        初始化熔断器
        
        Args:
            failure_threshold: 失败阈值（连续失败次数）
            recovery_timeout: 恢复超时时间（秒）
            half_open_max_calls: 半开状态下的最大测试调用数
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self._lock = threading.Lock()
    
    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        通过熔断器调用函数
        
        Args:
            func: 要调用的函数
            *args, **kwargs: 函数参数
        
        Returns:
            函数返回值
        
        Raises:
            CircuitBreakerOpenError: 如果熔断器打开
        """
        with self._lock:
            ***REMOVED*** 检查状态
            if self.state == CircuitState.OPEN:
                ***REMOVED*** 检查是否可以尝试恢复
                if self.last_failure_time:
                    time_since_failure = (datetime.now() - self.last_failure_time).total_seconds()
                    if time_since_failure >= self.recovery_timeout:
                        ***REMOVED*** 进入半开状态
                        self.state = CircuitState.HALF_OPEN
                        self.success_count = 0
                        logger.info("熔断器进入半开状态，开始测试恢复")
                    else:
                        raise CircuitBreakerOpenError(
                            f"熔断器打开，还需等待 {self.recovery_timeout - time_since_failure:.1f} 秒"
                        )
        
        ***REMOVED*** 执行调用
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """成功回调"""
        with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.half_open_max_calls:
                    ***REMOVED*** 恢复成功，关闭熔断器
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    logger.info("熔断器恢复成功，状态：关闭")
            elif self.state == CircuitState.CLOSED:
                ***REMOVED*** 重置失败计数
                self.failure_count = 0
    
    def _on_failure(self):
        """失败回调"""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.state == CircuitState.HALF_OPEN:
                ***REMOVED*** 半开状态下失败，立即打开
                self.state = CircuitState.OPEN
                logger.warning("熔断器在半开状态下失败，重新打开")
            elif self.state == CircuitState.CLOSED:
                if self.failure_count >= self.failure_threshold:
                    ***REMOVED*** 达到阈值，打开熔断器
                    self.state = CircuitState.OPEN
                    logger.warning(f"熔断器打开：连续失败 {self.failure_count} 次")
    
    def get_state(self) -> Dict[str, Any]:
        """获取熔断器状态"""
        with self._lock:
            return {
                "state": self.state.value,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            }


class CircuitBreakerOpenError(Exception):
    """熔断器打开异常"""
    pass


class RetryStrategy:
    """
    重试策略
    
    支持指数退避、最大重试次数等
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        retry_on_exceptions: tuple = (Exception,)
    ):
        """
        初始化重试策略
        
        Args:
            max_retries: 最大重试次数
            initial_delay: 初始延迟（秒）
            max_delay: 最大延迟（秒）
            exponential_base: 指数退避基数
            retry_on_exceptions: 需要重试的异常类型
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.retry_on_exceptions = retry_on_exceptions
    
    def execute(
        self,
        func: Callable[..., T],
        *args,
        **kwargs
    ) -> T:
        """
        执行函数，带重试
        
        Args:
            func: 要执行的函数
            *args, **kwargs: 函数参数
        
        Returns:
            函数返回值
        
        Raises:
            最后一次重试的异常
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except self.retry_on_exceptions as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    ***REMOVED*** 计算延迟（指数退避）
                    delay = min(
                        self.initial_delay * (self.exponential_base ** attempt),
                        self.max_delay
                    )
                    logger.warning(
                        f"函数调用失败（尝试 {attempt + 1}/{self.max_retries + 1}）：{e}，"
                        f"{delay:.2f} 秒后重试"
                    )
                    time.sleep(delay)
                else:
                    logger.error(f"函数调用失败，已达到最大重试次数: {e}")
        
        ***REMOVED*** 所有重试都失败
        raise last_exception


class ResilienceManager:
    """
    容错管理器
    
    整合 Circuit Breaker 和 Retry Strategy
    """
    
    def __init__(
        self,
        circuit_breaker: Optional[CircuitBreaker] = None,
        retry_strategy: Optional[RetryStrategy] = None
    ):
        """
        初始化容错管理器
        
        Args:
            circuit_breaker: 熔断器（可选）
            retry_strategy: 重试策略（可选）
        """
        self.circuit_breaker = circuit_breaker or CircuitBreaker()
        self.retry_strategy = retry_strategy or RetryStrategy()
    
    def execute(
        self,
        func: Callable[..., T],
        *args,
        **kwargs
    ) -> T:
        """
        通过容错管理器执行函数
        
        先通过熔断器，然后应用重试策略
        
        Args:
            func: 要执行的函数
            *args, **kwargs: 函数参数
        
        Returns:
            函数返回值
        """
        ***REMOVED*** 先通过熔断器
        def circuit_breaker_wrapper():
            return self.circuit_breaker.call(func, *args, **kwargs)
        
        ***REMOVED*** 然后应用重试策略
        return self.retry_strategy.execute(circuit_breaker_wrapper)
    
    def get_status(self) -> Dict[str, Any]:
        """获取容错管理器状态"""
        return {
            "circuit_breaker": self.circuit_breaker.get_state(),
            "retry_strategy": {
                "max_retries": self.retry_strategy.max_retries,
                "initial_delay": self.retry_strategy.initial_delay,
            }
        }
