***REMOVED*** Puppeteer 学习与迭代模块

***REMOVED******REMOVED*** 概述

本模块负责从实际创作任务和优质小说短剧数据中学习，持续优化动态编排和记忆系统。

***REMOVED******REMOVED*** 模块结构

***REMOVED******REMOVED******REMOVED*** 1. 数据收集（feedback_collector.py）
- 收集任务执行数据
- 收集用户反馈
- 数据清洗和预处理

***REMOVED******REMOVED******REMOVED*** 2. 任务分析（task_analyzer.py）
- 分析任务执行模式
- 评估创作质量
- 提取成功/失败因素

***REMOVED******REMOVED******REMOVED*** 3. 模式提取（pattern_extractor.py）
- 从小说数据中提取模式
- 结构化表示模式
- 模式质量评估

***REMOVED******REMOVED******REMOVED*** 4. 策略更新（strategy_updater.py）
- 更新 Policy 策略
- 优化 Agent 选择
- 调整决策规则

***REMOVED******REMOVED*** 使用示例

***REMOVED******REMOVED******REMOVED*** 收集任务执行数据
```python
from learning.feedback_collector import FeedbackCollector

collector = FeedbackCollector()
collector.collect_task_execution(task_id, execution_log)
```

***REMOVED******REMOVED******REMOVED*** 分析任务模式
```python
from learning.task_analyzer import TaskAnalyzer

analyzer = TaskAnalyzer()
patterns = analyzer.analyze_task_execution(execution_log, quality_score)
```

***REMOVED******REMOVED******REMOVED*** 更新策略
```python
from learning.strategy_updater import StrategyUpdater

updater = StrategyUpdater()
updater.update_policy_from_feedback(patterns)
```

***REMOVED******REMOVED*** 数据格式

***REMOVED******REMOVED******REMOVED*** 任务执行日志
```json
{
  "task_id": "task_001",
  "task_type": "novel",
  "start_time": "2026-01-06T10:00:00",
  "end_time": "2026-01-06T10:30:00",
  "agent_sequence": [
    {"agent": "planning", "timestamp": "...", "reason": "..."},
    {"agent": "reasoning", "timestamp": "...", "reason": "..."}
  ],
  "memory_interactions": {
    "retrieved": [
      {"query": "...", "count": 5, "timestamp": "..."}
    ],
    "stored": [
      {"memory_id": "...", "timestamp": "..."}
    ]
  },
  "quality_score": 0.85,
  "user_feedback": "很好"
}
```

