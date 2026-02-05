#!/usr/bin/env python3
"""
测试 Multi-Agent 协作系统
"""
import sys
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.multi_agent import (
    MasterAgent,
    SubAgent,
    CollaborationMode,
    get_master_agent
)


def test_task_delegation():
    """测试任务委托模式"""
    print("=" * 60)
    print("测试任务委托（Task Delegation）")
    print("=" * 60)
    
    master = MasterAgent(sandbox_dir=Path("agent/sandbox"))
    
    # 定义输出 Schema
    output_schema = {
        "type": "object",
        "properties": {
            "result": {"type": "string"},
            "status": {"type": "string"}
        },
        "required": ["result", "status"]
    }
    
    # 委托任务
    task_description = "计算 2 + 3 的结果"
    
    print(f"任务描述: {task_description}")
    print(f"输出 Schema: {json.dumps(output_schema, ensure_ascii=False, indent=2)}")
    print()
    
    success, result = master.delegate_task(
        task_description=task_description,
        output_schema=output_schema,
        verbose=False
    )
    
    print(f"执行结果: {'成功' if success else '失败'}")
    print(f"结果: {result}")
    print()


def test_info_sync():
    """测试信息同步模式"""
    print("=" * 60)
    print("测试信息同步（Information Synchronization）")
    print("=" * 60)
    
    master = MasterAgent(sandbox_dir=Path("agent/sandbox"))
    
    # 先运行一些任务，建立对话历史
    print("【建立 Master Agent 对话历史】")
    master.agent.conversation_history = [
        {"role": "system", "content": "你是一个助手"},
        {"role": "user", "content": "计算 2 + 3"},
        {"role": "assistant", "content": "答案是 5"},
        {"role": "user", "content": "再计算 10 * 2"},
        {"role": "assistant", "content": "答案是 20"},
    ]
    master.conversation_history = master.agent.conversation_history.copy()
    
    print(f"对话历史: {len(master.conversation_history)} 条消息")
    print()
    
    # 创建信息同步任务
    task_description = "基于之前的对话历史，总结我们进行了哪些计算"
    
    print(f"任务描述: {task_description}")
    print()
    
    success, result = master.sync_info_task(
        task_description=task_description,
        verbose=False
    )
    
    print(f"执行结果: {'成功' if success else '失败'}")
    print(f"结果: {result}")
    print()


def test_sub_agent_creation():
    """测试 Sub-Agent 创建"""
    print("=" * 60)
    print("测试 Sub-Agent 创建")
    print("=" * 60)
    
    master = MasterAgent(sandbox_dir=Path("agent/sandbox"))
    
    # 创建任务委托模式的 Sub-Agent
    sub1 = master.create_sub_agent(
        task_description="测试任务1",
        output_schema={"type": "object", "properties": {"result": {"type": "string"}}},
        mode=CollaborationMode.TASK_DELEGATION
    )
    
    print(f"Sub-Agent 1:")
    print(f"  ID: {sub1.agent_id}")
    print(f"  模式: {sub1.mode.value}")
    print(f"  任务: {sub1.task_description}")
    print(f"  输出 Schema: {sub1.output_schema is not None}")
    print()
    
    # 创建信息同步模式的 Sub-Agent
    master.conversation_history = [
        {"role": "user", "content": "测试消息"}
    ]
    
    sub2 = master.create_sub_agent(
        task_description="测试任务2",
        mode=CollaborationMode.INFO_SYNC
    )
    
    print(f"Sub-Agent 2:")
    print(f"  ID: {sub2.agent_id}")
    print(f"  模式: {sub2.mode.value}")
    print(f"  任务: {sub2.task_description}")
    print(f"  共享上下文: {len(sub2.shared_context)} 条消息")
    print()


def test_shared_sandbox():
    """测试共享沙箱"""
    print("=" * 60)
    print("测试共享沙箱")
    print("=" * 60)
    
    master = MasterAgent(sandbox_dir=Path("agent/sandbox"))
    
    # Master Agent 创建文件
    test_file = master.sandbox_dir / "master_file.txt"
    test_file.write_text("Master Agent 创建的文件", encoding="utf-8")
    
    print(f"Master Agent 创建文件: {test_file}")
    print(f"文件内容: {test_file.read_text(encoding='utf-8')}")
    print()
    
    # Sub-Agent 应该可以访问同一沙箱
    sub_agent = master.create_sub_agent(
        task_description="读取 master_file.txt",
        mode=CollaborationMode.TASK_DELEGATION
    )
    
    print(f"Sub-Agent 沙箱目录: {sub_agent.sandbox_dir}")
    print(f"文件是否存在: {(sub_agent.sandbox_dir / 'master_file.txt').exists()}")
    print()


if __name__ == "__main__":
    print("Multi-Agent 协作系统测试")
    print()
    
    test_sub_agent_creation()
    test_shared_sandbox()
    # 注意：实际的任务执行需要 LLM，这里只测试创建和配置
    # test_task_delegation()
    # test_info_sync()
    
    print("=" * 60)
    print("测试完成！")
    print("=" * 60)
