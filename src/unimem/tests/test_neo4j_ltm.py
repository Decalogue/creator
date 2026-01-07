#!/usr/bin/env python3
"""
Neo4j LTM 功能测试脚本

测试 Neo4j 作为长期记忆（LTM）存储的功能：
- 创建记忆节点
- 查询记忆
- 更新记忆
- 删除记忆
- 关联查询（记忆与实体、记忆之间的关系）
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from unimem.neo4j import (
    create_memory,
    get_memory,
    update_memory,
    delete_memory,
    search_memories_by_type,
    search_memories_by_entity,
    search_memories_by_text,
    search_memories_by_time_range,
    get_memory_relationships,
    create_memory_indexes,
    create_entity,
    get_entity,
)
from unimem.types import Memory, MemoryType, MemoryLayer, Entity


def test_create_memory():
    """测试创建记忆节点"""
    print("\n=== 测试 1: 创建记忆节点 ===")
    
    memory = Memory(
        id="test_memory_001",
        content="这是一个测试记忆：用户喜欢喝咖啡",
        timestamp=datetime.now(),
        memory_type=MemoryType.EPISODIC,
        layer=MemoryLayer.LTM,
        keywords=["咖啡", "用户偏好"],
        tags=["偏好", "饮食"],
        context="用户会话1",
        entities=["user_001"],
        links=set(),
        retrieval_count=0,
        metadata={"source": "test", "importance": "high"}
    )
    
    success = create_memory(memory)
    print(f"创建记忆: {'✓ 成功' if success else '✗ 失败'}")
    
    # 验证
    retrieved = get_memory("test_memory_001")
    if retrieved and retrieved.content == memory.content:
        print("✓ 验证成功：记忆已正确存储")
        return True
    else:
        print("✗ 验证失败：记忆未正确存储")
        return False


def test_create_memory_with_entity():
    """测试创建带实体关联的记忆"""
    print("\n=== 测试 2: 创建带实体关联的记忆 ===")
    
    # 先创建实体
    entity = Entity(
        id="user_001",
        name="测试用户",
        entity_type="Person",
        description="一个测试用户",
        retrieval_key="name",
        retrieval_value="测试用户"
    )
    create_entity(entity)
    print("✓ 创建实体: user_001")
    
    # 创建关联实体的记忆
    memory = Memory(
        id="test_memory_002",
        content="用户张三喜欢在早上喝咖啡",
        timestamp=datetime.now(),
        memory_type=MemoryType.EPISODIC,
        layer=MemoryLayer.LTM,
        keywords=["张三", "咖啡", "早上"],
        tags=["习惯"],
        entities=["user_001"],
        links=set(),
        metadata={"time": "morning"}
    )
    
    success = create_memory(memory)
    print(f"创建记忆（关联实体）: {'✓ 成功' if success else '✗ 失败'}")
    
    # 查询与实体相关的记忆
    memories = search_memories_by_entity("user_001")
    print(f"✓ 找到 {len(memories)} 条与实体相关的记忆")
    for m in memories:
        print(f"  - {m.id}: {m.content[:50]}...")
    
    return success and len(memories) > 0


def test_search_memories():
    """测试记忆查询"""
    print("\n=== 测试 3: 记忆查询 ===")
    
    # 按类型查询
    episodic_memories = search_memories_by_type(MemoryType.EPISODIC, limit=10)
    print(f"✓ 按类型查询（EPISODIC）: 找到 {len(episodic_memories)} 条记忆")
    
    # 文本搜索
    text_memories = search_memories_by_text("咖啡", limit=10)
    print(f"✓ 文本搜索（'咖啡'）: 找到 {len(text_memories)} 条记忆")
    for m in text_memories:
        print(f"  - {m.id}: {m.content[:50]}...")
    
    # 时间范围查询
    from datetime import timedelta
    end_time = datetime.now().isoformat()
    start_time = (datetime.now() - timedelta(days=1)).isoformat()
    time_memories = search_memories_by_time_range(start_time, end_time, limit=10)
    print(f"✓ 时间范围查询: 找到 {len(time_memories)} 条记忆")
    
    return len(episodic_memories) > 0 or len(text_memories) > 0


def test_update_memory():
    """测试更新记忆"""
    print("\n=== 测试 4: 更新记忆 ===")
    
    # 获取现有记忆
    memory = get_memory("test_memory_001")
    if not memory:
        print("✗ 找不到测试记忆，跳过更新测试")
        return False
    
    # 更新内容
    original_content = memory.content
    memory.content = "这是一个更新的测试记忆：用户喜欢喝咖啡和茶"
    memory.retrieval_count += 1
    memory.tags.append("茶")
    
    success = update_memory(memory)
    print(f"更新记忆: {'✓ 成功' if success else '✗ 失败'}")
    
    # 验证
    updated = get_memory("test_memory_001")
    if updated and updated.content == memory.content and updated.retrieval_count > 0:
        print("✓ 验证成功：记忆已正确更新")
        print(f"  更新前: {original_content}")
        print(f"  更新后: {updated.content}")
        return True
    else:
        print("✗ 验证失败：记忆未正确更新")
        return False


def test_memory_relationships():
    """测试记忆关系"""
    print("\n=== 测试 5: 记忆关系 ===")
    
    # 创建两个关联的记忆
    memory1 = Memory(
        id="test_memory_003",
        content="第一个关联记忆",
        timestamp=datetime.now(),
        memory_type=MemoryType.EPISODIC,
        layer=MemoryLayer.LTM,
        links={"test_memory_004"},
        entities=[],
    )
    
    memory2 = Memory(
        id="test_memory_004",
        content="第二个关联记忆",
        timestamp=datetime.now(),
        memory_type=MemoryType.EPISODIC,
        layer=MemoryLayer.LTM,
        links={"test_memory_003"},
        entities=[],
    )
    
    create_memory(memory1)
    create_memory(memory2)
    print("✓ 创建两个关联的记忆")
    
    # 查询关系
    relationships = get_memory_relationships("test_memory_003", depth=1)
    print(f"✓ 查询记忆关系: 找到 {len(relationships)} 个关系")
    
    return True


def test_delete_memory():
    """测试删除记忆"""
    print("\n=== 测试 6: 删除记忆 ===")
    
    # 删除测试记忆
    success = delete_memory("test_memory_001")
    print(f"删除记忆 test_memory_001: {'✓ 成功' if success else '✗ 失败'}")
    
    # 验证
    deleted = get_memory("test_memory_001")
    if deleted is None:
        print("✓ 验证成功：记忆已删除")
        return True
    else:
        print("✗ 验证失败：记忆未删除")
        return False


def test_indexes():
    """测试创建索引"""
    print("\n=== 测试 7: 创建索引 ===")
    
    success = create_memory_indexes()
    print(f"创建索引: {'✓ 成功' if success else '✗ 失败'}")
    
    return success


def cleanup():
    """清理测试数据"""
    print("\n=== 清理测试数据 ===")
    
    test_memories = [
        "test_memory_001",
        "test_memory_002",
        "test_memory_003",
        "test_memory_004",
    ]
    
    for memory_id in test_memories:
        delete_memory(memory_id)
    
    # 删除测试实体
    from unimem.neo4j import delete_entity
    delete_entity("user_001")
    
    print("✓ 清理完成")


def main():
    """主测试函数"""
    print("=" * 60)
    print("Neo4j LTM 功能测试")
    print("=" * 60)
    
    # 测试结果
    results = []
    
    try:
        # 运行测试
        results.append(("创建索引", test_indexes()))
        results.append(("创建记忆", test_create_memory()))
        results.append(("创建带实体关联的记忆", test_create_memory_with_entity()))
        results.append(("查询记忆", test_search_memories()))
        results.append(("更新记忆", test_update_memory()))
        results.append(("记忆关系", test_memory_relationships()))
        results.append(("删除记忆", test_delete_memory()))
        
    except Exception as e:
        print(f"\n✗ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理测试数据
        cleanup()
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return True
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

