#!/bin/bash
# 监控小说创作进度

echo "============================================================"
echo "小说创作进度监控"
echo "============================================================"
echo

# 检查进程
PID=$(ps aux | grep "create_novel_10_chapters" | grep -v grep | awk '{print $2}')
if [ -z "$PID" ]; then
    echo "❌ 创作进程未运行"
else
    echo "✅ 创作进程运行中 (PID: $PID)"
fi
echo

# 检查输出目录
OUTPUT_DIR="/root/data/AI/creator/src/novel_creation/outputs/时空旅者的日记"
if [ -d "$OUTPUT_DIR" ]; then
    echo "📁 输出目录: $OUTPUT_DIR"
    echo
    
    # 检查章节文件
    CHAPTERS_DIR="$OUTPUT_DIR/chapters"
    if [ -d "$CHAPTERS_DIR" ]; then
        CHAPTER_COUNT=$(ls -1 "$CHAPTERS_DIR"/chapter_*.txt 2>/dev/null | wc -l)
        echo "📖 已创作章节数: $CHAPTER_COUNT/10"
        
        if [ $CHAPTER_COUNT -gt 0 ]; then
            echo
            echo "【章节列表】"
            ls -lh "$CHAPTERS_DIR"/chapter_*.txt 2>/dev/null | awk '{printf "   %s: %s bytes\n", $9, $5}'
            echo
            
            # 统计总字数
            TOTAL_WORDS=0
            for file in "$CHAPTERS_DIR"/chapter_*.txt; do
                if [ -f "$file" ]; then
                    WORDS=$(wc -c < "$file" 2>/dev/null || echo 0)
                    TOTAL_WORDS=$((TOTAL_WORDS + WORDS))
                fi
            done
            echo "📊 总字数: $TOTAL_WORDS 字符"
        fi
    fi
    
    # 检查语义网格
    MESH_FILE="$OUTPUT_DIR/semantic_mesh/mesh.json"
    if [ -f "$MESH_FILE" ]; then
        MESH_SIZE=$(stat -c%s "$MESH_FILE" 2>/dev/null || echo 0)
        echo "🧠 语义网格: $MESH_SIZE bytes"
    fi
fi
echo

# 显示最新日志
echo "============================================================"
echo "最新日志（最后20行）"
echo "============================================================"
tail -20 /tmp/novel_creation_10ch.log 2>/dev/null || echo "日志文件不存在"
echo
