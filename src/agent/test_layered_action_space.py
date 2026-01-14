***REMOVED***!/usr/bin/env python3
"""
测试分层行动空间
"""
import sys
from pathlib import Path

***REMOVED*** 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.layered_action_space import get_layered_action_space


def test_l1_functions():
    """测试 L1 原子函数"""
    print("=" * 60)
    print("测试 L1 原子函数")
    print("=" * 60)
    
    las = get_layered_action_space()
    
    ***REMOVED*** 测试 read_file
    print("【测试 read_file】")
    test_file = Path("agent/sandbox/test_file.txt")
    test_file.write_text("这是测试文件内容\n第二行", encoding="utf-8")
    
    result = las.execute_l1_function("read_file", {"file_path": str(test_file)})
    print(result)
    print()
    
    ***REMOVED*** 测试 write_file
    print("【测试 write_file】")
    result = las.execute_l1_function(
        "write_file",
        {"file_path": "agent/sandbox/test_write.txt", "content": "写入的内容"}
    )
    print(result)
    print()
    
    ***REMOVED*** 测试 execute_shell
    print("【测试 execute_shell】")
    result = las.execute_l1_function("execute_shell", {"command": "echo 'Hello, World!'"})
    print(result)
    print()
    
    ***REMOVED*** 测试 search_files
    print("【测试 search_files】")
    result = las.execute_l1_function("search_files", {"pattern": "*.txt", "directory": "agent/sandbox"})
    print(result)
    print()


def test_l2_tools():
    """测试 L2 沙盒工具"""
    print("=" * 60)
    print("测试 L2 沙盒工具")
    print("=" * 60)
    
    las = get_layered_action_space()
    
    ***REMOVED*** 测试工具发现
    print("【测试工具发现】")
    for tool_name in ["grep", "curl", "python"]:
        description = las.discover_l2_tool(tool_name)
        if description:
            print(f"✓ {description}")
        else:
            print(f"✗ {tool_name}: 未找到")
    print()
    
    ***REMOVED*** 测试通过 L1 使用 L2 工具
    print("【测试通过 L1 使用 L2 工具（grep）】")
    test_file = Path("agent/sandbox/test_grep.txt")
    test_file.write_text("line1\nline2\nline3\n", encoding="utf-8")
    
    result = las.execute_l1_function(
        "execute_shell",
        {"command": f"grep 'line2' {test_file}"}
    )
    print(result)
    print()


def test_l3_scripts():
    """测试 L3 代码层"""
    print("=" * 60)
    print("测试 L3 代码层")
    print("=" * 60)
    
    las = get_layered_action_space()
    
    ***REMOVED*** 测试执行 Python 脚本
    print("【测试执行 Python 脚本】")
    script_content = """
import json
from datetime import datetime

data = {
    "timestamp": datetime.now().isoformat(),
    "message": "Hello from L3 script!"
}

print(json.dumps(data, ensure_ascii=False, indent=2))
"""
    
    summary, script_path = las.execute_l3_script(script_content, "test_l3.py")
    print(summary)
    print(f"脚本路径: {script_path}")
    print()


def test_descriptions():
    """测试描述生成"""
    print("=" * 60)
    print("测试描述生成")
    print("=" * 60)
    
    las = get_layered_action_space()
    
    print("【L1 函数描述】")
    print(las.get_l1_functions_description())
    print()
    
    print("【L2 工具描述】")
    print(las.get_l2_tools_description())
    print()
    
    print("【L3 代码层描述】")
    print(las.get_l3_description())
    print()


if __name__ == "__main__":
    print("分层行动空间测试")
    print()
    
    test_l1_functions()
    test_l2_tools()
    test_l3_scripts()
    test_descriptions()
    
    print("=" * 60)
    print("测试完成！")
    print("=" * 60)
