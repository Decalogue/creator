"""
清空该用户全部云端记忆（EverMemOS）。使用服务端「按 user_id 批量删除」接口。

用法（需在 seeme 环境下，且从 src 目录运行）：
  cd src && conda run -n seeme python delete_memory.py
  或先激活环境：conda activate seeme && cd src && python delete_memory.py

可选环境变量：DRY_RUN=1 仅获取并打印条数，不执行删除。
"""
import os
import sys

# 确保以 src 为工作目录，便于导入 config、api_EverMemOS
if __name__ == "__main__":
    _src_dir = os.path.dirname(os.path.abspath(__file__))
    if os.getcwd() != _src_dir and _src_dir not in sys.path:
        sys.path.insert(0, _src_dir)
    os.chdir(_src_dir)


def get_all_and_delete(dry_run: bool = False) -> int:
    """获取该用户当前页记忆条数，并调用「按 user_id 批量删除」清空全部。返回删除前条数（可能仅为首页）。"""
    from api_EverMemOS import (
        CREATOR_USER_ID,
        is_available,
        get_memory,
        delete_all_memories_for_user,
    )
    if not is_available():
        print("EverMemOS 未配置或不可用（检查 EVERMEMOS_API_KEY、EVERMEMOS_ENABLED）")
        return 0
    raw = get_memory(user_id=CREATOR_USER_ID)
    n = len(raw or [])
    print(f"当前获取到 {n} 条云端记忆（user_id={CREATOR_USER_ID}，可能分页仅首页）")
    if n == 0:
        print("已无记忆。")
        return 0
    if dry_run:
        print("DRY_RUN=1，未执行删除。")
        return 0
    deleted = delete_all_memories_for_user(CREATOR_USER_ID)
    print(f"已发起批量删除（本页约 {deleted} 条，服务端会清空该用户全部）。")
    remain = len(get_memory(user_id=CREATOR_USER_ID) or [])
    print(f"再次拉取剩余：{remain} 条。")
    return deleted


if __name__ == "__main__":
    dry = os.environ.get("DRY_RUN", "").strip() in ("1", "true", "yes")
    if dry:
        print("--- DRY_RUN 模式：仅获取并打印，不删除 ---")
    get_all_and_delete(dry_run=dry)
