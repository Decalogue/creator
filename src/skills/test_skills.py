"""
Skills 系统测试
验证所有功能是否正常工作
"""
from skills import default_manager
from skills.skill import Skill


def test_skill_loading():
    """测试 Skill 加载"""
    print("测试 Skill 加载...")
    
    skills = default_manager.list_skills()
    assert len(skills) >= 2, "应该至少加载 2 个 Skills"
    assert 'calculator' in skills, "应该包含 calculator"
    assert 'weather' in skills, "应该包含 weather"
    print("  ✓ Skill 加载正常")


def test_metadata():
    """测试元数据（第一层）"""
    print("\n测试元数据（第一层）...")
    
    calculator = default_manager.get_skill('calculator')
    assert calculator is not None, "calculator 应该存在"
    
    metadata = calculator.metadata
    assert metadata.name == 'calculator', "名称应该正确"
    assert len(metadata.description) > 0, "描述应该存在"
    assert len(metadata.tags) > 0, "应该有标签"
    assert len(metadata.triggers) > 0, "应该有触发词"
    
    print(f"  ✓ 元数据: {metadata.name}")
    print(f"  ✓ 描述: {metadata.description[:50]}...")
    print(f"  ✓ 标签: {metadata.tags}")
    print(f"  ✓ 触发词: {metadata.triggers}")


def test_progressive_disclosure():
    """测试渐进式披露"""
    print("\n测试渐进式披露...")
    
    calculator = default_manager.get_skill('calculator')
    
    ***REMOVED*** 第一层：元数据
    context_level1 = calculator.get_context(level=1)
    tokens_level1 = calculator.estimate_tokens(level=1)
    assert tokens_level1 < 200, "第一层应该在 ~100 tokens 左右"
    assert 'calculator' in context_level1, "应该包含名称"
    print(f"  ✓ 第一层: {tokens_level1} tokens")
    
    ***REMOVED*** 第二层：主体
    context_level2 = calculator.get_context(level=2)
    tokens_level2 = calculator.estimate_tokens(level=2)
    assert tokens_level2 > tokens_level1, "第二层应该比第一层大"
    assert tokens_level2 < 6000, "第二层应该在 <5k tokens"
    assert '功能描述' in context_level2, "应该包含主体内容"
    print(f"  ✓ 第二层: {tokens_level2} tokens")
    
    ***REMOVED*** 第三层：所有资源
    context_level3 = calculator.get_context(level=3)
    tokens_level3 = calculator.estimate_tokens(level=3)
    assert tokens_level3 > tokens_level2, "第三层应该比第二层大"
    print(f"  ✓ 第三层: {tokens_level3} tokens")


def test_resource_loading():
    """测试资源文件加载"""
    print("\n测试资源文件加载...")
    
    calculator = default_manager.get_skill('calculator')
    resources = calculator.list_resources()
    
    assert len(resources) > 0, "应该有资源文件"
    print(f"  ✓ 资源文件: {resources}")
    
    ***REMOVED*** 加载资源
    if 'examples.md' in resources:
        content = calculator.load_resource('examples.md')
        assert len(content) > 0, "资源内容应该存在"
        print(f"  ✓ 成功加载 examples.md ({len(content)} 字符)")


def test_skill_selection():
    """测试 Skill 选择"""
    print("\n测试 Skill 选择...")
    
    ***REMOVED*** 测试计算相关查询
    query1 = "帮我计算 10 * 5"
    selected1 = default_manager.select_skills(query1)
    assert len(selected1) > 0, "应该选择到 Skills"
    assert any(s.name == 'calculator' for s in selected1), "应该选择 calculator"
    print(f"  ✓ 查询 '{query1}' -> {[s.name for s in selected1]}")
    
    ***REMOVED*** 测试天气相关查询
    query2 = "查询北京的天气"
    selected2 = default_manager.select_skills(query2)
    assert len(selected2) > 0, "应该选择到 Skills"
    assert any(s.name == 'weather' for s in selected2), "应该选择 weather"
    print(f"  ✓ 查询 '{query2}' -> {[s.name for s in selected2]}")


def test_context_generation():
    """测试上下文生成"""
    print("\n测试上下文生成...")
    
    query = "帮我计算 25 * 8"
    context = default_manager.get_context_for_query(query, level=2)
    
    assert len(context) > 0, "应该生成上下文"
    assert 'calculator' in context.lower(), "上下文应该包含 calculator"
    print(f"  ✓ 上下文长度: {len(context)} 字符")
    print(f"  ✓ 上下文预览: {context[:100]}...")


def test_skill_structure():
    """测试 Skill 结构"""
    print("\n测试 Skill 结构...")
    
    calculator = default_manager.get_skill('calculator')
    
    ***REMOVED*** 检查路径
    assert calculator.skill_path.exists(), "Skill 路径应该存在"
    assert calculator.skill_md_path.exists(), "SKILL.md 应该存在"
    print(f"  ✓ Skill 路径: {calculator.skill_path}")
    
    ***REMOVED*** 检查属性
    assert calculator.name == 'calculator', "名称应该正确"
    assert len(calculator.description) > 0, "描述应该存在"
    print(f"  ✓ Skill 名称: {calculator.name}")
    print(f"  ✓ Skill 描述: {calculator.description}")


if __name__ == "__main__":
    print("=" * 60)
    print("Skills 系统测试")
    print("=" * 60)
    
    try:
        test_skill_loading()
        test_metadata()
        test_progressive_disclosure()
        test_resource_loading()
        test_skill_selection()
        test_context_generation()
        test_skill_structure()
        
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
