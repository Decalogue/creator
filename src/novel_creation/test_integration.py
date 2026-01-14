***REMOVED***!/usr/bin/env python3
"""
集成测试：验证创作上下文系统与 Novel Creator 的集成
"""
import sys
from pathlib import Path

***REMOVED*** 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from novel_creation import ReactNovelCreator, NovelChapter


def test_basic_creation():
    """测试基础创作功能（不使用创作上下文系统）"""
    print("=" * 60)
    print("测试1: 基础创作功能（不使用创作上下文系统）")
    print("=" * 60)
    
    creator = ReactNovelCreator(
        novel_title="测试小说_基础模式",
        enable_creative_context=False
    )
    
    print(f"✅ Novel Creator 初始化成功")
    print(f"   创作上下文系统: {'启用' if creator.enable_creative_context else '禁用'}")
    print()


def test_creative_context_integration():
    """测试创作上下文系统集成"""
    print("=" * 60)
    print("测试2: 创作上下文系统集成")
    print("=" * 60)
    
    creator = ReactNovelCreator(
        novel_title="测试小说_创作上下文",
        enable_creative_context=True
    )
    
    if creator.enable_creative_context:
        print("✅ 创作上下文系统已启用")
        print(f"   语义网格: {'已初始化' if creator.semantic_mesh else '未初始化'}")
        print(f"   上下文路由器: {'已初始化' if creator.context_router else '未初始化'}")
        print(f"   记忆总线: {'已初始化' if creator.memory_bus else '未初始化'}")
        
        ***REMOVED*** 测试语义网格
        print()
        print("【测试语义网格】")
        test_entity = creator.semantic_mesh.entities.get("test_entity")
        if test_entity is None:
            from creative_context import Entity, EntityType
            test_entity = Entity(
                id="test_entity",
                type=EntityType.CHARACTER,
                name="测试角色",
                content="这是一个测试角色"
            )
            creator.semantic_mesh.add_entity(test_entity)
            print("   ✅ 实体添加成功")
        
        ***REMOVED*** 测试记忆总线
        print()
        print("【测试记忆总线】")
        from creative_context import Topic
        notified = creator.memory_bus.publish(
            Topic.WORLDVIEW,
            "test_entity",
            {"content": "测试世界观描述"}
        )
        print(f"   ✅ 消息发布成功，通知了 {notified} 个 Agent")
        
    else:
        print("⚠️  创作上下文系统未启用（可能不可用）")
    
    print()


def test_chapter_creation_with_context():
    """测试带创作上下文的章节创作"""
    print("=" * 60)
    print("测试3: 带创作上下文的章节创作")
    print("=" * 60)
    
    creator = ReactNovelCreator(
        novel_title="测试小说_章节创作",
        enable_creative_context=True
    )
    
    if not creator.enable_creative_context:
        print("⚠️  创作上下文系统不可用，跳过测试")
        return
    
    ***REMOVED*** 创建测试章节
    test_chapter = NovelChapter(
        chapter_number=1,
        title="第一章：起点",
        content='''主角"张三"站在古老的城堡前，手中握着一个神秘的"吊坠"。
天空中飘着蓝色的云，这是一个充满魔法的世界。''',
        summary="主角发现神秘吊坠"
    )
    
    ***REMOVED*** 处理章节的创作上下文
    creator._process_chapter_with_creative_context(test_chapter)
    
    print("✅ 章节创作上下文处理完成")
    print(f"   语义网格实体数: {len(creator.semantic_mesh.entities)}")
    print(f"   语义网格关系数: {len(creator.semantic_mesh.relations)}")
    
    ***REMOVED*** 检查提取的实体
    print()
    print("【提取的实体】")
    for entity_id, entity in creator.semantic_mesh.entities.items():
        print(f"   - {entity.name} ({entity.type.value})")
    
    ***REMOVED*** 检查关系
    print()
    print("【创建的关系】")
    for relation in creator.semantic_mesh.relations:
        source = creator.semantic_mesh.entities.get(relation.source_id)
        target = creator.semantic_mesh.entities.get(relation.target_id)
        if source and target:
            print(f"   - {source.name} --{relation.relation_type.value}--> {target.name}")
    
    print()


def test_related_memories():
    """测试关联记忆查询"""
    print("=" * 60)
    print("测试4: 关联记忆查询")
    print("=" * 60)
    
    creator = ReactNovelCreator(
        novel_title="测试小说_关联记忆",
        enable_creative_context=True
    )
    
    if not creator.enable_creative_context:
        print("⚠️  创作上下文系统不可用，跳过测试")
        return
    
    ***REMOVED*** 创建测试章节并处理
    test_chapter = NovelChapter(
        chapter_number=1,
        title="第一章",
        content='主角"李四"找到了"神秘吊坠"。',
        summary="发现吊坠"
    )
    creator._process_chapter_with_creative_context(test_chapter)
    
    ***REMOVED*** 查找相关记忆
    chapter_entity_id = "chapter_001"
    related = creator.get_related_memories(chapter_entity_id, max_results=5)
    
    print(f"✅ 查询关联记忆成功")
    print(f"   找到 {len(related)} 个相关实体")
    for entity in related:
        print(f"   - {entity.name} ({entity.type.value})")
    
    print()


def test_context_routing():
    """测试上下文路由"""
    print("=" * 60)
    print("测试5: 上下文路由")
    print("=" * 60)
    
    creator = ReactNovelCreator(
        novel_title="测试小说_上下文路由",
        enable_creative_context=True
    )
    
    if not creator.enable_creative_context:
        print("⚠️  创作上下文系统不可用，跳过测试")
        return
    
    ***REMOVED*** 创建测试章节并处理
    test_chapter = NovelChapter(
        chapter_number=1,
        title="第一章",
        content='主角"王五"站在"天空"下。',
        summary="天空场景"
    )
    creator._process_chapter_with_creative_context(test_chapter)
    
    ***REMOVED*** 测试上下文路由
    from creative_context import UserBehavior
    behavior = UserBehavior(
        cursor_position=50,
        input_rate=30.0,
        pause_duration=0.6
    )
    creator.context_router.update_user_behavior(behavior)
    
    ***REMOVED*** 获取上下文
    context = creator.get_context_for_agent("chapter_001", agent_type="consistency_checker")
    
    print("✅ 上下文路由测试成功")
    print(f"   上下文包含: {len(context.get('related_entities', []))} 个相关实体")
    
    print()


if __name__ == "__main__":
    print("创作上下文系统集成测试")
    print()
    
    test_basic_creation()
    test_creative_context_integration()
    test_chapter_creation_with_context()
    test_related_memories()
    test_context_routing()
    
    print("=" * 60)
    print("✅ 所有集成测试完成！")
    print("=" * 60)
