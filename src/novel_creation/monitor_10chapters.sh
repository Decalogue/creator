***REMOVED***!/bin/bash
***REMOVED*** 监控10章测试的脚本

TEST_DIR="novel_creation/outputs/中篇小说测试"
CHECK_INTERVAL=30  ***REMOVED*** 每30秒检查一次

echo "开始监控10章中篇小说测试..."
echo "按 Ctrl+C 停止监控"
echo
echo "=" | head -c 70
echo

while true; do
    clear
    echo "10章测试进度监控 - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=" | head -c 70
    echo
    echo
    
    ***REMOVED*** 检查输出目录
    if [ ! -d "$TEST_DIR" ]; then
        echo "⏳ 状态: 测试尚未开始或正在初始化"
        echo "   输出目录不存在: $TEST_DIR"
        sleep $CHECK_INTERVAL
        continue
    fi
    
    echo "✅ 输出目录存在"
    echo
    
    ***REMOVED*** 检查大纲文件
    if [ -f "$TEST_DIR/novel_plan.json" ]; then
        echo "✅ 大纲文件: 已生成"
    else
        echo "⏳ 大纲文件: 尚未生成"
    fi
    
    ***REMOVED*** 检查章节文件
    if [ -d "$TEST_DIR/chapters" ]; then
        CHAPTER_COUNT=$(ls -1 "$TEST_DIR/chapters"/*.txt 2>/dev/null | wc -l)
        if [ "$CHAPTER_COUNT" -gt 0 ]; then
            echo "✅ 章节文件: $CHAPTER_COUNT / 10 章"
            
            ***REMOVED*** 显示最近3个章节
            echo "   最近完成的章节:"
            ls -1t "$TEST_DIR/chapters"/*.txt 2>/dev/null | head -3 | while read file; do
                SIZE=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
                echo "   - $(basename $file): $SIZE bytes"
            done
        else
            echo "⏳ 章节文件: 尚未生成"
        fi
    fi
    
    ***REMOVED*** 检查元数据文件
    if [ -f "$TEST_DIR/metadata.json" ]; then
        echo "✅ 元数据文件: 已生成"
        if command -v python3 &> /dev/null; then
            python3 -c "
import json
try:
    with open('$TEST_DIR/metadata.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f\"   总章节数: {data.get('total_chapters', 0)} / 10\")
    print(f\"   总字数: {data.get('total_words', 0):,} 字\")
except:
    pass
" 2>/dev/null
        fi
    else
        echo "⏳ 元数据文件: 尚未生成"
    fi
    
    ***REMOVED*** 检查完整小说文件
    if [ -f "$TEST_DIR/中篇小说测试_完整版.txt" ]; then
        echo "✅ 完整小说文件: 已生成"
        echo "🎉 测试完成！"
        break
    else
        echo "⏳ 完整小说文件: 尚未生成"
    fi
    
    echo
    echo "=" | head -c 70
    echo
    echo "下次检查: ${CHECK_INTERVAL}秒后 (按 Ctrl+C 停止)"
    
    sleep $CHECK_INTERVAL
done
