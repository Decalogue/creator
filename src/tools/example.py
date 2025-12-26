"""
Function Calling 使用示例
演示如何使用 Function Calling 系统，包括基本使用、LLM 集成和 API 集成
"""
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

***REMOVED*** 添加项目根目录到 Python 路径，以便可以独立运行此脚本
if __name__ == "__main__" and not __package__:
    src_dir = Path(__file__).parent.parent
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

from tools import default_registry
from tools.base import Tool

***REMOVED*** 可选依赖导入
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    OpenAI = None

try:
    from llm.chat import ark_deepseek_v3_2_stream
    HAS_LLM = True
except ImportError:
    HAS_LLM = False

***REMOVED*** 初始化 OpenAI 客户端
ark_client = None
if HAS_OPENAI and HAS_LLM:
    try:
        ark_client = OpenAI(
            base_url=os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3"),
            api_key=os.getenv("ARK_API_KEY", "93a67648-c2cd-4a51-99ba-c51114b537ee"),
        )
    except Exception:
        ark_client = None


***REMOVED*** ==================== 辅助函数 ====================

def print_section(title: str, width: int = 50):
    """打印章节标题"""
    print("\n" + "=" * width)
    print(title)
    print("=" * width)


***REMOVED*** ==================== 基础示例 ====================

def example_1_basic_usage():
    """示例 1：基本使用"""
    print_section("示例 1：基本使用")
    
    functions = default_registry.get_all_functions()
    print("\n可用的工具函数：")
    for func in functions:
        print(f"- {func['function']['name']}: {func['function']['description']}")
    
    print("\n函数定义（OpenAI 格式）：")
    print(json.dumps(functions, indent=2, ensure_ascii=False))


def example_2_execute_tool():
    """示例 2：执行工具"""
    print_section("示例 2：执行工具")
    
    test_cases = [
        ("calculator", {"expression": "2 + 3 * 4"}, "执行计算"),
        ("get_weather", {"city": "北京"}, "查询天气"),
        ("get_current_time", {"timezone": "Asia/Shanghai", "format": "full"}, "查询时间"),
    ]
    
    for i, (tool_name, args, desc) in enumerate(test_cases, 1):
        print(f"\n{i}. {desc}：")
        result = default_registry.execute_tool(tool_name, args)
        print(result)


def example_3_with_llm_simulation():
    """示例 3：与 LLM 集成（模拟）"""
    print_section("示例 3：与 LLM 集成（模拟）")
    
    ***REMOVED*** 模拟 LLM 返回的函数调用
    tool_calls = [
        {"name": "calculator", "arguments": {"expression": "10 * 5 + 20"}},
        {"name": "get_weather", "arguments": {"city": "上海"}},
    ]
    
    print("\n模拟 LLM 返回的函数调用：")
    print(json.dumps({"tool_calls": tool_calls}, indent=2, ensure_ascii=False))
    
    print("\n执行函数调用：")
    for tool_call in tool_calls:
        print(f"\n调用函数：{tool_call['name']}")
        print(f"参数：{tool_call['arguments']}")
        try:
            result = default_registry.execute_tool(tool_call['name'], tool_call['arguments'])
            print(f"结果：{result}")
        except Exception as e:
            print(f"错误：{str(e)}")


def example_4_custom_tool():
    """示例 4：创建自定义工具"""
    print_section("示例 4：创建自定义工具")
    
    class GreetingTool(Tool):
        """问候工具示例"""
        
        def __init__(self):
            super().__init__(name="greet", description="向用户打招呼")
        
        def get_function_schema(self) -> Dict[str, Any]:
            return {
                "type": "function",
                "function": {
                    "name": "greet",
                    "description": "向用户打招呼",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "用户名称"},
                            "language": {
                                "type": "string",
                                "description": "语言，'zh' 表示中文，'en' 表示英文",
                                "enum": ["zh", "en"],
                                "default": "zh"
                            }
                        },
                        "required": ["name"]
                    }
                }
            }
        
        def execute(self, arguments: Dict[str, Any]) -> str:
            name = arguments["name"]
            lang = arguments.get("language", "zh")
            return f"Hello, {name}! Nice to meet you!" if lang == "en" else f"你好，{name}！很高兴认识你！"
    
    ***REMOVED*** 注册并使用
    greeting_tool = GreetingTool()
    default_registry.register(greeting_tool)
    print("\n已注册自定义工具：greet")
    
    result = default_registry.execute_tool("greet", {"name": "小明", "language": "zh"})
    print(f"执行结果：{result}")


***REMOVED*** ==================== LLM 集成示例 ====================

