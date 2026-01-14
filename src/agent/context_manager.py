"""
上下文管理器
实现 Cursor 风格的 Context Offloading 和 Manus 风格的 Compaction + Summarization

核心思想：
- 将冗长的工具结果、终端会话、聊天历史转化为文件
- 在上下文中只保留文件路径，让 Agent 按需读取
- Compaction: 无损、可逆的缩减
- Summarization: 有损但带保险的压缩
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Callable
from datetime import datetime
import hashlib
import logging

logger = logging.getLogger(__name__)


class ContextManager:
    """
    上下文管理器
    实现 Context Offloading：将冗长内容写入文件，只保留引用
    """
    
    def __init__(
        self,
        output_dir: Optional[Path] = None,
        llm_func: Optional[Callable] = None,
        pre_rot_threshold: int = 128000
    ):
        """
        初始化上下文管理器
        
        Args:
            output_dir: 输出目录，默认为 agent/context_outputs/
            llm_func: LLM 调用函数，用于生成摘要（可选）
            pre_rot_threshold: 腐烂前阈值（tokens），默认128K
        """
        if output_dir is None:
            ***REMOVED*** 默认使用 agent/context_outputs/ 目录
            current_dir = Path(__file__).parent
            output_dir = current_dir / "context_outputs"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        ***REMOVED*** 创建子目录
        (self.output_dir / "tool_results").mkdir(exist_ok=True)
        (self.output_dir / "chat_history").mkdir(exist_ok=True)
        (self.output_dir / "terminal_sessions").mkdir(exist_ok=True)
        
        ***REMOVED*** LLM 函数（用于生成摘要）
        self.llm_func = llm_func
        self.pre_rot_threshold = pre_rot_threshold
    
    def offload_tool_result(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        tool_output: str,
        max_length: int = 500
    ) -> Tuple[str, Optional[Path]]:
        """
        卸载工具结果到文件
        
        如果工具结果过长，写入文件并返回文件路径引用
        
        Args:
            tool_name: 工具名称
            tool_input: 工具输入参数
            tool_output: 工具输出结果
            max_length: 最大长度（超过此长度则写入文件），默认500字符
        
        Returns:
            (结果文本或文件引用, 文件路径)
        """
        ***REMOVED*** 如果结果不长，直接返回
        if len(tool_output) <= max_length:
            return tool_output, None
        
        ***REMOVED*** 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        ***REMOVED*** 使用工具名称和输入参数的哈希值确保唯一性
        input_hash = hashlib.md5(
            json.dumps(tool_input, sort_keys=True).encode()
        ).hexdigest()[:8]
        filename = f"{tool_name}_{input_hash}_{timestamp}.txt"
        file_path = self.output_dir / "tool_results" / filename
        
        ***REMOVED*** 写入文件
        file_content = f"""工具: {tool_name}
输入参数: {json.dumps(tool_input, ensure_ascii=False, indent=2)}
执行时间: {datetime.now().isoformat()}

输出结果:
{tool_output}
"""
        file_path.write_text(file_content, encoding="utf-8")
        
        ***REMOVED*** 返回文件引用
        file_ref = f"工具执行结果已保存到文件: {file_path}\n结果长度: {len(tool_output)} 字符\n\n提示：可以使用 `read_file` 工具读取完整结果，或使用 `tail` 命令查看末尾内容。"
        
        return file_ref, file_path
    
    def offload_chat_history(
        self,
        conversation_history: List[Dict[str, Any]],
        summary: Optional[str] = None
    ) -> Tuple[str, Path]:
        """
        卸载聊天历史到文件
        
        在上下文接近限制时，将完整历史转储到文件，提供摘要+文件引用
        
        Args:
            conversation_history: 对话历史
            summary: 可选的摘要（如果已生成）
        
        Returns:
            (摘要+文件引用, 文件路径)
        """
        ***REMOVED*** 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_history_{timestamp}.json"
        file_path = self.output_dir / "chat_history" / filename
        
        ***REMOVED*** 保存完整历史
        history_data = {
            "timestamp": datetime.now().isoformat(),
            "message_count": len(conversation_history),
            "summary": summary,
            "full_history": conversation_history
        }
        file_path.write_text(
            json.dumps(history_data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        
        ***REMOVED*** 生成摘要（如果没有提供）
        if not summary:
            summary = self._generate_summary(conversation_history)
        
        ***REMOVED*** 返回摘要+文件引用
        file_ref = f"""聊天历史摘要:
{summary}

