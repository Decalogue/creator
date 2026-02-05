# Creator 研发路线图

> **目标**：按顶级产品打造；持续去冗余、高复用/可扩展/清晰。主线：**模块优化、去冗余、通用沉淀**。

**索引**：[Instructions/工程原则.md](../Instructions/工程原则.md) | [src/README.md](../src/README.md) | [docs/article.md](article.md)

---

## 一、当前状态

**主路径（已打通）**：`api_flask` → `api/creator_handlers`、`api/memory_handlers` → **task.novel**（react_novel_creator）+ **context**（semantic_mesh）。创作 API（run/stream）、记忆/图谱 API、前端、编排可观测（orchestration_events + stream）均已打通。编排层 **orchestrator/react**（ReAct）；工具层 **tools**（search_tool_docs、read_tool_doc）、**skills**（创作相关、无内置示例）。

**近期精简（已完成）**：config 合并进 config 包、五类领域；Qdrant → `local_storage/qdrant`；**orchestrator** 新增、react 迁入；**task** 新增、novel_creation → task/novel；workflow 已删；tools/skills 仅保留创作相关。支线：**puppeteer** 标实验，未接入主产品。

**进度**：P0/P1 ✅；P2 项目持久化基本具备，DAG/RAG/图增强待做；P3 回归与可观测未系统化。

---

## 二、阶段规划

| 阶段 | 任务 | 要点 |
|------|------|------|
| **A 去冗余** | A.1 主路径/支线文档 | 稳定主路径描述，支线标实验 |
| | A.2 LLM 收敛 | 梳理调用点，明确 LLM 门面 |
| | A.3 创作记忆抽象 | 接口：按 project 读/写 mesh，可选 recall/retain |
| | A.4 配置收敛 | 创作配置与 project_id/session 收敛到少量入口 |
| **B 通用沉淀** | B.1 LLM 门面 | 统一输入输出，配置驱动模型 |
| | B.2 记忆抽象实现 | mesh 读写 + UniMem 适配器 |
| | B.3 工具/技能统一 | 注册+发现+调用；skills 为工具之上封装 |
| | B.4 编排事件契约 | step 类型与 payload 稳定契约 |
| **C 能力增强** | C.1 DAG（可选） | 主路径可切换 ReAct / DAG |
| | C.2 RAG | 续写/润色前检索已有章节+mesh |
| | C.3 图增强 | 时序边、来源等，与 UniMem 对齐 |
| | C.4 项目持久化 | 列表、加载/切换，与前端联动 |
| **D 持续** | D.1 回归 | CI 回归创作 pipeline + memory API |
| | D.2 模型路由与缓存 | 按任务选模型、检索与上下文缓存 |
| | D.3 可观测与告警 | 耗时、Token、失败率与慢请求 |

**顺序**：A.1 → A.2 → A.3 → A.4，再 B.1/B.2；C、D 按需。每步可交付、可验证；动主路径时同步测试与文档（见工程原则自检）。

---

## 三、运行与验证

- **环境**：`conda activate seeme`，在 `src` 下 `python api_flask.py`（默认 5200）。
- **验证**：`cd src && conda run -n seeme python -c "from api_flask import _CREATOR_MEMORY_AVAILABLE; print('Creator/Memory:', _CREATOR_MEMORY_AVAILABLE)"`。
- **集成测试**：`cd src && python -m pytest api/test_creator_integration.py -v`。
- **前端**：`frontend/config/config.ts` 中 `API_URL` 指向后端。

**依赖**：UniMem（Redis/Neo4j/Qdrant）可选；puppeteer 标实验；DAG 选型阶段 C 再定。

---

工程原则与自检 → **[Instructions/工程原则.md](../Instructions/工程原则.md)**；模块与主路径 → **[src/README.md](../src/README.md)**。
