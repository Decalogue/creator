"""
简化版记忆持久化测试

直接测试：
1. 记忆存储到 Neo4j
2. 记忆检索功能
3. 跨任务记忆检索
"""

import os
import sys
import json
from datetime import datetime

***REMOVED*** 确保当前目录在 Python 路径中
if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

***REMOVED*** 切换到 puppeteer 目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from tools.unimem_tool import UniMemRetainTool, UniMemRecallTool

def test_memory_persistence_simple():
    """简化版记忆持久化测试"""
    print("=" * 60)
    print("记忆持久化测试（简化版）")
    print("=" * 60)
    
    retain_tool = UniMemRetainTool('test_retain')
    recall_tool = UniMemRecallTool('test_recall')
    
    ***REMOVED*** 测试 1：存储第一条记忆
    print("\n【测试 1】存储第一条记忆...")
    memory1_content = "任务ID: test_task_001\n类型: novel\n小说简介: 一个普通的大学生林动，在一次意外中获得了神秘的祖石，从此踏上了修炼之路。\n\n最终大纲:\n第一章：意外获得祖石。林动在矿井中发现祖石。\n第二章：初入修炼世界。林动开始修炼。"
    
    success1, result1 = retain_tool.execute(
        experience={
            "content": memory1_content,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "task_id": "test_task_001",
                "task_type": "novel",
                "category": "final_outline",
                "test": True
            }
        },
        context={
            "session_id": "test_session_001",
            "user_id": "creative_assistant",
            "metadata": {
                "task_id": "test_task_001",
                "task_type": "novel",
                "category": "final_outline"
            }
        }
    )
    
    if success1:
        print(f"  ✓ 成功存储第一条记忆")
        print(f"    记忆ID: {result1.get('id', 'N/A') if isinstance(result1, dict) else 'N/A'}")
    else:
        print(f"  ✗ 存储失败: {result1}")
        return
    
    import time
    time.sleep(1)  ***REMOVED*** 等待数据写入
    
    ***REMOVED*** 测试 2：存储第二条记忆
    print("\n【测试 2】存储第二条记忆...")
    memory2_content = "任务ID: test_task_002\n类型: novel\n小说简介: 叶修曾是荣耀游戏中的顶尖职业选手，被誉为斗神。\n\n最终大纲:\n第一章：退役归来。叶修被俱乐部驱逐。\n第二章：新区征程。叶修使用散人职业君莫笑。"
    
    success2, result2 = retain_tool.execute(
        experience={
            "content": memory2_content,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "task_id": "test_task_002",
                "task_type": "novel",
                "category": "final_outline",
                "test": True
            }
        },
        context={
            "session_id": "test_session_002",
            "user_id": "creative_assistant",
            "metadata": {
                "task_id": "test_task_002",
                "task_type": "novel",
                "category": "final_outline"
            }
        }
    )
    
    if success2:
        print(f"  ✓ 成功存储第二条记忆")
        print(f"    记忆ID: {result2.get('id', 'N/A') if isinstance(result2, dict) else 'N/A'}")
    else:
        print(f"  ✗ 存储失败: {result2}")
    
    time.sleep(1)  ***REMOVED*** 等待数据写入
    
    ***REMOVED*** 测试 3：检索记忆（查询 test_task_001）
    print("\n【测试 3】检索 'test_task_001' 相关记忆...")
    success3, memories3 = recall_tool.execute(
        query="test_task_001 小说大纲 祖石",
        context={
            "session_id": "test_session_003",
            "user_id": "creative_assistant",
            "metadata": {}
        },
        top_k=5
    )
    
    if success3 and memories3:
        print(f"  ✓ 检索到 {len(memories3)} 条记忆")
        found_task1 = False
        for i, mem in enumerate(memories3, 1):
            if isinstance(mem, dict):
                content = mem.get('content', '')
                mem_id = mem.get('id', 'N/A')
                if 'test_task_001' in content or 'test_task_001' in str(mem_id):
                    found_task1 = True
                    print(f"    记忆 {i}: {mem_id}")
                    print(f"    内容: {content[:150]}...")
        if not found_task1:
            print(f"  ⚠ 检索到记忆但未找到 test_task_001")
            if memories3:
                print(f"    第一条记忆: {str(memories3[0])[:200]}...")
    else:
        print(f"  ✗ 检索失败或未找到记忆: {memories3 if not success3 else '未找到'}")
    
    ***REMOVED*** 测试 4：检索记忆（查询 叶修）
    print("\n【测试 4】检索 '叶修' 相关记忆...")
    success4, memories4 = recall_tool.execute(
        query="叶修 荣耀游戏 斗神",
        context={
            "session_id": "test_session_004",
            "user_id": "creative_assistant",
            "metadata": {}
        },
        top_k=5
    )
    
    if success4 and memories4:
        print(f"  ✓ 检索到 {len(memories4)} 条记忆")
        found_task2 = False
        for i, mem in enumerate(memories4, 1):
            if isinstance(mem, dict):
                content = mem.get('content', '')
                mem_id = mem.get('id', 'N/A')
                if '叶修' in content or 'test_task_002' in content:
                    found_task2 = True
                    print(f"    记忆 {i}: {mem_id}")
                    print(f"    内容: {content[:150]}...")
        if not found_task2:
            print(f"  ⚠ 检索到记忆但未找到 叶修 相关内容")
    else:
        print(f"  ✗ 检索失败或未找到记忆: {memories4 if not success4 else '未找到'}")
    
    ***REMOVED*** 测试 5：验证 Neo4j 中的数据
    print("\n【测试 5】验证 Neo4j 中的数据...")
    try:
        from py2neo import Graph
        import os
        
        ***REMOVED*** 获取 Neo4j 连接信息
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        neo4j_password = os.getenv("NEO4J_PASSWORD", "neo4j")
        
        graph = Graph(neo4j_uri, auth=(neo4j_user, neo4j_password))
        
        ***REMOVED*** 查询所有 Memory 节点
        query = "MATCH (m:Memory) RETURN count(m) as count"
        result = graph.run(query).data()
        total_count = result[0]['count'] if result else 0
        print(f"  ✓ Neo4j 中共有 {total_count} 条记忆")
        
        ***REMOVED*** 查询测试任务的记忆
        query = """
        MATCH (m:Memory) 
        WHERE m.content CONTAINS 'test_task_001' OR m.content CONTAINS 'test_task_002'
        RETURN m.id, substring(m.content, 0, 100) as content_preview, m.timestamp
        ORDER BY m.timestamp DESC
        LIMIT 5
        """
        results = graph.run(query).data()
        
        if results:
            print(f"  ✓ 找到 {len(results)} 条测试任务的记忆:")
            for i, r in enumerate(results, 1):
                print(f"     {i}. ID: {r['m.id']}")
                print(f"        时间: {r['m.timestamp']}")
                print(f"        内容: {r['content_preview']}...")
        else:
            print("  ⚠ 未找到测试任务的记忆（可能还未同步）")
            
    except Exception as e:
        print(f"  ⚠ 无法连接到 Neo4j: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
    return {
        "memory1_stored": success1,
        "memory2_stored": success2,
        "memory1_retrieved": found_task1 if success3 and memories3 else False,
        "memory2_retrieved": found_task2 if success4 and memories4 else False,
        "neo4j_total_count": total_count if 'total_count' in locals() else 0
    }

if __name__ == "__main__":
    results = test_memory_persistence_simple()
    print("\n测试结果汇总:")
    print(json.dumps(results, indent=2, ensure_ascii=False))

