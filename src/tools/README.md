***REMOVED*** Function Calling 系统使用指南

***REMOVED******REMOVED*** 简介

这是一个基于 OpenAI Function Calling 格式的工具调用框架。它提供了统一的接口来定义和执行可被 LLM 调用的函数，使 AI 助手能够使用外部工具和功能。

**注意**：这是一个标准的 Function Calling 系统，完全兼容 OpenAI 的 Function Calling API。

***REMOVED******REMOVED*** 目录结构

```
tools/
├── __init__.py          ***REMOVED*** 模块导出和自动注册
├── base.py              ***REMOVED*** Function 基类和注册表
├── calculator.py        ***REMOVED*** 计算器工具示例
├── weather.py           ***REMOVED*** 天气查询工具示例
├── time.py              ***REMOVED*** 时间查询工具示例
├── example.py           ***REMOVED*** 完整使用示例（包括基础使用、LLM 集成和 API 集成）
├── test_tools.py        ***REMOVED*** 测试代码
└── README.md            ***REMOVED*** 本文档
```

***REMOVED******REMOVED*** 快速开始（5 分钟上手）

***REMOVED******REMOVED******REMOVED*** 1. 导入模块

```python
from tools import default_registry
```

***REMOVED******REMOVED******REMOVED*** 2. 查看可用工具

```python
***REMOVED*** 列出所有工具
print(default_registry.list_tools())
***REMOVED*** 输出: ['calculator', 'get_weather', 'get_current_time']

***REMOVED*** 获取工具定义（用于传递给 LLM，OpenAI Function Calling 格式）
functions = default_registry.get_all_functions()
```

***REMOVED******REMOVED******REMOVED*** 3. 执行工具调用

```python
***REMOVED*** 计算
result = default_registry.execute_tool(
    "calculator",
    {"expression": "10 * 5 + 20"}
)
print(result)  ***REMOVED*** 计算结果：10 * 5 + 20 = 70

***REMOVED*** 查询天气
result = default_registry.execute_tool(
    "get_weather",
    {"city": "北京"}
)
print(result)

***REMOVED*** 查询时间
result = default_registry.execute_tool(
    "get_current_time",
    {"timezone": "Asia/Shanghai"}
)
print(result)
```

***REMOVED******REMOVED******REMOVED*** 4. 运行示例

```bash
cd /root/data/AI/creator/src

***REMOVED*** 运行完整示例（包括基础使用、LLM 集成和 API 集成）
python -m tools.example

***REMOVED*** 或直接运行
python tools/example.py

***REMOVED*** 运行测试
python -m tools.test_tools
```

***REMOVED******REMOVED*** 详细使用指南

***REMOVED******REMOVED******REMOVED*** 1. 基本使用

```python
from tools import default_registry

***REMOVED*** 获取所有可用的工具定义（用于传递给 LLM）
functions = default_registry.get_all_functions()

***REMOVED*** 执行工具调用
result = default_registry.execute_tool(
    "calculator",
    {"expression": "2 + 3 * 4"}
)
print(result)  ***REMOVED*** 计算结果：2 + 3 * 4 = 14
```

***REMOVED******REMOVED******REMOVED*** 2. 与 LLM 集成

```python
import json
from openai import OpenAI
from tools import default_registry

client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key="your-api-key"
)

***REMOVED*** 1. 获取工具定义
functions = default_registry.get_all_functions()

***REMOVED*** 2. 调用 LLM，传入工具定义
messages = [
    {"role": "user", "content": "帮我计算 15 * 8 + 20"}
]

response = client.chat.completions.create(
    model="your-model",
    messages=messages,
    tools=functions,  ***REMOVED*** 传入工具定义
    tool_choice="auto"
)

***REMOVED*** 3. 处理工具调用
message = response.choices[0].message

if message.tool_calls:
    for tool_call in message.tool_calls:
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)
        
        ***REMOVED*** 执行工具
        result = default_registry.execute_tool(func_name, func_args)
        
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

***REMOVED******REMOVED******REMOVED*** 3. 创建自定义工具

```python
from tools.base import Tool, default_registry
from typing import Any, Dict

