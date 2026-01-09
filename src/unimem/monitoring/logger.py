"""
结构化日志模块

提供结构化日志记录功能，支持 JSON 格式输出
"""

import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional
from enum import Enum


class LogLevel(Enum):
    """日志级别"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class StructuredFormatter(logging.Formatter):
    """结构化日志格式化器
    
    将日志记录格式化为 JSON 格式，便于日志聚合和分析
    """
    
    def __init__(self, include_timestamp: bool = True, include_level: bool = True):
        """
        初始化结构化格式化器
        
        Args:
            include_timestamp: 是否包含时间戳
            include_level: 是否包含日志级别
        """
        super().__init__()
        self.include_timestamp = include_timestamp
        self.include_level = include_level
    
    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日志记录为 JSON
        
        Args:
            record: 日志记录
            
        Returns:
            JSON 格式的日志字符串
        """
        log_data: Dict[str, Any] = {
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if self.include_timestamp:
            log_data["timestamp"] = datetime.utcnow().isoformat() + "Z"
        
        if self.include_level:
            log_data["level"] = record.levelname
        
        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # 添加额外的上下文信息（如果有）
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data, ensure_ascii=False)
    
    def formatException(self, exc_info) -> str:
        """格式化异常信息"""
        import traceback
        return traceback.format_exception(*exc_info)


class StructuredLogger:
    """结构化日志记录器包装器"""
    
    def __init__(self, logger: logging.Logger):
        """
        初始化结构化日志记录器
        
        Args:
            logger: Python logging.Logger 实例
        """
        self.logger = logger
    
    def _log(self, level: int, msg: str, extra_fields: Optional[Dict[str, Any]] = None, **kwargs):
        """内部日志记录方法"""
        if extra_fields:
            # 将额外字段添加到日志记录中
            extra = {"extra_fields": extra_fields}
            extra.update(kwargs)
            self.logger.log(level, msg, extra=extra, **kwargs)
        else:
            self.logger.log(level, msg, **kwargs)
    
    def debug(self, msg: str, extra_fields: Optional[Dict[str, Any]] = None, **kwargs):
        """记录 DEBUG 级别日志"""
        self._log(logging.DEBUG, msg, extra_fields, **kwargs)
    
    def info(self, msg: str, extra_fields: Optional[Dict[str, Any]] = None, **kwargs):
        """记录 INFO 级别日志"""
        self._log(logging.INFO, msg, extra_fields, **kwargs)
    
    def warning(self, msg: str, extra_fields: Optional[Dict[str, Any]] = None, **kwargs):
        """记录 WARNING 级别日志"""
        self._log(logging.WARNING, msg, extra_fields, **kwargs)
    
    def error(self, msg: str, extra_fields: Optional[Dict[str, Any]] = None, exc_info=None, **kwargs):
        """记录 ERROR 级别日志"""
        if extra_fields:
            kwargs["extra"] = {"extra_fields": extra_fields}
        self.logger.error(msg, exc_info=exc_info, **kwargs)
    
    def critical(self, msg: str, extra_fields: Optional[Dict[str, Any]] = None, **kwargs):
        """记录 CRITICAL 级别日志"""
        self._log(logging.CRITICAL, msg, extra_fields, **kwargs)
    
    def log_operation(
        self,
        operation: str,
        duration: float,
        success: bool = True,
        **extra_fields
    ):
        """记录操作日志（带结构化字段）"""
        level = logging.INFO if success else logging.ERROR
        status = "success" if success else "failed"
        
        self._log(
            level,
            f"Operation {operation} {status}",
            extra_fields={
                "operation": operation,
                "duration_seconds": duration,
                "status": status,
                **extra_fields
            }
        )


def setup_structured_logging(
    level: str = "INFO",
    format_type: str = "json",
    log_file: Optional[str] = None
) -> None:
    """
    设置结构化日志
    
    Args:
        level: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
        format_type: 格式类型（"json" 或 "text"）
        log_file: 日志文件路径（可选，如果不提供则输出到控制台）
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # 创建根日志记录器
    root_logger = logging.getLogger("unimem")
    root_logger.setLevel(log_level)
    
    # 清除现有的处理器
    root_logger.handlers.clear()
    
    # 创建格式化器
    if format_type == "json":
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # 创建处理器
    if log_file:
        handler = logging.FileHandler(log_file, encoding='utf-8')
    else:
        handler = logging.StreamHandler()
    
    handler.setFormatter(formatter)
    handler.setLevel(log_level)
    
    root_logger.addHandler(handler)
    
    # 设置子模块的日志级别
    logging.getLogger("unimem").setLevel(log_level)
    logging.getLogger("unimem.core").setLevel(log_level)
    logging.getLogger("unimem.adapters").setLevel(log_level)
    logging.getLogger("unimem.storage").setLevel(log_level)
    logging.getLogger("unimem.retrieval").setLevel(log_level)


def get_logger(name: str) -> StructuredLogger:
    """
    获取结构化日志记录器
    
    Args:
        name: 日志记录器名称（通常是模块名）
        
    Returns:
        StructuredLogger 实例
    """
    logger = logging.getLogger(f"unimem.{name}")
    return StructuredLogger(logger)

