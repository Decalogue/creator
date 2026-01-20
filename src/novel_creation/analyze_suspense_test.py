#!/usr/bin/env python3
"""
分析《遗忘图书馆》测试结果
"""
import json
import os
from pathlib import Path

def analyze_test_results():
    """分析测试结果"""
    # 自动查找metadata.json文件
    outputs_dir = "outputs"
    metadata_path = None
    
    # 先尝试"遗忘图书馆"目录
    if os.path.exists(f"{outputs_dir}/遗忘图书馆/metadata.json"):
        metadata_path = f"{outputs_dir}/遗忘图书馆/metadata.json"
    else:
        # 查找包含"遗忘图书馆"完整版txt的目录
        for dirname in os.listdir(outputs_dir):
            dirpath = os.path.join(outputs_dir, dirname)
            if os.path.isdir(dirpath):
                if os.path.exists(os.path.join(dirpath, "metadata.json")):
                    # 检查是否包含"遗忘图书馆"
                    txt_files = [f for f in os.listdir(dirpath) if f.endswith("_完整版.txt")]
                    if any("遗忘图书馆" in f for f in txt_files):
                        metadata_path = os.path.join(dirpath, "metadata.json")
                        break
                # 如果没找到，尝试最新的目录
                if metadata_path is None and os.path.exists(os.path.join(dirpath, "metadata.json")):
                    metadata_path = os.path.join(dirpath, "metadata.json")
    
    if not metadata_path or not os.path.exists(metadata_path):
        print("❌ 测试尚未完成，metadata.json 文件不存在")
        return
    
    output_dir = os.path.dirname(metadata_path)
    
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    print("=" * 80)
    print("《遗忘图书馆》测试结果分析")
    print("=" * 80)
    print()
    
    # 基本信息
    print(f"📖 小说信息:")
    print(f"  标题: {metadata['title']}")
    print(f"  类型: {metadata['genre']}")
    print(f"  主题: {metadata['theme']}")
    print(f"  总章节: {metadata['total_chapters']}章")
    print(f"  总字数: {metadata['total_words']:,}字")
    print(f"  平均每章: {metadata['total_words'] // metadata['total_chapters']}字")
    print()
    
    # 质量评分
    periodic_checks = metadata.get('periodic_quality_checks', [])
    if periodic_checks:
        print(f"📈 阶段性质量评分:")
        for check in periodic_checks:
            scores = check.get('scores', {})
            print(f"  {check.get('chapter_range', '未知')}:")
            print(f"    综合评分: {scores.get('overall', 0):.2f}")
            print(f"    连贯性: {scores.get('coherence', 0):.2f}")
            print(f"    人物: {scores.get('character_consistency', 0):.2f}")
            print(f"    节奏: {scores.get('plot_rhythm', 0):.2f}")
            print(f"    世界观: {scores.get('worldview_consistency', 0):.2f}")
            suspense_score = scores.get('suspense', 0)
            if suspense_score >= 0.6:
                print(f"    悬念: {suspense_score:.2f} ✅ (优秀)")
            elif suspense_score >= 0.4:
                print(f"    悬念: {suspense_score:.2f} ⚠️ (良好)")
            else:
                print(f"    悬念: {suspense_score:.2f} ❌ (偏低)")
            print()
    
    # 质量问题统计
    quality_tracker = metadata.get('quality_tracker', {})
    chapter_history = quality_tracker.get('chapter_quality_history', [])
    
    if chapter_history:
        total_issues = sum(c.get('quality_issues', 0) for c in chapter_history)
        avg_issues = total_issues / len(chapter_history) if chapter_history else 0
        
        print(f"📊 质量问题统计:")
        print(f"  总问题数: {total_issues}个")
        print(f"  平均每章: {avg_issues:.1f}个问题")
        print(f"  严重问题章节: {metadata.get('quality_check', {}).get('high_severity_chapters', 0)}章")
        print()
        
        # 统计重写情况
        rewritten_chapters = []
        for chapter_info in chapter_history:
            chapter_num = chapter_info['chapter_number']
            meta_file = os.path.join(output_dir, "chapters", f"chapter_{chapter_num:03d}_meta.json")
            if os.path.exists(meta_file):
                with open(meta_file, 'r', encoding='utf-8') as f:
                    chapter_meta = json.load(f)
                    if chapter_meta.get('metadata', {}).get('rewritten', False):
                        original_issues = chapter_info.get('quality_issues', 0)
                        rewritten_issues = chapter_meta.get('metadata', {}).get('quality_check_after_rewrite', {}).get('total_issues', 0)
                        rewritten_chapters.append({
                            'chapter': chapter_num,
                            'original_issues': original_issues,
                            'rewritten_issues': rewritten_issues,
                            'improved': rewritten_issues < original_issues
                        })
        
        if rewritten_chapters:
            print(f"🔄 重写机制统计:")
            print(f"  重写章节数: {len(rewritten_chapters)}章 ({len(rewritten_chapters)/len(chapter_history)*100:.1f}%)")
            improved = sum(1 for c in rewritten_chapters if c['improved'])
            unchanged = sum(1 for c in rewritten_chapters if not c['improved'] and c['rewritten_issues'] == c['original_issues'])
            worsened = sum(1 for c in rewritten_chapters if c['rewritten_issues'] > c['original_issues'])
            print(f"  改善: {improved}章 ({improved/len(rewritten_chapters)*100:.1f}%)")
            print(f"  无变化: {unchanged}章 ({unchanged/len(rewritten_chapters)*100:.1f}%)")
            print(f"  恶化: {worsened}章 ({worsened/len(rewritten_chapters)*100:.1f}%)")
            print()
    
    # 字数控制
    word_deviations = []
    for c in chapter_history:
        target = c.get('target_words', 2048)
        actual = c.get('word_count', 0)
        if target > 0:
            deviation = (actual - target) / target * 100
            word_deviations.append(deviation)
    
    if word_deviations:
        avg_deviation = sum(word_deviations) / len(word_deviations)
        max_deviation = max(abs(d) for d in word_deviations)
        print(f"📝 字数控制:")
        print(f"  平均偏差: {avg_deviation:+.1f}%")
        print(f"  最大偏差: {max_deviation:.1f}%")
        print()
    
    # 关键发现
    print("=" * 80)
    print("关键发现:")
    print("=" * 80)
    
    if periodic_checks:
        latest_check = periodic_checks[-1]
        suspense_score = latest_check.get('scores', {}).get('suspense', 0)
        overall_score = latest_check.get('scores', {}).get('overall', 0)
        
        if suspense_score >= 0.6:
            print(f"✅ 悬念得分优秀 ({suspense_score:.2f})，悬疑主题确实提升了悬念表现")
        elif suspense_score >= 0.4:
            print(f"⚠️  悬念得分良好 ({suspense_score:.2f})，比治愈向主题有所提升，但仍需优化")
        else:
            print(f"❌ 悬念得分偏低 ({suspense_score:.2f})，需要进一步优化悬念机制")
        
        if overall_score >= 0.85:
            print(f"✅ 综合评分优秀 ({overall_score:.2f})，达到优质标准")
        elif overall_score >= 0.75:
            print(f"⚠️  综合评分良好 ({overall_score:.2f})，接近优质标准")
        else:
            print(f"❌ 综合评分偏低 ({overall_score:.2f})，需要进一步优化")
    
    print("=" * 80)

if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    analyze_test_results()
