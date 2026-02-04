***REMOVED*** Creator 项目研发路线图

> **产品与架构目标**：按**顶级产品**打造 Creator；**持续去冗余、提升整体性能**；架构保持**高复用性、高扩展性、高清晰度**。  
> 以**模块优化、去冗余、通用沉淀**为主线，逐步收敛架构并沉淀可复用能力。

**文档索引**：工程原则 → [Instructions/工程原则.md](../Instructions/工程原则.md)；主路径与模块 → [src/README.md](../src/README.md)；调研论文 → [docs/article.md](article.md)。

---

***REMOVED******REMOVED*** 一、当前状态

***REMOVED******REMOVED******REMOVED*** 1.1 主路径（已打通）

| 环节 | 说明 |
|------|------|
| **创作 API** | `POST /api/creator/run`、`POST /api/creator/stream`（SSE），mode=create/continue/polish/chat；任务轮询 `GET /api/creator/task/<task_id>` |
| **记忆 & 图谱 API** | `GET /api/memory/entities`、`graph`、`recents`、`note/<id>`；数据来自 semantic_mesh + 可选 UniMem |
| **后端入口** | `api_flask.py` → `api/creator_handlers`、`api/memory_handlers` → `novel_creation/react_novel_creator`、`context`（semantic_mesh） |
| **前端** | 创作页 create/continue/polish 用 `/api/creator/run` 或 `/stream`，chat 用 `/api/chat`；记忆/图谱用 memory API，节点点击 `note/:id` |
| **编排可观测** | `api/orchestration_events` + `/api/creator/stream` 推送 step_start/step_done/step_error；前端编排区随真实步骤更新 |

***REMOVED******REMOVED******REMOVED*** 1.2 支线（有代码未接入主产品）

