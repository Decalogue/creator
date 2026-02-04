***REMOVED*** 小说任务可选脚本

本目录为**非主路径**脚本，主路径为：`api_flask` → `api/creator_handlers` → `task.novel.ReactNovelCreator`（大纲/续写由前端 + `/api/creator/stream` 触发）。

| 脚本 | 说明 |
|------|------|
| `create_100_chapters_novel.py` | 一次性创作 100 章（长跑），需在 `src` 下执行 |
| `run_create_100_chapters.sh` | 后台启动上述创作 |
| `continue_n_chapters.py` | 对指定项目续写 N 章（测试/批量），默认 完美之墙_第二卷 10 章 |
| `monitor_*.sh` | 测试进度监控（字数/实体/重写等），需在 `src` 下或项目根执行 |
| `task/novel/full_novel_quality_agent.py` | 全本质量检查与优化（CLI），见 `task/novel/docs/全本质量检查Agent使用说明.md` |
| `task/novel/test_quality_optimizations.py` | 质量优化功能测试（字数/节奏/悬念等） |

运行前请激活环境：`conda activate seeme`，并在 **`src`** 目录下执行，例如：

```bash
cd src
***REMOVED*** 100 章创作
python scripts/novel/create_100_chapters_novel.py
bash scripts/novel/run_create_100_chapters.sh   ***REMOVED*** 后台运行

***REMOVED*** 全本质量检查、质量优化测试（模块在 task/novel）
python -m task.novel.full_novel_quality_agent --novel_dir task/novel/outputs/完美之墙
python -m task.novel.test_quality_optimizations --chapters 5

***REMOVED*** 测试监控（可选）
bash scripts/novel/monitor_optimization_test.sh
```
