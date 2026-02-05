import os

frontend_url = os.environ.get("CREATOR_FRONTEND_URL", "http://localhost:5002")
backend_url = os.environ.get("CREATOR_BACKEND_URL", "http://localhost:5200")
qdrant_url = os.environ.get("CREATOR_QDRANT_URL", "http://localhost:6333/dashboard")

ARK_BASE_URL = os.environ.get("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
ARK_API_KEY = os.environ.get("ARK_API_KEY", "")

OSS_ACCESS_KEY_ID = os.environ.get("OSS_ACCESS_KEY_ID", "")
OSS_ACCESS_KEY_SECRET = os.environ.get("OSS_ACCESS_KEY_SECRET", "")

__all__ = [
    "frontend_url",
    "backend_url",
    "qdrant_url",
    "ARK_BASE_URL",
    "ARK_API_KEY",
    "OSS_ACCESS_KEY_ID",
    "OSS_ACCESS_KEY_SECRET",
]
