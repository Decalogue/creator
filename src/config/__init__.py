import os
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
    _env_file = Path(__file__).resolve().parent.parent / ".env"
    if _env_file.exists():
        load_dotenv(_env_file)
except Exception:
    pass

# 创作输出根目录与 project 路径（A.4 配置收敛：project_id 与创作路径单一入口）
_SRC_DIR = Path(__file__).resolve().parent.parent
CREATOR_NOVEL_OUTPUTS = _SRC_DIR / "task" / "novel" / "outputs"


def project_dir(project_id: str) -> Path:
    """按 project_id 返回该项目的输出目录（outputs/<project_id>/）。"""
    pid = normalize_project_id(project_id)
    return CREATOR_NOVEL_OUTPUTS / pid


def normalize_project_id(project_id: Optional[str], default: str = "完美之墙") -> str:
    """将请求中的 project_id 规范为非空字符串，缺省为 default；去掉「（当前）」等后缀，与创作/续写写入记忆时一致。"""
    raw = (project_id or default).strip() or default
    for suffix in ("（当前）", " (当前)", "(当前)"):
        if raw.endswith(suffix):
            raw = raw[: -len(suffix)].strip()
            break
    return raw or default


def list_projects() -> list:
    """返回已创作小说列表：outputs 下存在 novel_plan.json 的目录名（project_id）。"""
    if not CREATOR_NOVEL_OUTPUTS.exists():
        return []
    out = []
    for p in CREATOR_NOVEL_OUTPUTS.iterdir():
        if p.is_dir() and (p / "novel_plan.json").exists():
            out.append(p.name)
    return sorted(out)


# 前端 / 后端 / 外部服务 URL
frontend_url = os.environ.get("CREATOR_FRONTEND_URL", "http://localhost:5002")
backend_url = os.environ.get("CREATOR_BACKEND_URL", "http://localhost:5200")
qdrant_url = os.environ.get("CREATOR_QDRANT_URL", "http://localhost:6333/dashboard")

# LLM：Ark、Moonshot
ARK_BASE_URL = os.environ.get("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
ARK_API_KEY = os.environ.get("ARK_API_KEY", "")
MOONSHOT_BASE_URL = os.environ.get("MOONSHOT_BASE_URL", "https://api.moonshot.cn/v1")
MOONSHOT_API_KEY = os.environ.get("MOONSHOT_API_KEY", "")

# EverMemOS 云记忆
EVERMEMOS_API_KEY = os.environ.get("EVERMEMOS_API_KEY", "")
EVERMEMOS_ENABLED = os.environ.get("EVERMEMOS_ENABLED", "1").strip().lower() in ("1", "true", "yes", "")

# Flask 应用
FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "0").strip().lower() in ("1", "true", "yes")
FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "you-will-never-guess")
FLASK_HOST = os.environ.get("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.environ.get("FLASK_PORT", "5200"))

# /api/chat：默认模型、最近对话轮数
CHAT_DEFAULT_MODEL = os.environ.get("CHAT_DEFAULT_MODEL", "DeepSeek-v3-2")
CHAT_MESSAGES_MAX_HISTORY = int(os.environ.get("CHAT_MESSAGES_MAX_HISTORY", "10"))

# 小说创作默认模型（create/continue/polish/chat 使用的 LLM）
NOVEL_LLM_MODEL = os.environ.get("NOVEL_LLM_MODEL", "kimi-k2-5").strip()

# 创作任务与 SSE
CREATOR_TASKS_MAX = int(os.environ.get("CREATOR_TASKS_MAX", "200"))
SSE_KEEPALIVE_SEC = int(os.environ.get("SSE_KEEPALIVE_SEC", "30"))

__all__ = [
    "frontend_url",
    "backend_url",
    "qdrant_url",
    "ARK_BASE_URL",
    "ARK_API_KEY",
    "MOONSHOT_BASE_URL",
    "MOONSHOT_API_KEY",
    "EVERMEMOS_API_KEY",
    "EVERMEMOS_ENABLED",
    "FLASK_DEBUG",
    "FLASK_SECRET_KEY",
    "FLASK_HOST",
    "FLASK_PORT",
    "CHAT_DEFAULT_MODEL",
    "CHAT_MESSAGES_MAX_HISTORY",
    "NOVEL_LLM_MODEL",
    "CREATOR_TASKS_MAX",
    "SSE_KEEPALIVE_SEC",
    "CREATOR_NOVEL_OUTPUTS",
    "project_dir",
    "normalize_project_id",
    "list_projects",
]
