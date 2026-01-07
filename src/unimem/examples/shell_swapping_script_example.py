"""
短剧换壳示例

展示如何使用换壳编排器和调味管理器实现短剧换壳。
"""

from typing import Dict, Any
from unimem.character import CharacterGrowthArcManager
from unimem.storage.hierarchical.hierarchical_storage import HierarchicalStorage, ContentLevel
from unimem.types import Memory
from workflow import ShellSwappingOrchestrator, SeasoningManager, SeasoningType


def example_script_swap_shell():
    """示例：短剧换壳工作流"""
    print("=" * 50)
    print("短剧换壳示例：都市短剧 → 玄幻短剧")
    print("=" * 50)
    
    ***REMOVED*** 1. 初始化组件
    growth_arc_manager = CharacterGrowthArcManager()
    hierarchical_storage = HierarchicalStorage()
    orchestrator = ShellSwappingOrchestrator(
        growth_arc_manager=growth_arc_manager,
        hierarchical_storage=hierarchical_storage
    )
    seasoning_manager = SeasoningManager()
    
    ***REMOVED*** 2. 创建短剧人物成长线（更紧凑）
    growth_arc = growth_arc_manager.create_growth_arc(
        character_id="char_001",
        character_name="张三",
        early_state="底层小人物，生活困顿（第1-5集）",
        mid_conflict="遇到机遇/冲突，被迫做出选择（第6-40集）",
        late_outcome="逆袭成功/黑化/成长（第41-50集）",
        metadata={
            "script_format": "short_drama",
            "growth_pace": "fast",
            "episodes_per_stage": {
                "early": "1-5集",
                "mid": "6-40集",
                "late": "41-50集"
            }
        }
    )
    print("✓ 创建短剧人物成长线")
    print(f"  成长线：\n{growth_arc.to_three_sentences()}\n")
    
    ***REMOVED*** 3. 存储核心记忆
    core_memory = growth_arc.to_memory()
    hierarchical_storage.store(core_memory, ContentLevel.WORK)
    core_memory.metadata["is_core"] = True
    print("✓ 存储核心记忆\n")
    
    ***REMOVED*** 4. 源故事（都市短剧）
    source_story = {
        "id": "script_001",
        "type": "script",  ***REMOVED*** 标记为短剧
        "title": "都市逆袭记",
        "episode_count": 50,
        "episode_length": "1-3分钟",
        "conflicts": [
            "商业竞争（每3-5集一个冲突）",
            "情感纠葛（每2-3集一个冲突）",
            "身份危机（每5-10集一个冲突）"
        ],
        "relationships": {"张三": "李四"},
        "emotional_progression": ["愤怒", "悲伤", "成长"],
        "pace": "fast",  ***REMOVED*** 快速节奏
        "metadata": {
            "genre": "urban",
            "target_audience": "都市白领"
        }
    }
    print("✓ 源故事（都市短剧）")
    print(f"  标题：{source_story['title']}")
    print(f"  集数：{source_story['episode_count']}集")
    print(f"  题材：{source_story['metadata']['genre']}\n")
    
    ***REMOVED*** 5. 换壳（从都市换到玄幻）
    shelled_story = orchestrator.swap_shell(
        source_story=source_story,
        target_shell="fantasy",
        character_ids=["char_001"]
    )
    print("✓ 换壳完成（都市 → 玄幻）")
    print(f"  新外壳：{shelled_story.shell.shell_type}")
    print(f"  背景：{shelled_story.shell.background}\n")
    
    ***REMOVED*** 6. 添加调味（短剧需要更密集的调味）
    seasoned_story = seasoning_manager.add_seasonings(
        story=shelled_story,
        seasonings=SeasoningManager.DEFAULT_SEASONINGS,
        shell_type="fantasy",
        intensity=1.2  ***REMOVED*** 提高强度
    )
    print("✓ 添加调味完成（短剧强度：1.2）")
    print(f"  调味数量：{len(seasoned_story.seasonings)}\n")
    
    ***REMOVED*** 7. 输出最终短剧故事
    print("=" * 50)
    print("最终短剧故事（玄幻题材）")
    print("=" * 50)
    print(seasoned_story.enhanced_content)
    print()
    
    ***REMOVED*** 8. 输出元数据
    print("=" * 50)
    print("短剧元数据")
    print("=" * 50)
    print(f"  类型：短剧")
    print(f"  集数：{source_story['episode_count']}集")
    print(f"  时长：{source_story['episode_length']}/集")
    print(f"  节奏：{source_story['pace']}")
    print(f"  题材：{shelled_story.shell.shell_type}")
    print(f"  调味强度：{seasoned_story.metadata.get('intensity', 1.0)}")
    print()


def example_script_seasoning_adaptation():
    """示例：短剧调味适配"""
    print("=" * 50)
    print("短剧调味适配示例")
    print("=" * 50)
    
    seasoning_manager = SeasoningManager()
    
    ***REMOVED*** 都市短剧调味
    print("都市短剧调味：")
    urban_seasonings = seasoning_manager.add_seasonings(
        story={"content": "都市短剧故事"},
        seasonings=[
            SeasoningType.LOVE,
            SeasoningType.GRUDGE,
            SeasoningType.MONEY,
            SeasoningType.POWER
        ],
        shell_type="urban",
        intensity=1.0
    )
    for seasoning in urban_seasonings.seasonings:
        print(f"  - {seasoning.seasoning_type.value}：{seasoning.description}")
    
    print("\n玄幻短剧调味：")
    fantasy_seasonings = seasoning_manager.add_seasonings(
        story={"content": "玄幻短剧故事"},
        seasonings=[
            SeasoningType.LOVE,
            SeasoningType.GRUDGE,
            SeasoningType.MONEY,
            SeasoningType.POWER
        ],
        shell_type="fantasy",
        intensity=1.2  ***REMOVED*** 提高强度
    )
    for seasoning in fantasy_seasonings.seasonings:
        print(f"  - {seasoning.seasoning_type.value}：{seasoning.description}")
    print()


def example_script_growth_arc_adaptation():
    """示例：短剧成长线适配"""
    print("=" * 50)
    print("短剧成长线适配示例")
    print("=" * 50)
    
    growth_arc_manager = CharacterGrowthArcManager()
    
    ***REMOVED*** 创建成长线
    growth_arc = growth_arc_manager.create_growth_arc(
        character_id="char_001",
        character_name="张三",
        early_state="底层小人物，生活困顿",
        mid_conflict="遇到机遇/冲突，被迫做出选择",
        late_outcome="逆袭成功/黑化/成长"
    )
    
    print("原始成长线：")
    print(growth_arc.to_three_sentences())
    print()
    
    ***REMOVED*** 适配到都市短剧
    urban_arc = growth_arc_manager.adapt_to_shell("char_001", "urban")
    print("适配到都市短剧：")
    print(urban_arc.to_three_sentences())
    print()
    
    ***REMOVED*** 适配到玄幻短剧
    fantasy_arc = growth_arc_manager.adapt_to_shell("char_001", "fantasy")
    print("适配到玄幻短剧：")
    print(fantasy_arc.to_three_sentences())
    print()


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("短剧换壳示例")
    print("=" * 50 + "\n")
    
    ***REMOVED*** 运行示例
    example_script_swap_shell()
    example_script_seasoning_adaptation()
    example_script_growth_arc_adaptation()
    
    print("=" * 50)
    print("所有示例运行完成！")
    print("=" * 50)
    print("\n结论：'换壳理论'完全适用于短剧创作！")
    print("只需要在节奏、强度、集数等方面进行适配即可。")