完整聊天历史已保存到文件: {file_path}
消息数量: {len(conversation_history)}

提示：如需查看完整历史记录，可以使用 `read_file` 工具读取该文件，或使用 `grep` 命令搜索特定内容。"""
        
        return file_ref, file_path
    
    def _generate_summary(
        self,
        conversation_history: List[Dict[str, Any]],
        use_llm: bool = True
    ) -> str:
        """
        生成对话历史摘要
        
        优先使用 LLM 生成高质量摘要，如果 LLM 不可用则使用简单统计
        
        Args:
            conversation_history: 对话历史
            use_llm: 是否使用 LLM 生成摘要（如果可用）
        
        Returns:
            摘要文本
        """
        if not conversation_history:
            return "无对话历史"
        
        ***REMOVED*** 如果 LLM 可用，使用 LLM 生成摘要
        if use_llm and self.llm_func:
            try:
                return self._generate_llm_summary(conversation_history)
            except Exception as e:
                logger.warning(f"LLM 摘要生成失败，使用简单摘要: {e}")
        
        ***REMOVED*** 简单摘要：统计消息类型和数量
        user_count = sum(1 for msg in conversation_history if msg.get("role") == "user")
        assistant_count = sum(1 for msg in conversation_history if msg.get("role") == "assistant")
        tool_count = sum(1 for msg in conversation_history if msg.get("role") == "tool")
        
        ***REMOVED*** 提取关键信息
        first_user_msg = next(
            (msg.get("content", "")[:100] for msg in conversation_history if msg.get("role") == "user"),
            ""
        )
        
        summary_lines = [
            f"对话历史摘要（共 {len(conversation_history)} 条消息）:",
            f"- 用户消息: {user_count} 条",
            f"- 助手消息: {assistant_count} 条",
            f"- 工具调用: {tool_count} 条",
        ]
        
        if first_user_msg:
            summary_lines.append(f"- 初始问题: {first_user_msg}...")
        
        return "\n".join(summary_lines)
    
    def _generate_llm_summary(self, conversation_history: List[Dict[str, Any]]) -> str:
        """
        使用 LLM 生成对话历史摘要
        
        Args:
            conversation_history: 对话历史
        
        Returns:
            LLM 生成的摘要
        """
        ***REMOVED*** 构建对话历史文本（限制长度）
        history_text_parts = []
        total_chars = 0
        max_chars = 8000  ***REMOVED*** 限制输入长度
        
        for msg in conversation_history:
            role = msg.get("role", "")
            content = str(msg.get("content", ""))
            
            ***REMOVED*** 如果是工具调用，简化显示
            if role == "tool":
                content = content[:200] + "..." if len(content) > 200 else content
            
            msg_text = f"{role}: {content}"
            if total_chars + len(msg_text) > max_chars:
                break
            history_text_parts.append(msg_text)
            total_chars += len(msg_text)
        
        history_text = "\n".join(history_text_parts)
        if total_chars >= max_chars:
            history_text += "\n... (更多内容已省略)"
        
        ***REMOVED*** 构建提示词
        prompt = f"""请对以下对话历史进行摘要，提取关键信息。

要求：
1. 总结用户的主要问题和需求
2. 总结助手的主要回答和解决方案
3. 总结使用的工具和关键结果
4. 保留重要的上下文信息
5. 使用简洁、清晰的语言
6. 摘要长度控制在200-400字

对话历史：
{history_text}

