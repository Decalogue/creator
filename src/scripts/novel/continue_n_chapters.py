#!/usr/bin/env python3
"""
对指定项目续写 N 章（用于测试或批量续写）。
需在 src 目录下执行：python scripts/novel/continue_n_chapters.py [project_id] [n]
默认：完美之墙_第二卷，10 章。
"""

import sys
import logging
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    project_id = sys.argv[1] if len(sys.argv) > 1 else "完美之墙_第二卷"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    from api.creator_handlers import run_continue

    logger.info("续写项目: %s，目标章数: %d", project_id, n)
    for i in range(n):
        code, msg, extra = run_continue("continue", "", project_id=project_id)
        if code != 0:
            logger.error("第 %d 章失败: %s", i + 1, msg)
            sys.exit(1)
        ch = (extra or {}).get("chapter_number", "?")
        logger.info("第 %d 章完成: chapter_%s", i + 1, str(ch).zfill(3))
    logger.info("全部 %d 章续写完成。", n)


if __name__ == "__main__":
    main()
