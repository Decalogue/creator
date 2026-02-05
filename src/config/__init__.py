***REMOVED*** 配置子包：按创作领域分五类，见各子目录 README
***REMOVED***
***REMOVED*** - config.novel    — 小说创作（已实现 defaults/prompts）
***REMOVED*** - config.article  — 论文/学术文章（预留）
***REMOVED*** - config.document — 学习笔记、博客、公众号等文档（预留）
***REMOVED*** - config.script   — 剧本/影视脚本（预留）
***REMOVED*** - config.video    — 视频脚本、电商短视频等（预留）
***REMOVED***
***REMOVED*** 全局 URL / API 配置（原 src/config.py）
frontend_url = "http://azj1.dc.huixingyun.com:58185"  ***REMOVED*** 自定义端口：5002 公网映射端口：58185
backend_url = "http://azj1.dc.huixingyun.com:53115"  ***REMOVED*** 自定义端口：5200 公网映射端口：53115
qdrant_url = "http://azj1.dc.huixingyun.com:50499/dashboard"  ***REMOVED*** 自定义端口：6333 公网映射端口：50499

ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
ARK_API_KEY = "93a67648-c2cd-4a51-99ba-c51114b537ee"
MODEL_NAME = "ep-20251209150604-gxb42"

OSS_ACCESS_KEY_ID = "LTAI5tGnX6CUm2TJkHEkkJwU"
OSS_ACCESS_KEY_SECRET = "GjtFbtjByylIffYwk19zveabsjw4Xa"

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
