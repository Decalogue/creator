#!/usr/bin/env python3
"""
20章长篇小说测试脚本

测试系统在更长篇幅上的表现和稳定性
"""
import sys
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from novel_creation.react_novel_creator import ReactNovelCreator

logger = logging.getLogger(__name__)


def test_20_chapters(
    novel_title: str = "20章长篇小说测试",
    genre: str = "玄幻",
    theme: str = "修仙与飞升",
    words_per_chapter: int = 3000,
    target_chapters: int = 20
):
    """
    测试长篇小说创作
    
    Args:
        novel_title: 小说标题
        genre: 小说类型
        theme: 主题
        words_per_chapter: 每章目标字数
        target_chapters: 目标章节数
    """
    print("=" * 70)
    print(f"{target_chapters}章长篇小说测试")
    print("=" * 70)
    print()
    print(f"📖 小说标题: {novel_title}")
    print(f"📚 类型: {genre}")
    print(f"🎯 主题: {theme}")
    print(f"📑 章节数: {target_chapters} 章")
    print(f"📝 每章字数: {words_per_chapter} 字（目标）")
    print(f"📊 总字数目标: {target_chapters * words_per_chapter:,} 字")
    print()
    estimated_minutes = target_chapters * 2  # 每章约2分钟
    print(f"⏱️  预计耗时: {estimated_minutes}-{estimated_minutes + 10} 分钟")
    print(f"💾 输出目录: novel_creation/outputs/{novel_title}/")
    print()
    
    start_time = datetime.now()
    
    try:
        # 创建创作器（启用所有优化功能）
        print("🔧 初始化创作器...")
        creator = ReactNovelCreator(
            novel_title=novel_title,
            enable_context_offloading=True,
            enable_creative_context=True,
            enable_enhanced_extraction=True,
            enable_unimem=False,  # 暂时禁用 UniMem，避免额外依赖
            enable_quality_check=True
        )
        print("✅ 创作器初始化成功")
        print()
        
        # 生成大纲
        print("📋 生成小说大纲...")
        plan = creator.create_novel_plan(
            genre=genre,
            theme=theme,
            target_chapters=target_chapters,
            words_per_chapter=words_per_chapter
        )
        print("✅ 大纲生成成功")
        print()
        
        # 开始创作
        print("✍️  开始创作章节...")
        print("=" * 70)
        print()
        
        result = creator.create_novel(
            genre=genre,
            theme=theme,
            target_chapters=target_chapters,
            words_per_chapter=words_per_chapter
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print()
        print("=" * 70)
        print("✅ 测试完成！")
        print("=" * 70)
        print()
        print(f"📊 测试结果:")
        print(f"   - 总章节数: {result['total_chapters']} 章")
        print(f"   - 总字数: {result['total_words']:,} 字")
        print(f"   - 平均字数/章: {result['total_words'] // result['total_chapters']:,} 字")
        print(f"   - 耗时: {duration / 60:.1f} 分钟")
        print(f"   - 平均速度: {result['total_words'] / duration * 60:.0f} 字/分钟")
        print()
        print(f"📁 输出目录: {result['output_dir']}")
        print()
        
        # 检查优化功能效果
        if creator.enable_creative_context and creator.semantic_mesh:
            entities_count = len(creator.semantic_mesh.entities)
            relations_count = len(creator.semantic_mesh.relations)
            print(f"🎯 优化功能效果:")
            print(f"   - 实体提取: {entities_count} 个（平均 {entities_count // result['total_chapters']:.1f} 个/章）")
            print(f"   - 关系提取: {relations_count} 个")
            print()
        
        # 字数控制效果
        if creator.chapters:
            word_diffs = []
            for chapter in creator.chapters:
                metadata = chapter.metadata
                if 'word_diff_percent' in metadata:
                    word_diffs.append(abs(metadata['word_diff_percent']))
            
            if word_diffs:
                avg_diff = sum(word_diffs) / len(word_diffs)
                max_diff = max(word_diffs)
                print(f"📏 字数控制效果:")
                print(f"   - 平均偏差: {avg_diff:.1f}%")
                print(f"   - 最大偏差: {max_diff:.1f}%")
                print()
        
        # 质量检查统计
        if creator.enable_quality_check:
            total_issues = 0
            high_severity = 0
            for chapter in creator.chapters:
                quality = chapter.metadata.get('quality_check', {})
                total_issues += quality.get('total_issues', 0)
                if quality.get('has_high_severity', False):
                    high_severity += 1
            
            print(f"✅ 质量检查统计:")
            print(f"   - 总问题数: {total_issues} 个")
            print(f"   - 严重问题章节: {high_severity} 章")
            print(f"   - 平均问题/章: {total_issues / result['total_chapters']:.1f} 个")
            print()
        
        print("=" * 70)
        print("📝 测试报告已保存到输出目录")
        print("=" * 70)
        
        return result
        
    except KeyboardInterrupt:
        print()
        print("⚠️  测试被用户中断")
        print(f"⏱️  已运行时间: {(datetime.now() - start_time).total_seconds() / 60:.1f} 分钟")
        print(f"📊 已完成章节: {len(creator.chapters) if 'creator' in locals() else 0} 章")
        raise
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        print()
        print("❌ 测试失败")
        print(f"错误信息: {e}")
        print(f"⏱️  已运行时间: {(datetime.now() - start_time).total_seconds() / 60:.1f} 分钟")
        print(f"📊 已完成章节: {len(creator.chapters) if 'creator' in locals() else 0} 章")
        raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="20章长篇小说测试")
    parser.add_argument('--title', type=str, default="20章长篇小说测试", help='小说标题')
    parser.add_argument('--genre', type=str, default="玄幻", help='小说类型')
    parser.add_argument('--theme', type=str, default="修仙与飞升", help='主题')
    parser.add_argument('--words', type=int, default=3000, help='每章目标字数')
    parser.add_argument('--chapters', type=int, default=20, help='章节数')
    
    args = parser.parse_args()
    
    test_20_chapters(
        novel_title=args.title,
        genre=args.genre,
        theme=args.theme,
        words_per_chapter=args.words,
        target_chapters=args.chapters
    )
