***REMOVED***!/bin/bash
***REMOVED*** 监控测试进度脚本

LOG_FILE="/tmp/test_50chapters_word_control_optimization.log"
OUTPUT_DIR="novel_creation/outputs/50章字数控制优化测试"

echo "📊 测试进度监控"
echo "=================="
echo ""

***REMOVED*** 检查日志文件
if [ -f "$LOG_FILE" ]; then
    echo "📝 最新日志（最后20行）:"
    echo "---"
    tail -n 20 "$LOG_FILE"
    echo "---"
    echo ""
else
    echo "⚠️  日志文件不存在: $LOG_FILE"
    echo ""
fi

***REMOVED*** 检查输出目录
if [ -d "$OUTPUT_DIR" ]; then
    CHAPTERS_DIR="$OUTPUT_DIR/chapters"
    if [ -d "$CHAPTERS_DIR" ]; then
        ***REMOVED*** 统计已生成的章节
        CHAPTER_COUNT=$(ls -1 "$CHAPTERS_DIR"/chapter_*_meta.json 2>/dev/null | wc -l)
        echo "✅ 已生成章节数: $CHAPTER_COUNT / 50"
        echo ""
        
        ***REMOVED*** 统计字数（使用Python脚本）
        if [ $CHAPTER_COUNT -gt 0 ]; then
            echo "📊 字数统计:"
            cd "$(dirname "$0")/.." || exit
            python3 -c "
import json
from pathlib import Path

chapters_dir = Path('$CHAPTERS_DIR')
chapter_files = sorted(chapters_dir.glob('chapter_*_meta.json'))

if chapter_files:
    word_stats = []
    for f in chapter_files:
        try:
            with open(f, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
                actual = data.get('actual_words', 0)
                target = data.get('target_words', 2048)
                diff_percent = data.get('word_diff_percent', 0)
                word_stats.append({
                    'actual': actual,
                    'target': target,
                    'diff_percent': diff_percent
                })
        except:
            pass
    
    if word_stats:
        avg_words = sum(s['actual'] for s in word_stats) / len(word_stats)
        avg_diff = sum(abs(s['diff_percent']) for s in word_stats) / len(word_stats)
        within_target = sum(1 for s in word_stats if abs(s['diff_percent']) <= 10)
        within_limit = sum(1 for s in word_stats if s['actual'] <= 3000)
        
        print(f'  平均字数: {avg_words:.0f} 字 (目标: 2048字)')
        print(f'  平均偏差: {avg_diff:.1f}%')
        print(f'  目标±10%内: {within_target}/{len(word_stats)} ({within_target/len(word_stats)*100:.1f}%)')
        print(f'  3000字上限内: {within_limit}/{len(word_stats)} ({within_limit/len(word_stats)*100:.1f}%)')
        
        ***REMOVED*** 显示最近5章的字数
        if len(word_stats) >= 5:
            print(f'')
            print(f'  最近5章字数:')
            for i, s in enumerate(word_stats[-5:], 1):
                status = '✅' if abs(s['diff_percent']) <= 10 else '⚠️'
                print(f'    {status} 第{len(word_stats)-5+i}章: {s[\"actual\"]}字 (偏差: {s[\"diff_percent\"]:+.1f}%)')
"
            echo ""
        fi
    else
        echo "⚠️  章节目录不存在或为空"
        echo ""
    fi
else
    echo "⚠️  输出目录不存在: $OUTPUT_DIR"
    echo ""
fi

***REMOVED*** 检查是否有错误
if [ -f "$LOG_FILE" ]; then
    ERROR_COUNT=$(grep -i "error\|exception\|failed" "$LOG_FILE" | wc -l)
    if [ $ERROR_COUNT -gt 0 ]; then
        echo "⚠️  检测到 $ERROR_COUNT 个错误/异常"
        echo "   最近错误:"
        grep -i "error\|exception\|failed" "$LOG_FILE" | tail -n 3
        echo ""
    fi
fi

echo "💡 提示: 使用 'tail -f $LOG_FILE' 实时查看日志"
