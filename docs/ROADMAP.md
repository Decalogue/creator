# Creator 研发路线图

> **目标**：按顶级产品打造；持续去冗余、高复用/可扩展/清晰。主线：**模块优化、去冗余、通用沉淀**。当前阶段：**Memory Genesis 2026 参赛交付** 与产品巩固并行。

**索引**：[Instructions/工程原则.md](../Instructions/工程原则.md) | [src/README.md](../src/README.md) | [docs/README.md](README.md)（主文档索引） | [docs/VIDEO_DEMO.md](VIDEO_DEMO.md)（参赛与视频）

---

## 一、当前状态

**主路径（已打通）**：`api_flask` → `api/creator_handlers`、`api/memory_handlers` → **task.novel**（react_novel_creator）+ **context**（semantic_mesh）。创作 API（run/stream create·continue、单章全文 chapter）、记忆/图谱 API（含 EverMemOS）、前端、编排可观测（orchestration_events + stream）均已打通。编排层 **orchestrator/react**（ReAct）；工具层 **tools**、**skills** 聚焦创作。

**创作流程与前端**：主流程 构思→记忆召回→续写→质检⇄重写→实体提取→记忆入库；创作页模式（大纲/章节/润色/对话）、章节列表与单章全文 Drawer、记忆图谱 2D/3D 与 intro 节点；支线 **orchestrator** 等标实验，未接入主产品。

**近期精简（已完成）**：config 合并、Qdrant → `local_storage/qdrant`；**orchestrator**、**task/novel** 结构稳定；workflow、**puppeteer** 已移除；主文档已集中至 **docs/**（ROADMAP、VIDEO_DEMO、EVERMEMOS_INTEGRATION、VISION_AND_PLAYBOOK、EVERMEMOS_LEARN、因果核_三项目对比等），子模块文档仍保留在各自目录。

**EverMemOS 参赛（Memory Genesis 2026）**：主攻 Track 1 Content Creator Copilot。retain/recall 全流程已接入（规划·续写·润色·对话）；长程召回（章节≥21）、云端记忆列表、CLI、双写与「续写时注入云端记忆」开关可配置。提交要求与三赛道策略见 [VIDEO_DEMO.md](VIDEO_DEMO.md)。

**进度**：P0/P1 ✅；P2 项目持久化基本具备，DAG/RAG/图增强待做；P3 回归与可观测未系统化。**E 参赛交付** 进行中（见下）。

---

## 二、参赛提交前待办（对齐官方 Submission Checklist）

**当前状态**：必选项已就绪。Video Demo 见 [creator-1080p.mp4](creator-1080p.mp4)。

按 [Memory Genesis 2026 How to Submit](https://github.com/EverMind-AI/EverMemOS) 与 [VIDEO_DEMO.md](VIDEO_DEMO.md) 执行，提交前逐项勾选：

| 必选 | 项 | 说明 |
|------|-----|------|
| ✅ | **GitHub 仓库** | 仓库公开可访问，代码完整可复现 |
| ✅ | **README.md** | 含项目概览、**环境与运行（Setup）**、**How EverMemOS is used** 表格；详见根目录 README。 |
| ✅ | **Video Demo（3–5 分钟）** | 已就绪：[creator-1080p.mp4](creator-1080p.mp4)。Covers functionality + concept；详见 [VIDEO_DEMO.md](VIDEO_DEMO.md) 结构与自检。 |
| ✅ | **Live Demo** | 链接已写入 README（根目录首段下与 Submission 小节）。 |

**推荐顺序**：README（概览 + setup + How EverMemOS is used）已就绪 → 录 Video Demo（按 VIDEO_DEMO 七～十一节）；Live Demo 链接已写入 README。

---

## 三、阶段规划

| 阶段 | 任务 | 要点 |
|------|------|------|
| **A 去冗余** | A.1 主路径/支线文档 ✅ | 稳定主路径描述，支线标实验（见 src/README.md） |
| | A.2 LLM 收敛 ✅ | 梳理调用点，明确 LLM 门面（见 src/llm/README.md） |
| | A.3 创作记忆抽象 ✅ | 接口：按 project 读/写 mesh，可选 recall/retain（见 api/memory_handlers 文档头） |
| | A.4 配置收敛 ✅ | 创作配置与 project_id 收敛到 config（project_dir, normalize_project_id, list_projects；见 config/README.md） |
| **B 通用沉淀** | B.1 LLM 门面 ✅ | 统一输入输出，配置驱动模型（get_default_novel_llm、call_llm_for_novel；见 src/llm/README.md） |
| | B.2 记忆抽象实现 ✅ | mesh 读写 + UniMem 适配器（见 api/README.md、api/memory_handlers 文档头） |
| | B.3 工具/技能统一 ✅ | 注册+发现+调用（tools）；skills 为工具之上封装（SOP、按需注入）；见 tools/README、skills/README |
| | B.4 编排事件契约 ✅ | step 类型（CREATOR_STEPS）与 payload 稳定契约；见 api/orchestration_events、api/README.md |
| **C 能力增强** | C.1 DAG（可选） | 主路径可切换 ReAct / DAG |
| | C.2 RAG | 续写/润色前检索已有章节+mesh |
| | C.3 图增强 | 时序边、来源等，与 UniMem 对齐 |
| | C.4 项目持久化 | 列表、加载/切换，与前端联动 |
| **D 持续** | D.1 回归 | CI 回归创作 pipeline + memory API |
| | D.2 模型路由与缓存 | 按任务选模型、检索与上下文缓存 |
| | D.3 可观测与告警 | 耗时、Token、失败率与慢请求 |
| **E 参赛交付** | E.1 提交清单 | 见上文**二、参赛提交前待办**；GitHub 公开、README（概览+setup+EverMemOS 角色）、Video Demo（3–5 min，functionality+concept）、可选 Live Demo |
| | E.2 视频与自检 | 结构、开关云端记忆对比、提交前自检见 [VIDEO_DEMO.md](VIDEO_DEMO.md) |

**顺序**：A～B 已完成；**E 优先**（提交截止前）；C、D 按需。每步可交付、可验证；动主路径时同步测试与文档（见工程原则自检）。

---

## 四、运行与验证

- **环境**：`conda activate seeme`，在 `src` 下 `python api_flask.py`（默认 5200）。
- **验证**：`cd src && conda run -n seeme python -c "from api_flask import _CREATOR_MEMORY_AVAILABLE; print('Creator/Memory:', _CREATOR_MEMORY_AVAILABLE)"`。
- **集成测试**：`cd src && python -m pytest api/test_creator_integration.py -v`。
- **前端**：`frontend/config/config.ts` 中 `API_URL` 指向后端。

**依赖**：UniMem（Redis/Neo4j/Qdrant）可选；EverMemOS 需 `EVERMEMOS_API_KEY` 启用；DAG 选型阶段 C 再定。

---

工程原则与自检 → **[Instructions/工程原则.md](../Instructions/工程原则.md)**；模块与主路径 → **[src/README.md](../src/README.md)**；参赛提交 → **[VIDEO_DEMO.md](VIDEO_DEMO.md)**、**[EVERMEMOS_INTEGRATION.md](EVERMEMOS_INTEGRATION.md)**。
