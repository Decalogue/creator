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
import time
from typing import List, Dict, Optional, Tuple, Any

from tools import default_registry, get_discovery
from agent.context_manager import get_context_manager
from agent.layered_action_space import get_layered_action_space
from llm.chat import client, deepseek_v3_2


class ReActAgent:
    """
    ReAct 代理
    实现 Reasoning + Acting 的推理模式
    """

    def __init__(self, max_iterations: int = 10, enable_context_offloading: bool = True, max_new_tokens: Optional[int] = None, llm_client = None, enable_observability: bool = True):
        """
        初始化 ReAct 代理

        Args:
            max_iterations: 最大迭代次数，防止无限循环
            enable_context_offloading: 是否启用上下文卸载（Context Offloading）
            max_new_tokens: 最大生成 token 数（None = 使用模型默认值）
            llm_client: LLM客户端函数（如gemini_3_flash、deepseek_v3_2），如果为None则使用默认的OpenAI client
            enable_observability: 是否启用可观测性（指标收集）
        """
        self.max_iterations = max_iterations
        self.tools = default_registry
        self.conversation_history: List[Dict[str, str]] = []
        self.enable_context_offloading = enable_context_offloading
        self.context_manager = get_context_manager() if enable_context_offloading else None
        self.layered_action_space = get_layered_action_space()
        self.max_new_tokens = max_new_tokens
        self.llm_client = llm_client

        # 可观测性（可选）
        self.enable_observability = enable_observability
        if enable_observability:
            try:
                from agent.infra.observability import get_agent_observability
                self.observability = get_agent_observability()
            except ImportError:
                self.observability = None
                self.enable_observability = False
        else:
            self.observability = None

    def _get_tools_description(self) -> str:
        """
        获取工具描述（Index Layer + Layered Action Space）
        只返回工具名称列表，详细描述在 Discovery Layer 中按需查找
        """
        discovery = get_discovery()
        index_layer = discovery.get_index_layer()

        # 添加分层行动空间描述
        las = self.layered_action_space
        layered_desc = f"""
{las.get_l1_functions_description()}

{las.get_l2_tools_description()}

{las.get_l3_description()}
"""

        return index_layer + layered_desc

    def _parse_action(self, text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        从模型输出中解析行动

        格式示例：
        Action: search_tool_docs
        Action Input: {"query": "创作", "max_results": 5}
        
        或者：
        Action: read_tool_doc
        Action Input: {"tool_name": "search_tool_docs"}
        """
        # 尝试匹配 Action: xxx 和 Action Input: xxx 格式
        action_pattern = r'Action:\s*(\w+)'
        input_pattern = r'Action Input:\s*(.+)'

        action_match = re.search(action_pattern, text, re.IGNORECASE)
        input_match = re.search(input_pattern, text, re.IGNORECASE)

        if action_match and input_match:
            action_name = action_match.group(1).strip()
            action_input_str = input_match.group(1).strip()

            # 尝试解析 JSON
            try:
                # 移除可能的代码块标记
                action_input_str = action_input_str.strip('`').strip()
                if action_input_str.startswith('json'):
                    action_input_str = action_input_str[4:].strip()

                action_input = json.loads(action_input_str)
                return action_name, action_input
            except json.JSONDecodeError:
                # 如果不是 JSON，尝试提取引号内的内容
                quoted_match = re.search(r'["\'](.+?)["\']', action_input_str)
                if quoted_match:
                    # 简单处理：如果是单个字符串参数
                    return action_name, {"query": quoted_match.group(1)}

        return None

    def _execute_action(self, action_name: str, action_input: Dict[str, Any]) -> str:
        """
        执行行动并返回观察结果
        如果启用 Context Offloading，会将冗长的结果写入文件
        """
        try:
            result = self.tools.execute_tool(action_name, action_input)
            result_str = str(result)

            # 如果启用 Context Offloading 且结果过长，写入文件
            if self.enable_context_offloading and self.context_manager:
                offloaded_result, file_path = self.context_manager.offload_tool_result(
                    tool_name=action_name,
                    tool_input=action_input,
                    tool_output=result_str,
                    max_length=500  # 超过500字符则写入文件
                )
                return offloaded_result

            return f"执行成功: {result_str}"
        except ValueError as e:
            return f"执行失败: {str(e)}"
        except Exception as e:
            return f"执行出错: {str(e)}"

    def _execute_tool_with_metrics(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        tools_called: int
    ) -> tuple[str, int]:
        """
        执行工具并收集指标（简化嵌套）

        Args:
            tool_name: 工具名称
            tool_args: 工具参数
            tools_called: 当前工具调用计数

        Returns:
            (观察结果, 更新后的工具调用计数)

        Raises:
            工具执行异常
        """
        tool_start_time = time.time()
        try:
            observation = self._execute_action(tool_name, tool_args)
            tool_latency = time.time() - tool_start_time
            tools_called += 1

            # 记录工具调用成功
            if self.enable_observability and self.observability:
                self.observability.record_tool_call(
                    tool_name=tool_name,
                    success=True,
                    latency=tool_latency
                )
            return observation, tools_called
        except Exception as e:
            tool_latency = time.time() - tool_start_time
            tools_called += 1

            # 记录工具调用失败
            if self.enable_observability and self.observability:
                self.observability.record_tool_call(
                    tool_name=tool_name,
                    success=False,
                    latency=tool_latency,
                    error_type=type(e).__name__
                )
            raise  # 重新抛出异常

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

        context_offloading_note = ""
        if self.enable_context_offloading:
            context_offloading_note = """
**上下文管理**：
- 如果工具返回结果过长，会自动保存到文件，只返回文件路径引用
- 如果上下文接近限制，会将完整历史保存到文件，提供摘要+文件引用
- 可以使用 `read_file` 工具读取保存的文件，或使用 `grep` 命令搜索特定内容
"""

        return f"""你是一个使用 ReAct (Reasoning + Acting) 方式解决问题的 AI 助手。

{tools_desc}

**工具发现机制**：
- 系统提示词中只包含工具名称列表（Index Layer）
- 如需了解工具的详细描述、参数定义和使用方法，请使用 `search_tool_docs` 工具搜索工具文档
- 找到相关工具后，可以使用 `read_tool_doc` 工具读取完整的工具文档（Discovery Layer）
{context_offloading_note}
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
3. 如果不确定工具的使用方法，先使用 `search_tool_docs` 搜索工具文档
4. 如果工具返回文件路径引用，可以使用 `read_file` 工具读取完整内容
5. 仔细分析 Observation 结果，再决定下一步
6. 如果工具执行失败，尝试其他方法或给出合理的解释"""

    def run(self, query: str, verbose: bool = True) -> str:
        """
        运行 ReAct 推理

        Args:
            query: 用户查询
            verbose: 是否打印详细过程

        Returns:
            最终答案
        """
        import uuid

        # 生成查询ID用于追踪
        query_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        iterations = 0
        tools_called = 0
        tokens_used = 0
        error_type = None
        error_message = None

        # 初始化对话历史
        self.conversation_history = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": query}
        ]

        if verbose:
            print(f"问题: {query}\n")
            print("=" * 60)

        # ReAct 循环
        for iteration in range(self.max_iterations):
            if verbose:
                print(f"\n[迭代 {iteration + 1}/{self.max_iterations}]")

            # 检查上下文长度，如果接近限制则卸载历史（Context Offloading）
            if self.enable_context_offloading and self.context_manager:
                estimated_tokens, needs_reduction = self.context_manager.estimate_context_length(
                    self.conversation_history,
                    threshold=128000  # Pre-rot threshold: 128K tokens
                )

                if needs_reduction and iteration > 0:  # 至少执行一次迭代后再缩减
                    if verbose:
                        print(f"⚠️  上下文长度: {estimated_tokens} tokens，触发上下文缩减...")

                    # 第一步：Compaction（紧凑化）- 无损、可逆
                    compacted_history, removed_records = self.context_manager.compact_conversation_history(
                        self.conversation_history,
                        keep_recent=3  # 保留最近3条作为 Few-shot Examples
                    )

                    if verbose and removed_records:
                        print(f"  ✓ Compaction: 紧凑化了 {len(removed_records)} 条记录")

                    # 如果 Compaction 后仍然超过阈值，进行 Summarization
                    compacted_tokens, still_needs_reduction = self.context_manager.estimate_context_length(
                        compacted_history,
                        threshold=self.context_manager.pre_rot_threshold
                    )

                    if still_needs_reduction:
                        if verbose:
                            print(f"  ⚠️  Compaction 后仍超过阈值 ({compacted_tokens} tokens)，进行 Summarization...")

                        # 第二步：Summarization（摘要化）- 有损但带保险
                        summary_ref, dump_file, recent_history = self.context_manager.summarize_with_dump(
                            self.conversation_history,
                            keep_recent=3
                        )

                        if verbose:
                            print(f"  ✓ Summarization: 完整上下文已转储到 {dump_file}")

                        # 替换对话历史为摘要+文件引用+最近记录
                        self.conversation_history = [
                            {"role": "system", "content": self._build_system_prompt()},
                            {"role": "user", "content": f"之前的对话历史摘要:\n{summary_ref}"},
                        ] + recent_history
                    else:
                        # 只进行 Compaction，不进行 Summarization
                        self.conversation_history = compacted_history
                        if verbose:
                            print(f"  ✓ 仅 Compaction 已足够，当前 tokens: {compacted_tokens}")

            # 获取工具定义
            tools = self.tools.get_all_functions()

            # 调用 LLM 进行推理（尝试使用 Function Calling）
            try:
                # 如果提供了自定义LLM客户端函数，使用它
                if self.llm_client is not None:
                    # 使用自定义LLM函数（如gemini_3_flash、deepseek_v3_2）
                    max_tokens = self.max_new_tokens if self.max_new_tokens is not None else 8192
                    reasoning_content, content = self.llm_client(self.conversation_history, max_new_tokens=max_tokens)
                    tool_calls = None  # 自定义LLM函数可能不支持Function Calling
                else:
                    # 使用默认的 OpenAI Function Calling API
                    model_name = os.getenv("REACT_MODEL", "ep-20251209150604-gxb42")
                    # 使用 max_new_tokens 如果设置了，否则使用默认值 8192
                    max_tokens = self.max_new_tokens if self.max_new_tokens is not None else 8192
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=self.conversation_history,
                        tools=tools if tools else None,
                        tool_choice="auto" if tools else None,
                        stream=False,
                        max_tokens=max_tokens
                    )

                    message = response.choices[0].message
                    content = message.content or ""
                    tool_calls = message.tool_calls

                # 添加到对话历史
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

                # 如果有工具调用，执行它们
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

                        # 执行行动（带指标收集）- 使用提取的方法简化嵌套
                        try:
                            observation, tools_called = self._execute_tool_with_metrics(
                                tool_name=func_name,
                                tool_args=func_args,
                                tools_called=tools_called
                            )
                        except Exception as e:
                            observation = f"错误: {str(e)}"
                            raise  # 重新抛出异常

                        if verbose:
                            print(f"观察结果: {observation}\n")

                        # 将观察结果添加到对话历史
                        self.conversation_history.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": func_name,
                            "content": observation
                        })

                    # 继续循环，让模型基于工具结果生成回复
                    continue

                # 如果没有工具调用，检查是否有最终答案
                final_answer = self._extract_final_answer(content)
                if final_answer:
                    if verbose:
                        print("=" * 60)
                        print(f"\n最终答案: {final_answer}")

                    # 记录指标
                    latency = time.time() - start_time
                    if self.enable_observability and self.observability:
                        self.observability.record_query(
                            query_id=query_id,
                            success=True,
                            latency=latency,
                            iterations=iterations + 1,
                            tokens_used=tokens_used,
                            tools_called=tools_called
                        )

                    return final_answer

                # 如果只有内容没有工具调用，可能是最终答案
                if content and not tool_calls:
                    if verbose:
                        print("模型返回了最终答案")

                    # 记录指标
                    latency = time.time() - start_time
                    if self.enable_observability and self.observability:
                        self.observability.record_query(
                            query_id=query_id,
                            success=True,
                            latency=latency,
                            iterations=iterations + 1,
                            tokens_used=tokens_used,
                            tools_called=tools_called
                        )

                    return content

            except Exception as e:
                # 如果 Function Calling 失败，回退到文本解析模式
                if verbose:
                    print(f"Function Calling 失败，使用文本解析模式: {e}\n")

                # 调用 LLM 进行推理（文本模式）
                if self.max_new_tokens is not None:
                    reasoning_content, content = deepseek_v3_2(self.conversation_history, max_new_tokens=self.max_new_tokens)
                else:
                    reasoning_content, content = deepseek_v3_2(self.conversation_history)

                if verbose:
                    print(f"模型输出:\n{content}\n")

                # 添加到对话历史
                self.conversation_history.append({
                    "role": "assistant",
                    "content": content
                })

                # 检查是否有最终答案
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

                        # 记录指标
                        latency = time.time() - start_time
                        if self.enable_observability and self.observability:
                            self.observability.record_query(
                                query_id=query_id,
                                success=True,
                                latency=latency,
                                iterations=iterations + 1,
                                tokens_used=tokens_used,
                                tools_called=tools_called
                            )

                        return final_answer

                # 解析行动
                action_info = self._parse_action(content)

                if action_info is None:
                    # 如果没有解析到行动，可能是模型在思考
                    if verbose:
                        print("未检测到行动，继续推理...")
                    continue

                action_name, action_input = action_info

                if verbose:
                    print(f"执行行动: {action_name}")
                    print(f"行动参数: {action_input}")

                # 执行行动（带指标收集）- 使用提取的方法简化嵌套
                try:
                    observation, tools_called = self._execute_tool_with_metrics(
                        tool_name=action_name,
                        tool_args=action_input,
                        tools_called=tools_called
                    )
                except Exception as e:
                    observation = f"错误: {str(e)}"
                    raise  # 重新抛出异常

                if verbose:
                    print(f"观察结果: {observation}")

                # 将观察结果添加到对话历史
                observation_text = f"Action: {action_name}\nAction Input: {json.dumps(action_input, ensure_ascii=False)}\nObservation: {observation}"
                self.conversation_history.append({
                    "role": "user",
                    "content": observation_text
                })

        # 如果达到最大迭代次数
        if verbose:
            print("\n达到最大迭代次数，返回最后的内容")

        # 记录指标（失败）
        latency = time.time() - start_time
        if self.enable_observability and self.observability:
            self.observability.record_query(
                query_id=query_id,
                success=False,
                latency=latency,
                iterations=iterations,
                tokens_used=tokens_used,
                tools_called=tools_called,
                error_type="MaxIterationsReached",
                error_message="达到最大迭代次数"
            )

        # 尝试从最后一条消息中提取内容
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
    # 运行示例
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
