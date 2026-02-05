#!/bin/bash
# 监控实体类型配额分配效果（需在 src 目录下执行，或从项目根执行时路径已自动切到 src）

LOG_FILE="/tmp/test_50chapters_entity_quota_optimization.log"
OUTPUT_DIR="task/novel/outputs/50章实体配额优化测试"
SRCDIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$SRCDIR" || exit 1

echo "📊 实体配额分配监控"
echo "=================="
echo ""

if [ -f "$LOG_FILE" ]; then
    echo "📝 最新日志（最后15行）:"
    echo "---"
    tail -n 15 "$LOG_FILE"
    echo "---"
    echo ""
else
    echo "⚠️  日志文件不存在: $LOG_FILE"
    echo ""
fi

if [ -d "$OUTPUT_DIR" ]; then
    CHAPTERS_DIR="$OUTPUT_DIR/chapters"
    if [ -d "$CHAPTERS_DIR" ]; then
        CHAPTER_COUNT=$(ls -1 "$CHAPTERS_DIR"/chapter_*_meta.json 2>/dev/null | wc -l)
        echo "✅ 已生成章节数: $CHAPTER_COUNT / 50"
        echo ""

        if [ "$CHAPTER_COUNT" -gt 0 ]; then
            echo "📊 最近3章实体类型分布:"
            python3 -c "
import re
from pathlib import Path

chapters_dir = Path('$CHAPTERS_DIR')
chapter_files = sorted(chapters_dir.glob('chapter_*_meta.json'))

for chapter_num in range(max(1, len(chapter_files)-2), len(chapter_files)+1):
    prompt_file = chapters_dir / f'chapter_{chapter_num:03d}_prompt.txt'
    if prompt_file.exists():
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        char_count = setting_count = symbol_count = 0
        if '角色:' in content:
            char_match = re.search(r'角色:\n(.*?)(?=\n\n请确保|\n地点/设定:|\n物品/符号:|\Z)', content, re.DOTALL)
            if char_match:
                char_count = len([l for l in char_match.group(1).split('\n') if l.strip().startswith('  -')])
        if '地点/设定:' in content:
            setting_match = re.search(r'地点/设定:\n(.*?)(?=\n\n请确保|\n物品/符号:|\Z)', content, re.DOTALL)
            if setting_match:
                setting_count = len([l for l in setting_match.group(1).split('\n') if l.strip().startswith('  -')])
        if '物品/符号:' in content:
            symbol_match = re.search(r'物品/符号:\n(.*?)(?=\n\n请确保|\Z)', content, re.DOTALL)
            if symbol_match:
                symbol_count = len([l for l in symbol_match.group(1).split('\n') if l.strip().startswith('  -')])
        total = char_count + setting_count + symbol_count
        print(f'  第{chapter_num}章: 角色{char_count} / 地点{setting_count} / 物品{symbol_count} (总计{total})')
" 2>/dev/null || echo "  解析中..."
            echo ""
        fi
    fi
else
    echo "⚠️  输出目录不存在: $OUTPUT_DIR"
    echo ""
fi

echo "💡 提示: 使用 'tail -f $LOG_FILE' 实时查看日志"
