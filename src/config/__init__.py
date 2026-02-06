import os
from pathlib import Path

# 在 seeme 环境下加载 src/.env，使 EVERMEMOS_API_KEY 等生效
try:
    from dotenv import load_dotenv
    _env_file = Path(__file__).resolve().parent.parent / ".env"
    if _env_file.exists():
        load_dotenv(_env_file)
except Exception:
    pass

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
]
