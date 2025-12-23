***REMOVED*** Function Calling 系统快速开始

***REMOVED******REMOVED*** 5 分钟上手

这是一个基于 OpenAI Function Calling 格式的工具调用框架。

***REMOVED******REMOVED******REMOVED*** 1. 导入模块

```python
from skills import default_registry
```

***REMOVED******REMOVED******REMOVED*** 2. 查看可用函数

```python
***REMOVED*** 列出所有函数
print(default_registry.list_skills())
***REMOVED*** 输出: ['calculator', 'get_weather', 'get_current_time']

***REMOVED*** 获取函数定义（用于传递给 LLM，OpenAI Function Calling 格式）
functions = default_registry.get_all_functions()
```

***REMOVED******REMOVED******REMOVED*** 3. 执行函数调用

```python
***REMOVED*** 计算
result = default_registry.execute_skill(
    "calculator",
    {"expression": "10 * 5 + 20"}
)
print(result)  ***REMOVED*** 计算结果：10 * 5 + 20 = 70

***REMOVED*** 查询天气
result = default_registry.execute_skill(
    "get_weather",
    {"city": "北京"}
)
print(result)

***REMOVED*** 查询时间
result = default_registry.execute_skill(
    "get_current_time",
    {"timezone": "Asia/Shanghai"}
)
print(result)
```

***REMOVED******REMOVED******REMOVED*** 4. 运行示例

```bash
***REMOVED*** 运行基础示例
python -m skills.example

***REMOVED*** 运行测试
python -m skills.test_skills

***REMOVED*** 查看集成示例（需要 API key）
python -m skills.integration_example
```

***REMOVED******REMOVED*** 文件说明

- `base.py` - Function Calling 基类和注册表
- `calculator.py` - 计算器函数示例
- `weather.py` - 天气查询函数示例
- `time.py` - 时间查询函数示例
- `example.py` - 使用示例
- `test_skills.py` - 测试代码
- `integration_example.py` - API 集成示例
- `README.md` - 完整文档

***REMOVED******REMOVED*** 下一步

1. 阅读 `README.md` 了解详细用法
2. 查看 `example.py` 学习更多用法
3. 创建自己的函数（参考现有函数实现）

**注意**：虽然内部使用 "Skill" 命名，但这是一个标准的 Function Calling 系统，完全兼容 OpenAI 的 Function Calling API。
