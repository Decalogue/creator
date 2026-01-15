"""
快速冒烟测试脚本

最小化测试：验证系统基本功能
"""
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.WARNING,  ***REMOVED*** 只显示警告和错误
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from novel_creation.react_novel_creator import ReactNovelCreator

def main():
    print("=" * 70)
    print("冒烟测试 - 验证系统基本功能")
    print("=" * 70)
    print()
    
    try:
        ***REMOVED*** 初始化创作器
        print("1. 初始化创作器...", end=" ")
        creator = ReactNovelCreator(
            novel_title="冒烟测试",
            enable_context_offloading=True,
            enable_creative_context=True,
            enable_enhanced_extraction=True,
            enable_unimem=False,
            enable_quality_check=True
        )
        print("✅")
        
        ***REMOVED*** 测试大纲生成
        print("2. 生成小说大纲...", end=" ")
        plan = creator.create_novel_plan(
            genre="科幻",
            theme="时间旅行",
            target_chapters=1,
            words_per_chapter=1000
        )
        print("✅")
        print(f"   - 大纲包含 {len(plan.get('chapter_outline', []))} 个章节")
        
        ***REMOVED*** 测试章节创作
        print("3. 创作章节...", end=" ")
        chapter_info = plan.get('chapter_outline', [{}])[0] if plan.get('chapter_outline') else {}
        chapter = creator.create_chapter(
            chapter_number=1,
            chapter_title=chapter_info.get('title', '第一章'),
            chapter_summary=chapter_info.get('summary', '测试章节'),
            target_words=1000
        )
        print("✅")
        print(f"   - 章节标题: {chapter.title}")
        print(f"   - 章节字数: {len(chapter.content)} 字")
        
        ***REMOVED*** 检查输出文件
        print("4. 检查输出文件...", end=" ")
        output_dir = creator.output_dir
        chapter_file = output_dir / "chapters" / "chapter_001.txt"
        if chapter_file.exists():
            print("✅")
            print(f"   - 章节文件: {chapter_file}")
        else:
            print("❌")
            return False
        
        ***REMOVED*** 检查元数据
        metadata_file = output_dir / "metadata.json"
        if metadata_file.exists():
            print(f"   - 元数据文件: {metadata_file}")
        
        print()
        print("=" * 70)
        print("✅ 冒烟测试通过！")
        print("=" * 70)
        print()
        print(f"输出目录: {output_dir}")
        return True
        
    except Exception as e:
        print(f"❌")
        print()
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