class MyCustomTool(Tool):
    """
    自定义工具，继承 Tool 基类
    注意：Tool 对应 Function Calling 中的 Function
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

***REMOVED*** 注册工具
custom_tool = MyCustomTool()
default_registry.register(custom_tool)
```

***REMOVED******REMOVED*** 内置工具

以下是系统内置的可调用工具示例，它们遵循 OpenAI Function Calling 格式：

***REMOVED******REMOVED******REMOVED*** 1. CalculatorTool（计算器）

- **工具名**: `calculator`
- **功能**: 执行数学计算，支持基本运算（+、-、*、/）和幂运算（**）
- **参数**:
  - `expression` (string, 必需): 数学表达式

**示例**:
```python
result = default_registry.execute_tool(
    "calculator",
    {"expression": "10 * 5 + 20"}
)
***REMOVED*** 输出: 计算结果：10 * 5 + 20 = 70
```

***REMOVED******REMOVED******REMOVED*** 2. WeatherTool（天气查询）

- **工具名**: `get_weather`
- **功能**: 查询城市天气（模拟实现）
- **参数**:
  - `city` (string, 必需): 城市名称
  - `date` (string, 可选): 查询日期，格式 YYYY-MM-DD

**示例**:
```python
result = default_registry.execute_tool(
    "get_weather",
    {"city": "北京"}
)
```

***REMOVED******REMOVED******REMOVED*** 3. TimeTool（时间查询）

- **工具名**: `get_current_time`
- **功能**: 获取当前时间和日期
- **参数**:
  - `timezone` (string, 可选): 时区名称，默认 "Asia/Shanghai"
  - `format` (string, 可选): 格式类型，"full"/"date"/"time"，默认 "full"

**示例**:
```python
result = default_registry.execute_tool(
    "get_current_time",
    {"timezone": "Asia/Shanghai", "format": "full"}
)
```

***REMOVED******REMOVED*** API 参考

***REMOVED******REMOVED******REMOVED*** ToolRegistry（工具注册表）

- `register(tool: Tool) -> None`: 注册工具（Tool 对应 Function Calling 中的 Function）
- `get_tool(name: str) -> Optional[Tool]`: 根据名称获取工具
- `get_all_functions() -> List[Dict[str, Any]]`: 获取所有工具定义（OpenAI Function Calling 格式）
- `execute_tool(name: str, arguments: Union[Dict[str, Any], str]) -> Any`: 执行工具调用
- `list_tools() -> List[str]`: 列出所有已注册的工具名称

***REMOVED******REMOVED******REMOVED*** Tool 基类（Function 基类）

所有可调用工具需要继承 `Tool` 并实现：

- `get_function_schema() -> Dict[str, Any]`: 返回 OpenAI Function Calling 格式的工具定义
- `execute(arguments: Dict[str, Any]) -> Any`: 执行工具逻辑
- `validate_arguments(arguments: Dict[str, Any]) -> bool`: 验证参数（可选，默认返回 True）

**注意**：`Tool` 对应 Function Calling 中的 Function。

***REMOVED******REMOVED*** 注意事项

1. **命名说明**: 这是一个标准的 Function Calling 系统，完全兼容 OpenAI 的 Function Calling API
2. **安全性**: 计算器工具使用了 `eval()`，已添加安全检查，但在生产环境中建议使用更安全的表达式解析库
3. **时区支持**: 时间工具需要 `pytz` 库支持完整时区功能，如果没有安装则只支持 UTC
4. **错误处理**: 所有工具都应该有适当的错误处理，返回友好的错误信息
5. **路径处理**: 可以直接运行 `python tools/example.py`，脚本会自动处理导入路径

***REMOVED******REMOVED*** 扩展建议

- 添加更多实用工具（如文件操作、数据库查询、API 调用等）
- 支持工具链式调用
- 添加工具使用统计和日志
- 支持异步执行工具
- 添加工具权限管理

***REMOVED******REMOVED*** 下一步

1. 查看 `example.py` 学习更多用法和完整示例
2. 运行 `python -m tools.example` 查看所有示例
3. 运行 `python -m tools.test_tools` 验证功能
4. 参考现有工具实现创建自己的工具
