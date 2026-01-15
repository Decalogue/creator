***REMOVED***!/bin/bash
***REMOVED*** 监控测试进度的脚本

TEST_DIR="novel_creation/outputs/冒烟测试"
CHECK_INTERVAL=10  ***REMOVED*** 每10秒检查一次

echo "开始监控测试进度..."
echo "按 Ctrl+C 停止监控"
echo
echo "=" | head -c 70
echo

while true; do
    clear
    echo "测试进度监控 - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=" | head -c 70
    echo
    echo
    
    ***REMOVED*** 检查输出目录
    if [ -d "$TEST_DIR" ]; then
        echo "✅ 输出目录存在"
    else
        echo "⏳ 输出目录尚未创建"
        sleep $CHECK_INTERVAL
        continue
    fi
    
    ***REMOVED*** 检查文件
    FILES_FOUND=0
    
    if [ -f "$TEST_DIR/novel_plan.json" ]; then
        echo "✅ 大纲文件: novel_plan.json"
        PLAN_SIZE=$(stat -f%z "$TEST_DIR/novel_plan.json" 2>/dev/null || stat -c%s "$TEST_DIR/novel_plan.json" 2>/dev/null || echo "0")
        echo "   大小: $PLAN_SIZE bytes"
        FILES_FOUND=$((FILES_FOUND + 1))
    else
        echo "⏳ 大纲文件: 尚未生成"
    fi
    
    if [ -d "$TEST_DIR/chapters" ]; then
        CHAPTER_COUNT=$(ls -1 "$TEST_DIR/chapters"/*.txt 2>/dev/null | wc -l)
        if [ "$CHAPTER_COUNT" -gt 0 ]; then
            echo "✅ 章节文件: $CHAPTER_COUNT 个"
            FILES_FOUND=$((FILES_FOUND + 1))
            ls -1 "$TEST_DIR/chapters"/*.txt 2>/dev/null | head -3 | while read file; do
                SIZE=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
                echo "   - $(basename $file): $SIZE bytes"
            done
        else
            echo "⏳ 章节文件: 尚未生成"
        fi
    fi
    
    if [ -f "$TEST_DIR/metadata.json" ]; then
        echo "✅ 元数据文件: metadata.json"
        FILES_FOUND=$((FILES_FOUND + 1))
    else
        echo "⏳ 元数据文件: 尚未生成"
    fi
    
    if [ -f "$TEST_DIR/冒烟测试_完整版.txt" ]; then
        echo "✅ 完整小说文件: 已生成"
        FILES_FOUND=$((FILES_FOUND + 1))
    else
        echo "⏳ 完整小说文件: 尚未生成"
    fi
    
    echo
    echo "=" | head -c 70
    echo
    echo "已生成文件数: $FILES_FOUND / 4"
    echo
    echo "下次检查: ${CHECK_INTERVAL}秒后 (按 Ctrl+C 停止)"
    
    ***REMOVED*** 如果所有文件都生成了，退出
    if [ "$FILES_FOUND" -ge 4 ]; then
        echo
        echo "🎉 测试完成！所有文件已生成"
        break
    fi
    
    sleep $CHECK_INTERVAL
done
