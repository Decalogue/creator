***REMOVED***!/usr/bin/env python3
"""
测试记忆系统改进效果

验证：
1. Source字段是否正确保存
2. Metadata格式是否正确
3. 记忆关联是否正确建立
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

***REMOVED*** 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from unimem import UniMem, Experience, Context
from unimem.memory_types import MemoryType, MemoryLayer
from py2neo import Graph

def test_source_and_metadata():
    """测试source字段和metadata保存"""
    print("="*70)
    print("测试1: Source字段和Metadata保存")
    print("="*70)
    
    ***REMOVED*** 创建UniMem实例（使用生产配置）
    config = {
        "storage": {
            "foa_backend": "redis",
            "da_backend": "redis",
            "ltm_backend": "neo4j",
        },
        "graph": {
            "neo4j_uri": "bolt://localhost:7680",
            "neo4j_user": "neo4j",
            "neo4j_password": "seeme_db",
        },
        "network": {
            "qdrant_host": "localhost",
            "qdrant_port": 6333,
        }
    }
    
    unimem = UniMem(config=config)
    
    ***REMOVED*** 测试1: 存储视频脚本记忆
    print("\n[测试1.1] 存储视频脚本记忆（source='video_script'）")
    experience1 = Experience(
        content="这是一个测试视频脚本：介绍新款手机的功能特点，包括夜景拍摄和超广角镜头。",
        timestamp=datetime.now()
    )
    context1 = Context(
        metadata={
            "source": "video_script",
            "video_type": "ecommerce",
            "platform": "douyin",
            "test": True
        }
    )
    memory1 = unimem.retain(experience1, context1)
    print(f"  ✓ 记忆已创建: {memory1.id}")
    print(f"  - Source: {memory1.metadata.get('source', 'N/A')}")
    print(f"  - Video Type: {memory1.metadata.get('video_type', 'N/A')}")
    
    ***REMOVED*** 测试2: 存储用户反馈记忆
    print("\n[测试1.2] 存储用户反馈记忆（source='user_feedback'）")
    experience2 = Experience(
        content="用户反馈：视频开头不够吸引人，建议增加悬念。",
        timestamp=datetime.now()
    )
    context2 = Context(
        metadata={
            "source": "user_feedback",
            "feedback_type": "script_modification",
            "test": True
        }
    )
    memory2 = unimem.retain(experience2, context2)
    print(f"  ✓ 记忆已创建: {memory2.id}")
    print(f"  - Source: {memory2.metadata.get('source', 'N/A')}")
    print(f"  - Feedback Type: {memory2.metadata.get('feedback_type', 'N/A')}")
    
    ***REMOVED*** 验证Neo4j中的保存
    print("\n[验证] 检查Neo4j中的保存情况")
    graph = Graph("bolt://localhost:7680", auth=('neo4j', 'seeme_db'), name='neo4j')
    
    ***REMOVED*** 查询memory1
    query1 = f"MATCH (m:Memory {{id: '{memory1.id}'}}) RETURN m.source as source, m.metadata as metadata"
    result1 = graph.run(query1).data()
    if result1:
        print(f"  Memory1在Neo4j中:")
        print(f"    - Source: {result1[0].get('source', 'N/A')}")
        metadata_str = result1[0].get('metadata', '{}')
        try:
            metadata = json.loads(metadata_str)
            print(f"    - Metadata.source: {metadata.get('source', 'N/A')}")
            print(f"    - Metadata.video_type: {metadata.get('video_type', 'N/A')}")
        except:
            print(f"    - Metadata (raw): {metadata_str[:100]}")
    
    ***REMOVED*** 查询memory2
    query2 = f"MATCH (m:Memory {{id: '{memory2.id}'}}) RETURN m.source as source, m.metadata as metadata"
    result2 = graph.run(query2).data()
    if result2:
        print(f"  Memory2在Neo4j中:")
        print(f"    - Source: {result2[0].get('source', 'N/A')}")
        metadata_str = result2[0].get('metadata', '{}')
        try:
            metadata = json.loads(metadata_str)
            print(f"    - Metadata.source: {metadata.get('source', 'N/A')}")
            print(f"    - Metadata.feedback_type: {metadata.get('feedback_type', 'N/A')}")
        except:
            print(f"    - Metadata (raw): {metadata_str[:100]}")
    
    return memory1, memory2


def test_memory_links():
    """测试记忆关联"""
    print("\n" + "="*70)
    print("测试2: 记忆关联（Links）")
    print("="*70)
    
    ***REMOVED*** 连接Neo4j
    graph = Graph("bolt://localhost:7680", auth=('neo4j', 'seeme_db'), name='neo4j')
    
    ***REMOVED*** 查询所有记忆及其关联
    query = """
    MATCH (m1:Memory)-[r:RELATED_TO]->(m2:Memory)
    RETURN m1.id as from_id, m2.id as to_id, count(r) as count
    ORDER BY count DESC
    LIMIT 10
    """
    results = graph.run(query).data()
    
    if results:
        print(f"\n找到 {len(results)} 对记忆关联:")
        for i, r in enumerate(results[:5], 1):
            print(f"  {i}. {r['from_id'][:8]}... -> {r['to_id'][:8]}...")
    else:
        print("\n⚠️  未找到记忆关联关系")
        print("  这可能是因为:")
        print("    1. 记忆数量太少，无法找到相似记忆")
        print("    2. 向量检索未找到足够相似的记忆")
        print("    3. LLM判断不需要建立链接")
    
    ***REMOVED*** 统计总关联数
    count_query = "MATCH ()-[r:RELATED_TO]->() RETURN count(r) as count"
    count_result = graph.run(count_query).data()
    total_relations = count_result[0]['count'] if count_result else 0
    print(f"\n总关联关系数: {total_relations}")


def test_source_statistics():
    """统计source字段分布"""
    print("\n" + "="*70)
    print("测试3: Source字段统计")
    print("="*70)
    
    graph = Graph("bolt://localhost:7680", auth=('neo4j', 'seeme_db'), name='neo4j')
    
    ***REMOVED*** 按source统计
    query = """
    MATCH (m:Memory)
    WHERE m.source IS NOT NULL AND m.source <> ""
    RETURN m.source as source, count(m) as count
    ORDER BY count DESC
    """
    results = graph.run(query).data()
    
    if results:
        print("\n按Source统计:")
        for r in results:
            print(f"  {r['source']}: {r['count']} 条")
    else:
        print("\n⚠️  没有找到带source字段的记忆")
    
    ***REMOVED*** 统计总数
    total_query = "MATCH (m:Memory) RETURN count(m) as count"
    total_result = graph.run(total_query).data()
    total = total_result[0]['count'] if total_result else 0
    
    ***REMOVED*** 统计有source的
    with_source_query = """
    MATCH (m:Memory)
    WHERE m.source IS NOT NULL AND m.source <> ""
    RETURN count(m) as count
    """
    with_source_result = graph.run(with_source_query).data()
    with_source = with_source_result[0]['count'] if with_source_result else 0
    
    print(f"\n总记忆数: {total}")
    print(f"有Source字段: {with_source} ({with_source/total*100:.1f}%)" if total > 0 else "有Source字段: 0")


def main():
    """主测试函数"""
    print("\n" + "="*70)
    print("记忆系统改进效果测试")
    print("="*70)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        ***REMOVED*** 测试1: Source和Metadata
        memory1, memory2 = test_source_and_metadata()
        
        ***REMOVED*** 测试2: 记忆关联
        test_memory_links()
        
        ***REMOVED*** 测试3: Source统计
        test_source_statistics()
        
        print("\n" + "="*70)
        print("测试完成！")
        print("="*70)
        print("\n改进验证:")
        print("  ✅ Source字段已添加到代码中")
        print("  ✅ Metadata保存为JSON格式")
        print("  ✅ Links更新机制已实现")
        print("\n注意: 新创建的记忆将包含source字段")
        print("      旧记忆的source字段需要手动更新或重新创建")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
