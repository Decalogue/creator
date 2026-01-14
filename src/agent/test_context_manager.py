#!/usr/bin/env python3
"""
测试上下文管理器
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.context_manager import get_context_manager


def test_tool_result_offloading():
    """测试工具结果卸载"""
    print("=" * 60)
    print("测试工具结果卸载")
    print("=" * 60)
    
    manager = get_context_manager()
    
    # 测试短结果（不卸载）
    short_result = "计算结果：2 + 3 = 5"
    result, file_path = manager.offload_tool_result(
        tool_name="calculator",
        tool_input={"expression": "2 + 3"},
        tool_output=short_result,
        max_length=500
    )
    
    print(f"短结果测试:")
    print(f"  结果: {result}")
    print(f"  文件路径: {file_path}")
    print()
    
    # 测试长结果（卸载）
    long_result = "这是一个很长的工具输出结果。\n" * 100  # 生成长结果
    result, file_path = manager.offload_tool_result(
        tool_name="get_weather",
        tool_input={"city": "北京"},
        tool_output=long_result,
        max_length=500
    )
    
    print(f"长结果测试:")
    print(f"  结果预览: {result[:200]}...")
    print(f"  文件路径: {file_path}")
    if file_path:
        print(f"  文件大小: {file_path.stat().st_size} bytes")
        print(f"  文件内容预览:")
        print(file_path.read_text(encoding='utf-8')[:300] + "...")
    print()


def test_chat_history_offloading():
    """测试聊天历史卸载"""
    print("=" * 60)
    print("测试聊天历史卸载")
    print("=" * 60)
    
    manager = get_context_manager()
    
    # 模拟对话历史
    conversation_history = [
        {"role": "system", "content": "你是一个助手"},
        {"role": "user", "content": "计算 2 + 3"},
        {"role": "assistant", "content": "我来帮你计算"},
        {"role": "tool", "content": "计算结果：5"},
        {"role": "assistant", "content": "答案是 5"},
    ]
    
    summary_ref, history_file = manager.offload_chat_history(conversation_history)
    
    print(f"摘要+文件引用:")
    print(summary_ref)
    print()
    print(f"历史文件: {history_file}")
    print(f"文件大小: {history_file.stat().st_size} bytes")
    print()


def test_context_length_estimation():
    """测试上下文长度估算"""
    print("=" * 60)
    print("测试上下文长度估算")
    print("=" * 60)
    
    manager = get_context_manager()
    
    # 测试短对话
    short_history = [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好！"},
    ]
    
    tokens, needs_reduction = manager.estimate_context_length(short_history, threshold=128000)
    print(f"短对话:")
    print(f"  估算 tokens: {tokens}")
    print(f"  需要缩减: {needs_reduction}")
    print()
    
    # 测试长对话（模拟）
    long_history = [
        {"role": "user", "content": "这是一个很长的用户消息。" * 1000},
        {"role": "assistant", "content": "这是一个很长的助手回复。" * 1000},
    ] * 50  # 50轮对话
    
    tokens, needs_reduction = manager.estimate_context_length(long_history, threshold=128000)
    print(f"长对话:")
    print(f"  估算 tokens: {tokens}")
    print(f"  需要缩减: {needs_reduction}")
    print()


def test_compact_tool_call():
    """测试工具调用紧凑化"""
    print("=" * 60)
    print("测试工具调用紧凑化")
    print("=" * 60)
    
    manager = get_context_manager()
    
    # 测试有文件路径的情况
    long_output = "这是一个很长的工具输出。" * 100
    file_path = manager.output_dir / "tool_results" / "test_output.txt"
    file_path.write_text(long_output, encoding="utf-8")
    
    compact_record = manager.compact_tool_call(
        tool_name="test_tool",
        tool_input={"param": "value"},
        tool_output=long_output,
        file_path=file_path
    )
    
    print("紧凑化记录:")
    print(f"  工具: {compact_record['tool']}")
    print(f"  输入: {compact_record['input']}")
    print(f"  输出文件: {compact_record.get('output_file')}")
    print(f"  输出长度: {compact_record.get('output_length')}")
    print(f"  输出预览: {compact_record.get('output_preview')}")
    print()


def test_compaction():
    """测试对话历史紧凑化"""
    print("=" * 60)
    print("测试对话历史紧凑化（Compaction）")
    print("=" * 60)
    
    manager = get_context_manager()
    
    # 创建包含长工具结果的对话历史
    conversation_history = [
        {"role": "system", "content": "你是一个助手"},
        {"role": "user", "content": "查询天气"},
        {"role": "assistant", "content": "我来查询"},
        {"role": "tool", "content": "这是一个很长的工具输出结果。\n" * 100},  # 长结果
        {"role": "assistant", "content": "查询完成"},
        {"role": "user", "content": "再查询一次"},
        {"role": "assistant", "content": "好的"},
    ]
    
    compacted_history, removed_records = manager.compact_conversation_history(
        conversation_history,
        keep_recent=3
    )
    
    print(f"原始历史: {len(conversation_history)} 条消息")
    print(f"紧凑化后: {len(compacted_history)} 条消息")
    print(f"移除的记录: {len(removed_records)} 条")
    print()
    
    # 检查紧凑化结果
    for i, msg in enumerate(compacted_history):
        if msg.get("compacted"):
            print(f"消息 {i+1}: [已紧凑化] {msg.get('content', '')[:100]}...")
            print(f"  文件路径: {msg.get('file_path', 'N/A')}")
        else:
            print(f"消息 {i+1}: {msg.get('role', 'unknown')} - {str(msg.get('content', ''))[:50]}...")
    print()


def test_summarization_with_dump():
    """测试摘要化（带转储）"""
    print("=" * 60)
    print("测试摘要化（Summarization with Dump）")
    print("=" * 60)
    
    manager = get_context_manager()
    
    # 创建对话历史
    conversation_history = [
        {"role": "system", "content": "你是一个助手"},
        {"role": "user", "content": "计算 2 + 3"},
        {"role": "assistant", "content": "我来计算"},
        {"role": "tool", "content": "计算结果：5"},
        {"role": "assistant", "content": "答案是 5"},
        {"role": "user", "content": "再计算 10 * 2"},
        {"role": "assistant", "content": "我来计算"},
        {"role": "tool", "content": "计算结果：20"},
        {"role": "assistant", "content": "答案是 20"},
    ]
    
    summary_ref, dump_file, recent_history = manager.summarize_with_dump(
        conversation_history,
        keep_recent=3
    )
    
    print("摘要+文件引用:")
    print(summary_ref[:300] + "..." if len(summary_ref) > 300 else summary_ref)
    print()
    print(f"转储文件: {dump_file}")
    print(f"文件大小: {dump_file.stat().st_size} bytes")
    print(f"保留的最近记录: {len(recent_history)} 条")
    print()


if __name__ == "__main__":
    print("上下文管理器测试")
    print()
    
    test_tool_result_offloading()
    test_chat_history_offloading()
    test_context_length_estimation()
    test_compact_tool_call()
    test_compaction()
    test_summarization_with_dump()
    
    print("=" * 60)
    print("测试完成！")
    print("=" * 60)
