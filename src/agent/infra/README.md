***REMOVED*** Agent Infrastructure Layer

Agent 基础设施层，提供可观测性、实验管理、性能优化和容错恢复功能。

***REMOVED******REMOVED*** 快速开始

***REMOVED******REMOVED******REMOVED*** 1. 可观测性（Observability）

自动收集 Agent 指标，无需额外代码：

```python
from react import ReActAgent

***REMOVED*** 创建 Agent（默认启用可观测性）
agent = ReActAgent(enable_observability=True)

***REMOVED*** 正常运行，指标自动收集
result = agent.run("创建一个文件")

***REMOVED*** 查看指标
from agent.infra.observability import get_agent_observability
observability = get_agent_observability()
metrics = observability.get_dashboard_metrics()
print(metrics)
```

***REMOVED******REMOVED******REMOVED*** 2. 实验管理（Experimentation）

对比不同策略的效果：

```python
from agent.infra.experiment import ExperimentManager

manager = ExperimentManager()

***REMOVED*** 创建实验
experiment = manager.create_experiment(
    name="rewrite_strategy_test",
    description="测试不同重写策略",
    variants=[
        {"name": "standard", "params": {"strategy": "standard"}},
        {"name": "aggressive", "params": {"strategy": "aggressive"}},
    ],
    metrics=["rewrite_success_rate", "quality_improvement"]
)

***REMOVED*** 运行实验
def test_rewrite(strategy: str):
    ***REMOVED*** 你的测试代码
    return {"rewrite_success_rate": 0.8, "quality_improvement": 0.5}

results = manager.run_experiment(
    "rewrite_strategy_test",
    test_fn=test_rewrite
)

***REMOVED*** 对比结果
comparison = manager.compare_results("rewrite_strategy_test")
print(comparison)
```

***REMOVED******REMOVED******REMOVED*** 3. 缓存（Cache）

减少重复计算：

```python
from agent.infra.cache import get_agent_cache, cached

cache = get_agent_cache()

***REMOVED*** 手动使用缓存
context = cache.get_entity_context(entities=["林墨", "艾薇"])
if not context:
    context = generate_context(entities)
    cache.set_entity_context(entities, context)

***REMOVED*** 使用装饰器
@cached(cache_type="entity_context")
def get_entity_context(entities: List[str]) -> str:
    ***REMOVED*** 自动缓存
    return generate_context(entities)
```

***REMOVED******REMOVED******REMOVED*** 4. 容错（Resilience）

自动重试和熔断：

```python
from agent.infra.resilience import ResilienceManager, CircuitBreaker, RetryStrategy

resilience = ResilienceManager(
    circuit_breaker=CircuitBreaker(failure_threshold=5),
    retry_strategy=RetryStrategy(max_retries=3)
)

***REMOVED*** 带容错的函数调用
def call_llm(prompt: str):
    return llm_client(prompt)

result = resilience.execute(call_llm, prompt="Hello")
```

***REMOVED******REMOVED*** 前端集成

Dashboard API 已创建在 `api/dashboard.py`，可以通过 FastAPI 提供服务：

```python
from fastapi import FastAPI
from api.dashboard import router

app = FastAPI()
app.include_router(router)

***REMOVED*** 访问指标: GET /api/dashboard/metrics
***REMOVED*** 访问缓存统计: GET /api/dashboard/cache/stats
***REMOVED*** 访问实验: GET /api/dashboard/experiments
```

前端可以通过这些 API 获取实时数据并展示 Dashboard。

***REMOVED******REMOVED*** 架构设计

```
Agent Infra Layer
├── Observability (可观测性)
│   ├── 指标收集（查询、工具调用）
│   ├── 追踪记录
│   └── Dashboard 数据导出
├── Experiment (实验管理)
│   ├── A/B 测试
│   ├── 结果对比
│   └── 实验历史
├── Cache (缓存)
│   ├── 实体上下文缓存
│   ├── 质量检查缓存
│   └── Prompt 缓存
└── Resilience (容错)
    ├── Circuit Breaker
    ├── Retry Strategy
    └── 优雅降级
```

***REMOVED******REMOVED*** 优势

1. **零侵入**：大部分功能自动工作，不需要修改现有代码
2. **可插拔**：可以按需启用/禁用功能
3. **前端就绪**：Dashboard API 已准备好，可以直接集成到前端
4. **生产级**：线程安全、错误处理、性能优化

***REMOVED******REMOVED*** 下一步

1. 在前端项目中集成 Dashboard API
2. 可视化 Agent 指标和趋势
3. 使用实验管理框架优化策略
4. 根据指标数据持续改进系统
