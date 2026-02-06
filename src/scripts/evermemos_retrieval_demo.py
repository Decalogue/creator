"""
EverMemOS 几类检索测试与记录（跨章人物、伏笔、长线设定）。

与创作流程整合：前端记忆面板「跑检索测试」按钮会调同一逻辑并写同一日志。
本脚本供命令行使用（需在 src 目录或 PYTHONPATH 含 src）：
  python -m scripts.evermemos_retrieval_demo 玄灵科学家 --top-k 8
  python -m scripts.evermemos_retrieval_demo 玄灵科学家 --log ./my_log.jsonl
"""

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="跑几类 EverMemOS 检索（跨章人物、伏笔、长线设定）并追加到 JSONL 日志。"
    )
    parser.add_argument("project_id", help="项目 id（如 玄灵科学家）")
    parser.add_argument("--top-k", type=int, default=8, help="每类 query 最多返回条数，默认 8")
    parser.add_argument("--log", type=Path, default=None, help="日志路径，默认使用 memory_handlers 中的默认路径")
    args = parser.parse_args()

    from api.memory_handlers import (
        DEFAULT_RETRIEVAL_DEMO_LOG_PATH,
        run_retrieval_demo,
    )
    from api_EverMemOS import is_available

    if not is_available():
        print("EverMemOS 未配置（请设置 EVERMEMOS_API_KEY）", file=sys.stderr)
        return 1

    log_path = args.log or DEFAULT_RETRIEVAL_DEMO_LOG_PATH
    entries = run_retrieval_demo(args.project_id, top_k=args.top_k, log_path=log_path)

    for e in entries:
        print(f"--- {e['query_type']} ---")
        print(f"  query: {e['query']}")
        print(f"  result_count: {e['result_count']}")
        for i, ex in enumerate(e.get("excerpts") or [], 1):
            print(f"  [{i}] {ex}")
        print()
    print(f"已追加到 {log_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