- **workflow/**：NovelWorkflow、CreativeOrchestrator（Puppeteer 编排）
- **puppeteer/**：多智能体/GraphReasoning，未接入 `/api/creator`

***REMOVED******REMOVED******REMOVED*** 1.3 进度小结

| 阶段 | 状态 |
|------|------|
| P0 闭环打通 | ✅ 已完成 |
| P1 编排可观测 & UniMem 贯通 | ✅ 已完成 |
| P2 DAG / RAG / 图增强 / 项目持久化 | 3.4 项目持久化基本具备；3.1/3.2/3.3 待做 |
| P3 回归、模型路由、可观测 | 零散测试与日志，未系统化 |

---

***REMOVED******REMOVED*** 二、主线：模块优化与通用沉淀

**目标**：去冗余、收敛支线、通用部分模块化沉淀。

| 类别 | 现状 | 优化方向 |
|------|------|----------|
| **编排** | 主路径 ReAct + workflow/puppeteer 未接入 | 主路径唯一；支线标实验或收敛为可选 DAG |
| **记忆** | semantic_mesh、UniMem、context 多源 | 统一「创作记忆」抽象（mesh + 可选 UniMem），按存储/检索/图分层 |
| **LLM** | api_flask、novel_creation、unimem 多处调用 | 统一 LLM 门面，配置驱动模型 |
| **工具/技能** | tools/、skills/ 重叠 | 统一注册+发现，skills 为工具之上封装；以 CodeAct 模式为主流方向 |
| **配置** | 环境变量与 config 散落 | 创作配置与上下文（project_id、session）收敛到少量入口 |
| **文档/示例** | unimem/docs、examples 多而杂 | 每模块一个 README；示例最小可运行+主路径相关 |

**沉淀目标**：LLM 门面、创作记忆抽象、编排事件契约、工具/技能统一层、项目与运行配置集中。详见下表阶段 B。

---

***REMOVED******REMOVED*** 三、阶段规划

***REMOVED******REMOVED******REMOVED*** 阶段 A：去冗余与边界清晰（优先）

**目标**：主路径唯一化、支线标清、删除或归档明显冗余。

| 序号 | 任务 | 说明 |
|------|------|------|
| **A.1** | **主路径与支线文档固化** | 在 README/ROADMAP 中稳定「主路径 = api → creator_handlers + memory_handlers → react_novel_creator + semantic_mesh」；workflow、puppeteer 标为「实验/研究用」，不承诺接入主产品 |
| **A.2** | **LLM 调用收敛** | 梳理 api_flask、novel_creation、unimem 中 LLM 使用点；引入或明确「LLM 门面」单一入口，逐步替换直接调用各模型实现 |
| **A.3** | **创作记忆抽象** | 定义「创作记忆」接口（按 project 读 mesh、写 mesh、可选 recall/retain）；memory_handlers 与 react_novel_creator 通过该接口访问，内部再对接 mesh.json 与 UniMem |
| **A.4** | **配置与上下文收敛** | 创作相关配置（outputs 路径、project 默认名、UniMem 开关等）集中到 config 或环境变量文档；上下文结构（project_id、session 等）在 api 与 novel_creation 间统一 |

***REMOVED******REMOVED******REMOVED*** 阶段 B：通用模块沉淀

**目标**：把可复用部分拆成清晰接口/子包，便于单测与复用。

| 序号 | 任务 | 说明 |
|------|------|------|
| **B.1** | **LLM 门面模块** | 独立包或子模块：输入（messages、stream、模型名/策略）、输出统一；配置驱动模型选择，便于后续「按任务选模型」（P3） |
| **B.2** | **记忆抽象实现** | 实现阶段 A.3 的创作记忆接口：mesh 读写实现 + UniMem 适配器；主路径只依赖接口 |
| **B.3** | **工具/技能统一层** | 统一「工具注册 + 发现 + 调用」；skills 作为工具组合或高阶封装，避免与 tools 重复实现 |
| **B.4** | **编排事件契约** | 将 step 类型、payload 字段写成稳定契约（文档或类型），前端与后端共遵；避免后续扩展时破坏兼容 |

***REMOVED******REMOVED******REMOVED*** 阶段 C：能力增强（在精简架构上）

**目标**：在冗余减少、边界清晰后，按需做 DAG、RAG、图增强等。

| 序号 | 任务 | 说明 |
|------|------|------|
| **C.1** | **DAG 编排（可选）** | 将创作流程抽象为 DAG（自研小图或 LangGraph）；主路径可切换「单 ReAct」或「DAG」；workflow/puppeteer 可收敛为 DAG 的一种实现或废弃 |
| **C.2** | **RAG over 已写内容** | 续写/润色前，对已有章节 + semantic_mesh 做检索并注入上下文；依赖创作记忆抽象与 LLM 门面 |
| **C.3** | **记忆图增强** | 时序边、来源、置信度等；与 UniMem AtomLink/图能力对齐，不新增重复图存储 |
| **C.4** | **项目级持久化完善** | 项目列表、章节列表、加载/切换已有项目；已在主路径部分具备，查漏补缺与前端联动 |

***REMOVED******REMOVED******REMOVED*** 阶段 D：稳定性与成本（持续）

| 序号 | 任务 | 说明 |
|------|------|------|
| **D.1** | **质量基线 & 回归** | 固定 1～2 个标杆流程；CI 回归创作 pipeline + memory API；主路径集成测试已有一例（api/test_creator_integration.py） |
| **D.2** | **模型路由与缓存** | 按任务类型选模型（提纲/终稿）；重复检索与上下文缓存 |
| **D.3** | **可观测与告警** | 链路耗时、Token 用量、失败率与慢请求告警 |

---

***REMOVED******REMOVED*** 四、实施顺序建议

```
阶段 A（去冗余）   → 阶段 B（通用沉淀） → 阶段 C（能力增强） → 阶段 D（持续）
A.1 主路径/支线文档  B.1 LLM 门面          C.1 DAG（可选）       D.1 回归
A.2 LLM 收敛        B.2 记忆抽象实现       C.2 RAG
A.3 创作记忆抽象    B.3 工具/技能统一     C.3 图增强
A.4 配置收敛        B.4 编排事件契约      C.4 项目持久化完善    D.2/D.3 路由与观测
```

- **优先级**：A.1（主路径/支线文档）→ A.2 → A.3 → A.4，再 B.1/B.2；C、D 按需排期。
- **原则**：每步可交付、可验证；动主路径时同步更新测试与文档（见 [Instructions/工程原则.md](../Instructions/工程原则.md) 自检）。

---

***REMOVED******REMOVED*** 五、运行与验证

- **环境**：`conda activate seeme`，在 `src` 下执行 `python api_flask.py`（默认端口 5200）。
- **验证创作/记忆是否就绪**：`cd src && conda run -n seeme python -c "from api_flask import _CREATOR_MEMORY_AVAILABLE; print('Creator/Memory:', _CREATOR_MEMORY_AVAILABLE)"`。
- **主路径集成测试**：`cd src && python -m pytest api/test_creator_integration.py -v`（环境不可用时自动 skip）。
- **前端**：`frontend/config/config.ts` 中 `API_URL` 指向后端（如 `http://localhost:5200`）。

---

***REMOVED******REMOVED*** 六、风险与依赖

- **UniMem**：Redis、Neo4j、Qdrant 可选；主路径不强制依赖，通过记忆抽象可选接入。
- **支线**：workflow、puppeteer 在「去冗余」阶段不删除则标为实验，避免新人误以为必维护。
- **DAG 选型**：可在阶段 C 再定（LangGraph vs 自研），阶段 A/B 不依赖 DAG。

---

***REMOVED******REMOVED*** 七、总结

1. **主路径已闭环**：创作 API + 记忆/图谱 API + 前端 + 编排可观测均已打通。
2. **主线为优化与沉淀**：A 去冗余与边界清晰 → B 通用模块沉淀 → C 能力增强 → D 稳定性；每步可交付、可验证。
3. **文档与测试同步**：阶段 A/B 每步完成后更新 README/ROADMAP 与主路径测试；自检见 [Instructions/工程原则.md](../Instructions/工程原则.md)。

工程原则与自检见 **[Instructions/工程原则.md](../Instructions/工程原则.md)**；模块与主路径说明见 **[src/README.md](../src/README.md)**。
