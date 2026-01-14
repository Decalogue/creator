***REMOVED***!/usr/bin/env python3
"""
小说创作示例
"""
import sys
from pathlib import Path

***REMOVED*** 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from novel_creation.react_novel_creator import ReactNovelCreator


def main():
    """示例：创作一部中长篇小说"""
    
    ***REMOVED*** 创建小说创作器
    creator = ReactNovelCreator(
        novel_title="时空旅者的日记",
        enable_context_offloading=True  ***REMOVED*** 启用上下文卸载
    )
    
    ***REMOVED*** 创作小说
    result = creator.create_novel(
        genre="科幻",
        theme="时间旅行、平行世界、人性探索",
        target_chapters=10,  ***REMOVED*** 先创作10章作为示例
        words_per_chapter=2000,  ***REMOVED*** 每章2000字
        start_from_chapter=1
    )
    
    print("\n" + "=" * 60)
    print("小说创作完成！")
    print("=" * 60)
    print(f"小说标题：{result['novel_title']}")
    print(f"总章节数：{result['total_chapters']}")
    print(f"总字数：{result['total_words']}")
    print(f"输出目录：{result['output_dir']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