def chat_with_tools(messages: List[Dict[str, str]], stream: bool = False) -> Any:
    """带 Function Calling 的对话函数"""
    if not HAS_OPENAI:
        raise RuntimeError("openai 模块未安装，请运行: pip install openai")
    if not HAS_LLM or ark_client is None:
        raise RuntimeError("LLM 模块未导入或 API key 未配置")
    
    functions = default_registry.get_all_functions()
    
    if stream:
        for chunk in ark_deepseek_v3_2_stream(messages):
            yield chunk
        return
    
    try:
        response = ark_client.chat.completions.create(
            model=os.getenv("ARK_MODEL", "ep-20251209150604-gxb42"),
            messages=messages,
            tools=functions,
            tool_choice="auto",
            max_tokens=8192,
        )
        
        message = response.choices[0].message
        
        if not message.tool_calls:
            return message.content
        
        ***REMOVED*** 处理函数调用
        tool_results = []
        for tool_call in message.tool_calls:
            try:
                func_args = json.loads(tool_call.function.arguments)
                result = default_registry.execute_tool(tool_call.function.name, func_args)
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "content": str(result)
                })
            except Exception as e:
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "content": f"执行失败：{str(e)}"
                })
        
        ***REMOVED*** 添加工具调用和结果到对话
        messages.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": tc.id,
                "type": "function",
                "function": {"name": tc.function.name, "arguments": tc.function.arguments}
            } for tc in message.tool_calls]
        })
        messages.extend(tool_results)
        
        ***REMOVED*** 再次调用 LLM 生成最终回复
        response = ark_client.chat.completions.create(
            model=os.getenv("ARK_MODEL", "ep-20251209150604-gxb42"),
            messages=messages,
            tools=functions,
            max_tokens=8192,
        )
        return response.choices[0].message.content
        
    except Exception as e:
        return f"错误：{str(e)}"


def example_5_chat_with_llm():
    """示例 5：与 LLM 实际对话（需要 API key）"""
    print_section("示例 5：与 LLM 实际对话")
    
    if not HAS_OPENAI:
        print("\n⚠️  需要安装 openai 模块：pip install openai")
        return
    
    if not HAS_LLM or ark_client is None:
        print("\n⚠️  需要配置 API key：设置环境变量 ARK_API_KEY 和 ARK_BASE_URL")
        return
    
    test_cases = [
        "帮我计算 25 * 8 + 100",
        "查询北京的天气",
        "现在几点了？",
    ]
    
    for i, query in enumerate(test_cases, 1):
        print(f"\n【示例 {i}】用户：{query}")
        try:
            result = chat_with_tools([{"role": "user", "content": query}], stream=False)
            print(f"AI: {result}")
        except Exception as e:
            print(f"错误：{str(e)}")


***REMOVED*** ==================== API 集成代码示例 ====================

def example_6_api_integration():
    """示例 6：API 集成代码示例"""
    print_section("示例 6：API 集成代码示例")
    
    code_example = '''***REMOVED*** OpenAI API 集成示例
from openai import OpenAI
from tools import default_registry
import json

client = OpenAI(base_url="your-api-url", api_key="your-api-key")
functions = default_registry.get_all_functions()

messages = [{"role": "user", "content": "帮我计算 15 * 8 + 20"}]
response = client.chat.completions.create(
    model="your-model",
    messages=messages,
    tools=functions,
    tool_choice="auto"
)

***REMOVED*** 处理函数调用
if message := response.choices[0].message:
    if message.tool_calls:
        for tool_call in message.tool_calls:
            func_args = json.loads(tool_call.function.arguments)
            result = default_registry.execute_tool(tool_call.function.name, func_args)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })
        
        ***REMOVED*** 再次调用生成最终回复
        response = client.chat.completions.create(
            model="your-model",
            messages=messages,
            tools=functions
        )
    
    print(response.choices[0].message.content)
'''
    print(code_example)


***REMOVED*** ==================== 主程序 ====================

if __name__ == "__main__":
    print_section("Function Calling 系统使用示例", 60)
    
    ***REMOVED*** 运行基础示例
    example_1_basic_usage()
    example_2_execute_tool()
    example_3_with_llm_simulation()
    example_4_custom_tool()
    example_6_api_integration()
    example_5_chat_with_llm()
    
    print_section("所有示例运行完成！", 60)
    print("\n提示：")
    print("- 示例 1-4、6 不需要 API key，可以直接运行")
    print("- 示例 5 需要配置环境变量 ARK_API_KEY 和 ARK_BASE_URL")
