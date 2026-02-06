"""
EverMemOS 记忆操作命令行工具（参赛 Track 2 加分：CLI Tool）。

用法（需在 src 目录或设置 PYTHONPATH=src）：
  python -m scripts.evermemos_cli get    --user-id 完美之墙
  python -m scripts.evermemos_cli search --user-id 完美之墙 --query "前文 情节"
  python -m scripts.evermemos_cli add    --user-id 完美之墙 --content "一段记忆内容"
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

# 保证可导入 src 内模块
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def _ensure_src_cwd():
    """若当前目录不是 src，则建议用户 cd 到 src 再执行。"""
    cwd = Path.cwd()
    if _ROOT.name != "src":
        # 若 scripts 的 parent 不是 src（例如在 repo 根目录运行）
        pass
    if cwd != _ROOT and _ROOT not in (cwd, cwd.parent):
        print("建议在项目 src 目录下执行: cd src && python -m scripts.evermemos_cli ...", file=sys.stderr)


def cmd_get(user_id: str) -> int:
    from api_EverMemOS import get_memory, is_available
    if not is_available():
        print("EverMemOS 未配置（请设置 EVERMEMOS_API_KEY）", file=sys.stderr)
        return 1
    memories = get_memory(user_id)
    if not memories:
        print("无记忆")
        return 0
    for m in memories:
        content = getattr(m, "content", None) or getattr(m, "memory_content", None)
        if isinstance(m, dict):
            content = m.get("content") or m.get("memory_content")
        mid = getattr(m, "memory_id", None) or (m.get("memory_id") if isinstance(m, dict) else "")
        print(f"[{mid}] {str(content or '')[:200]}")
    return 0


def cmd_search(user_id: str, query: str, top_k: int) -> int:
    from api_EverMemOS import search_memory, is_available
    if not is_available():
        print("EverMemOS 未配置（请设置 EVERMEMOS_API_KEY）", file=sys.stderr)
        return 1
    memories = search_memory(query, user_id=user_id)
    if not memories:
        print("无结果")
        return 0
    for m in memories[:top_k]:
        content = getattr(m, "content", None) or getattr(m, "memory_content", None)
        if isinstance(m, dict):
            content = m.get("content") or m.get("memory_content")
        print(str(content or "")[:400])
        print("---")
    return 0


def cmd_add(user_id: str, content: str, group_id: str | None) -> int:
    from api_EverMemOS import add_memory, is_available
    if not is_available():
        print("EverMemOS 未配置（请设置 EVERMEMOS_API_KEY）", file=sys.stderr)
        return 1
    if not content or not content.strip():
        print("请提供 --content 或通过管道传入内容", file=sys.stderr)
        return 1
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    msg_id = f"cli_{user_id}_{ts.replace(':', '').replace('-', '')[:15]}"
    message = {
        "message_id": msg_id,
        "create_time": ts,
        "sender": user_id,
        "content": content.strip()[:8000],
    }
    if group_id:
        message["group_id"] = group_id
    add_memory([message])
    print("已写入 1 条记忆")
    return 0


def main() -> int:
    _ensure_src_cwd()
    parser = argparse.ArgumentParser(
        description="EverMemOS 记忆操作 CLI（Memory Genesis 2026 Track 2）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    def _add_user_id(p):
        p.add_argument("--user-id", default="完美之墙", help="user_id")

    p_get = sub.add_parser("get", help="按 user_id 拉取记忆列表")
    _add_user_id(p_get)

    p_search = sub.add_parser("search", help="按 user_id 与 query 检索")
    _add_user_id(p_search)
    p_search.add_argument("--query", required=True, help="自然语言检索词")
    p_search.add_argument("--top-k", type=int, default=10, help="最多返回条数")

    p_add = sub.add_parser("add", help="写入一条记忆")
    _add_user_id(p_add)
    p_add.add_argument("--content", default="", help="记忆内容（也可从 stdin 读）")
    p_add.add_argument("--group-id", default=None, help="可选 group_id")

    args = parser.parse_args()
    user_id = getattr(args, "user_id", None) or "完美之墙"
    if args.cmd == "get":
        return cmd_get(user_id)
    if args.cmd == "search":
        return cmd_search(user_id, args.query, getattr(args, "top_k", 10))
    if args.cmd == "add":
        content = getattr(args, "content", "") or ""
        if not content and not sys.stdin.isatty():
            content = sys.stdin.read()
        return cmd_add(user_id, content or "", getattr(args, "group_id", None))
    return 0


if __name__ == "__main__":
    sys.exit(main())
