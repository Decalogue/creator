#!/bin/bash
# 快速查看章节实体信息的脚本

NOVEL_TITLE="${1:-20章长篇小说测试}"
CHAPTER_NUM="${2:-2}"

OUTPUT_DIR="novel_creation/outputs/${NOVEL_TITLE}/chapters"

if [ ! -d "$OUTPUT_DIR" ]; then
    echo "❌ 输出目录不存在: $OUTPUT_DIR"
    exit 1
fi

CHAPTER_PADDED=$(printf "%03d" $CHAPTER_NUM)
ENTITIES_FILE="${OUTPUT_DIR}/chapter_${CHAPTER_PADDED}_entities.txt"
PROMPT_FILE="${OUTPUT_DIR}/chapter_${CHAPTER_PADDED}_prompt.txt"
META_FILE="${OUTPUT_DIR}/chapter_${CHAPTER_PADDED}_meta.json"

echo "=" | head -c 70 && echo
echo "查看第 ${CHAPTER_NUM} 章的实体信息"
echo "=" | head -c 70 && echo
echo ""

# 检查文件是否存在
if [ ! -f "$ENTITIES_FILE" ]; then
    echo "⚠️  实体信息文件不存在: $ENTITIES_FILE"
    echo "   提示：第 1 章没有实体信息（因为没有前面的章节）"
    echo ""
fi

# 显示实体信息
if [ -f "$ENTITIES_FILE" ]; then
    echo "📋 实体信息："
    echo "---"
    cat "$ENTITIES_FILE"
    echo ""
    echo "---"
    echo ""
fi

# 显示提示词文件信息
if [ -f "$PROMPT_FILE" ]; then
    PROMPT_SIZE=$(stat -c%s "$PROMPT_FILE" 2>/dev/null || echo "0")
    echo "📝 完整提示词文件: $PROMPT_FILE (${PROMPT_SIZE} bytes)"
    echo "   使用以下命令查看完整提示词："
    echo "   cat $PROMPT_FILE"
    echo ""
fi

# 显示元数据信息
if [ -f "$META_FILE" ]; then
    echo "📊 元数据文件: $META_FILE"
    if command -v jq &> /dev/null; then
        echo "   字数信息："
        jq -r '.metadata | "   目标字数: \(.target_words) 字\n   实际字数: \(.actual_words) 字\n   差异: \(.word_diff) 字 (\(.word_diff_percent)%)"' "$META_FILE" 2>/dev/null || echo "   无法解析"
    fi
    echo ""
fi

# 列出所有可用的章节
echo "📚 所有已完成的章节："
ls -1 "$OUTPUT_DIR"/*_entities.txt 2>/dev/null | sed 's/.*chapter_\([0-9]*\)_entities.txt/\1/' | sort -n | while read num; do
    echo "   第 ${num} 章"
done

echo ""
echo "💡 使用方式："
echo "   ./view_entities.sh [小说标题] [章节号]"
echo "   示例: ./view_entities.sh \"20章长篇小说测试\" 2"
