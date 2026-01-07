***REMOVED***!/usr/bin/env python3
"""
存储和检索用户画像示例

展示如何使用 UniMem 存储和检索用户的长期记忆和画像信息。
"""

import sys
from pathlib import Path
from datetime import datetime

***REMOVED*** 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from unimem.types import Memory, MemoryType, MemoryLayer
from unimem.neo4j import (
    create_memory,
    search_memories_by_type,
    search_memories_by_text,
    create_memory_indexes,
)


def store_user_profile_memories():
    """存储用户画像相关的记忆"""
    print("存储用户画像记忆...")
    
    ***REMOVED*** 创建索引
    create_memory_indexes()
    
    memories = [
        ***REMOVED*** 用户偏好记忆
        Memory(
            id="user_profile_preference_001",
            content="用户偏好使用最简单的代码解决方案，不喜欢过度复杂的实现",
            timestamp=datetime.now(),
            memory_type=MemoryType.USER_PROFILE,
            layer=MemoryLayer.LTM,
            keywords=["偏好", "简单", "代码风格"],
            tags=["coding_style", "preference"],
            metadata={
                "category": "preference",
                "importance": "high",
                "source": "conversation_history"
            }
        ),
        
        ***REMOVED*** 架构偏好记忆
        Memory(
            id="user_profile_architecture_001",
            content="用户关注架构简化，偏好减少系统复杂度（例如：将4个数据库简化为3个）",
            timestamp=datetime.now(),
            memory_type=MemoryType.USER_PROFILE,
            layer=MemoryLayer.LTM,
            keywords=["架构", "简化", "复杂度"],
            tags=["architecture", "optimization"],
            metadata={
                "category": "architecture",
                "importance": "high"
            }
        ),
        
        ***REMOVED*** 目录组织偏好
        Memory(
            id="user_profile_organization_001",
            content="用户偏好统一管理目录结构，将相关文件（如config、scripts）放到统一目录",
            timestamp=datetime.now(),
            memory_type=MemoryType.USER_PROFILE,
            layer=MemoryLayer.LTM,
            keywords=["目录", "组织", "管理"],
            tags=["file_organization", "preference"],
            metadata={
                "category": "organization",
                "importance": "medium"
            }
        ),
        
        ***REMOVED*** Cursor 使用习惯
        Memory(
            id="user_profile_cursor_001",
            content="用户使用 Cursor IDE 进行开发，偏好中文简体交流",
            timestamp=datetime.now(),
            memory_type=MemoryType.USER_PROFILE,
            layer=MemoryLayer.LTM,
            keywords=["Cursor", "IDE", "开发工具"],
            tags=["tool", "cursor", "ide"],
            metadata={
                "category": "tool_usage",
                "importance": "high"
            }
        ),
        
        ***REMOVED*** 技术栈记忆
        Memory(
            id="user_profile_tech_001",
            content="用户使用 Neo4j、Redis、PostgreSQL、Qdrant 等技术栈进行 AI 创作项目开发",
            timestamp=datetime.now(),
            memory_type=MemoryType.USER_PROFILE,
            layer=MemoryLayer.LTM,
            keywords=["技术栈", "Neo4j", "Redis", "数据库"],
            tags=["tech_stack", "database"],
            metadata={
                "category": "technology",
                "importance": "high"
            }
        ),
    ]
    
    ***REMOVED*** 存储所有记忆
    for memory in memories:
        success = create_memory(memory)
        if success:
            print(f"✓ 存储记忆: {memory.id}")
        else:
            print(f"✗ 存储失败: {memory.id}")
    
    return memories


def retrieve_user_profile():
    """检索用户画像"""
    print("\n" + "=" * 60)
    print("检索用户画像")
    print("=" * 60)
    
    ***REMOVED*** 1. 按类型检索（USER_PROFILE）
    print("\n【按类型检索 - USER_PROFILE】")
    profile_memories = search_memories_by_type(MemoryType.USER_PROFILE, limit=20)
    print(f"找到 {len(profile_memories)} 条用户画像记忆：")
    for m in profile_memories:
        print(f"  - {m.id}: {m.content[:60]}...")
        if m.metadata.get("category"):
            print(f"    分类: {m.metadata['category']}")
    
    ***REMOVED*** 2. 文本搜索（Cursor 相关）
    print("\n【文本搜索 - 'Cursor'】")
    cursor_memories = search_memories_by_text("Cursor", limit=10)
    print(f"找到 {len(cursor_memories)} 条与 Cursor 相关的记忆：")
    for m in cursor_memories:
        print(f"  - {m.content}")
    
    ***REMOVED*** 3. 文本搜索（偏好相关）
    print("\n【文本搜索 - '偏好'】")
    preference_memories = search_memories_by_text("偏好", limit=10)
    print(f"找到 {len(preference_memories)} 条偏好相关记忆：")
    for m in preference_memories:
        print(f"  - {m.content}")
    
    return profile_memories


def generate_user_profile_summary(memories):
    """生成用户画像摘要"""
    print("\n" + "=" * 60)
    print("用户画像摘要")
    print("=" * 60)
    
    categories = {}
    for m in memories:
        category = m.metadata.get("category", "other")
        if category not in categories:
            categories[category] = []
        categories[category].append(m)
    
    for category, mems in categories.items():
        print(f"\n【{category.upper()}】")
        for m in mems:
            print(f"  • {m.content}")


if __name__ == "__main__":
    print("=" * 60)
    print("用户画像记忆系统示例")
    print("=" * 60)
    
    ***REMOVED*** 存储用户画像
    memories = store_user_profile_memories()
    
    ***REMOVED*** 检索用户画像
    retrieved = retrieve_user_profile()
    
    ***REMOVED*** 生成摘要
    generate_user_profile_summary(retrieved)
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
    print("\n提示：这些记忆已存储在 Neo4j 中，下次可以通过 recall 操作检索。")

