"""
开始创作：使用优化后的系统进行实际创作
"""
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from novel_creation.react_novel_creator import ReactNovelCreator


def main():
    """开始创作"""
    print("=" * 70)
    print("小说创作系统 - 开始创作")
    print("=" * 70)
    print()
    
    ***REMOVED*** 用户配置
    novel_title = input("请输入小说标题（默认：我的小说）: ").strip() or "我的小说"
    genre = input("请输入小说类型（默认：科幻）: ").strip() or "科幻"
    theme = input("请输入小说主题（默认：时间旅行）: ").strip() or "时间旅行"
    
    try:
        target_chapters = int(input("请输入目标章节数（默认：10）: ").strip() or "10")
        words_per_chapter = int(input("请输入每章目标字数（默认：3000）: ").strip() or "3000")
    except ValueError:
        target_chapters = 10
        words_per_chapter = 3000
        print("使用默认值：10章，每章3000字")
    
    print()
    print("功能选项（默认全部启用）：")
    use_enhanced = input("启用增强实体提取？(y/n, 默认y): ").strip().lower() != 'n'
    use_quality = input("启用质量检查？(y/n, 默认y): ").strip().lower() != 'n'
    use_unimem = input("启用 UniMem 长期记忆？(y/n, 默认n): ").strip().lower() == 'y'
    
    print()
    print("=" * 70)
    print("开始初始化创作器...")
    print("=" * 70)
    
    ***REMOVED*** 创建创作器
    creator = ReactNovelCreator(
        novel_title=novel_title,
        enable_context_offloading=True,
        enable_creative_context=True,
        enable_enhanced_extraction=use_enhanced,
        enable_unimem=use_unimem,
        enable_quality_check=use_quality
    )
    
    print("✅ 创作器初始化成功")
    print()
    print("配置状态：")
    print(f"  - 增强实体提取: {creator.enable_enhanced_extraction}")
    print(f"  - 质量检查: {creator.enable_quality_check}")
    print(f"  - 创作上下文: {creator.enable_creative_context}")
    print(f"  - UniMem: {creator.enable_unimem}")
    print()
    
    print("=" * 70)
    print("开始创作...")
    print("=" * 70)
    print()
    
    try:
        ***REMOVED*** 创作小说
        result = creator.create_novel(
            genre=genre,
            theme=theme,
            target_chapters=target_chapters,
            words_per_chapter=words_per_chapter,
            start_from_chapter=1
        )
        
        print()
        print("=" * 70)
        print("✅ 创作完成！")
        print("=" * 70)
        print()
        print(f"小说标题: {result['novel_title']}")
        print(f"总章节数: {result['total_chapters']}")
        print(f"总字数: {result['total_words']:,} 字")
        print(f"输出目录: {result['output_dir']}")
        print()
        
        ***REMOVED*** 显示统计信息
        metadata_file = Path(result['output_dir']) / "metadata.json"
        if metadata_file.exists():
            import json
            metadata = json.loads(metadata_file.read_text(encoding='utf-8'))
            
            print("创作统计：")
            creative_context = metadata.get('creative_context', {})
            if creative_context.get('enabled'):
                print(f"  实体数: {creative_context.get('entities_count', 0)}")
                print(f"  关系数: {creative_context.get('relations_count', 0)}")
            
            quality_check = metadata.get('quality_check', {})
            if quality_check.get('enabled'):
                print(f"  质量问题: {quality_check.get('total_issues', 0)} 个")
                if quality_check.get('high_severity_chapters', 0) > 0:
                    print(f"  严重问题章节: {quality_check.get('high_severity_chapters', 0)} 个")
        
        print()
        print("=" * 70)
        print("创作成功完成！")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n创作已中断")
    except Exception as e:
        print(f"\n\n❌ 创作失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