请直接返回摘要内容，不要包含其他格式："""
        
        ***REMOVED*** 调用 LLM
        try:
            messages = [
                {"role": "user", "content": prompt}
            ]
            result = self.llm_func(messages)
            ***REMOVED*** 处理不同的返回格式
            if isinstance(result, tuple):
                ***REMOVED*** 如果返回 (reasoning, content) 元组
                summary = result[1] if len(result) > 1 else result[0]
            elif isinstance(result, str):
                summary = result
            else:
                summary = str(result)
            
            return summary if summary else self._generate_simple_summary(conversation_history)
        except Exception as e:
            logger.error(f"LLM 摘要生成失败: {e}")
            return self._generate_simple_summary(conversation_history)
    
    def _generate_simple_summary(self, conversation_history: List[Dict[str, Any]]) -> str:
        """生成简单统计摘要（fallback）"""
        user_count = sum(1 for msg in conversation_history if msg.get("role") == "user")
        assistant_count = sum(1 for msg in conversation_history if msg.get("role") == "assistant")
        tool_count = sum(1 for msg in conversation_history if msg.get("role") == "tool")
        
        first_user_msg = next(
            (msg.get("content", "")[:100] for msg in conversation_history if msg.get("role") == "user"),
            ""
        )
        
        summary_lines = [
            f"对话历史摘要（共 {len(conversation_history)} 条消息）:",
            f"- 用户消息: {user_count} 条",
            f"- 助手消息: {assistant_count} 条",
            f"- 工具调用: {tool_count} 条",
        ]
        
        if first_user_msg:
            summary_lines.append(f"- 初始问题: {first_user_msg}...")
        
        return "\n".join(summary_lines)
    
    def offload_terminal_output(
        self,
        command: str,
        output: str,
        exit_code: int = 0
    ) -> Tuple[str, Path]:
        """
        卸载终端输出到文件
        
        自动同步终端会话输出到文件系统
        
        Args:
            command: 执行的命令
            output: 命令输出
            exit_code: 退出码
        
        Returns:
            (文件引用, 文件路径)
        """
        ***REMOVED*** 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        ***REMOVED*** 使用命令的哈希值
        command_hash = hashlib.md5(command.encode()).hexdigest()[:8]
        filename = f"terminal_{command_hash}_{timestamp}.log"
        file_path = self.output_dir / "terminal_sessions" / filename
        
        ***REMOVED*** 写入文件
        file_content = f"""命令: {command}
执行时间: {datetime.now().isoformat()}
退出码: {exit_code}

