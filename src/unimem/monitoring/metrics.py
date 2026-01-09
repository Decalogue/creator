"""
指标收集模块

收集和聚合系统运行指标，支持 Prometheus 格式导出
"""

import time
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class MetricValue:
    """指标值"""
    value: float
    timestamp: float = field(default_factory=time.time)
    labels: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "value": self.value,
            "timestamp": self.timestamp,
            "labels": self.labels
        }


@dataclass
class CounterMetric:
    """计数器指标"""
    name: str
    value: float = 0.0
    labels: Dict[str, str] = field(default_factory=dict)
    
    def increment(self, amount: float = 1.0):
        """增加计数"""
        self.value += amount
    
    def reset(self):
        """重置计数"""
        self.value = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "type": "counter",
            "value": self.value,
            "labels": self.labels
        }


@dataclass
class GaugeMetric:
    """仪表盘指标（可增可减）"""
    name: str
    value: float = 0.0
    labels: Dict[str, str] = field(default_factory=dict)
    
    def set(self, value: float):
        """设置值"""
        self.value = value
    
    def increment(self, amount: float = 1.0):
        """增加"""
        self.value += amount
    
    def decrement(self, amount: float = 1.0):
        """减少"""
        self.value -= amount
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "type": "gauge",
            "value": self.value,
            "labels": self.labels
        }


@dataclass
class HistogramMetric:
    """直方图指标"""
    name: str
    buckets: List[float] = field(default_factory=lambda: [0.1, 0.5, 1.0, 2.5, 5.0, 10.0])
    values: List[float] = field(default_factory=list)
    labels: Dict[str, str] = field(default_factory=dict)
    
    def observe(self, value: float):
        """记录观察值"""
        self.values.append(value)
        # 限制历史记录数量（避免内存溢出）
        if len(self.values) > 10000:
            self.values = self.values[-5000:]
    
    def get_count(self) -> int:
        """获取总计数"""
        return len(self.values)
    
    def get_sum(self) -> float:
        """获取总和"""
        return sum(self.values)
    
    def get_bucket_counts(self) -> Dict[str, int]:
        """获取各桶的计数"""
        counts = {str(bucket): 0 for bucket in self.buckets}
        counts["+Inf"] = 0
        
        for value in self.values:
            for bucket in sorted(self.buckets):
                if value <= bucket:
                    counts[str(bucket)] += 1
                    break
            else:
                counts["+Inf"] += 1
        
        return counts
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "type": "histogram",
            "count": self.get_count(),
            "sum": self.get_sum(),
            "buckets": self.get_bucket_counts(),
            "labels": self.labels
        }


class MetricsCollector:
    """指标收集器
    
    收集和聚合系统运行指标，支持多种指标类型
    """
    
    def __init__(self):
        """初始化指标收集器"""
        self._lock = threading.RLock()
        self._counters: Dict[str, CounterMetric] = {}
        self._gauges: Dict[str, GaugeMetric] = {}
        self._histograms: Dict[str, HistogramMetric] = {}
        logger.info("MetricsCollector initialized")
    
    def counter(self, name: str, labels: Optional[Dict[str, str]] = None) -> CounterMetric:
        """
        获取或创建计数器指标
        
        Args:
            name: 指标名称
            labels: 标签字典
            
        Returns:
            CounterMetric 实例
        """
        labels = labels or {}
        key = self._make_key(name, labels)
        
        with self._lock:
            if key not in self._counters:
                self._counters[key] = CounterMetric(name=name, labels=labels)
            return self._counters[key]
    
    def gauge(self, name: str, labels: Optional[Dict[str, str]] = None) -> GaugeMetric:
        """
        获取或创建仪表盘指标
        
        Args:
            name: 指标名称
            labels: 标签字典
            
        Returns:
            GaugeMetric 实例
        """
        labels = labels or {}
        key = self._make_key(name, labels)
        
        with self._lock:
            if key not in self._gauges:
                self._gauges[key] = GaugeMetric(name=name, labels=labels)
            return self._gauges[key]
    
    def histogram(self, name: str, labels: Optional[Dict[str, str]] = None) -> HistogramMetric:
        """
        获取或创建直方图指标
        
        Args:
            name: 指标名称
            labels: 标签字典
            
        Returns:
            HistogramMetric 实例
        """
        labels = labels or {}
        key = self._make_key(name, labels)
        
        with self._lock:
            if key not in self._histograms:
                self._histograms[key] = HistogramMetric(name=name, labels=labels)
            return self._histograms[key]
    
    def _make_key(self, name: str, labels: Dict[str, str]) -> str:
        """生成指标键"""
        if labels:
            label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
            return f"{name}{{{label_str}}}"
        return name
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """
        获取所有指标
        
        Returns:
            包含所有指标的字典
        """
        with self._lock:
            return {
                "counters": [metric.to_dict() for metric in self._counters.values()],
                "gauges": [metric.to_dict() for metric in self._gauges.values()],
                "histograms": [metric.to_dict() for metric in self._histograms.values()],
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
    
    def get_prometheus_format(self) -> str:
        """
        获取 Prometheus 格式的指标字符串
        
        Returns:
            Prometheus 格式的指标文本
        """
        lines = []
        
        with self._lock:
            # 计数器
            for metric in self._counters.values():
                labels_str = ""
                if metric.labels:
                    labels_str = "{" + ",".join(f'{k}="{v}"' for k, v in metric.labels.items()) + "}"
                lines.append(f"unimem_{metric.name}{labels_str} {metric.value}")
            
            # 仪表盘
            for metric in self._gauges.values():
                labels_str = ""
                if metric.labels:
                    labels_str = "{" + ",".join(f'{k}="{v}"' for k, v in metric.labels.items()) + "}"
                lines.append(f"unimem_{metric.name}{labels_str} {metric.value}")
            
            # 直方图
            for metric in self._histograms.values():
                bucket_counts = metric.get_bucket_counts()
                for bucket, count in bucket_counts.items():
                    labels_str = f'le="{bucket}"'
                    if metric.labels:
                        labels_str = "{" + ",".join(f'{k}="{v}"' for k, v in metric.labels.items()) + f',{labels_str}}}'
                    lines.append(f"unimem_{metric.name}_bucket{labels_str} {count}")
                
                labels_str = ""
                if metric.labels:
                    labels_str = "{" + ",".join(f'{k}="{v}"' for k, v in metric.labels.items()) + "}"
                lines.append(f"unimem_{metric.name}_count{labels_str} {metric.get_count()}")
                lines.append(f"unimem_{metric.name}_sum{labels_str} {metric.get_sum()}")
        
        return "\n".join(lines)
    
    def reset(self):
        """重置所有指标"""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()


# 全局指标收集器实例
_metrics_collector: Optional[MetricsCollector] = None
_collector_lock = threading.Lock()


def get_metrics_collector() -> MetricsCollector:
    """
    获取全局指标收集器实例（单例模式）
    
    Returns:
        MetricsCollector 实例
    """
    global _metrics_collector
    
    if _metrics_collector is None:
        with _collector_lock:
            if _metrics_collector is None:
                _metrics_collector = MetricsCollector()
    
    return _metrics_collector

