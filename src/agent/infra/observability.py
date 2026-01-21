"""
Agent 可观测性系统

提供 Agent 系统的指标收集、追踪和监控功能
支持前端 Dashboard 集成
"""
import time
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict, deque
from dataclasses import dataclass, field
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class QueryMetrics:
    """查询指标"""
    query_id: str
    timestamp: datetime
    success: bool
    latency: float
    iterations: int
    tokens_used: int = 0
    tools_called: int = 0
    error_type: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class ToolCallMetrics:
    """工具调用指标"""
    tool_name: str
    timestamp: datetime
    success: bool
    latency: float
    error_type: Optional[str] = None


@dataclass
class AgentMetrics:
    """Agent 总体指标"""
    total_queries: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    total_iterations: int = 0
    total_tokens: int = 0
    total_tool_calls: int = 0
    
    ***REMOVED*** 延迟统计
    avg_latency: float = 0.0
    min_latency: float = float('inf')
    max_latency: float = 0.0
    
    ***REMOVED*** 工具调用统计
    tool_call_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    tool_call_success: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    tool_call_failures: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    tool_avg_latency: Dict[str, float] = field(default_factory=lambda: defaultdict(float))
    
    ***REMOVED*** 错误统计
    error_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    
    ***REMOVED*** 时间窗口统计（最近1小时）
    recent_queries: deque = field(default_factory=lambda: deque(maxlen=1000))
    recent_tool_calls: deque = field(default_factory=lambda: deque(maxlen=5000))


