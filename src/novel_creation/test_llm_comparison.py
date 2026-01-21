#!/usr/bin/env python3
"""
LLM模型对比测试脚本

对比 deepseek_v3_2 和 gemini_3_flash 在小说创作中的表现：
1. 章节生成质量
2. 字数控制
3. 重写效果
4. 质量问题数量
"""
import sys
import os
import argparse
import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from novel_creation.react_novel_creator import ReactNovelCreator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_with_model(
    model_name: str,
    novel_title: str,
    genre: str,
    theme: str,
    target_chapters: int,
    words_per_chapter: int = 2048,
    test_title: str = None
) -> Dict[str, Any]:
    """
    使用指定模型进行测试
    
    Returns:
        测试结果统计
    """
    logger.info("=" * 80)
    logger.info(f"开始测试模型: {model_name}")
    logger.info("=" * 80)
    
    # 选择LLM客户端
    if model_name == "gemini_3_flash":
        from llm.chat import gemini_3_flash
        llm_client = gemini_3_flash
    elif model_name == "deepseek_v3_2":
        from llm.chat import deepseek_v3_2
        llm_client = deepseek_v3_2
    else:
        raise ValueError(f"不支持的模型: {model_name}")
    
    logger.info(f"使用LLM模型: {model_name}")
    
    # 创建输出目录
    output_dir = f"novel_creation/outputs/{test_title}_{model_name}"
    
    # 创建创作器
    creator = ReactNovelCreator(
        novel_title=novel_title,
        output_dir=output_dir,
        enable_quality_check=True,
        enable_creative_context=True,
        llm_client=llm_client
    )
    
    try:
        # 创作小说
        result = creator.create_novel(
            genre=genre,
            theme=theme,
            target_chapters=target_chapters,
            words_per_chapter=words_per_chapter,
            use_progressive=target_chapters >= 50
        )
        
        # 统计结果
        stats = analyze_results(creator, output_dir, model_name)
        return stats
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        return {
            "model": model_name,
            "error": str(e),
            "success": False
        }


