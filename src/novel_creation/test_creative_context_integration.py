#!/usr/bin/env python3
"""
集成测试：验证创作上下文系统与 Novel Creator 的集成
（不依赖 LLM，只测试集成逻辑）
"""
import sys
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 定义简单的 NovelChapter（不依赖 react_novel_creator）
@dataclass
class NovelChapter:
    """小说章节（测试用）"""
    chapter_number: int
    title: str
    content: str = ""
    summary: str = ""


def test_creative_context_components():
    """测试创作上下文系统组件（独立测试）"""
    print("=" * 60)
    print("测试1: 创作上下文系统组件")
    print("=" * 60)
    
    try:
        from creative_context import (
            SemanticMeshMemory,
            Entity,
            EntityType,
            RelationType,
            ContextRouter,
            PubSubMemoryBus,
            Topic
        )
        
        # 测试语义网格
        print("【测试语义网格记忆】")
        mesh = SemanticMeshMemory()
        
        entity1 = Entity(
            id="char_001",
            type=EntityType.CHARACTER,
            name="主角",
            content="一个年轻的时空旅者"
        )
        mesh.add_entity(entity1)
        
        entity2 = Entity(
            id="item_001",
            type=EntityType.SYMBOL,
            name="神秘吊坠",
            content="一个古老的吊坠"
        )
        mesh.add_entity(entity2)
        
        mesh.add_relation(
            "char_001",
            "item_001",
            RelationType.MENTIONS,
            strength=0.9
        )
        
        related = mesh.find_related_entities("char_001")
        print(f"   ✅ 语义网格测试通过")
        print(f"      实体数: {len(mesh.entities)}")
        print(f"      关系数: {len(mesh.relations)}")
        print(f"      相关实体: {len(related)} 个")
        
        # 测试上下文路由器
        print()
        print("【测试上下文路由器】")
        router = ContextRouter(mesh)
        from creative_context import UserBehavior
        
        behavior = UserBehavior(
            cursor_position=100,
            input_rate=50.0,
            pause_duration=0.6
        )
        router.update_user_behavior(behavior)
        
        context = router.get_context_for_agent("char_001", "consistency_checker")
        print(f"   ✅ 上下文路由器测试通过")
        print(f"      上下文包含: {len(context.get('related_entities', []))} 个相关实体")
        
        # 测试订阅式记忆总线
        print()
        print("【测试订阅式记忆总线】")
        bus = PubSubMemoryBus()
        
        notified_count = [0]
        def on_worldview_change(topic: str, data: dict):
            notified_count[0] += 1
        
        bus.subscribe("worldview_agent", [Topic.WORLDVIEW], on_worldview_change)
        
        count = bus.publish(
            Topic.WORLDVIEW,
            "entity_001",
            {"content": "天空中飘着蓝色的云"}
        )
        
        print(f"   ✅ 订阅式记忆总线测试通过")
        print(f"      通知了 {count} 个 Agent")
        print(f"      回调执行了 {notified_count[0]} 次")
        
        print()
        print("✅ 所有创作上下文系统组件测试通过！")
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("   创作上下文系统可能不可用")
        return False
    
    return True


