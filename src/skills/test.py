"""
Skills 系统测试（创作相关）

验证 SkillManager 与渐进式披露；当前无内置 Skill 示例时仅测试管理器 API。
"""
import sys
from pathlib import Path

if __name__ == "__main__" and not __package__:
    src_dir = Path(__file__).parent.parent
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

from skills import default_manager, Skill


def test_manager_api():
    """测试管理器 API"""
    print("测试 Skill Manager API...")

    skills = default_manager.list_skills()
    print(f"  当前 Skills: {skills}")

    all_metadata = default_manager.get_all_metadata()
    assert len(all_metadata) == len(skills), "metadata 数量应与 list_skills 一致"
    print(f"  ✓ list_skills / get_all_metadata 一致")

    not_found = default_manager.get_skill("not_exist")
    assert not_found is None
    print("  ✓ 不存在的 Skill 返回 None")

    selected = default_manager.select_skills("创作相关查询", max_skills=3)
    assert isinstance(selected, list)
    print(f"  ✓ select_skills 返回列表，长度 {len(selected)}")

    context = default_manager.get_context_for_query("创作", level=2)
    assert isinstance(context, str)
    print(f"  ✓ get_context_for_query 返回字符串，长度 {len(context)}")


def test_skill_structure_when_present():
    """当存在至少一个 Skill 时，测试其结构"""
    skills = default_manager.list_skills()
    if not skills:
        print("\n跳过 Skill 结构测试（当前无 Skill 目录，可添加创作相关 Skill 到 skills/）")
        return

    name = skills[0]
    skill = default_manager.get_skill(name)
    assert skill is not None
    assert skill.name == name
    assert hasattr(skill, "metadata")
    assert hasattr(skill, "get_context")
    assert hasattr(skill, "list_resources")
    print(f"\n  ✓ Skill 结构正常: {name}")


def test_chapter_creation_sop_skill():
    """测试内置 Skill「章节创作规范」：存在、可选中、上下文含关键内容"""
    skills = default_manager.list_skills()
    assert "章节创作规范" in skills, "应存在 Skill「章节创作规范」"
    print("  ✓ 章节创作规范 已加载")

    skill = default_manager.get_skill("章节创作规范")
    assert skill is not None
    assert skill.metadata.name == "章节创作规范"
    assert "字数" in skill.metadata.triggers or "节奏" in skill.metadata.triggers
    assert "章节" in skill.metadata.tags or "创作规范" in skill.metadata.tags
    print("  ✓ 元数据与触发词/标签正确")

    selected = default_manager.select_skills("写本章，注意字数与节奏", max_skills=3)
    assert len(selected) >= 1, "按「写本章 字数 节奏」应至少选中 1 个 Skill"
    assert any(s.name == "章节创作规范" for s in selected), "应选中「章节创作规范」"
    print("  ✓ 按查询选中「章节创作规范」")

    context = skill.get_context(level=2)
    assert len(context) > 200, "level=2 上下文应包含主体内容"
    for keyword in ("2048", "节奏", "对话"):
        assert keyword in context, f"上下文应包含关键词「{keyword}」"
    print("  ✓ level=2 上下文含字数/节奏/对话等关键内容")


if __name__ == "__main__":
    print("=" * 60)
    print("Skills 系统测试（创作相关）")
    print("=" * 60)

    try:
        test_manager_api()
        test_skill_structure_when_present()
        test_chapter_creation_sop_skill()

        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
