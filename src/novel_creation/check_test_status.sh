***REMOVED***!/bin/bash
***REMOVED*** 检查测试状态的脚本

TEST_DIR="novel_creation/outputs/冒烟测试"

echo "=" | head -c 70
echo
echo "测试状态检查"
echo "=" | head -c 70
echo
echo

***REMOVED*** 检查输出目录
if [ ! -d "$TEST_DIR" ]; then
    echo "⏳ 状态: 测试尚未开始或正在初始化"
    echo "   输出目录不存在: $TEST_DIR"
    exit 0
fi

echo "✅ 输出目录已创建: $TEST_DIR"
echo

***REMOVED*** 检查大纲文件
if [ -f "$TEST_DIR/novel_plan.json" ]; then
    echo "✅ 大纲文件已生成"
    PLAN_SIZE=$(stat -f%z "$TEST_DIR/novel_plan.json" 2>/dev/null || stat -c%s "$TEST_DIR/novel_plan.json" 2>/dev/null || echo "0")
    echo "   文件大小: $PLAN_SIZE bytes"
else
    echo "⏳ 大纲文件尚未生成"
fi

***REMOVED*** 检查章节文件
if [ -d "$TEST_DIR/chapters" ]; then
    CHAPTER_COUNT=$(ls -1 "$TEST_DIR/chapters"/*.txt 2>/dev/null | wc -l)
    if [ "$CHAPTER_COUNT" -gt 0 ]; then
        echo "✅ 章节文件已生成: $CHAPTER_COUNT 个"
        ls -1 "$TEST_DIR/chapters"/*.txt 2>/dev/null | head -5 | while read file; do
            SIZE=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
            echo "   - $(basename $file): $SIZE bytes"
        done
    else
        echo "⏳ 章节文件尚未生成"
    fi
else
    echo "⏳ 章节目录尚未创建"
fi

***REMOVED*** 检查元数据文件
if [ -f "$TEST_DIR/metadata.json" ]; then
    echo "✅ 元数据文件已生成"
    echo "   内容摘要:"
    if command -v python3 &> /dev/null; then
        python3 -c "
import json
import sys
try:
    with open('$TEST_DIR/metadata.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f\"   总章节数: {data.get('total_chapters', 0)}\")
    print(f\"   总字数: {data.get('total_words', 0):,}\")
    if 'creative_context' in data:
        cc = data['creative_context']
        print(f\"   实体数: {cc.get('entities_count', 0)}\")
        print(f\"   关系数: {cc.get('relations_count', 0)}\")
except Exception as e:
    print(f\"   解析失败: {e}\")
" 2>/dev/null
    fi
else
    echo "⏳ 元数据文件尚未生成"
fi

***REMOVED*** 检查完整小说文件
if [ -f "$TEST_DIR/冒烟测试_完整版.txt" ]; then
    echo "✅ 完整小说文件已生成"
    SIZE=$(stat -f%z "$TEST_DIR/冒烟测试_完整版.txt" 2>/dev/null || stat -c%s "$TEST_DIR/冒烟测试_完整版.txt" 2>/dev/null || echo "0")
    echo "   文件大小: $SIZE bytes"
else
    echo "⏳ 完整小说文件尚未生成"
fi

echo
echo "=" | head -c 70
echo
echo "检查完成"
echo "=" | head -c 70
echo
