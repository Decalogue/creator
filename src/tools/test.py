"""
tools 模块测试：工具发现与注册表

当前内置工具仅保留创作相关：search_tool_docs、read_tool_doc。
"""
import json
from tools import default_registry, get_discovery


def test_discovery_tools():
    """测试工具发现相关工具"""
    print("测试工具发现相关工具...")

    # search_tool_docs
    try:
        discovery = get_discovery()
        result = discovery.search_tool_docs("工具", max_results=3)
        print(f"  ✓ search_tool_docs('工具') -> {len(result)} 条")
    except Exception as e:
        print(f"  ✗ search_tool_docs -> 错误: {e}")

    # read_tool_doc（read_tool_doc 工具）
    try:
        doc = default_registry.execute_tool("read_tool_doc", {"tool_name": "search_tool_docs"})
        print(f"  ✓ read_tool_doc('search_tool_docs') -> 长度 {len(doc)}")
    except Exception as e:
        print(f"  ✗ read_tool_doc -> 错误: {e}")


def test_function_schema():
    """测试函数定义格式"""
    print("\n测试函数定义格式...")

    functions = default_registry.get_all_functions()
    print(f"  共 {len(functions)} 个工具函数")

    for func in functions:
        func_def = func["function"]
        print(f"  ✓ {func_def['name']}: {func_def['description'][:40]}...")
        assert "type" in func
        assert "function" in func
        assert "name" in func_def
        assert "description" in func_def
        assert "parameters" in func_def

    print("  所有函数定义格式正确")


def test_registry():
    """测试注册表功能"""
    print("\n测试注册表功能...")

    tools = default_registry.list_tools()
    print(f"  已注册工具: {tools}")
    assert len(tools) >= 2, "至少应有 search_tool_docs 与 read_tool_doc"

    for name in ["search_tool_docs", "read_tool_doc"]:
        t = default_registry.get_tool(name)
        assert t is not None, f"应能获取工具 {name}"
        print(f"  ✓ 获取工具 {name} 正常")

    not_found = default_registry.get_tool("not_exist")
    assert not_found is None
    print("  ✓ 不存在的工具返回 None")


if __name__ == "__main__":
    print("=" * 60)
    print("tools 模块测试（创作相关）")
    print("=" * 60)

    try:
        test_discovery_tools()
        test_function_schema()
        test_registry()

        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