def analyze_results(creator: ReactNovelCreator, output_dir: str, model_name: str) -> Dict[str, Any]:
    """
    分析测试结果
    """
    chapters_dir = Path(output_dir) / "chapters"
    
    stats = {
        "model": model_name,
        "success": True,
        "total_chapters": 0,
        "total_words": 0,
        "avg_words_per_chapter": 0,
        "word_control": {
            "avg_diff_percent": 0,
            "chapters_within_target": 0,
            "chapters_over_target": 0,
        },
        "quality": {
            "total_issues": 0,
            "avg_issues_per_chapter": 0,
            "chapters_with_issues": 0,
            "high_severity_issues": 0,
        },
        "rewrite": {
            "rewritten_chapters": 0,
            "improved_chapters": 0,
            "unchanged_chapters": 0,
            "worsened_chapters": 0,
            "avg_rewrite_rounds": 0,
            "improvement_rate": 0,
        },
        "issue_types": {},
    }
    
    # 读取metadata
    metadata_file = Path(output_dir) / "metadata.json"
    if metadata_file.exists():
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        stats["total_chapters"] = metadata.get("total_chapters", 0)
        stats["total_words"] = metadata.get("total_words", 0)
        stats["avg_words_per_chapter"] = stats["total_words"] / max(stats["total_chapters"], 1)
    
    # 分析各章节
    word_diffs = []
    total_rewrite_rounds = 0
    
    for i in range(1, stats["total_chapters"] + 1):
        meta_file = chapters_dir / f"chapter_{i:03d}_meta.json"
        if not meta_file.exists():
            continue
        
        with open(meta_file, 'r', encoding='utf-8') as f:
            chapter_meta = json.load(f)
        
        metadata = chapter_meta.get('metadata', {})
        
        # 字数统计
        target_words = metadata.get('target_words', 2048)
        actual_words = metadata.get('actual_words', 0)
        word_diff_percent = metadata.get('word_diff_percent', 0)
        word_diffs.append(word_diff_percent)
        
        if abs(word_diff_percent) <= 10:
            stats["word_control"]["chapters_within_target"] += 1
        elif word_diff_percent > 10:
            stats["word_control"]["chapters_over_target"] += 1
        
        # 质量问题统计
        quality_check = metadata.get('quality_check', {})
        if isinstance(quality_check, dict) and quality_check:
            issues_count = quality_check.get('total_issues', 0)
            if issues_count > 0:
                stats["quality"]["chapters_with_issues"] += 1
                stats["quality"]["total_issues"] += issues_count
                
                # 统计问题类型
                issues = quality_check.get('issues', [])
                for issue in issues:
                    issue_type = issue.get('type', 'unknown')
                    stats["issue_types"][issue_type] = stats["issue_types"].get(issue_type, 0) + 1
                
                # 严重问题
                by_severity = quality_check.get('by_severity', {})
                if isinstance(by_severity, dict):
                    stats["quality"]["high_severity_issues"] += by_severity.get('high', 0)
        
        # 重写统计
        if metadata.get('rewritten', False):
            stats["rewrite"]["rewritten_chapters"] += 1
            rewrite_rounds = metadata.get('rewrite_rounds', 0)
            total_rewrite_rounds += rewrite_rounds
            
            original_issues = metadata.get('original_issue_count', 0)
            final_issues = metadata.get('final_issue_count', 0)
            
            if isinstance(original_issues, int) and isinstance(final_issues, int):
                if final_issues < original_issues:
                    stats["rewrite"]["improved_chapters"] += 1
                elif final_issues == original_issues:
                    stats["rewrite"]["unchanged_chapters"] += 1
                elif final_issues > original_issues:
                    stats["rewrite"]["worsened_chapters"] += 1
    
    # 计算平均值
    if word_diffs:
        stats["word_control"]["avg_diff_percent"] = sum(word_diffs) / len(word_diffs)
    
    if stats["total_chapters"] > 0:
        stats["quality"]["avg_issues_per_chapter"] = stats["quality"]["total_issues"] / stats["total_chapters"]
    
    if stats["rewrite"]["rewritten_chapters"] > 0:
        stats["rewrite"]["avg_rewrite_rounds"] = total_rewrite_rounds / stats["rewrite"]["rewritten_chapters"]
        stats["rewrite"]["improvement_rate"] = stats["rewrite"]["improved_chapters"] / stats["rewrite"]["rewritten_chapters"] * 100
    
    return stats


