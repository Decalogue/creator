"""
Skills 系统使用示例
演示渐进式披露机制和 Skill 管理
"""
import sys
from pathlib import Path

***REMOVED*** 添加项目根目录到 Python 路径
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
    print(f"\n可用 Skills: {skills}")
    
    all_metadata = default_manager.get_all_metadata()
    print(f"\n共 {len(all_metadata)} 个 Skills:\n")
    
    for metadata in all_metadata:
        print(f"- {metadata.name}")
        print(f"  描述: {metadata.description}")
        print(f"  标签: {', '.join(metadata.tags) if metadata.tags else '无'}")
        print(f"  触发词: {', '.join(metadata.triggers) if metadata.triggers else '无'}")
        print()


def example_2_progressive_disclosure():
    """示例 2：渐进式披露机制"""
    print_section("示例 2：渐进式披露机制")
    
    calculator = default_manager.get_skill('calculator')
    if not calculator:
        print("Calculator skill not found")
        return
    
    ***REMOVED*** 第一层：元数据（始终加载，~100 tokens）
    print("\n【第一层】元数据（始终加载）")
    print("-" * 60)
    context_level1 = calculator.get_context(level=1)
    tokens_level1 = calculator.estimate_tokens(level=1)
    print(context_level1)
    print(f"\n估算 Token 数: {tokens_level1}")
    
    ***REMOVED*** 第二层：主体内容（触发时加载，<5k tokens）
    print("\n【第二层】主体内容（触发时加载）")
    print("-" * 60)
    context_level2 = calculator.get_context(level=2)
    tokens_level2 = calculator.estimate_tokens(level=2)
    preview = context_level2[:500] + "..." if len(context_level2) > 500 else context_level2
    print(preview)
    print(f"\n估算 Token 数: {tokens_level2}")
    
    ***REMOVED*** 第三层：所有资源（按需加载，无限制）
    print("\n【第三层】所有资源（按需加载）")
    print("-" * 60)
    resources = calculator.list_resources()
    print(f"可用资源: {resources}")
    if resources:
        print(f"\n加载资源 '{resources[0]}':")
        resource_content = calculator.load_resource(resources[0])
        preview = resource_content[:300] + "..." if len(resource_content) > 300 else resource_content
        print(preview)
    
    context_level3 = calculator.get_context(level=3)
    tokens_level3 = calculator.estimate_tokens(level=3)
    print(f"\n估算 Token 数: {tokens_level3}")


def example_3_skill_selection():
    """示例 3：根据查询选择 Skills"""
    print_section("示例 3：根据查询选择 Skills")
    
    queries = [
        "帮我计算 10 * 5 + 20",
        "查询北京的天气",
        "今天温度多少",
        "算一下 2 的 8 次方",
    ]
    
    for query in queries:
        print(f"\n查询: {query}")
        selected_skills = default_manager.select_skills(query)
        print(f"选择的 Skills: {[s.name for s in selected_skills]}")
        
        if selected_skills:
            context = default_manager.get_context_for_query(query, level=2)
            print(f"上下文长度: {len(context)} 字符")
            print(f"上下文预览: {context[:200]}...")


def example_4_with_llm():
    """示例 4：与 LLM 集成"""
    print_section("示例 4：与 LLM 集成（代码示例）")
    
    example_code = '''from skills import default_manager
from llm.chat import ark_deepseek_v3_2

def chat_with_skills(user_query: str):
    ***REMOVED*** 1. 根据查询选择相关 Skills
    selected_skills = default_manager.select_skills(user_query)
    
    ***REMOVED*** 2. 获取 Skills 上下文（第二层：主体内容）
    skills_context = default_manager.get_context_for_query(user_query, level=2)
    
    ***REMOVED*** 3. 构建消息
    messages = [
        {
            "role": "system",
            "content": f"""你是一个 AI 助手，可以使用以下 Skills：

{skills_context}

请根据用户需求，使用相应的 Skills 来完成任务。"""
        },
        {
            "role": "user",
            "content": user_query
        }
    ]
    
    ***REMOVED*** 4. 调用 LLM
    _, response = ark_deepseek_v3_2(messages)
    return response

***REMOVED*** 使用示例
result = chat_with_skills("帮我计算 25 * 8 + 100")
print(result)
'''
    print(example_code)


if __name__ == "__main__":
    print_section("Skills 系统使用示例", 60)
    
    example_1_list_skills()
    example_2_progressive_disclosure()
    example_3_skill_selection()
    example_4_with_llm()
    
    print_section("所有示例运行完成！", 60)
