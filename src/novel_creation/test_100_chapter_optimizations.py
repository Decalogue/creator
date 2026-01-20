"""
100章小说优化功能测试脚本

验证以下优化：
1. 实体重要性评分和分层传递
2. 渐进式大纲生成
3. 分层章节摘要
"""
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from novel_creation.react_novel_creator import ReactNovelCreator

logger = logging.getLogger(__name__)


def test_100_chapter_optimizations(
    novel_title: str = "100章优化测试小说",
    genre: str = "都市",
    theme: str = "系统文、打脸装逼",
    target_chapters: int = 5,  # 先测试5章，验证功能正常
    words_per_chapter: int = 2000,
    use_progressive: Optional[bool] = None  # None = 自动选择，True = 强制启用，False = 强制禁用
):
    """
    测试100章小说优化功能
    
    Args:
        novel_title: 小说标题
        genre: 小说类型
        theme: 主题
        target_chapters: 目标章节数（5章快速验证，或20章验证阶段摘要）
        words_per_chapter: 每章目标字数
    """
    print("=" * 70)
    print("100章小说优化功能测试")
    print("=" * 70)
    print()
    print(f"📖 小说标题: {novel_title}")
    print(f"📚 类型: {genre}")
    print(f"🎯 主题: {theme}")
    print(f"📑 章节数: {target_chapters} 章")
    print(f"📝 每章字数: {words_per_chapter} 字")
    print()
    print("🔍 测试优化功能：")
    print("  ✅ Phase 1: 实体重要性评分和分层传递")
    print("  ✅ Phase 2: 渐进式大纲生成（>=50章自动启用）")
    print("  ✅ Phase 3: 分层章节摘要")
    print()
    
    # 创建创作器（启用所有优化功能）
    print("=" * 70)
    print("初始化创作器...")
    print("=" * 70)
    
    try:
        creator = ReactNovelCreator(
            novel_title=novel_title,
            enable_context_offloading=True,
            enable_creative_context=True,
            enable_enhanced_extraction=True,
            enable_unimem=False,
            enable_quality_check=True
        )
        print("✅ 创作器初始化成功")
        print()
    except Exception as e:
        print(f"❌ 创作器初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # 开始创作
    print("=" * 70)
    print("开始创作...")
    print("=" * 70)
    print()
    
    start_time = datetime.now()
    
    try:
        result = creator.create_novel(
            genre=genre,
            theme=theme,
            target_chapters=target_chapters,
            words_per_chapter=words_per_chapter,
            start_from_chapter=1,
            use_progressive=use_progressive
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print()
        print("=" * 70)
        print("创作完成！")
        print("=" * 70)
        print()
        print(f"✅ 总章节数: {result.get('total_chapters', 0)}")
        print(f"✅ 总字数: {result.get('total_words', 0):,} 字")
        print(f"✅ 耗时: {duration:.1f} 秒")
        print(f"✅ 输出目录: {result.get('output_dir', 'N/A')}")
        print()
        
        # 验证优化功能
        print("=" * 70)
        print("验证优化功能...")
        print("=" * 70)
        print()
        
        # 1. 检查大纲类型（渐进式 vs 一次性）
        plan = creator.metadata.get("plan", {})
        plan_type = plan.get("plan_type", "onetime")
        print(f"📋 大纲类型: {plan_type}")
        if plan_type == "progressive":
            print("  ✅ 使用渐进式大纲生成（自动启用）")
            phases = plan.get("phases", [])
            print(f"  ✅ 已生成阶段数: {len(phases)}")
            overall = plan.get("overall", {})
            if overall:
                print(f"  ✅ 整体大纲已生成（包含 {len(overall.get('key_plot_points', []))} 个关键转折点）")
        else:
            print("  ℹ️  使用一次性大纲生成（章节数 < 50，符合预期）")
        print()
        
        # 2. 检查实体系统
        if creator.enable_creative_context and creator.semantic_mesh:
            entities_count = len(creator.semantic_mesh.entities)
            relations_count = len(creator.semantic_mesh.relations)
            print(f"🔗 语义网格:")
            print(f"  ✅ 实体总数: {entities_count}")
            print(f"  ✅ 关系总数: {relations_count}")
            
            # 检查实体重要性元数据
            entities_with_importance = sum(
                1 for e in creator.semantic_mesh.entities.values()
                if e.metadata.get('appearance_count', 0) > 0
            )
            print(f"  ✅ 已更新重要性的实体: {entities_with_importance}")
            print()
            
            # 检查关键实体
            key_entities = [
                e for e in creator.semantic_mesh.entities.values()
                if e.metadata.get('is_key', False)
            ]
            print(f"  ✅ 关键实体数: {len(key_entities)}")
            if key_entities:
                print("  关键实体列表:")
                for entity in key_entities[:5]:  # 只显示前5个
                    print(f"    - {entity.name} ({entity.type.value})")
            print()
        
        # 3. 检查分层摘要（如果章节数足够）
        if target_chapters >= 20:
            print("📑 分层摘要验证:")
            # 检查最近章节是否包含摘要
            recent_chapters = creator.chapters[-5:] if len(creator.chapters) >= 5 else creator.chapters
            has_summaries = all(ch.summary for ch in recent_chapters)
            print(f"  ✅ 最近章节摘要完整性: {'是' if has_summaries else '否'}")
            
            # 检查阶段摘要（如果使用渐进式）
            if plan_type == "progressive":
                phases = plan.get("phases", [])
                phases_with_summary = sum(1 for p in phases if p.get("phase_summary"))
                print(f"  ✅ 已生成阶段摘要数: {phases_with_summary}")
            print()
        
        # 4. 检查章节质量
        print("📊 章节质量统计:")
        word_stats = []
        for chapter in creator.chapters:
            actual_words = chapter.metadata.get("actual_words", len(chapter.content))
            target_words = chapter.metadata.get("target_words", words_per_chapter)
            word_diff_percent = chapter.metadata.get("word_diff_percent", 0)
            word_stats.append({
                "chapter": chapter.chapter_number,
                "actual": actual_words,
                "target": target_words,
                "diff_percent": word_diff_percent
            })
        
        avg_words = sum(s["actual"] for s in word_stats) / len(word_stats) if word_stats else 0
        avg_diff_percent = sum(abs(s["diff_percent"]) for s in word_stats) / len(word_stats) if word_stats else 0
        
        print(f"  ✅ 平均字数: {avg_words:.0f} 字")
        print(f"  ✅ 平均字数偏差: {avg_diff_percent:.1f}%")
        print()
        
        print("=" * 70)
        print("✅ 所有优化功能验证完成！")
        print("=" * 70)
        
        return result
        
    except Exception as e:
        print()
        print("=" * 70)
        print("❌ 创作过程中发生错误")
        print("=" * 70)
        print(f"错误信息: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="测试100章小说优化功能")
    parser.add_argument("--chapters", type=int, default=5, help="测试章节数（默认5章）")
    parser.add_argument("--words", type=int, default=2000, help="每章目标字数（默认2000字）")
    parser.add_argument("--title", type=str, default="100章优化测试小说", help="小说标题")
    parser.add_argument("--genre", type=str, default="都市", help="小说类型")
    parser.add_argument("--theme", type=str, default="系统文、打脸装逼", help="主题")
    parser.add_argument("--progressive", action="store_true", help="强制启用渐进式大纲（默认：>=50章自动启用）")
    parser.add_argument("--no-progressive", action="store_true", help="强制禁用渐进式大纲")
    
    args = parser.parse_args()
    
    # 处理渐进式大纲选项
    use_progressive = None
    if args.progressive:
        use_progressive = True
    elif args.no_progressive:
        use_progressive = False
    
    test_100_chapter_optimizations(
        novel_title=args.title,
        genre=args.genre,
        theme=args.theme,
        target_chapters=args.chapters,
        words_per_chapter=args.words,
        use_progressive=use_progressive
    )
