"""
测试记忆持久化存储和检索

验证：
1. 记忆是否正确存储到 Neo4j
2. 不同任务之间能否检索到之前的记忆
3. 全流程是否打通
"""

import os
import sys
import json

***REMOVED*** 确保当前目录在 Python 路径中
if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

from inference.reasoning.reasoning_with_memory import GraphReasoningWithMemory
from inference.graph.agent_graph import AgentGraph
from agent.register.register_with_memory import agent_global_registry_with_memory
from agent.register.register import agent_global_registry

***REMOVED*** 确保 UniMem 工具被导入
from tools.unimem_tool import UniMemRetainTool, UniMemRecallTool

import yaml
global_config = yaml.safe_load(open("./config/global.yaml", "r"))

def test_memory_persistence():
    """测试记忆持久化"""
    print("=" * 60)
    print("记忆持久化测试")
    print("=" * 60)
    
    ***REMOVED*** 测试任务 1：创建第一个任务并存储记忆
    print("\n【测试 1】创建第一个任务并存储记忆...")
    task1 = {
        "id": "test_task_001",
        "type": "novel",
        "Question": "生成小说大纲",
        "Introduction": "一个普通的大学生林动，在一次意外中获得了神秘的祖石，从此踏上了修炼之路。"
    }
    
    ***REMOVED*** 创建 AgentGraph
    graph1 = AgentGraph()
    
    ***REMOVED*** 使用带记忆的 GraphReasoning
    reasoning1 = GraphReasoningWithMemory(
        task1, 
        graph1, 
        unimem_enabled=True
    )
    
    ***REMOVED*** 执行推理（简化版本，只测试记忆存储）
    print("  执行推理...")
    reasoning1.start(None)
    
    ***REMOVED*** 模拟最终答案（用于存储测试）
    final_answer1 = "这是测试任务1的最终大纲：第一章测试内容..."
    
    ***REMOVED*** 存储记忆
    print("  存储最终结果到记忆系统...")
    reasoning1._store_final_result(final_answer1)
    
    print(f"  ✓ 任务1完成")
    print(f"  - 检索到的记忆: {len(reasoning1.retrieved_memories)} 条")
    print(f"  - 存储的记忆: {len(reasoning1.stored_memories)} 条")
    
    ***REMOVED*** 等待一下确保数据写入
    import time
    time.sleep(2)
    
    ***REMOVED*** 测试任务 2：创建第二个任务并检索之前的记忆
    print("\n【测试 2】创建第二个任务并检索之前的记忆...")
    task2 = {
        "id": "test_task_002",
        "type": "novel",
        "Question": "生成小说大纲",
        "Introduction": "一个普通的大学生林动，在一次意外中获得了神秘的祖石，从此踏上了修炼之路。"
    }
    
    ***REMOVED*** 创建 AgentGraph
    graph2 = AgentGraph()
    
    ***REMOVED*** 使用带记忆的 GraphReasoning
    reasoning2 = GraphReasoningWithMemory(
        task2, 
        graph2, 
        unimem_enabled=True
    )
    
    ***REMOVED*** 执行推理（只测试记忆检索）
    print("  执行推理并检索记忆...")
    reasoning2.start(None)
    
    print(f"  ✓ 任务2完成")
    print(f"  - 检索到的记忆: {len(reasoning2.retrieved_memories)} 条")
    
    ***REMOVED*** 检查是否检索到了任务1的记忆
    found_task1 = False
    for mem in reasoning2.retrieved_memories:
        if isinstance(mem, dict):
            content = mem.get('content', '')
            if 'test_task_001' in content or '测试任务1' in content:
                found_task1 = True
                print(f"  ✓ 成功检索到任务1的记忆!")
                print(f"    内容预览: {content[:200]}...")
                break
    
    if not found_task1 and len(reasoning2.retrieved_memories) > 0:
        print(f"  ⚠ 检索到了 {len(reasoning2.retrieved_memories)} 条记忆，但未找到任务1的记忆")
        print(f"    第一条记忆: {str(reasoning2.retrieved_memories[0])[:200]}...")
    elif not found_task1:
        print(f"  ⚠ 未检索到任何记忆")
    
    ***REMOVED*** 验证 Neo4j 中的数据
    print("\n【测试 3】验证 Neo4j 中的记忆数据...")
    from unimem.neo4j import get_graph
    
    graph = get_graph()
    if graph:
        query = "MATCH (m:Memory) RETURN count(m) as count"
        result = graph.run(query).data()
        count = result[0]['count'] if result else 0
        print(f"  ✓ Neo4j 中共有 {count} 条记忆")
        
        ***REMOVED*** 查询测试任务的记忆
        query = "MATCH (m:Memory) WHERE m.content CONTAINS 'test_task' OR m.content CONTAINS '测试任务' RETURN m.id, m.content, m.timestamp ORDER BY m.timestamp DESC LIMIT 5"
        results = graph.run(query).data()
        
        if results:
            print(f"  ✓ 找到 {len(results)} 条测试任务的记忆:")
            for i, r in enumerate(results, 1):
                content = r['m.content'][:100] if r['m.content'] else ""
                print(f"     {i}. {r['m.id']}: {content}...")
        else:
            print("  ⚠ 未找到测试任务的记忆")
    else:
        print("  ✗ 无法连接到 Neo4j")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
    ***REMOVED*** 返回测试结果
    return {
        "task1_retrieved": len(reasoning1.retrieved_memories),
        "task1_stored": len(reasoning1.stored_memories),
        "task2_retrieved": len(reasoning2.retrieved_memories),
        "found_task1_memory": found_task1,
        "neo4j_memory_count": count if graph else 0
    }

if __name__ == "__main__":
    results = test_memory_persistence()
    print("\n测试结果汇总:")
    print(json.dumps(results, indent=2, ensure_ascii=False))

