import json
from tools import default_registry


def test_calculator():
    """测试计算器工具"""
    print("测试计算器工具...")
    
    test_cases = [
        {"expression": "2 + 3"},
        {"expression": "10 * 5 + 20"},
        {"expression": "100 / 4"},
        {"expression": "2 ** 8"},
        {"expression": "10 ^ 3"},  ***REMOVED*** 测试 ^ 转 **
    ]
    
    for case in test_cases:
        try:
            result = default_registry.execute_tool("calculator", case)
            print(f"  ✓ {case['expression']} -> {result}")
        except Exception as e:
            print(f"  ✗ {case['expression']} -> 错误: {e}")


def test_weather():
    """测试天气查询工具"""
    print("\n测试天气查询工具...")
    
    test_cases = [
        {"city": "北京"},
        {"city": "上海"},
        {"city": "未知城市"},
        {"city": "深圳", "date": "2024-01-01"},
    ]
    
    for case in test_cases:
        try:
            result = default_registry.execute_tool("get_weather", case)
            print(f"  ✓ {case['city']} -> {result[:50]}...")
        except Exception as e:
            print(f"  ✗ {case['city']} -> 错误: {e}")


def test_time():
    """测试时间查询工具"""
    print("\n测试时间查询工具...")
    
    test_cases = [
        {},
        {"timezone": "Asia/Shanghai", "format": "full"},
        {"timezone": "UTC", "format": "date"},
        {"timezone": "Asia/Shanghai", "format": "time"},
    ]
    
    for case in test_cases:
        try:
            result = default_registry.execute_tool("get_current_time", case)
            print(f"  ✓ {case} -> {result[:60]}...")
        except Exception as e:
            print(f"  ✗ {case} -> 错误: {e}")


def test_function_schema():
    """测试函数定义格式"""
    print("\n测试函数定义格式...")
    
    functions = default_registry.get_all_functions()
    
    print(f"  共 {len(functions)} 个工具函数")
    
    for func in functions:
        func_def = func["function"]
        print(f"  ✓ {func_def['name']}: {func_def['description']}")
        
        ***REMOVED*** 验证格式
        assert "type" in func
        assert "function" in func
        assert "name" in func_def
        assert "description" in func_def
        assert "parameters" in func_def
    
    print("  所有函数定义格式正确")


def test_registry():
    """测试注册表功能"""
    print("\n测试注册表功能...")
    
    ***REMOVED*** 测试列出所有工具
    tools = default_registry.list_tools()
    print(f"  已注册工具: {tools}")
    assert len(tools) >= 3
    
    ***REMOVED*** 测试获取工具
    calculator = default_registry.get_tool("calculator")
    assert calculator is not None
    assert calculator.name == "calculator"
    print("  ✓ 工具获取正常")
    
    ***REMOVED*** 测试获取不存在的工具
    not_found = default_registry.get_tool("not_exist")
    assert not_found is None
    print("  ✓ 不存在的工具返回 None")


def test_validation():
    """测试参数验证"""
    print("\n测试参数验证...")
    
    ***REMOVED*** 测试计算器验证
    calculator = default_registry.get_tool("calculator")
    
    ***REMOVED*** 有效参数
    assert calculator.validate_arguments({"expression": "2 + 3"})
    print("  ✓ 计算器有效参数验证通过")
    
    ***REMOVED*** 无效参数（缺少 expression）
    assert not calculator.validate_arguments({})
    print("  ✓ 计算器无效参数验证通过")
    
    ***REMOVED*** 危险表达式（应该被拒绝）
    assert not calculator.validate_arguments({"expression": "import os"})
    print("  ✓ 计算器危险表达式被拒绝")


if __name__ == "__main__":
    print("=" * 60)
    print("Function Calling 系统测试")
    print("=" * 60)
    
    try:
        test_calculator()
        test_weather()
        test_time()
        test_function_schema()
        test_registry()
        test_validation()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
