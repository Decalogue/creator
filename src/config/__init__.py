***REMOVED*** 敏感信息（密钥）仅从环境变量读取，不得写入仓库。参见 .env.example 或文档。
import os
from pathlib import Path

***REMOVED*** 加载 src/.env 到 os.environ，使 os.environ.get 能读到 .env 中的变量（需安装 python-dotenv）
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_path)
    except ImportError:
        pass  ***REMOVED*** 未安装 python-dotenv 时仅使用系统环境变量

frontend_url = os.environ.get("CREATOR_FRONTEND_URL", "http://localhost:5002")
backend_url = os.environ.get("CREATOR_BACKEND_URL", "http://localhost:5200")
qdrant_url = os.environ.get("CREATOR_QDRANT_URL", "http://localhost:6333/dashboard")

ARK_BASE_URL = os.environ.get("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
ARK_API_KEY = os.environ.get("ARK_API_KEY", "")
MODEL_NAME = os.environ.get("ARK_MODEL_NAME", "")

OSS_ACCESS_KEY_ID = os.environ.get("OSS_ACCESS_KEY_ID", "")
OSS_ACCESS_KEY_SECRET = os.environ.get("OSS_ACCESS_KEY_SECRET", "")

__all__ = [
    "frontend_url",
    "backend_url",
    "qdrant_url",
    "ARK_BASE_URL",
    "ARK_API_KEY",
    "MODEL_NAME",
    "OSS_ACCESS_KEY_ID",
    "OSS_ACCESS_KEY_SECRET",
]
