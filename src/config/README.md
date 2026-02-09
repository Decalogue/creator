# config — 按创作领域划分的配置包

按创作领域分为五类，每类独立子包，便于扩展与复用。创作配置与 project_id 收敛到本包入口（A.4）。

## 全局配置（包根 `__init__.py`）

`frontend_url`、`backend_url`、`qdrant_url` 以及 ARK 相关常量定义在包根。创作路径与 project_id 单一入口：`CREATOR_NOVEL_OUTPUTS`、`project_dir(project_id)`、`normalize_project_id(project_id)`、`list_projects()`。`normalize_project_id` 会去掉「（当前）」等后缀，保证与创作/续写及记忆 API 使用的 project_id 一致。

```python
from config import backend_url, project_dir, normalize_project_id, list_projects
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
