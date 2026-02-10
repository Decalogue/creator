#!/usr/bin/env bash
# 激活 seeme 环境并执行：获取全部云端记忆并删除。
# 用法：./scripts/run_delete_memory.sh  或  bash scripts/run_delete_memory.sh
# 仅查看不删除：DRY_RUN=1 ./scripts/run_delete_memory.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$SRC_DIR"

if command -v conda &>/dev/null; then
  eval "$(conda shell.bash hook)"
  conda activate seeme 2>/dev/null || true
fi

python delete_memory.py "$@"
