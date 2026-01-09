"""
换壳理论使用示例

展示如何使用换壳编排器和调味管理器实现故事换壳。
"""

from typing import Dict, Any, List
from unimem.character import CharacterGrowthArcManager, GrowthArc
from unimem.storage.hierarchical.hierarchical_storage import (
    HierarchicalStorage,
    ContentLevel,
    MemoryType
)
from unimem.memory_types import Memory
from workflow import ShellSwappingOrchestrator, SeasoningManager, SeasoningType


def example_create_growth_arc():
    """示例：创建人物成长线"""
    print("=" * 50)
    print("示例1：创建人物成长线")
    print("=" * 50)
    
    ***REMOVED*** 初始化成长线管理器
    manager = CharacterGrowthArcManager()
    
    ***REMOVED*** 创建成长线（三句话骨架）
    growth_arc = manager.create_growth_arc(
        character_id="char_001",
        character_name="张三",
        early_state="底层小混混，生活困顿",
        mid_conflict="被卷进帮派冲突，被迫做出选择",
        late_outcome="黑化成狠角，掌控一方势力"
    )
    
    print(f"人物：{growth_arc.character_name}")
    print(f"成长线：\n{growth_arc.to_three_sentences()}")
    print()


def example_store_core_and_shell():
    """示例：存储核心记忆和外壳记忆"""
    print("=" * 50)
    print("示例2：存储核心记忆和外壳记忆")
    print("=" * 50)
    
    ***REMOVED*** 初始化分层存储
    hierarchical_storage = HierarchicalStorage()
    
    ***REMOVED*** 创建核心记忆（人物成长线）
    core_memory = Memory(
        id="core_001",
        content="人物成长线：张三从底层小混混成长为一方势力",
        memory_type="experience",
        keywords=["成长线", "人物"],
        metadata={"character_id": "char_001", "is_core": True}
    )
    
    ***REMOVED*** 存储核心记忆
    hierarchical_storage.store_core(core_memory, ContentLevel.WORK)
    print("✓ 存储核心记忆（人物成长线）")
    
    ***REMOVED*** 创建外壳记忆（都市题材背景）
    shell_memory = Memory(
        id="shell_urban_001",
        content="现代都市背景，强调现实生活、职场竞争、都市情感",
        memory_type="world",
        keywords=["都市", "背景"],
        metadata={"shell_type": "urban"}
    )
    
    ***REMOVED*** 存储外壳记忆
    hierarchical_storage.store_shell(shell_memory, ContentLevel.WORK, "urban")
    print("✓ 存储外壳记忆（都市题材）")
    
    ***REMOVED*** 获取统计信息
    stats = hierarchical_storage.get_statistics()
    print(f"\n统计信息：")
    print(f"  - 核心记忆数：{stats.get('core_memories', 0)}")
    print(f"  - 外壳记忆数：{stats.get('shell_memories', 0)}")
    print(f"  - 外壳类型分布：{stats.get('shell_type_distribution', {})}")
    print()


def example_retrieve_with_shell():
    """示例：检索核心记忆和外壳记忆"""
    print("=" * 50)
    print("示例3：检索核心记忆和外壳记忆")
    print("=" * 50)
    
    ***REMOVED*** 初始化分层存储
    hierarchical_storage = HierarchicalStorage()
    
    ***REMOVED*** 存储一些记忆（示例）
    core_memory = Memory(
        id="core_001",
        content="人物成长线：张三从底层小混混成长为一方势力",
        memory_type="experience",
        keywords=["成长线", "人物"],
        metadata={"is_core": True}
    )
    hierarchical_storage.store_core(core_memory, ContentLevel.WORK)
    
    shell_memory = Memory(
        id="shell_urban_001",
        content="现代都市背景，强调现实生活、职场竞争、都市情感",
        memory_type="world",
        keywords=["都市", "背景"],
        metadata={"shell_type": "urban"}
    )
    hierarchical_storage.store_shell(shell_memory, ContentLevel.WORK, "urban")
    
    ***REMOVED*** 检索：核心记忆 + 外壳记忆融合
    memories = hierarchical_storage.retrieve_with_shell(
        query="人物成长",
        level=ContentLevel.WORK,
        shell_type="urban",
        top_k=10
    )
    
    print(f"检索到 {len(memories)} 条记忆：")
    for memory in memories:
        memory_type = hierarchical_storage.get_memory_type(memory.id)
        shell_type = hierarchical_storage.get_shell_type(memory.id)
        print(f"  - {memory.id}: {memory_type.value if memory_type else 'unknown'}")
        if shell_type:
            print(f"    外壳类型：{shell_type}")
    print()


