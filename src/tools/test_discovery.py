***REMOVED***!/usr/bin/env python3
"""
测试工具发现系统
"""
import sys
from pathlib import Path

***REMOVED*** 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools import default_registry, get_discovery


def test_index_layer():
    """测试 Index Layer"""
    print("=" * 60)
    print("测试 Index Layer")
    print("=" * 60)
    
    discovery = get_discovery()
    index_content = discovery.get_index_layer()
    
    print(index_content)
    print()
    
    ***REMOVED*** 统计 Token 数量（粗略估算：1 token ≈ 4 字符）
    token_count = len(index_content) // 4
    print(f"Index Layer Token 数量（估算）: {token_count}")
    print()


def test_discovery_layer():
    """测试 Discovery Layer"""
    print("=" * 60)
    print("测试 Discovery Layer")
    print("=" * 60)
    
    discovery = get_discovery()
    
    ***REMOVED*** 列出所有文档
    docs = discovery.list_tool_docs()
    print(f"已同步 {len(docs)} 个工具文档: {docs}")
    print()
    
    ***REMOVED*** 测试搜索
    print("【搜索测试 1: '计算'】")
    result = discovery.search_tool_docs("计算", max_results=3)
    print(result)
    print()
    
    print("【搜索测试 2: '天气'】")
    result = discovery.search_tool_docs("天气", max_results=3)
    print(result)
    print()
    
    ***REMOVED*** 测试读取完整文档
    print("【读取完整文档: calculator】")
    doc = discovery.get_tool_doc("calculator")
    if doc:
        print(doc[:500] + "..." if len(doc) > 500 else doc)
    print()


def test_token_savings():
    """测试 Token 节省效果"""
    print("=" * 60)
    print("Token 节省效果对比")
    print("=" * 60)
    
    discovery = get_discovery()
    
    ***REMOVED*** Index Layer（新方式）
    index_content = discovery.get_index_layer()
    index_tokens = len(index_content) // 4
    
    ***REMOVED*** 旧方式：所有工具详细描述
    tools = default_registry.get_all_functions()
    old_content_parts = []
    for tool in tools:
        func = tool.get("function", {})
        name = func.get("name", "")
        desc = func.get("description", "")
        params = func.get("parameters", {}).get("properties", {})
        
        param_desc = ", ".join([f"{k}: {v.get('description', '')}" 
                               for k, v in params.items()])
        
        old_content_parts.append(f"- {name}: {desc} (参数: {param_desc})")
    
    old_content = "\n".join(old_content_parts)
    old_tokens = len(old_content) // 4
    
    print(f"旧方式（所有工具详细描述）: {old_tokens} tokens")
    print(f"新方式（Index Layer）: {index_tokens} tokens")
    print(f"节省: {old_tokens - index_tokens} tokens ({((old_tokens - index_tokens) / old_tokens * 100):.1f}%)")
    print()


if __name__ == "__main__":
    print("工具发现系统测试")
    print()
    
    test_index_layer()
    test_discovery_layer()
    test_token_savings()
    
    print("=" * 60)
    print("测试完成！")
    print("=" * 60)
