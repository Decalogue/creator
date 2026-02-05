"""
Skills 系统使用示例（创作相关）

演示渐进式披露与 Skill 管理。当前无内置 Skill 时仅展示管理器用法；
添加创作相关 Skill（如短剧节奏规范、对话质量 SOP）到 skills/ 目录后即可被扫描与选择。
"""
import sys
from pathlib import Path

if __name__ == "__main__" and not __package__:
    src_dir = Path(__file__).parent.parent
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

from skills import default_manager


def print_section(title: str, width: int = 60):
    """打印章节标题"""
    print("\n" + "=" * width)
    print(title)
    print("=" * width)


def example_1_list_skills():
    """示例 1：列出所有 Skills"""
    print_section("示例 1：列出所有 Skills")

    skills = default_manager.list_skills()
    print(f"\n当前 Skills: {skills}")

    all_metadata = default_manager.get_all_metadata()
    print(f"共 {len(all_metadata)} 个 Skill\n")

    if not all_metadata:
        print("  当前无 Skill。请将创作相关 Skill（含 SKILL.md 的目录）放入 skills/ 目录，")
        print("  例如：短剧节奏规范、对话质量 SOP 等。")
        return

    for metadata in all_metadata:
        print(f"- {metadata.name}")
        print(f"  描述: {metadata.description}")
        print(f"  标签: {', '.join(metadata.tags) if metadata.tags else '无'}")
        print(f"  触发词: {', '.join(metadata.triggers) if metadata.triggers else '无'}")
        print()


def example_2_progressive_disclosure():
    """示例 2：渐进式披露（当存在 Skill 时）"""
    print_section("示例 2：渐进式披露")

    skill = default_manager.get_skill(default_manager.list_skills()[0]) if default_manager.list_skills() else None
    if not skill:
        print("\n  当前无 Skill，跳过。添加创作相关 Skill 后可查看各层级上下文。")
        return

    print(f"\n以 Skill「{skill.name}」为例：")
    for level in (1, 2, 3):
        ctx = skill.get_context(level=level)
        tokens = skill.estimate_tokens(level=level)
        preview = (ctx[:300] + "...") if len(ctx) > 300 else ctx
        print(f"\n【第 {level} 层】约 {tokens} tokens")
        print("-" * 40)
        print(preview)


def example_3_skill_selection():
    """示例 3：根据查询选择 Skills"""
    print_section("示例 3：根据查询选择 Skills")

    queries = ["创作节奏规范", "对话质量要求", "短剧大纲"]
    for query in queries:
        selected = default_manager.select_skills(query, max_skills=3)
        names = [s.name for s in selected]
        print(f"\n查询: 「{query}」 -> 选择: {names}")
        if selected:
            context = default_manager.get_context_for_query(query, level=2)
            print(f"  上下文长度: {len(context)} 字符")


def example_4_integration_code():
    """示例 4：与创作流程集成的代码示例"""
    print_section("示例 4：与创作流程集成（代码示例）")

    code = '''from skills import default_manager

# 根据创作任务选择相关 Skill（如节奏、对话质量 SOP）
query = "本章对话占比与节奏要求"
selected = default_manager.select_skills(query, max_skills=3)

# 获取 Skill 上下文，注入编排层或创作助手
context = default_manager.get_context_for_query(query, level=2)

# 将 context 加入 system 或 user 消息，供 LLM 使用
messages = [
    {"role": "system", "content": f"创作规范与 SOP：\\n{context}"},
    {"role": "user", "content": "请按上述规范写本章。"},
]
# 调用 LLM...
'''
    print(code)


if __name__ == "__main__":
    print_section("Skills 系统使用示例（创作相关）", 60)

    example_1_list_skills()
    example_2_progressive_disclosure()
    example_3_skill_selection()
    example_4_integration_code()

    print_section("所有示例运行完成！", 60)