def example_swap_shell():
    """示例：换壳工作流"""
    print("=" * 50)
    print("示例4：换壳工作流")
    print("=" * 50)
    
    ***REMOVED*** 初始化组件
    growth_arc_manager = CharacterGrowthArcManager()
    hierarchical_storage = HierarchicalStorage()
    
    ***REMOVED*** 创建成长线
    growth_arc = growth_arc_manager.create_growth_arc(
        character_id="char_001",
        character_name="张三",
        early_state="底层小混混，生活困顿",
        mid_conflict="被卷进帮派冲突，被迫做出选择",
        late_outcome="黑化成狠角，掌控一方势力"
    )
    
    ***REMOVED*** 初始化换壳编排器
    orchestrator = ShellSwappingOrchestrator(
        growth_arc_manager=growth_arc_manager,
        hierarchical_storage=hierarchical_storage
    )
    
    ***REMOVED*** 源故事（都市题材）
    source_story = {
        "id": "story_001",
        "conflicts": ["商业竞争", "情感纠葛"],
        "relationships": {"张三": "李四"},
        "emotional_progression": ["愤怒", "悲伤", "成长"]
    }
    
    ***REMOVED*** 执行换壳（从都市换到玄幻）
    shelled_story = orchestrator.swap_shell(
        source_story=source_story,
        target_shell="fantasy",
        character_ids=["char_001"]
    )
    
    print("换壳后的故事：")
    print(shelled_story.content)
    print()


def example_add_seasonings():
    """示例：添加调味"""
    print("=" * 50)
    print("示例5：添加调味")
    print("=" * 50)
    
    ***REMOVED*** 初始化调味管理器
    seasoning_manager = SeasoningManager()
    
    ***REMOVED*** 创建一个简单的故事对象
    class SimpleStory:
        def __init__(self, content):
            self.content = content
    
    story = SimpleStory("这是一个关于人物成长的故事。")
    
    ***REMOVED*** 添加调味
    seasoned_story = seasoning_manager.add_seasonings(
        story=story,
        seasonings=[
            SeasoningType.LOVE,
            SeasoningType.GRUDGE,
            SeasoningType.MONEY,
            SeasoningType.POWER
        ],
        shell_type="urban",
        intensity=1.0
    )
    
    print("添加调味后的故事：")
    print(seasoned_story.enhanced_content)
    print()


def example_full_workflow():
    """示例：完整工作流"""
    print("=" * 50)
    print("示例6：完整工作流（创建成长线 → 换壳 → 添加调味）")
    print("=" * 50)
    
    ***REMOVED*** 1. 初始化组件
    growth_arc_manager = CharacterGrowthArcManager()
    hierarchical_storage = HierarchicalStorage()
    orchestrator = ShellSwappingOrchestrator(
        growth_arc_manager=growth_arc_manager,
        hierarchical_storage=hierarchical_storage
    )
    seasoning_manager = SeasoningManager()
    
    ***REMOVED*** 2. 创建成长线
    growth_arc = growth_arc_manager.create_growth_arc(
        character_id="char_001",
        character_name="张三",
        early_state="底层小混混，生活困顿",
        mid_conflict="被卷进帮派冲突，被迫做出选择",
        late_outcome="黑化成狠角，掌控一方势力"
    )
    print("✓ 创建成长线")
    
    ***REMOVED*** 3. 存储核心记忆
    core_memory = growth_arc.to_memory()
    hierarchical_storage.store_core(core_memory, ContentLevel.WORK)
    print("✓ 存储核心记忆")
    
    ***REMOVED*** 4. 换壳
    source_story = {
        "id": "story_001",
        "conflicts": ["商业竞争", "情感纠葛"],
        "relationships": {"张三": "李四"},
        "emotional_progression": ["愤怒", "悲伤", "成长"]
    }
    shelled_story = orchestrator.swap_shell(
        source_story=source_story,
        target_shell="fantasy",
        character_ids=["char_001"]
    )
    print("✓ 换壳完成")
    
    ***REMOVED*** 5. 添加调味
    seasoned_story = seasoning_manager.add_seasonings(
        story=shelled_story,
        seasonings=SeasoningManager.DEFAULT_SEASONINGS,
        shell_type="fantasy",
        intensity=1.0
    )
    print("✓ 添加调味完成")
    
    print("\n最终故事：")
    print(seasoned_story.enhanced_content)
    print()


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("换壳理论使用示例")
    print("=" * 50 + "\n")
    
    ***REMOVED*** 运行示例
    example_create_growth_arc()
    example_store_core_and_shell()
    example_retrieve_with_shell()
    example_swap_shell()
    example_add_seasonings()
    example_full_workflow()
    
    print("=" * 50)
    print("所有示例运行完成！")
    print("=" * 50)

