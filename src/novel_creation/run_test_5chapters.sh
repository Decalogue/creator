***REMOVED***!/bin/bash
***REMOVED*** 运行5章测试脚本（激活 seeme 环境）

***REMOVED*** 初始化 conda（如果需要）
if [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi

***REMOVED*** 尝试激活 seeme 环境
if command -v conda &> /dev/null; then
    eval "$(conda shell.bash hook)"
    conda activate seeme 2>/dev/null || {
        echo "⚠️  警告: 无法激活 seeme 环境，使用当前环境"
    }
fi

echo "当前环境: ${CONDA_DEFAULT_ENV:-base}"
echo ""

***REMOVED*** 切换到项目目录
cd /root/data/AI/creator/src

***REMOVED*** 运行测试
echo "开始运行5章测试..."
python novel_creation/test_20_chapters.py \
    --title "5章测试_实体修复" \
    --genre "玄幻" \
    --theme "修仙与飞升" \
    --words 3000 \
    --chapters 5
