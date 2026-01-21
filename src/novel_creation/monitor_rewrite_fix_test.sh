#!/bin/bash
# 监控重写机制修复验证测试进度

TEST_LOG="/tmp/test_rewrite_fix_verification.log"
OUTPUT_DIR="novel_creation/outputs/重写机制修复验证"

echo "=========================================="
echo "重写机制修复验证测试监控"
echo "=========================================="
echo ""

# 检查测试是否在运行
if pgrep -f "test_quality_optimizations.py.*重写机制修复验证" > /dev/null; then
    echo "✅ 测试正在运行中..."
else
    echo "⚠️  测试未运行或已完成"
fi

echo ""
echo "📊 测试日志（最后20行）："
echo "----------------------------------------"
tail -20 "$TEST_LOG" 2>/dev/null || echo "日志文件不存在"
echo ""

# 检查输出目录
if [ -d "$OUTPUT_DIR" ]; then
    echo "📁 输出目录: $OUTPUT_DIR"
    
    # 统计生成的章节数
    chapter_count=$(find "$OUTPUT_DIR/chapters" -name "chapter_*.txt" 2>/dev/null | wc -l)
    echo "   已生成章节: $chapter_count 章"
    
    # 检查重写情况
    if [ -d "$OUTPUT_DIR/chapters" ]; then
        rewritten_count=$(find "$OUTPUT_DIR/chapters" -name "*_meta.json" -exec grep -l '"rewritten":\s*true' {} \; 2>/dev/null | wc -l)
        if [ "$rewritten_count" -gt 0 ]; then
            echo "   重写章节: $rewritten_count 章"
        fi
    fi
    
    # 检查质量检查结果
    if [ -f "$OUTPUT_DIR/metadata.json" ]; then
        echo ""
        echo "📈 质量统计（从metadata.json）："
        python3 -c "
import json
import sys
import os

metadata_path = '$OUTPUT_DIR/metadata.json'
if os.path.exists(metadata_path):
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        quality_tracker = metadata.get('quality_tracker', {})
        chapter_history = quality_tracker.get('chapter_quality_history', [])
        
        if chapter_history:
            total_issues = sum(c.get('quality_issues', 0) for c in chapter_history)
            avg_issues = total_issues / len(chapter_history)
            
            # 字数统计
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
                
                print(f'   平均质量问题数: {avg_issues:.2f}个/章')
                print(f'   平均字数偏差: {avg_deviation:+.1f}%')
                print(f'   最大字数偏差: {max_deviation:.1f}%')
            
            # 重写统计（详细版 - 修复后）
            rewritten_chapters = []
            zero_issue_rewritten = 0  # 问题数为0但被重写的章节数
            
            for i in range(1, len(chapter_history) + 1):
                meta_file = f'$OUTPUT_DIR/chapters/chapter_{i:03d}_meta.json'
                if os.path.exists(meta_file):
                    try:
                        with open(meta_file, 'r', encoding='utf-8') as f:
                            chapter_meta = json.load(f)
                            if chapter_meta.get('metadata', {}).get('rewritten', False):
                                original_issues = chapter_meta.get('quality_check', {}).get('total_issues', 0)
                                rewritten_issues = chapter_meta.get('metadata', {}).get('quality_check_after_rewrite', {}).get('total_issues', 0)
                                rewrite_rounds = chapter_meta.get('metadata', {}).get('rewrite_rounds', 1)
                                
                                # 检查是否问题数为0但被重写（这是bug）
                                if original_issues == 0:
                                    zero_issue_rewritten += 1
                                
                                if rewritten_issues < original_issues:
                                    rewritten_chapters.append({'improved': True, 'rounds': rewrite_rounds, 'original': original_issues, 'final': rewritten_issues})
                                elif rewritten_issues == original_issues:
                                    rewritten_chapters.append({'improved': False, 'unchanged': True, 'rounds': rewrite_rounds, 'issues': original_issues})
                                else:
                                    rewritten_chapters.append({'improved': False, 'worsened': True, 'rounds': rewrite_rounds, 'original': original_issues, 'final': rewritten_issues})
                    except:
                        pass
            
            if rewritten_chapters:
                improved = [c for c in rewritten_chapters if c.get('improved')]
                unchanged = [c for c in rewritten_chapters if c.get('unchanged')]
                worsened = [c for c in rewritten_chapters if c.get('worsened')]
                
                total_rewritten = len(rewritten_chapters)
                print(f'')
                print(f'   🔄 重写机制效果（修复后）:')
                print(f'      重写章节: {total_rewritten}章')
                
                # 🔴 关键指标：问题数为0但被重写的章节数（应该是0）
                if zero_issue_rewritten > 0:
                    print(f'      ⚠️  问题数为0但被重写: {zero_issue_rewritten}章（这是bug，应该为0）')
                else:
                    print(f'      ✅ 问题数为0但被重写: 0章（修复成功）')
                
                if total_rewritten > 0:
                    print(f'      改善: {len(improved)}章 ({len(improved)/total_rewritten*100:.1f}%)')
                    print(f'      无变化: {len(unchanged)}章 ({len(unchanged)/total_rewritten*100:.1f}%)')
                    print(f'      恶化: {len(worsened)}章 ({len(worsened)/total_rewritten*100:.1f}%)')
                    
                    # 显示改善详情
                    if improved:
                        avg_improvement = sum(c['original'] - c['final'] for c in improved) / len(improved)
                        print(f'      平均改善: {avg_improvement:.1f}个问题/章')
                        print(f'      平均重写轮次: {sum(c.get(\"rounds\", 1) for c in improved) / len(improved):.1f}轮')
                    
                    # 显示恶化详情
                    if worsened:
                        avg_worsening = sum(c['final'] - c['original'] for c in worsened) / len(worsened)
                        print(f'      平均恶化: {avg_worsening:.1f}个问题/章')
                        print(f'      ⚠️  注意：恶化章节应该被质量保护机制回退')
    except Exception as e:
        print(f'   无法读取质量统计: {e}')
" 2>/dev/null || echo "   无法读取质量统计"
    fi
else
    echo "⚠️  输出目录不存在"
fi

echo ""
echo "=========================================="
echo "使用以下命令查看完整日志:"
echo "tail -f $TEST_LOG"
echo "=========================================="
