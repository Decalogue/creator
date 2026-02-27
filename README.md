# Creator — 创作助手

基于多智能体编排与记忆系统的**小说创作助手**，支持长篇连载、记忆增强续写与润色，并接入 **EverMemOS** 参与 [Memory Genesis Competition 2026](https://github.com/EverMind-AI/EverMemOS)。

**Live Demo**：[http://azj1.dc.huixingyun.com:58185/](http://azj1.dc.huixingyun.com:58185/)

---

## 环境与运行（Setup）


| 步骤                | 说明                                                                                                                            |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| **环境**            | Python 3.10+；推荐 `conda activate seeme`（项目虚拟环境）                                                                                |
| **后端**            | 在 `src` 目录下执行 `python api_flask.py`，默认端口 5200                                                                                 |
| **前端**            | 在 `frontend` 目录下 `pnpm install` 后 `pnpm dev`；在 `frontend/config/config.ts` 中将 `API_URL` 指向后端地址（如 `http://localhost:5200`） |
| **EverMemOS（可选）** | 设置环境变量 `EVERMEMOS_API_KEY` 启用云端记忆；`EVERMEMOS_ENABLED=1` 开启双写与检索。未配置时仅使用本地 mesh，创作与续写仍可用                                       |


更详细的命令与验证见 [docs/ROADMAP.md](docs/ROADMAP.md)「四、运行与验证」。

---

## 已实现（DONE）


| 层级 / 入口    | 说明                                                                                                                                                                            |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **编排层**    | `orchestrator/react`（ReAct）                                                                                                                                                   |
| **创作层**    | `task.novel`（ReactNovelCreator）：大纲、续写、质检⇄重写、实体提取、记忆入库                                                                                                                         |
| **记忆与上下文** | UniMem、`context`（semantic_mesh）、**EverMemOS 云记忆**（可选，参赛主记忆层）                                                                                                                  |
| **API 入口** | `api_flask` → `api/creator_handlers`、`api/memory_handlers`；流式 `POST /api/creator/stream`（create/continue）；单章全文 `GET /api/creator/chapter`；记忆 `GET/POST /api/memory/evermemos` |
| **能力扩展**   | `tools`、`skills` 聚焦创作                                                                                                                                                         |


### 创作流程与前端

- **主流程**：构思 → 记忆召回（跨章人物、伏笔、长线设定）→ 续写 → 质检 ⇄ 重写 → 实体提取 → 记忆入库；与主页流程图、创作页指挥中心一致。
- **创作页**：模式切换（大纲 / 章节 / 润色 / 对话）；章节列表可点击已写章节，单章全文 Drawer 展示；输入区与顶部模式 Segmented 一致。
- **记忆图谱**：主页「探索你的记忆系统」默认 3D；2D 力导向与 intro 节点（实体八面体、事实扁圆柱、原子笔记球体）；图例按类型上色。
- **润色与对话**：润色召回 polish 记忆、LLM 润色后 retain_polish；对话使用 kimi-k2-5，系统提示固定身份。

## 计划中（TODO）

由 **Agentic RL 推理模型** 实现：动态选 Agent、提取记忆、综合优化决策路径与记忆系统。

对应能力点：

- **动态编排**：按状态实时选 Agent，不依赖固定流程
- **自适应学习**：用强化学习优化协作模式
- **环状协作**：涌现「反复打磨」式协作
- **记忆管理**：压缩、更新、重组记忆
- **成本优化**：平衡质量与成本，学习高效策略

---

## EverMemOS 集成与参赛（Memory Genesis 2026）

Creator 以 **Content Creator Copilot** 形态参与 [Memory Genesis Competition 2026](https://github.com/EverMind-AI/EverMemOS)，使用 **EverMemOS 官方云 API** 作为项目级长期记忆层。记忆分工：**本地 mesh**（必选）管实体/关系结构，**EverMemOS** 管摘要与跨章叙事细节；可选 UniMem 图谱扩展。详见 [docs/EVERMEMOS_INTEGRATION.md](docs/EVERMEMOS_INTEGRATION.md)。

### How EverMemOS is used


| 维度       | 说明                                                                                                                                                    |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **谁写入**  | 大纲生成、章节完成、润色、对话成功后，由 `memory_handlers` 调用 `retain_plan` / `retain_chapter` / `retain_polish` / `retain_chat` 写入 EverMemOS（`api_EverMemOS.add_memory`） |
| **谁检索**  | 规划前、续写前、润色/对话前，由 `creator_handlers` 调用 `recall_from_evermemos(project_id, query, ...)`，将召回结果注入对应 prompt                                               |
| **何时调用** | 创作流程中上述步骤自动触发；续写可通过前端「续写时注入云端记忆」开关或请求体 `use_evermemos_context` 控制是否注入云端检索                                                                             |


### 参赛定位

本作品（小说创作助手）**主攻 Track 1: Agent + Memory**，即 Content Creator Copilot；在本项目中体现为**作品设定与世界观、过往章节与伏笔、角色与情节一致性**的长期记忆支撑。Track 2、Track 3 为辅助展示。

| 赛道 | 对应 | 状态 |
|------|------|------|
| **Track 1: Agent + Memory** | Content Creator Copilot（本作品：作品设定与世界观、过往章节与伏笔、角色与情节一致性） | **主攻**：本创作助手；retain/recall 全流程已接入 |
| **Track 2: Platform Plugins** | LangChain 记忆后端 / CLI 工具 | 辅：`scripts` 下 EverMemOS CLI 已实现 |
| **Track 3: OS Infrastructure** | 混合检索（EverMemOS + UniMem/图谱）、中文创作、领域记忆 | 辅：双写 + 作品内图谱 + 中文长篇 |


### 已实现能力

- **写入**：大纲生成、章节完成、润色、对话后自动写入 EverMemOS（`retain_plan` / `retain_chapter` / `retain_polish` / `retain_chat`）；可选 `use_evermemos_context` 控制续写是否注入云端记忆。
- **检索**：规划前、续写前、润色/对话前按 project 召回并注入 prompt；续写章节≥21 时启用**长程召回**；前端「云端记忆」列表拉取并展示。
- **配置**：`EVERMEMOS_API_KEY` 必填启用；`EVERMEMOS_ENABLED=1` 开启双写与检索。详见 [docs/EVERMEMOS_INTEGRATION.md](docs/EVERMEMOS_INTEGRATION.md)。

---

## Submission（Memory Genesis 2026）

*Note: A submission portal will be available soon. Stay tuned for updates.*

**Required**：GitHub 公开仓库 | README（项目介绍、环境与运行说明、**how EverMemOS is used**）| **Video Demo**（3–5 分钟，demonstrating your project and explaining the concept，covers functionality + concept）。

**Optional (Preferred)**：**[Live Demo](http://azj1.dc.huixingyun.com:58185/)** — 可访问的在线创作助手（前端 + 后端）。

**Submission Checklist**：仓库公开可访问；README 含项目概览与 setup；README 说明 EverMemOS 如何支撑方案；视频 3–5 分钟且 **covers functionality + concept**；Live Demo URL 见上。参赛策略、提交清单与视频准备见 [docs/VIDEO_DEMO.md](docs/VIDEO_DEMO.md)。

---

## 相关文档


| 文档                                                             | 说明                                    |
| -------------------------------------------------------------- | ------------------------------------- |
| 本页                                                             | 项目总览                                  |
| [docs/README.md](docs/README.md)                               | 主文档目录索引                               |
| [docs/ROADMAP.md](docs/ROADMAP.md)                             | 研发路线图与阶段规划                            |
| [docs/VIDEO_DEMO.md](docs/VIDEO_DEMO.md)                       | 参赛与视频指南（三赛道、提交要求、Video Demo、开关云端记忆对比） |
| [docs/EVERMEMOS_INTEGRATION.md](docs/EVERMEMOS_INTEGRATION.md) | Creator + EverMemOS 集成方案（配置、实现要点）     |
| [docs/VISION_AND_PLAYBOOK.md](docs/VISION_AND_PLAYBOOK.md)     | 愿景与执行清单（改进清单、检索测试）                    |
| [docs/EVERMEMOS_LEARN.md](docs/EVERMEMOS_LEARN.md)             | EverMemOS 通读摘要                        |
| [docs/因果核_三项目对比.md](docs/因果核_三项目对比.md)                         | 同大纲_开/关云端、新大纲_关云端 三项目 21–25 章对比       |
| [src/README.md](src/README.md)                                 | 模块说明与主路径/支线划分                         |
| [src/api/README.md](src/api/README.md)                         | 记忆抽象、章节/单章 API、编排事件契约                 |
| [frontend/README.md](frontend/README.md)                       | 前端页面与创作页、记忆图谱组件                       |
| [Instructions/工程原则.md](Instructions/工程原则.md) | 工程原则与规范 |
| [Instructions/项目介绍.md](Instructions/项目介绍.md) | 项目简介（精简版） |