def compare_results(results: Dict[str, Dict[str, Any]]) -> str:
    """
    对比两个模型的结果并生成报告
    """
    report = []
    report.append("=" * 80)
    report.append("LLM模型对比测试报告")
    report.append("=" * 80)
    report.append("")
    
    models = list(results.keys())
    if len(models) != 2:
        return "需要两个模型的测试结果进行对比"
    
    model1, model2 = models[0], models[1]
    r1, r2 = results[model1], results[model2]
    
    # 基本信息
    report.append("测试配置:")
    report.append(f"  小说标题: {r1.get('novel_title', 'N/A')}")
    report.append(f"  类型: {r1.get('genre', 'N/A')}")
    report.append(f"  章节数: {r1.get('target_chapters', 'N/A')}")
    report.append("")
    
    # 字数控制对比
    report.append("=" * 80)
    report.append("1. 字数控制对比")
    report.append("=" * 80)
    
    w1 = r1.get("word_control", {})
    w2 = r2.get("word_control", {})
    
    report.append(f"{model1}:")
    report.append(f"  平均字数差异: {w1.get('avg_diff_percent', 0):.1f}%")
    report.append(f"  目标范围内章节: {w1.get('chapters_within_target', 0)}/{r1.get('total_chapters', 0)}")
    report.append(f"  超出目标章节: {w1.get('chapters_over_target', 0)}/{r1.get('total_chapters', 0)}")
    report.append("")
    
    report.append(f"{model2}:")
    report.append(f"  平均字数差异: {w2.get('avg_diff_percent', 0):.1f}%")
    report.append(f"  目标范围内章节: {w2.get('chapters_within_target', 0)}/{r2.get('total_chapters', 0)}")
    report.append(f"  超出目标章节: {w2.get('chapters_over_target', 0)}/{r2.get('total_chapters', 0)}")
    report.append("")
    
    diff1 = abs(w1.get('avg_diff_percent', 0))
    diff2 = abs(w2.get('avg_diff_percent', 0))
    if diff1 < diff2:
        report.append(f"✅ {model1} 字数控制更准确（差异 {diff1:.1f}% vs {diff2:.1f}%）")
    elif diff2 < diff1:
        report.append(f"✅ {model2} 字数控制更准确（差异 {diff2:.1f}% vs {diff1:.1f}%）")
    else:
        report.append(f"⚖️ 字数控制相当（差异 {diff1:.1f}% vs {diff2:.1f}%）")
    report.append("")
    
    # 质量问题对比
    report.append("=" * 80)
    report.append("2. 质量问题对比")
    report.append("=" * 80)
    
    q1 = r1.get("quality", {})
    q2 = r2.get("quality", {})
    
    report.append(f"{model1}:")
    report.append(f"  总问题数: {q1.get('total_issues', 0)}")
    report.append(f"  平均每章问题数: {q1.get('avg_issues_per_chapter', 0):.2f}")
    report.append(f"  有问题的章节: {q1.get('chapters_with_issues', 0)}/{r1.get('total_chapters', 0)}")
    report.append(f"  严重问题数: {q1.get('high_severity_issues', 0)}")
    report.append("")
    
    report.append(f"{model2}:")
    report.append(f"  总问题数: {q2.get('total_issues', 0)}")
    report.append(f"  平均每章问题数: {q2.get('avg_issues_per_chapter', 0):.2f}")
    report.append(f"  有问题的章节: {q2.get('chapters_with_issues', 0)}/{r2.get('total_chapters', 0)}")
    report.append(f"  严重问题数: {q2.get('high_severity_issues', 0)}")
    report.append("")
    
    avg1 = q1.get('avg_issues_per_chapter', 0)
    avg2 = q2.get('avg_issues_per_chapter', 0)
    if avg1 < avg2:
        report.append(f"✅ {model1} 质量问题更少（平均 {avg1:.2f} vs {avg2:.2f} 个/章）")
    elif avg2 < avg1:
        report.append(f"✅ {model2} 质量问题更少（平均 {avg2:.2f} vs {avg1:.2f} 个/章）")
    else:
        report.append(f"⚖️ 质量问题相当（平均 {avg1:.2f} vs {avg2:.2f} 个/章）")
    report.append("")
    
    # 重写效果对比
    report.append("=" * 80)
    report.append("3. 重写效果对比")
    report.append("=" * 80)
    
    rw1 = r1.get("rewrite", {})
    rw2 = r2.get("rewrite", {})
    
    report.append(f"{model1}:")
    report.append(f"  重写章节数: {rw1.get('rewritten_chapters', 0)}/{r1.get('total_chapters', 0)}")
    report.append(f"  改善章节: {rw1.get('improved_chapters', 0)} ({rw1.get('improvement_rate', 0):.1f}%)")
    report.append(f"  未变化章节: {rw1.get('unchanged_chapters', 0)}")
    report.append(f"  恶化章节: {rw1.get('worsened_chapters', 0)}")
    report.append(f"  平均重写轮数: {rw1.get('avg_rewrite_rounds', 0):.2f}")
    report.append("")
    
    report.append(f"{model2}:")
    report.append(f"  重写章节数: {rw2.get('rewritten_chapters', 0)}/{r2.get('total_chapters', 0)}")
    report.append(f"  改善章节: {rw2.get('improved_chapters', 0)} ({rw2.get('improvement_rate', 0):.1f}%)")
    report.append(f"  未变化章节: {rw2.get('unchanged_chapters', 0)}")
    report.append(f"  恶化章节: {rw2.get('worsened_chapters', 0)}")
    report.append(f"  平均重写轮数: {rw2.get('avg_rewrite_rounds', 0):.2f}")
    report.append("")
    
    rate1 = rw1.get('improvement_rate', 0)
    rate2 = rw2.get('improvement_rate', 0)
    if rate1 > rate2:
        report.append(f"✅ {model1} 重写改善率更高（{rate1:.1f}% vs {rate2:.1f}%）")
    elif rate2 > rate1:
        report.append(f"✅ {model2} 重写改善率更高（{rate2:.1f}% vs {rate1:.1f}%）")
    else:
        report.append(f"⚖️ 重写改善率相当（{rate1:.1f}% vs {rate2:.1f}%）")
    report.append("")
    
    # 综合建议
    report.append("=" * 80)
    report.append("4. 综合建议")
    report.append("=" * 80)
    
    recommendations = []
    
    # 字数控制建议
    if diff1 < diff2:
        recommendations.append(f"📝 章节生成：推荐使用 {model1}（字数控制更准确）")
    elif diff2 < diff1:
        recommendations.append(f"📝 章节生成：推荐使用 {model2}（字数控制更准确）")
    
    # 质量问题建议
    if avg1 < avg2:
        recommendations.append(f"✅ 初始质量：{model1} 生成质量更好（问题更少）")
    elif avg2 < avg1:
        recommendations.append(f"✅ 初始质量：{model2} 生成质量更好（问题更少）")
    
    # 重写效果建议
    if rate1 > rate2:
        recommendations.append(f"🔄 重写机制：推荐使用 {model1}（改善率更高）")
    elif rate2 > rate1:
        recommendations.append(f"🔄 重写机制：推荐使用 {model2}（改善率更高）")
    
    if not recommendations:
        recommendations.append("⚖️ 两个模型表现相当，可根据成本、速度等因素选择")
    
    for rec in recommendations:
        report.append(rec)
    
    report.append("")
    report.append("=" * 80)
    
    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description="LLM模型对比测试")
    parser.add_argument("--novel-title", type=str, default="对比测试小说", help="小说标题")
    parser.add_argument("--genre", type=str, default="科幻", help="小说类型")
    parser.add_argument("--theme", type=str, default="时间旅行、平行世界、记忆碎片", help="主题")
    parser.add_argument("--chapters", type=int, default=10, help="章节数（建议10章进行快速对比）")
    parser.add_argument("--words", type=int, default=2048, help="每章目标字数")
    parser.add_argument("--test-title", type=str, default="LLM对比测试", help="测试标题")
    
    args = parser.parse_args()
    
    # 测试两个模型
    models = ["gemini_3_flash", "deepseek_v3_2"]
    results = {}
    
    for model in models:
        try:
            stats = test_with_model(
                model_name=model,
                novel_title=args.novel_title,
                genre=args.genre,
                theme=args.theme,
                target_chapters=args.chapters,
                words_per_chapter=args.words,
                test_title=args.test_title
            )
            
            # 添加测试配置信息
            stats["novel_title"] = args.novel_title
            stats["genre"] = args.genre
            stats["target_chapters"] = args.chapters
            
            results[model] = stats
            
            # 保存单个模型的结果
            result_file = Path(f"novel_creation/outputs/{args.test_title}_{model}/comparison_result.json")
            result_file.parent.mkdir(parents=True, exist_ok=True)
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            
            logger.info(f"{model} 测试完成")
            
        except Exception as e:
            logger.error(f"{model} 测试失败: {e}", exc_info=True)
            results[model] = {
                "model": model,
                "error": str(e),
                "success": False
            }
    
    # 生成对比报告
    if len(results) == 2 and all(r.get("success", False) for r in results.values()):
        report = compare_results(results)
        print("\n" + report)
        
        # 保存对比报告
        report_file = Path(f"novel_creation/outputs/{args.test_title}_comparison_report.txt")
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"对比报告已保存到: {report_file}")
    else:
        logger.warning("部分测试失败，无法生成完整对比报告")


if __name__ == "__main__":
    main()
