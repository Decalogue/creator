***REMOVED*** Function Calling 系统使用指南

***REMOVED******REMOVED*** 简介

这是一个基于 OpenAI Function Calling 格式的工具调用框架。它提供了统一的接口来定义和执行可被 LLM 调用的函数，使 AI 助手能够使用外部工具和功能。

**注意**：虽然内部使用 "Skill" 命名，但这是一个标准的 Function Calling 系统，完全兼容 OpenAI 的 Function Calling API。

***REMOVED******REMOVED*** 目录结构

```
skills/
├── __init__.py          ***REMOVED*** 模块导出和自动注册
├── base.py              ***REMOVED*** Function 基类和注册表
├── calculator.py        ***REMOVED*** 计算器函数示例
├── weather.py           ***REMOVED*** 天气查询函数示例
├── time.py              ***REMOVED*** 时间查询函数示例
├── example.py           ***REMOVED*** 使用示例
└── README.md            ***REMOVED*** 本文档
```

***REMOVED******REMOVED*** 快速开始

***REMOVED******REMOVED******REMOVED*** 1. 基本使用

```python
from skills import default_registry

***REMOVED*** 获取所有可用的函数定义（用于传递给 LLM）
functions = default_registry.get_all_functions()

***REMOVED*** 执行函数调用
result = default_registry.execute_skill(
    "calculator",
    {"expression": "2 + 3 * 4"}
)
print(result)  ***REMOVED*** 计算结果：2 + 3 * 4 = 14
```

***REMOVED******REMOVED******REMOVED*** 2. 与 LLM 集成

```python
from openai import OpenAI
from skills import default_registry
import json

client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key="your-api-key"
)

***REMOVED*** 1. 获取函数定义
functions = default_registry.get_all_functions()

***REMOVED*** 2. 调用 LLM，传入函数定义
messages = [
    {"role": "user", "content": "帮我计算 15 * 8 + 20"}
]

response = client.chat.completions.create(
    model="your-model",
    messages=messages,
    tools=functions,  ***REMOVED*** 传入函数定义
    tool_choice="auto"
)

***REMOVED*** 3. 处理函数调用
message = response.choices[0].message

if message.tool_calls:
    for tool_call in message.tool_calls:
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)
        
        ***REMOVED*** 执行函数
        result = default_registry.execute_skill(func_name, func_args)
        
        ***REMOVED*** 将结果添加到对话
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": str(result)
        })
    
    ***REMOVED*** 再次调用 LLM，生成最终回复
    response = client.chat.completions.create(
        model="your-model",
        messages=messages,
        tools=functions
    )
    
    print(response.choices[0].message.content)
```

***REMOVED******REMOVED******REMOVED*** 3. 创建自定义函数

```python
from skills.base import Skill, default_registry
from typing import Any, Dict

class MyCustomFunction(Skill):
    """
    自定义函数，继承 Skill 基类
    注意：Skill 是内部命名，实际是 Function Calling 中的 Function
    """
    def __init__(self):
        super().__init__(
            name="my_function",
            description="我的自定义函数"
        )
    
    def get_function_schema(self) -> Dict[str, Any]:
        """返回 OpenAI Function Calling 格式的函数定义"""
        return {
            "type": "function",
            "function": {
                "name": "my_function",
                "description": "函数描述",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "param1": {
                            "type": "string",
                            "description": "参数1的描述"
                        }
                    },
                    "required": ["param1"]
                }
            }
        }
    
    def execute(self, arguments: Dict[str, Any]) -> Any:
        """执行函数逻辑"""
        param1 = arguments["param1"]
        ***REMOVED*** 实现函数逻辑
        return f"处理结果：{param1}"

***REMOVED*** 注册函数
custom_function = MyCustomFunction()
default_registry.register(custom_function)
```

***REMOVED******REMOVED*** 内置函数

以下是系统内置的可调用函数示例，它们遵循 OpenAI Function Calling 格式：

***REMOVED******REMOVED******REMOVED*** 1. CalculatorFunction（计算器）

- **函数名**: `calculator`
- **功能**: 执行数学计算
- **参数**:
  - `expression` (string, 必需): 数学表达式

**示例**:
```python
result = default_registry.execute_skill(
    "calculator",
    {"expression": "10 * 5 + 20"}
)
```

***REMOVED******REMOVED******REMOVED*** 2. WeatherFunction（天气查询）

- **函数名**: `get_weather`
- **功能**: 查询城市天气（模拟实现）
- **参数**:
  - `city` (string, 必需): 城市名称
  - `date` (string, 可选): 查询日期，格式 YYYY-MM-DD

**示例**:
```python
result = default_registry.execute_skill(
    "get_weather",
    {"city": "北京"}
)
```

***REMOVED******REMOVED******REMOVED*** 3. TimeFunction（时间查询）

- **函数名**: `get_current_time`
- **功能**: 获取当前时间和日期
- **参数**:
  - `timezone` (string, 可选): 时区名称，默认 "Asia/Shanghai"
  - `format` (string, 可选): 格式类型，"full"/"date"/"time"，默认 "full"

**示例**:
```python
result = default_registry.execute_skill(
    "get_current_time",
    {"timezone": "Asia/Shanghai", "format": "full"}
)
```

***REMOVED******REMOVED*** 运行示例

```bash
cd /root/data/AI/creator/src
python -m skills.example
```

***REMOVED******REMOVED*** API 参考

***REMOVED******REMOVED******REMOVED*** SkillRegistry（函数注册表）

- `register(skill: Skill)`: 注册函数（Skill 是内部命名，实际是 Function）
- `get_skill(name: str) -> Optional[Skill]`: 获取函数
- `get_all_functions() -> list[Dict]`: 获取所有函数定义（OpenAI Function Calling 格式）
- `execute_skill(name: str, arguments: Dict) -> Any`: 执行函数调用
- `list_skills() -> list[str]`: 列出所有函数名称

***REMOVED******REMOVED******REMOVED*** Skill 基类（Function 基类）

所有可调用函数需要继承 `Skill` 并实现：

- `get_function_schema() -> Dict[str, Any]`: 返回 OpenAI Function Calling 格式的函数定义
- `execute(arguments: Dict[str, Any]) -> Any`: 执行函数逻辑
- `validate_arguments(arguments: Dict[str, Any]) -> bool`: 验证参数（可选）

**注意**：`Skill` 是内部类名，实际对应 Function Calling 中的 Function。

***REMOVED******REMOVED*** 注意事项

1. **命名说明**: 虽然内部使用 "Skill" 命名，但这是一个标准的 Function Calling 系统，完全兼容 OpenAI 的 Function Calling API
2. **安全性**: 计算器函数使用了 `eval()`，已添加安全检查，但在生产环境中建议使用更安全的表达式解析库
3. **时区支持**: 时间函数需要 `pytz` 库支持完整时区功能，如果没有安装则只支持 UTC
4. **错误处理**: 所有函数都应该有适当的错误处理，返回友好的错误信息

***REMOVED******REMOVED*** 扩展建议

- 添加更多实用函数（如文件操作、数据库查询、API 调用等）
- 支持函数链式调用
- 添加函数使用统计和日志
- 支持异步执行函数
- 考虑重命名为更明确的 `Function` 或 `Tool` 命名（保持向后兼容）
