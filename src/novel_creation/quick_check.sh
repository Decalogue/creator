***REMOVED***!/bin/bash
***REMOVED*** 快速检查测试进度

TEST_DIR="novel_creation/outputs/中篇小说测试"

echo "=" | head -c 60
echo
echo "快速进度检查"
echo "=" | head -c 60
echo
echo

if [ ! -d "$TEST_DIR" ]; then
    echo "⏳ 测试尚未开始"
    exit 0
fi

***REMOVED*** 检查章节数
if [ -d "$TEST_DIR/chapters" ]; then
    CHAPTER_COUNT=$(ls -1 "$TEST_DIR/chapters"/*.txt 2>/dev/null | wc -l)
    echo "📑 已完成章节: $CHAPTER_COUNT / 10"
    
    if [ "$CHAPTER_COUNT" -gt 0 ]; then
        echo ""
        echo "最近完成的章节:"
        ls -1t "$TEST_DIR/chapters"/*.txt 2>/dev/null | head -3 | while read file; do
            SIZE=$(stat -c%s "$file" 2>/dev/null || echo "0")
            WORDS=$(wc -w < "$file" 2>/dev/null || echo "0")
            echo "  - $(basename $file): ${SIZE} bytes, ~${WORDS} 字"
        done
    fi
    
    if [ "$CHAPTER_COUNT" -ge 10 ]; then
        echo ""
        echo "🎉 所有章节已完成！"
    else
        REMAINING=$((10 - CHAPTER_COUNT))
        ESTIMATED=$((REMAINING * 2))
        echo ""
        echo "⏳ 剩余章节: $REMAINING 章"
        echo "⏱️  预计剩余时间: $ESTIMATED 分钟"
    fi
else
    echo "⏳ 章节目录尚未创建"
fi

***REMOVED*** 检查完整文件
if [ -f "$TEST_DIR/中篇小说测试_完整版.txt" ]; then
    echo ""
    echo "✅ 完整小说文件已生成"
    echo "🎉 测试完成！"
fi

echo
echo "=" | head -c 60
echo