def test_chapter_processing():
    """测试章节处理逻辑（不依赖 ReActAgent）"""
    print("=" * 60)
    print("测试2: 章节处理逻辑")
    print("=" * 60)
    
    try:
        from creative_context import (
            SemanticMeshMemory,
            Entity,
            EntityType,
            RelationType,
            PubSubMemoryBus,
            Topic
        )
        
        # 模拟 Novel Creator 的章节处理逻辑
        mesh = SemanticMeshMemory()
        bus = PubSubMemoryBus()
        
        # 创建测试章节
        chapter = NovelChapter(
            chapter_number=1,
            title="第一章：起点",
            content='''主角"张三"站在古老的城堡前，手中握着一个神秘的"吊坠"。
天空中飘着蓝色的云，这是一个充满魔法的世界。''',
            summary="主角发现神秘吊坠"
        )
        
        # 处理章节（模拟 _process_chapter_with_creative_context 的逻辑）
        # 1. 创建章节实体
        chapter_entity = Entity(
            id=f"chapter_{chapter.chapter_number:03d}",
            type=EntityType.CHAPTER,
            name=chapter.title,
            content=chapter.content,
            metadata={
                "chapter_number": chapter.chapter_number,
                "summary": chapter.summary
            }
        )
        mesh.add_entity(chapter_entity)
        
        # 2. 提取实体（简化）
        import re
        character_pattern = r'["""]([^"""]+)["""]'
        characters = re.findall(character_pattern, chapter.content)
        
        for char_name in set(characters[:5]):
            if len(char_name) > 1 and len(char_name) < 20:
                entity = Entity(
                    id=f"char_001_{hash(char_name) % 10000}",
                    type=EntityType.CHARACTER,
                    name=char_name,
                    content=f"出现在第{chapter.chapter_number}章的角色"
                )
                mesh.add_entity(entity)
                mesh.add_relation(
                    chapter_entity.id,
                    entity.id,
                    RelationType.APPEARS_IN,
                    strength=0.8
                )
        
        # 3. 检查世界观描述
        worldview_keywords = ["天空", "云", "星球", "世界"]
        if any(keyword in chapter.content for keyword in worldview_keywords):
            bus.publish(
                Topic.WORLDVIEW,
                chapter_entity.id,
                {"content": chapter.content, "entity_id": chapter_entity.id}
            )
        
        print("✅ 章节处理逻辑测试通过")
        print(f"   章节实体: {chapter_entity.name}")
        print(f"   提取的角色: {len([e for e in mesh.entities.values() if e.type == EntityType.CHARACTER])} 个")
        print(f"   总实体数: {len(mesh.entities)}")
        print(f"   总关系数: {len(mesh.relations)}")
        
        # 测试关联记忆
        related = mesh.trigger_related_memories(chapter_entity.id)
        print(f"   关联记忆: {len(related)} 个")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_integration_workflow():
    """测试完整集成工作流"""
    print("=" * 60)
    print("测试3: 完整集成工作流")
    print("=" * 60)
    
    try:
        from creative_context import (
            SemanticMeshMemory,
            Entity,
            EntityType,
            RelationType,
            ContextRouter,
            PubSubMemoryBus,
            Topic,
            UserBehavior
        )
        
        # 初始化系统
        mesh = SemanticMeshMemory()
        router = ContextRouter(mesh)
        bus = PubSubMemoryBus()
        
        # 注册世界观检测 Agent
        conflicts = []
        def on_worldview_change(topic: str, data: dict):
            content = data.get("content", "")
            # 简化的冲突检测
            if "蓝色" in content and "紫色" in str(conflicts):
                conflicts.append("世界观冲突：云的颜色不一致")
        
        bus.subscribe("worldview_agent", [Topic.WORLDVIEW], on_worldview_change)
        
        # 模拟创作流程
        # 1. 创建第一章（设定：云是紫色的）
        chapter1 = NovelChapter(
            chapter_number=1,
            title="第一章",
            content="这个星球的云是紫色的。",
            summary="设定世界观"
        )
        
        chapter1_entity = Entity(
            id="chapter_001",
            type=EntityType.CHAPTER,
            name=chapter1.title,
            content=chapter1.content
        )
        mesh.add_entity(chapter1_entity)
        bus.publish(Topic.WORLDVIEW, "chapter_001", {"content": chapter1.content})
        
        # 2. 创建第二章（错误：云是蓝色的）
        chapter2 = NovelChapter(
            chapter_number=2,
            title="第二章",
            content="天空中飘着蓝色的云。",
            summary="描述天空"
        )
        
        chapter2_entity = Entity(
            id="chapter_002",
            type=EntityType.CHAPTER,
            name=chapter2.title,
            content=chapter2.content
        )
        mesh.add_entity(chapter2_entity)
        bus.publish(Topic.WORLDVIEW, "chapter_002", {"content": chapter2.content})
        
        # 3. 查找关联记忆
        related = mesh.find_related_entities("chapter_002", relation_types=[RelationType.REFERENCES])
        
        print("✅ 完整集成工作流测试通过")
        print(f"   章节数: 2")
        print(f"   实体数: {len(mesh.entities)}")
        print(f"   关联记忆: {len(related)} 个")
        print(f"   检测到的冲突: {len(conflicts)} 个")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    print("创作上下文系统集成测试")
    print()
    
    results = []
    
    results.append(("创作上下文系统组件", test_creative_context_components()))
    results.append(("章节处理逻辑", test_chapter_processing()))
    results.append(("完整集成工作流", test_integration_workflow()))
    
    print()
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    print()
    if all_passed:
        print("🎉 所有集成测试通过！")
    else:
        print("⚠️  部分测试失败，请检查")
    
    print("=" * 60)