输出:
{output}
"""
        file_path.write_text(file_content, encoding="utf-8")
        
        ***REMOVED*** 返回文件引用
        file_ref = f"终端输出已保存到文件: {file_path}\n输出长度: {len(output)} 字符\n\n提示：可以使用 `read_file` 工具读取完整输出，或使用 `grep` 命令搜索特定内容。"
        
        return file_ref, file_path
    
    def estimate_context_length(
        self,
        conversation_history: List[Dict[str, Any]],
        threshold: int = 128000  ***REMOVED*** Pre-rot threshold (tokens)
    ) -> Tuple[int, bool]:
        """
        估算上下文长度并检查是否需要缩减
        
        Args:
            conversation_history: 对话历史
            threshold: 阈值（tokens），默认128K（Manus 的建议）
        
        Returns:
            (估算的token数量, 是否需要缩减)
        """
        ***REMOVED*** 粗略估算：1 token ≈ 4 字符
        total_chars = sum(
            len(str(msg.get("content", ""))) for msg in conversation_history
        )
        estimated_tokens = total_chars // 4
        
        needs_reduction = estimated_tokens >= threshold
        
        return estimated_tokens, needs_reduction
    
    def compact_tool_call(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        tool_output: str,
        file_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        紧凑化工具调用（Compaction）- 无损、可逆
        
        移除可从外部状态重建的信息（如冗长的content），只保留path
        信息被"外部化"到文件系统，但可通过路径重建
        
        Args:
            tool_name: 工具名称
            tool_input: 工具输入
            tool_output: 工具输出（如果已写入文件，这里可以是摘要）
            file_path: 文件路径（如果已写入文件）
        
        Returns:
            紧凑化的工具调用记录
        """
        compact_record = {
            "tool": tool_name,
            "input": tool_input,
            "timestamp": datetime.now().isoformat()
        }
        
        if file_path:
            ***REMOVED*** 如果已写入文件，只保留路径（Compaction 核心：可逆的外部化）
            compact_record["output_file"] = str(file_path)
            compact_record["output_length"] = len(tool_output)
            compact_record["output_preview"] = tool_output[:100] + "..." if len(tool_output) > 100 else tool_output
            ***REMOVED*** 标记为已紧凑化，信息可通过文件路径重建
            compact_record["compacted"] = True
        else:
            ***REMOVED*** 如果结果不长，保留完整输出
            compact_record["output"] = tool_output
            compact_record["compacted"] = False
        
        return compact_record
    
    def compact_conversation_history(
        self,
        conversation_history: List[Dict[str, Any]],
        keep_recent: int = 3
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        紧凑化对话历史（Compaction）
        
        对早期的历史记录进行紧凑化，保留最近的完整记录作为 Few-shot Examples
        
        Args:
            conversation_history: 完整对话历史
            keep_recent: 保留最近多少条完整记录，默认3条
        
        Returns:
            (紧凑化的历史记录, 被移除的完整记录)
        """
        if len(conversation_history) <= keep_recent:
            return conversation_history, []
        
        ***REMOVED*** 分离早期和最近的历史
        early_history = conversation_history[:-keep_recent]
        recent_history = conversation_history[-keep_recent:]
        
        ***REMOVED*** 对早期历史进行紧凑化
        compacted_history = []
        removed_records = []
        
        for msg in early_history:
            role = msg.get("role", "")
            content = str(msg.get("content", ""))
            
            ***REMOVED*** 如果是工具调用结果且内容过长，进行紧凑化
            if role == "tool" and len(content) > 500:
                ***REMOVED*** 检查是否已经有文件路径
                if "file_path" in msg or "output_file" in msg:
                    ***REMOVED*** 已经紧凑化，只保留路径引用
                    compacted_msg = {
                        "role": role,
                        "content": f"[工具结果已保存到文件，长度: {len(content)} 字符]",
                        "file_path": msg.get("file_path") or msg.get("output_file"),
                        "compacted": True
                    }
                else:
                    ***REMOVED*** 需要紧凑化：写入文件
                    tool_name = msg.get("name", "unknown_tool")
                    file_path = self.output_dir / "tool_results" / f"{tool_name}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.txt"
                    file_path.write_text(content, encoding="utf-8")
                    
                    compacted_msg = {
                        "role": role,
                        "content": f"[工具结果已保存到文件: {file_path}，长度: {len(content)} 字符]",
                        "file_path": str(file_path),
                        "compacted": True
                    }
                    removed_records.append(msg)
                compacted_history.append(compacted_msg)
            else:
                ***REMOVED*** 保留原样（短消息不需要紧凑化）
                compacted_history.append(msg)
        
        ***REMOVED*** 合并紧凑化的早期历史和完整的最近历史
        return compacted_history + recent_history, removed_records
    
    def summarize_with_dump(
        self,
        conversation_history: List[Dict[str, Any]],
        keep_recent: int = 3
    ) -> Tuple[str, Path, List[Dict[str, Any]]]:
        """
        摘要化对话历史（Summarization）- 有损但带保险
        
        在生成摘要前，将完整上下文转储到文件（保险）
        然后生成摘要，保留最近几条完整记录作为 Few-shot Examples
        
        Args:
            conversation_history: 完整对话历史
            keep_recent: 保留最近多少条完整记录，默认3条
        
        Returns:
            (摘要+文件引用, 转储文件路径, 保留的最近记录)
        """
        ***REMOVED*** 第一步：转储完整上下文到文件（保险）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dump_file = self.output_dir / "chat_history" / f"full_context_dump_{timestamp}.json"
        
        dump_data = {
            "timestamp": datetime.now().isoformat(),
            "message_count": len(conversation_history),
            "full_history": conversation_history
        }
        dump_file.write_text(
            json.dumps(dump_data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        
        ***REMOVED*** 第二步：生成摘要（使用完整版本的数据，不是紧凑版本）
        summary = self._generate_summary(conversation_history, use_llm=True)
        
        ***REMOVED*** 第三步：保留最近几条完整记录
        recent_history = conversation_history[-keep_recent:] if len(conversation_history) > keep_recent else conversation_history
        
        ***REMOVED*** 返回摘要+文件引用
        file_ref = f"""对话历史摘要:
{summary}

完整上下文已转储到文件: {dump_file}
消息数量: {len(conversation_history)}
保留的最近 {len(recent_history)} 条完整记录作为 Few-shot Examples

提示：如需查看完整历史记录，可以使用 `read_file` 工具读取转储文件，或使用 `grep` 命令搜索特定内容。"""
        
        return file_ref, dump_file, recent_history


***REMOVED*** 全局上下文管理器实例（延迟初始化）
_context_manager_instance: Optional[ContextManager] = None


def get_context_manager(
    output_dir: Optional[Path] = None,
    llm_func: Optional[Callable] = None,
    pre_rot_threshold: int = 128000
) -> ContextManager:
    """
    获取全局上下文管理器实例
    
    Args:
        output_dir: 输出目录，如果为 None 则使用默认目录
        llm_func: LLM 调用函数，用于生成摘要（可选）
        pre_rot_threshold: 腐烂前阈值（tokens），默认128K
    
    Returns:
        ContextManager 实例
    """
    global _context_manager_instance
    
    if _context_manager_instance is None:
        _context_manager_instance = ContextManager(
            output_dir=output_dir,
            llm_func=llm_func,
            pre_rot_threshold=pre_rot_threshold
        )
    
    return _context_manager_instance
