"""
简化直接测试脚本

绕过 Agent 工具搜索，直接使用 LLM 生成大纲和章节
用于诊断和验证核心功能
"""
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from llm.chat import client

logger = logging.getLogger(__name__)


def test_llm_direct():
    """测试 LLM 直接调用"""
    print("=" * 70)
    print("简化直接测试 - 测试 LLM 核心功能")
    print("=" * 70)
    print()
    
    ***REMOVED*** 测试 1: 简单对话
    print("测试 1: LLM 简单对话...", end=" ")
    try:
        model_name = "ep-20251209150604-gxb42"  ***REMOVED*** 使用正确的模型名称
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "你好，请用一句话回复"}],
            max_tokens=50
        )
        result = response.choices[0].message.content
        print("✅")
        print(f"   回复: {result[:50]}...")
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False
    
    print()
    
    ***REMOVED*** 测试 2: 生成简单大纲
    print("测试 2: 生成简单大纲...", end=" ")
    try:
        prompt = """请为小说创建大纲（1章）：
- 标题：测试小说
- 类型：科幻
- 主题：时间旅行

请以 JSON 格式返回，包含以下字段：
{
  "background": "背景设定",
  "characters": ["角色1", "角色2"],
  "chapter_outline": [{"chapter_number": 1, "title": "第一章", "summary": "章节摘要"}],
  "main_plot": "故事主线",
  "key_plot_points": ["情节1", "情节2"]
}"""
        
        model_name = "ep-20251209150604-gxb42"  ***REMOVED*** 使用正确的模型名称
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7
        )
        
        result = response.choices[0].message.content
        print("✅")
        
        ***REMOVED*** 尝试解析 JSON
        try:
            ***REMOVED*** 提取 JSON 部分
            if "```json" in result:
                json_start = result.find("```json") + 7
                json_end = result.find("```", json_start)
                json_str = result[json_start:json_end].strip()
            elif "{" in result:
                json_start = result.find("{")
                json_end = result.rfind("}") + 1
                json_str = result[json_start:json_end]
            else:
                json_str = result
            
            plan = json.loads(json_str)
            print(f"   背景: {plan.get('background', '')[:50]}...")
            print(f"   角色数: {len(plan.get('characters', []))}")
            print(f"   章节数: {len(plan.get('chapter_outline', []))}")
            print(f"   主线: {plan.get('main_plot', '')[:50]}...")
            
            ***REMOVED*** 保存测试结果
            test_dir = Path(__file__).parent / "outputs" / "简化测试"
            test_dir.mkdir(parents=True, exist_ok=True)
            
            plan_file = test_dir / "test_plan.json"
            plan_file.write_text(
                json.dumps(plan, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            print(f"   已保存到: {plan_file}")
            
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON 解析失败: {e}")
            print(f"   原始内容前200字: {result[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    
    ***REMOVED*** 测试 3: 生成章节内容
    print("测试 3: 生成章节内容...", end=" ")
    try:
        chapter_prompt = """请创作小说的第一章内容：

标题：第一次旅行
摘要：主角发现时间旅行的秘密，进行第一次时间旅行

要求：
- 字数：约1000字
- 风格：科幻小说
- 包含对话和描写
- 引人入胜的开头"""
        
        model_name = "ep-20251209150604-gxb42"  ***REMOVED*** 使用正确的模型名称
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": chapter_prompt}],
            max_tokens=2000,
            temperature=0.8
        )
        
        content = response.choices[0].message.content
        word_count = len(content)
        
        print("✅")
        print(f"   字数: {word_count} 字")
        print(f"   内容预览: {content[:100]}...")
        
        ***REMOVED*** 保存章节内容
        chapter_file = test_dir / "test_chapter_001.txt"
        chapter_file.write_text(
            f"第一章 第一次旅行\n\n{content}",
            encoding="utf-8"
        )
        print(f"   已保存到: {chapter_file}")
        
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    print("=" * 70)
    print("✅ 简化直接测试完成！")
    print("=" * 70)
    print()
    print(f"测试结果保存在: {test_dir}")
    print()
    print("结论：")
    print("  ✅ LLM 连接正常")
    print("  ✅ LLM 可以生成大纲")
    print("  ✅ LLM 可以生成章节内容")
    print()
    print("下一步：")
    print("  如果以上测试都成功，说明问题在 Agent 的处理逻辑")
    print("  需要优化 Agent 的提示词或处理流程")
    print()
    
    return True


def test_with_react_creator_direct():
    """测试使用 ReactNovelCreator，但直接调用 LLM"""
    print("=" * 70)
    print("测试 4: 使用 ReactNovelCreator（直接模式）")
    print("=" * 70)
    print()
    
    ***REMOVED*** 这里可以测试一个简化的创作流程
    ***REMOVED*** 暂时跳过，先完成上面的基础测试
    
    print("（此测试待后续实现）")
    return True


def main():
    """主函数"""
    print()
    
    ***REMOVED*** 运行简化测试
    success = test_llm_direct()
    
    if success:
        print("✅ 所有基础测试通过")
        return 0
    else:
        print("❌ 测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
