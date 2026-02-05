#!/bin/bash
# 在 seeme 环境中后台运行 100 章小说创作（需在 src 目录下执行）

source /opt/miniconda/etc/profile.d/conda.sh 2>/dev/null || true
conda activate seeme

SRC_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$SRC_DIR"

nohup python3 scripts/novel/create_100_chapters_novel.py > /tmp/novel_creation_完美之墙.log 2>&1 &
echo "创作进程已启动，PID: $!"
echo "日志: /tmp/novel_creation_完美之墙.log"
echo "查看: tail -f /tmp/novel_creation_完美之墙.log"
