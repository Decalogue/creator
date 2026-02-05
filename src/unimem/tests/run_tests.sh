#!/bin/bash
# UniMem 测试运行脚本
# 自动激活 myswift 环境并运行测试

set -e

echo "=========================================="
echo "UniMem 测试运行脚本"
echo "=========================================="

# 检查是否在 myswift 环境中
if [ "$CONDA_DEFAULT_ENV" != "myswift" ]; then
    echo "正在激活 myswift 环境..."
    
    # 尝试激活 myswift 环境
    # 注意：这需要在 conda 已初始化的 shell 中运行
    if command -v conda &> /dev/null; then
        # 初始化 conda（如果还没有）
        eval "$(conda shell.bash hook)"
        conda activate myswift
        
        if [ "$CONDA_DEFAULT_ENV" != "myswift" ]; then
            echo "错误：无法激活 myswift 环境"
            echo "请手动运行: conda activate myswift"
            exit 1
        fi
    else
        echo "错误：未找到 conda 命令"
        echo "请手动激活 myswift 环境后运行测试"
        exit 1
    fi
fi

echo "当前环境: $CONDA_DEFAULT_ENV"
echo "Python 路径: $(which python)"
echo ""

# 切换到项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "项目根目录: $PROJECT_ROOT"
echo ""

# 运行测试
echo "开始运行测试..."
echo ""

# 使用 pytest
if command -v pytest &> /dev/null; then
    echo "使用 pytest 运行测试..."
    python -m pytest "$SCRIPT_DIR" -v --tb=short
else
    echo "使用 unittest 运行测试..."
    python -m unittest discover -s "$SCRIPT_DIR" -p "test_*.py" -v
fi

echo ""
echo "=========================================="
echo "测试完成"
echo "=========================================="

