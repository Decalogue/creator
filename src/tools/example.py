"""
Function Calling 使用示例
演示如何使用 Function Calling 系统

注意：虽然内部使用 "Skill" 命名，但这是一个标准的 Function Calling 系统，
完全兼容 OpenAI 的 Function Calling API。
"""
import json
from skills import default_registry
from skills.calculator import CalculatorSkill
from skills.weather import WeatherSkill
from skills.time import TimeSkill


def example_1_basic_usage():
    """示例 1：基本使用"""
    print("=" * 50)
    print("示例 1：基本使用")
    print("=" * 50)
    
    ***REMOVED*** 获取所有可用的函数定义（用于传递给 LLM）
    functions = default_registry.get_all_functions()
    print("\n可用的技能函数：")
    for func in functions:
        print(f"- {func['function']['name']}: {func['function']['description']}")
    
    print("\n函数定义（OpenAI 格式）：")
    print(json.dumps(functions, indent=2, ensure_ascii=False))


def example_2_execute_skill():
    """示例 2：执行技能"""
    print("\n" + "=" * 50)
    print("示例 2：执行技能")
    print("=" * 50)
    
    ***REMOVED*** 执行计算器技能
    print("\n1. 执行计算：")
    result = default_registry.execute_skill(
        "calculator",
        {"expression": "2 + 3 * 4"}
    )
    print(result)
    
    ***REMOVED*** 执行天气查询技能
    print("\n2. 查询天气：")
    result = default_registry.execute_skill(
        "get_weather",
        {"city": "北京"}
    )
    print(result)
    
    ***REMOVED*** 执行时间查询技能
    print("\n3. 查询时间：")
    result = default_registry.execute_skill(
        "get_current_time",
        {"timezone": "Asia/Shanghai", "format": "full"}
    )
    print(result)


def example_3_with_llm():
    """示例 3：与 LLM 集成（模拟）"""
    print("\n" + "=" * 50)
    print("示例 3：与 LLM 集成（模拟）")
    print("=" * 50)
    
    ***REMOVED*** 模拟 LLM 返回的函数调用
    llm_response = {
        "tool_calls": [
            {
                "id": "call_123",
                "type": "function",
                "function": {
                    "name": "calculator",
                    "arguments": '{"expression": "10 * 5 + 20"}'
                }
            },
            {
                "id": "call_124",
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "arguments": '{"city": "上海"}'
                }
            }
        ]
    }
    
    print("\n模拟 LLM 返回的函数调用：")
    print(json.dumps(llm_response, indent=2, ensure_ascii=False))
    
    print("\n执行函数调用：")
    for tool_call in llm_response["tool_calls"]:
        func_name = tool_call["function"]["name"]
        func_args = json.loads(tool_call["function"]["arguments"])
        
        print(f"\n调用函数：{func_name}")
        print(f"参数：{func_args}")
        
        try:
            result = default_registry.execute_skill(func_name, func_args)
            print(f"结果：{result}")
        except Exception as e:
            print(f"错误：{str(e)}")


def example_4_custom_skill():
    """示例 4：创建自定义技能"""
    print("\n" + "=" * 50)
    print("示例 4：创建自定义技能")
    print("=" * 50)
    
    from skills.base import Skill
    
    class GreetingSkill(Skill):
        """问候技能示例"""
        
        def __init__(self):
            super().__init__(
                name="greet",
                description="向用户打招呼"
            )
        
        def get_function_schema(self):
            return {
                "type": "function",
                "function": {
                    "name": "greet",
                    "description": "向用户打招呼",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "用户名称"
                            },
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
        
        def execute(self, arguments):
            name = arguments["name"]
            language = arguments.get("language", "zh")
            
            if language == "en":
                return f"Hello, {name}! Nice to meet you!"
            else:
                return f"你好，{name}！很高兴认识你！"
    
    ***REMOVED*** 注册自定义技能
    greeting_skill = GreetingSkill()
    default_registry.register(greeting_skill)
    
    print("\n已注册自定义技能：greet")
    
    ***REMOVED*** 使用自定义技能
    result = default_registry.execute_skill(
        "greet",
        {"name": "小明", "language": "zh"}
    )
    print(f"执行结果：{result}")


def example_5_with_openai_api():
    """示例 5：与 OpenAI API 集成"""
    print("\n" + "=" * 50)
    print("示例 5：与 OpenAI API 集成示例代码")
    print("=" * 50)
    
    example_code = '''
from openai import OpenAI
from skills import default_registry

client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key="your-api-key"
)

***REMOVED*** 1. 获取所有技能的函数定义
functions = default_registry.get_all_functions()

***REMOVED*** 2. 调用 LLM，传入函数定义
messages = [
    {"role": "user", "content": "帮我计算 15 * 8 + 20，然后查询北京的天气"}
]

response = client.chat.completions.create(
    model="your-model",
    messages=messages,
    tools=functions,  ***REMOVED*** 传入函数定义
    tool_choice="auto"
)

***REMOVED*** 3. 处理 LLM 返回的函数调用
message = response.choices[0].message

if message.tool_calls:
    ***REMOVED*** LLM 想要调用函数
    for tool_call in message.tool_calls:
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)
        
        ***REMOVED*** 执行函数
        result = default_registry.execute_skill(func_name, func_args)
        
        ***REMOVED*** 将结果添加到对话中
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": str(result)
        })
    
    ***REMOVED*** 再次调用 LLM，让它基于函数结果生成回复
    response = client.chat.completions.create(
        model="your-model",
        messages=messages,
        tools=functions
    )
    
    final_answer = response.choices[0].message.content
    print(final_answer)
'''
    
    print(example_code)


if __name__ == "__main__":
    ***REMOVED*** 运行所有示例
    example_1_basic_usage()
    example_2_execute_skill()
    example_3_with_llm()
    example_4_custom_skill()
    example_5_with_openai_api()
    
    print("\n" + "=" * 50)
    print("所有示例运行完成！")
    print("=" * 50)
