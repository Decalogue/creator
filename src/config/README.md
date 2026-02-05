# config — 按创作领域划分的配置包

按创作领域分为五类，每类独立子包，便于扩展与复用。

## 全局配置（包根 `__init__.py`）

`frontend_url`、`backend_url`、`qdrant_url` 以及 ARK 相关常量（`ARK_BASE_URL`、`ARK_API_KEY`、`MODEL_NAME`）定义在包根，供 API/前端等使用，例如：

```python
from config import backend_url, ARK_BASE_URL
```

## 领域子包

| 子包 | 说明 | 状态 |
|------|------|------|
| **novel** | 小说创作 | 已实现 defaults / prompts |
| **article** | 论文、学术文章 | 预留 |
| **document** | 学习笔记、博客、公众号等文档 | 预留 |
| **script** | 剧本、影视/短剧脚本 | 预留 |
| **video** | 视频脚本、电商短视频等 | 预留 |

各子目录见对应 `README.md`。新增领域时在此增加子包并补全 `__init__.py` 与 README 即可。
