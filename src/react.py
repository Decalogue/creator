"""
ReAct (Reasoning + Acting) 推理示例
结合推理和行动，通过循环的思考-行动-观察过程解决问题

ReAct 流程：
1. Thought: 模型思考下一步应该做什么
2. Action: 执行一个行动（调用工具/函数）
3. Observation: 观察行动的结果
4. 重复上述过程，直到得到最终答案
"""
import json
import os
import re
from typing import List, Dict, Optional, Tuple, Any

from tools import default_registry
from llm.chat import ark_client, ark_deepseek_v3_2


class ReActAgent:
    """
    ReAct 代理
    实现 Reasoning + Acting 的推理模式
    """
    
    def __init__(self, max_iterations: int = 10):
        """
        初始化 ReAct 代理
        
        Args:
            max_iterations: 最大迭代次数，防止无限循环
        """
        self.max_iterations = max_iterations
        self.tools = default_registry
        self.conversation_history: List[Dict[str, str]] = []
    
    def _get_tools_description(self) -> str:
        """获取所有可用工具的文本描述"""
        tools = self.tools.get_all_functions()
        if not tools:
            return "没有可用的工具。"
        
        descriptions = []
        for tool in tools:
            func = tool.get("function", {})
            name = func.get("name", "")
            desc = func.get("description", "")
            params = func.get("parameters", {}).get("properties", {})
            
            param_desc = ", ".join([f"{k}: {v.get('description', '')}" 
                                   for k, v in params.items()])
            
            descriptions.append(f"- {name}: {desc} (参数: {param_desc})")
        
        return "\n".join(descriptions)
    
    def _parse_action(self, text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        从模型输出中解析行动
        
        格式示例：
        Action: calculator
        Action Input: {"expression": "2 + 3"}
        
        或者：
        Action: get_weather
        Action Input: {"city": "北京"}
        """
        ***REMOVED*** 尝试匹配 Action: xxx 和 Action Input: xxx 格式
        action_pattern = r'Action:\s*(\w+)'
        input_pattern = r'Action Input:\s*(.+)'
        
        action_match = re.search(action_pattern, text, re.IGNORECASE)
        input_match = re.search(input_pattern, text, re.IGNORECASE)
        
        if action_match and input_match:
            action_name = action_match.group(1).strip()
            action_input_str = input_match.group(1).strip()
            
            ***REMOVED*** 尝试解析 JSON
            try:
                ***REMOVED*** 移除可能的代码块标记
                action_input_str = action_input_str.strip('`').strip()
                if action_input_str.startswith('json'):
                    action_input_str = action_input_str[4:].strip()
                
                action_input = json.loads(action_input_str)
                return action_name, action_input
            except json.JSONDecodeError:
                ***REMOVED*** 如果不是 JSON，尝试提取引号内的内容
                quoted_match = re.search(r'["\'](.+?)["\']', action_input_str)
                if quoted_match:
                    ***REMOVED*** 简单处理：如果是单个字符串参数
                    return action_name, {"query": quoted_match.group(1)}
        
        return None
    
    def _execute_action(self, action_name: str, action_input: Dict[str, Any]) -> str:
        """执行行动并返回观察结果"""
        try:
            result = self.tools.execute_tool(action_name, action_input)
            return f"执行成功: {result}"
        except ValueError as e:
            return f"执行失败: {str(e)}"
        except Exception as e:
            return f"执行出错: {str(e)}"
    
    def _extract_final_answer(self, content: str) -> Optional[str]:
        """从内容中提取最终答案"""
        if not content:
            return None
        
        if "Final Answer:" in content or "最终答案:" in content:
            final_answer_match = re.search(
                r'(?:Final Answer|最终答案):\s*(.+)',
                content,
                re.IGNORECASE | re.DOTALL
            )
            if final_answer_match:
                return final_answer_match.group(1).strip()
        return None
    
    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        tools_desc = self._get_tools_description()
        
        return f"""你是一个使用 ReAct (Reasoning + Acting) 方式解决问题的 AI 助手。

你可以使用以下工具：
{tools_desc}

请按照以下格式思考和行动：

Thought: [你的思考过程，分析问题并决定下一步行动]
Action: [工具名称]
Action Input: [工具参数的 JSON 格式]
Observation: [工具执行的结果]

然后根据观察结果继续思考，如果需要，可以再次使用工具。重复这个过程直到你能够给出最终答案。

当你确定可以给出最终答案时，使用以下格式：
Thought: [你的最终思考]
Final Answer: [最终答案]

重要提示：
1. 每次只能执行一个 Action
2. Action Input 必须是有效的 JSON 格式
3. 仔细分析 Observation 结果，再决定下一步
4. 如果工具执行失败，尝试其他方法或给出合理的解释"""
    
    def run(self, query: str, verbose: bool = True) -> str:
        """
        运行 ReAct 推理
        
        Args:
            query: 用户查询
            verbose: 是否打印详细过程
        
        Returns:
            最终答案
        """
        ***REMOVED*** 初始化对话历史
        self.conversation_history = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": query}
        ]
        
        if verbose:
            print(f"问题: {query}\n")
            print("=" * 60)
        
        ***REMOVED*** ReAct 循环
        for iteration in range(self.max_iterations):
            if verbose:
                print(f"\n[迭代 {iteration + 1}/{self.max_iterations}]")
            
            ***REMOVED*** 获取工具定义
            tools = self.tools.get_all_functions()
            
            ***REMOVED*** 调用 LLM 进行推理（尝试使用 Function Calling）
            try:
                ***REMOVED*** 尝试使用 OpenAI Function Calling API
                ***REMOVED*** 模型名称可以通过环境变量或配置设置
                model_name = os.getenv("REACT_MODEL", "ep-20251209150604-gxb42")
                response = ark_client.chat.completions.create(
                    model=model_name,
                    messages=self.conversation_history,
                    tools=tools if tools else None,
                    tool_choice="auto" if tools else None,
                    stream=False,
                    max_tokens=8192
                )
                
                message = response.choices[0].message
                content = message.content or ""
                tool_calls = message.tool_calls
                
                ***REMOVED*** 添加到对话历史
                assistant_message = {"role": "assistant", "content": content}
                if tool_calls:
                    assistant_message["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in tool_calls
                    ]
                self.conversation_history.append(assistant_message)
                
                if verbose:
                    if content:
                        print(f"模型输出:\n{content}\n")
                    if tool_calls:
                        print(f"检测到 {len(tool_calls)} 个工具调用\n")
                
                ***REMOVED*** 如果有工具调用，执行它们
                if tool_calls:
                    for tool_call in tool_calls:
                        func_name = tool_call.function.name
                        func_args_str = tool_call.function.arguments
                        
                        try:
                            func_args = json.loads(func_args_str)
                        except json.JSONDecodeError:
                            func_args = {}
                        
                        if verbose:
                            print(f"执行行动: {func_name}")
                            print(f"行动参数: {func_args}")
                        
                        ***REMOVED*** 执行行动
                        observation = self._execute_action(func_name, func_args)
                        
                        if verbose:
                            print(f"观察结果: {observation}\n")
                        
                        ***REMOVED*** 将观察结果添加到对话历史
                        self.conversation_history.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": func_name,
                            "content": observation
                        })
                    
                    ***REMOVED*** 继续循环，让模型基于工具结果生成回复
                    continue
                
                ***REMOVED*** 如果没有工具调用，检查是否有最终答案
                final_answer = self._extract_final_answer(content)
                if final_answer:
                    if verbose:
                        print("=" * 60)
                        print(f"\n最终答案: {final_answer}")
                    return final_answer
                
                ***REMOVED*** 如果只有内容没有工具调用，可能是最终答案
                if content and not tool_calls:
                    if verbose:
                        print("模型返回了最终答案")
                    return content
                    
            except Exception as e:
                ***REMOVED*** 如果 Function Calling 失败，回退到文本解析模式
                if verbose:
                    print(f"Function Calling 失败，使用文本解析模式: {e}\n")
                
                ***REMOVED*** 调用 LLM 进行推理（文本模式）
                reasoning_content, content = ark_deepseek_v3_2(self.conversation_history)
                
                if verbose:
                    print(f"模型输出:\n{content}\n")
                
                ***REMOVED*** 添加到对话历史
                self.conversation_history.append({
                    "role": "assistant",
                    "content": content
                })
                
                ***REMOVED*** 检查是否有最终答案
                if "Final Answer:" in content or "最终答案:" in content:
                    final_answer_match = re.search(
                        r'(?:Final Answer|最终答案):\s*(.+)',
                        content,
                        re.IGNORECASE | re.DOTALL
                    )
                    if final_answer_match:
                        final_answer = final_answer_match.group(1).strip()
                        if verbose:
                            print("=" * 60)
                            print(f"\n最终答案: {final_answer}")
                        return final_answer
                
                ***REMOVED*** 解析行动
                action_info = self._parse_action(content)
                
                if action_info is None:
                    ***REMOVED*** 如果没有解析到行动，可能是模型在思考
                    if verbose:
                        print("未检测到行动，继续推理...")
                    continue
                
                action_name, action_input = action_info
                
                if verbose:
                    print(f"执行行动: {action_name}")
                    print(f"行动参数: {action_input}")
                
                ***REMOVED*** 执行行动
                observation = self._execute_action(action_name, action_input)
                
                if verbose:
                    print(f"观察结果: {observation}")
                
                ***REMOVED*** 将观察结果添加到对话历史
                observation_text = f"Action: {action_name}\nAction Input: {json.dumps(action_input, ensure_ascii=False)}\nObservation: {observation}"
                self.conversation_history.append({
                    "role": "user",
                    "content": observation_text
                })
        
        ***REMOVED*** 如果达到最大迭代次数
        if verbose:
            print("\n达到最大迭代次数，返回最后的内容")
        
        ***REMOVED*** 尝试从最后一条消息中提取内容
        if self.conversation_history:
            last_message = self.conversation_history[-1]
            if isinstance(last_message, dict) and "content" in last_message:
                return last_message["content"] or "达到最大迭代次数，未能获得最终答案"
        
        return "达到最大迭代次数，未能获得最终答案"


def example_1_simple_calculation():
    """示例 1: 简单计算"""
    print("=" * 60)
    print("示例 1: 简单计算")
    print("=" * 60)
    
    agent = ReActAgent(max_iterations=5)
    result = agent.run("计算 15 * 8 + 20 的结果")
    return result


def example_2_weather_query():
    """示例 2: 天气查询"""
    print("\n" + "=" * 60)
    print("示例 2: 天气查询")
    print("=" * 60)
    
    agent = ReActAgent(max_iterations=5)
    result = agent.run("查询北京的天气情况")
    return result


def example_3_complex_task():
    """示例 3: 复杂任务（多步骤）"""
    print("\n" + "=" * 60)
    print("示例 3: 复杂任务")
    print("=" * 60)
    
    agent = ReActAgent(max_iterations=10)
    result = agent.run("先计算 100 * 5 的结果，然后查询上海的天气，最后告诉我当前时间")
    return result


def example_4_time_query():
    """示例 4: 时间查询"""
    print("\n" + "=" * 60)
    print("示例 4: 时间查询")
    print("=" * 60)
    
    agent = ReActAgent(max_iterations=5)
    result = agent.run("现在几点了？请告诉我北京时间的完整信息")
    return result


if __name__ == "__main__":
    ***REMOVED*** 运行示例
    print("ReAct 推理示例")
    print("=" * 60)
    
    try:
        example_1_simple_calculation()
        example_2_weather_query()
        example_3_complex_task()
        example_4_time_query()
        
        print("\n" + "=" * 60)
        print("所有示例运行完成！")
        print("=" * 60)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
