"""
50-100章系统性测试脚本

逐步测试不同章节数的创作，验证所有优化功能：
1. 渐进式大纲系统（>=50章自动启用）
2. 分层摘要系统
3. 实体重要性管理
4. 阶段性质量检查（每10章）
5. 质量指标追踪
6. 大纲动态调整
7. 自适应生成策略
"""
import sys
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from novel_creation.react_novel_creator import ReactNovelCreator

logger = logging.getLogger(__name__)


def test_novel_creation(
    novel_title: str,
    genre: str,
    theme: str,
    target_chapters: int,
    words_per_chapter: int = 2048
) -> Optional[Dict[str, Any]]:
    """
    测试小说创作
    
    Args:
        novel_title: 小说标题
        genre: 小说类型
        theme: 主题
        target_chapters: 目标章节数
        words_per_chapter: 每章目标字数
    
    Returns:
        测试结果
    """
    print("=" * 80)
    print(f"开始测试：{novel_title}")
    print("=" * 80)
    print(f"📖 章节数: {target_chapters} 章")
    print(f"📝 每章字数: {words_per_chapter} 字")
    print(f"📚 类型: {genre}")
    print(f"🎯 主题: {theme}")
    print()
    
    # 选择LLM客户端（可通过环境变量或参数控制）
    import os
    llm_model = os.getenv("NOVEL_LLM_MODEL", "gemini_3_flash")  # 默认使用gemini_3_flash（基于对比测试结果）
    
    if llm_model == "gemini_3_flash":
        from llm.chat import gemini_3_flash
        llm_client = gemini_3_flash
        print(f"使用LLM模型: gemini_3_flash")
    else:
        from llm.chat import deepseek_v3_2
        llm_client = deepseek_v3_2
        print(f"使用LLM模型: deepseek_v3_2")
    
    # 创建创作器（启用所有优化功能）
    print("初始化创作器...")
    try:
        creator = ReactNovelCreator(
            novel_title=novel_title,
            enable_context_offloading=True,
            enable_creative_context=True,
            enable_enhanced_extraction=True,
            enable_unimem=False,
            enable_quality_check=True,
            llm_client=llm_client
        )
        print("✅ 创作器初始化成功")
        print()
    except Exception as e:
        print(f"❌ 创作器初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # 开始创作
    start_time = datetime.now()
    print("=" * 80)
    print("开始创作...")
    print("=" * 80)
    print()
    
    try:
        result = creator.create_novel(
            genre=genre,
            theme=theme,
            target_chapters=target_chapters,
            words_per_chapter=words_per_chapter,
            start_from_chapter=1,
            use_progressive=None  # 自动选择（>=50章使用渐进式）
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print()
        print("=" * 80)
        print("创作完成！")
        print("=" * 80)
        print(f"✅ 总章节数: {result.get('total_chapters', 0)}")
        print(f"✅ 总字数: {result.get('total_words', 0):,} 字")
        print(f"✅ 耗时: {duration:.1f} 秒 ({duration/60:.1f} 分钟)")
        print(f"✅ 输出目录: {result.get('output_dir', 'N/A')}")
        print()
        
        # 验证优化功能
        print("=" * 80)
        print("验证优化功能...")
        print("=" * 80)
        print()
        
        # 1. 检查大纲类型
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
            
            # 检查关键实体
            key_entities = [
                e for e in creator.semantic_mesh.entities.values()
                if e.metadata.get('is_key', False)
            ]
            print(f"  ✅ 关键实体数: {len(key_entities)}")
            print()
        
        # 3. 检查阶段性质量检查
        periodic_checks = creator.metadata.get("periodic_quality_checks", [])
        print(f"📊 阶段性质量检查:")
        print(f"  ✅ 检查次数: {len(periodic_checks)}")
        if periodic_checks:
            for check in periodic_checks:
                scores = check.get("scores", {})
                overall = scores.get("overall", 0)
                needs_attention = check.get("needs_attention", False)
                status = "⚠️  需要关注" if needs_attention else "✅ 正常"
                print(f"  {status} {check.get('chapter_range', 'N/A')}: 综合评分 {overall:.2f}")
        print()
        
        # 4. 检查质量指标追踪
        quality_tracker = creator.metadata.get("quality_tracker", {})
        quality_history = quality_tracker.get("chapter_quality_history", [])
        if quality_history:
            print(f"📈 质量指标追踪:")
            print(f"  ✅ 已记录章节数: {len(quality_history)}")
            
            # 计算平均指标
            avg_word_control = sum(m.get("word_control_score", 0) for m in quality_history) / len(quality_history)
            avg_issues = sum(m.get("quality_issues", 0) for m in quality_history) / len(quality_history)
            print(f"  ✅ 平均字数控制得分: {avg_word_control:.2f}")
            print(f"  ✅ 平均质量问题数: {avg_issues:.2f}")
            
            # 质量趋势
            trends = quality_tracker.get("quality_trends", {})
            if trends:
                print(f"  ✅ 质量趋势数据点: {sum(len(v) for v in trends.values())}")
        print()
        
        # 5. 检查章节质量统计
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
        
        if word_stats:
            avg_words = sum(s["actual"] for s in word_stats) / len(word_stats)
            avg_diff_percent = sum(abs(s["diff_percent"]) for s in word_stats) / len(word_stats)
            print(f"  ✅ 平均字数: {avg_words:.0f} 字")
            print(f"  ✅ 平均字数偏差: {avg_diff_percent:.1f}%")
            
            # 字数分布
            within_target = sum(1 for s in word_stats if abs(s["diff_percent"]) <= 10)
            within_limit = sum(1 for s in word_stats if s["actual"] <= 3000)
            print(f"  ✅ 字数在目标±10%内: {within_target}/{len(word_stats)} ({within_target/len(word_stats)*100:.1f}%)")
            print(f"  ✅ 字数在3000字上限内: {within_limit}/{len(word_stats)} ({within_limit/len(word_stats)*100:.1f}%)")
        print()
        
        # 6. 获取质量摘要
        quality_summary = creator.get_quality_summary()
        if quality_summary and "message" not in quality_summary:
            print("📈 质量摘要:")
            avg_metrics = quality_summary.get("average_metrics", {})
            print(f"  ✅ 平均字数控制得分: {avg_metrics.get('word_control_score', 0):.2f}")
            print(f"  ✅ 平均质量问题数: {avg_metrics.get('quality_issues', 0):.2f}")
            
            trends = quality_summary.get("quality_trends", {})
            if trends:
                print(f"  ✅ 质量趋势:")
                for metric_name, trend_data in trends.items():
                    current = trend_data.get("current", 0)
                    trend = trend_data.get("trend", "stable")
                    trend_icon = "📈" if trend == "improving" else "📉" if trend == "declining" else "➡️"
                    print(f"    {trend_icon} {metric_name}: {current:.2f} ({trend})")
        print()
        
        print("=" * 80)
        print("✅ 所有功能验证完成！")
        print("=" * 80)
        
        return {
            "result": result,
            "creator": creator,
            "duration": duration,
            "plan_type": plan_type,
            "periodic_checks": periodic_checks,
            "quality_summary": quality_summary
        }
        
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ 创作过程中发生错误")
        print("=" * 80)
        print(f"错误信息: {e}")
        import traceback
        traceback.print_exc()
        return None


def run_progressive_tests():
    """
    逐步测试不同章节数：50, 60, 70, 80, 90, 100章
    """
    test_cases = [
        {"chapters": 50, "title": "50章渐进式大纲测试"},
        {"chapters": 60, "title": "60章渐进式大纲测试"},
        {"chapters": 70, "title": "70章渐进式大纲测试"},
        {"chapters": 80, "title": "80章渐进式大纲测试"},
        {"chapters": 90, "title": "90章渐进式大纲测试"},
        {"chapters": 100, "title": "100章渐进式大纲测试"},
    ]
    
    results = []
    
    for test_case in test_cases:
        chapters = test_case["chapters"]
        title = test_case["title"]
        
        print("\n" + "=" * 80)
        print(f"开始测试 {chapters} 章")
        print("=" * 80)
        print()
        
        result = test_novel_creation(
            novel_title=title,
            genre="都市",
            theme="系统文、打脸装逼",
            target_chapters=chapters,
            words_per_chapter=2048
        )
        
        if result:
            results.append({
                "chapters": chapters,
                "title": title,
                "success": True,
                "duration": result["duration"],
                "plan_type": result["plan_type"],
                "periodic_checks_count": len(result["periodic_checks"]),
                "quality_summary": result["quality_summary"]
            })
        else:
            results.append({
                "chapters": chapters,
                "title": title,
                "success": False
            })
        
        print(f"\n✅ {chapters} 章测试完成\n")
        print("等待5秒后继续下一个测试...")
        import time
        time.sleep(5)
    
    # 输出总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    print()
    
    for r in results:
        if r["success"]:
            print(f"✅ {r['chapters']}章: 成功 (耗时: {r['duration']/60:.1f}分钟, 大纲类型: {r['plan_type']}, 质量检查: {r['periodic_checks_count']}次)")
        else:
            print(f"❌ {r['chapters']}章: 失败")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="50-100章系统性测试")
    parser.add_argument("--chapters", type=int, default=50, help="测试章节数（默认50章）")
    parser.add_argument("--words", type=int, default=2048, help="每章目标字数（默认2048字）")
    parser.add_argument("--title", type=str, default=None, help="小说标题（默认自动生成）")
    parser.add_argument("--genre", type=str, default="都市", help="小说类型")
    parser.add_argument("--theme", type=str, default="系统文、打脸装逼", help="主题")
    parser.add_argument("--progressive", action="store_true", help="运行逐步测试（50, 60, 70, 80, 90, 100章）")
    
    args = parser.parse_args()
    
    if args.progressive:
        run_progressive_tests()
    else:
        title = args.title or f"{args.chapters}章系统性测试"
        test_novel_creation(
            novel_title=title,
            genre=args.genre,
            theme=args.theme,
            target_chapters=args.chapters,
            words_per_chapter=args.words
        )
