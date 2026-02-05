# UniMem 监控和可观测性模块

提供结构化日志、指标收集和健康监控功能。

## 功能特性

### 1. 结构化日志 (logger.py)

- **JSON 格式输出**：便于日志聚合和分析
- **上下文字段**：支持添加额外的结构化字段
- **操作日志**：自动记录操作耗时和状态

#### 使用示例

```python
from unimem.monitoring import setup_structured_logging, get_logger

# 设置结构化日志
setup_structured_logging(level="INFO", format_type="json")

# 获取日志记录器
logger = get_logger("core")

# 基本日志
logger.info("System initialized")

# 带结构化字段的日志
logger.log_operation(
    operation="retain",
    duration=0.123,
    success=True,
    memory_id="mem_123"
)
```

### 2. 指标收集 (metrics.py)

- **多种指标类型**：Counter（计数器）、Gauge（仪表盘）、Histogram（直方图）
- **Prometheus 格式**：支持导出 Prometheus 格式的指标
- **线程安全**：所有操作都是线程安全的

#### 使用示例

```python
from unimem.monitoring import get_metrics_collector

collector = get_metrics_collector()

# 计数器
counter = collector.counter("operations_total", labels={"operation": "retain"})
counter.increment()

# 仪表盘
gauge = collector.gauge("memory_usage_bytes")
gauge.set(1024 * 1024)

# 直方图（记录操作耗时）
histogram = collector.histogram("operation_duration_seconds", labels={"operation": "recall"})
histogram.observe(0.123)

# 获取所有指标
all_metrics = collector.get_all_metrics()

# 获取 Prometheus 格式
prometheus_text = collector.get_prometheus_format()
```

### 3. 健康监控 (health.py)

- **多检查支持**：可注册多个健康检查
- **状态报告**：HEALTHY/DEGRADED/UNHEALTHY/UNKNOWN
- **结果缓存**：避免频繁执行检查

#### 使用示例

```python
from unimem.monitoring import HealthMonitor, HealthStatus, HealthCheckResult

monitor = HealthMonitor()

# 注册健康检查
def check_database():
    # 执行检查逻辑
    is_healthy = check_db_connection()
    return HealthCheckResult(
        name="database",
        status=HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY,
        message="Database connection OK" if is_healthy else "Database connection failed"
    )

monitor.register_check("database", check_database)

# 运行所有检查
results = monitor.run_all_checks()

# 获取整体状态
status = monitor.get_status()
```

## 集成到 UniMem

监控模块已准备好集成到 UniMem 核心系统。可以在 `core.py` 中使用：

```python
from unimem.monitoring import get_logger, get_metrics_collector

logger = get_logger("core")
metrics = get_metrics_collector()

# 在操作中使用
def retain(...):
    counter = metrics.counter("unimem_operations_total", labels={"operation": "retain"})
    histogram = metrics.histogram("unimem_operation_duration_seconds", labels={"operation": "retain"})
    
    start = time.time()
    try:
        result = ...
        counter.increment()
        histogram.observe(time.time() - start)
        logger.log_operation("retain", time.time() - start, success=True)
        return result
    except Exception as e:
        histogram.observe(time.time() - start)
        logger.error("retain failed", exc_info=e)
        raise
```

## 配置

通过环境变量配置：

```bash
# 日志级别
export UNIMEM_LOG_LEVEL=INFO

# 日志格式（json 或 text）
export UNIMEM_LOG_FORMAT=json

# 日志文件路径（可选）
export UNIMEM_LOG_FILE=/var/log/unimem.log
```