class AgentObservability:
    """
    Agent 可观测性系统
    
    收集和追踪 Agent 系统的各项指标，支持：
    - 实时指标监控
    - 历史趋势分析
    - 错误追踪和分析
    - 性能瓶颈识别
    """
    
    def __init__(self, enable_tracing: bool = True):
        """
        初始化可观测性系统
        
        Args:
            enable_tracing: 是否启用详细追踪（会增加内存使用）
        """
        self.enable_tracing = enable_tracing
        self._lock = threading.RLock()
        self.metrics = AgentMetrics()
        
        ***REMOVED*** 追踪数据（可选）
        self.traces: List[Dict[str, Any]] = [] if enable_tracing else None
        self._trace_lock = threading.Lock()
        self._max_traces = 1000  ***REMOVED*** 最多保存1000条追踪记录
    
    def record_query(
        self,
        query_id: str,
        success: bool,
        latency: float,
        iterations: int = 0,
        tokens_used: int = 0,
        tools_called: int = 0,
        error_type: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """
        记录查询指标
        
        Args:
            query_id: 查询唯一标识
            success: 是否成功
            latency: 延迟（秒）
            iterations: 迭代次数
            tokens_used: 使用的 tokens 数
            tools_called: 工具调用次数
            error_type: 错误类型（如果失败）
            error_message: 错误消息（如果失败）
        """
        with self._lock:
            self.metrics.total_queries += 1
            if success:
                self.metrics.successful_queries += 1
            else:
                self.metrics.failed_queries += 1
                if error_type:
                    self.metrics.error_counts[error_type] += 1
            
            ***REMOVED*** 更新延迟统计
            if self.metrics.total_queries == 1:
                self.metrics.avg_latency = latency
                self.metrics.min_latency = latency
                self.metrics.max_latency = latency
            else:
                ***REMOVED*** 移动平均
                self.metrics.avg_latency = (
                    self.metrics.avg_latency * (self.metrics.total_queries - 1) + latency
                ) / self.metrics.total_queries
                self.metrics.min_latency = min(self.metrics.min_latency, latency)
                self.metrics.max_latency = max(self.metrics.max_latency, latency)
            
            ***REMOVED*** 更新其他统计
            self.metrics.total_iterations += iterations
            self.metrics.total_tokens += tokens_used
            self.metrics.total_tool_calls += tools_called
            
            ***REMOVED*** 记录到时间窗口
            query_metric = QueryMetrics(
                query_id=query_id,
                timestamp=datetime.now(),
                success=success,
                latency=latency,
                iterations=iterations,
                tokens_used=tokens_used,
                tools_called=tools_called,
                error_type=error_type,
                error_message=error_message
            )
            self.metrics.recent_queries.append(query_metric)
            
            ***REMOVED*** 追踪（如果启用）
            if self.enable_tracing and self.traces is not None:
                with self._trace_lock:
                    if len(self.traces) >= self._max_traces:
                        self.traces.pop(0)  ***REMOVED*** 移除最旧的
                    self.traces.append({
                        "type": "query",
                        "query_id": query_id,
                        "timestamp": datetime.now().isoformat(),
                        "success": success,
                        "latency": latency,
                        "iterations": iterations,
                        "tokens_used": tokens_used,
                        "tools_called": tools_called,
                        "error_type": error_type,
                    })
    
    def record_tool_call(
        self,
        tool_name: str,
        success: bool,
        latency: float,
        error_type: Optional[str] = None
    ):
        """
        记录工具调用指标
        
        Args:
            tool_name: 工具名称
            success: 是否成功
            latency: 延迟（秒）
            error_type: 错误类型（如果失败）
        """
        with self._lock:
            self.metrics.tool_call_counts[tool_name] += 1
            
            if success:
                self.metrics.tool_call_success[tool_name] += 1
            else:
                self.metrics.tool_call_failures[tool_name] += 1
                if error_type:
                    self.metrics.error_counts[f"tool_{error_type}"] += 1
            
            ***REMOVED*** 更新工具平均延迟（移动平均）
            count = self.metrics.tool_call_counts[tool_name]
            if count == 1:
                self.metrics.tool_avg_latency[tool_name] = latency
            else:
                current_avg = self.metrics.tool_avg_latency[tool_name]
                self.metrics.tool_avg_latency[tool_name] = (
                    current_avg * (count - 1) + latency
                ) / count
            
            ***REMOVED*** 记录到时间窗口
            tool_metric = ToolCallMetrics(
                tool_name=tool_name,
                timestamp=datetime.now(),
                success=success,
                latency=latency,
                error_type=error_type
            )
            self.metrics.recent_tool_calls.append(tool_metric)
            
            ***REMOVED*** 追踪（如果启用）
            if self.enable_tracing and self.traces is not None:
                with self._trace_lock:
                    if len(self.traces) >= self._max_traces:
                        self.traces.pop(0)
                    self.traces.append({
                        "type": "tool_call",
                        "tool_name": tool_name,
                        "timestamp": datetime.now().isoformat(),
                        "success": success,
                        "latency": latency,
                        "error_type": error_type,
                    })
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """
        获取 Dashboard 所需指标
        
        Returns:
            包含所有关键指标的字典，适合前端展示
        """
        with self._lock:
            ***REMOVED*** 计算成功率
            success_rate = (
                self.metrics.successful_queries / self.metrics.total_queries
                if self.metrics.total_queries > 0 else 0.0
            )
            
            ***REMOVED*** 计算平均迭代次数
            avg_iterations = (
                self.metrics.total_iterations / self.metrics.total_queries
                if self.metrics.total_queries > 0 else 0.0
            )
            
            ***REMOVED*** 计算平均 tokens
            avg_tokens = (
                self.metrics.total_tokens / self.metrics.total_queries
                if self.metrics.total_queries > 0 else 0.0
            )
            
            ***REMOVED*** 工具调用统计
            tool_stats = {}
            for tool_name in self.metrics.tool_call_counts:
                total = self.metrics.tool_call_counts[tool_name]
                success = self.metrics.tool_call_success[tool_name]
                failures = self.metrics.tool_call_failures[tool_name]
                tool_stats[tool_name] = {
                    "total_calls": total,
                    "successful_calls": success,
                    "failed_calls": failures,
                    "success_rate": success / total if total > 0 else 0.0,
                    "avg_latency": self.metrics.tool_avg_latency[tool_name],
                }
            
            ***REMOVED*** 最近1小时的统计（从 recent_queries 计算）
            recent_queries_list = list(self.metrics.recent_queries)
            recent_1h = [
                q for q in recent_queries_list
                if (datetime.now() - q.timestamp).total_seconds() <= 3600
            ]
            
            recent_success_rate = (
                sum(1 for q in recent_1h if q.success) / len(recent_1h)
                if recent_1h else 0.0
            )
            recent_avg_latency = (
                sum(q.latency for q in recent_1h) / len(recent_1h)
                if recent_1h else 0.0
            )
            
            return {
                ***REMOVED*** 总体统计
                "total_queries": self.metrics.total_queries,
                "successful_queries": self.metrics.successful_queries,
                "failed_queries": self.metrics.failed_queries,
                "success_rate": success_rate,
                
                ***REMOVED*** 性能指标
                "avg_latency": self.metrics.avg_latency,
                "min_latency": self.metrics.min_latency if self.metrics.min_latency != float('inf') else 0.0,
                "max_latency": self.metrics.max_latency,
                "avg_iterations": avg_iterations,
                "avg_tokens": avg_tokens,
                
                ***REMOVED*** 工具调用统计
                "total_tool_calls": self.metrics.total_tool_calls,
                "tool_stats": tool_stats,
                
                ***REMOVED*** 错误统计
                "error_breakdown": dict(self.metrics.error_counts),
                
                ***REMOVED*** 最近1小时统计
                "recent_1h": {
                    "queries": len(recent_1h),
                    "success_rate": recent_success_rate,
                    "avg_latency": recent_avg_latency,
                },
                
                ***REMOVED*** 时间戳
                "timestamp": datetime.now().isoformat(),
            }
    
    def get_traces(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取追踪记录
        
        Args:
            limit: 返回的最大记录数
        
        Returns:
            追踪记录列表
        """
        if not self.enable_tracing or self.traces is None:
            return []
        
        with self._trace_lock:
            return list(self.traces[-limit:])
    
    def export_metrics(self, file_path: str):
        """
        导出指标到文件（JSON 格式）
        
        Args:
            file_path: 文件路径
        """
        metrics = self.get_dashboard_metrics()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"指标已导出到: {file_path}")
    
    def reset_metrics(self):
        """重置所有指标（用于测试或重新开始）"""
        with self._lock:
            self.metrics = AgentMetrics()
            if self.traces is not None:
                with self._trace_lock:
                    self.traces.clear()
        logger.info("指标已重置")


***REMOVED*** 全局可观测性实例
_observability_instance: Optional[AgentObservability] = None
_observability_lock = threading.Lock()


def get_agent_observability(
    enable_tracing: bool = True,
    reset: bool = False
) -> AgentObservability:
    """
    获取全局 Agent 可观测性实例（单例模式）
    
    Args:
        enable_tracing: 是否启用追踪
        reset: 是否重置现有实例
    
    Returns:
        AgentObservability 实例
    """
    global _observability_instance
    
    with _observability_lock:
        if _observability_instance is None or reset:
            _observability_instance = AgentObservability(enable_tracing=enable_tracing)
        
        return _observability_instance
