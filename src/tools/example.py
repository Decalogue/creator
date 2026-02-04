"""
tools 使用示例：创作相关工具发现与自定义工具

当前内置工具仅保留创作相关：search_tool_docs、read_tool_doc。
编排层（如 ReActAgent）通过它们按需查找工具文档；新增创作工具时继承 Tool 并注册。
"""
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

if __name__ == "__main__" and not __package__:
    src_dir = Path(__file__).parent.parent
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

from tools import default_registry, get_discovery
from tools.base import Tool


def print_section(title: str, width: int = 50):
    """打印章节标题"""
    print("\n" + "=" * width)
    print(title)
    print("=" * width)


def example_1_basic_usage():
    """示例 1：基本使用（列出工具与发现层）"""
    print_section("示例 1：基本使用")

    functions = default_registry.get_all_functions()
    print("\n当前可用工具（创作相关）：")
    for func in functions:
        print(f"- {func['function']['name']}: {func['function']['description']}")

    discovery = get_discovery()
    index_content = discovery.get_index_layer()
    print("\nIndex Layer 内容（供编排层注入系统提示词）：")
    print(index_content[:500] + "..." if len(index_content) > 500 else index_content)


def example_2_execute_discovery_tools():
    """示例 2：执行工具发现相关工具"""
    print_section("示例 2：执行工具发现相关工具")

    ***REMOVED*** search_tool_docs
    result = default_registry.execute_tool("search_tool_docs", {"query": "工具", "max_results": 3})
    print("\nsearch_tool_docs('工具', max_results=3):")
    print(result)

    ***REMOVED*** read_tool_doc
    doc = default_registry.execute_tool("read_tool_doc", {"tool_name": "search_tool_docs"})
    print("\nread_tool_doc('search_tool_docs') 片段:")
    print(doc[:400] + "..." if len(doc) > 400 else doc)


def example_3_custom_tool():
    """示例 3：创建自定义创作相关工具（示例：字数统计）"""
    print_section("示例 3：创建自定义工具（示例）")

    class WordCountTool(Tool):
        """示例：字数统计工具（创作相关）"""

        def __init__(self):
            super().__init__(name="word_count", description="统计文本字数，用于创作字数控制")

        def get_function_schema(self) -> Dict[str, Any]:
            return {
                "type": "function",
                "function": {
                    "name": "word_count",
                    "description": "统计文本字数，用于创作字数控制",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "待统计的文本"}
                        },
                        "required": ["text"],
                    },
                },
            }

        def execute(self, arguments: Dict[str, Any]) -> Any:
            text = arguments.get("text", "")
            return f"字数：{len(text)}"

    tool = WordCountTool()
    default_registry.register(tool)
    result = default_registry.execute_tool("word_count", {"text": "这是一段示例文本。"})
    print(result)


if __name__ == "__main__":
    print_section("tools 使用示例（创作相关）", 60)

    example_1_basic_usage()
    example_2_execute_discovery_tools()
    example_3_custom_tool()

    print_section("所有示例运行完成！", 60)
    print("\n提示：编排层（orchestrator/react.ReActAgent）使用 default_registry 与 get_discovery()；")
    print("新增创作相关工具时继承 Tool、注册到 default_registry，并在 tools/docs/ 下提供对应 .md。")
