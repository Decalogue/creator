***REMOVED*** Creator 项目研发路线图

> 结合当前 Agent 与 Memory 领域的高速发展，对创作助手项目的优先级、阶段划分与落地顺序的建议。

---

***REMOVED******REMOVED*** 一、现状与缺口

***REMOVED******REMOVED******REMOVED*** 1.1 已有能力

| 模块 | 状态 | 说明 |
|------|------|------|
| **创作引擎** | ✅ 可用 | ReAct + 语义网格，分章创作、大纲、质检 |
| **语义网格记忆** | ✅ 在用 | 实体-关系图，章节前后一致性，`mesh.json` |
| **UniMem** | ⚠️ 可选 | Retain/Recall/Reflect，Neo4j/Redis/Qdrant，已接创作器但默认关 |
| **编排** | ⚠️ 部分 | 单 ReAct 循环为主；Puppeteer/Workflow 有代码未深度打通 |
| **前端** | ⚠️ 演示 | 工作流/记忆图谱为 UI 展示，**未接真实编排与记忆 API** |
| **API** | ⚠️ 单一 | 仅有 `/api/chat` 通用对话，**无创作专属、记忆、图谱接口** |

***REMOVED******REMOVED******REMOVED*** 1.2 与行业的差距

- **Agent**：多智能体编排、DAG 工作流、可观测（步骤/状态推送）已成主流；当前以单 ReAct 为主，编排不可视、难扩展。
- **Memory**：图+向量混合、长期/工作记忆分离、跨会话持久化是趋势；UniMem 与语义网格未在前后端贯通，图数据未对前端开放。
- **产品闭环**：前端与真实「创作 + 记忆」 pipeline 未打通，无法端到端体现多智能体与记忆价值。

---

***REMOVED******REMOVED*** 二、研发阶段与优先级

***REMOVED******REMOVED******REMOVED*** 阶段一：闭环打通（P0）— 建议 2–3 周

**目标**：前端驱动真实创作流程，并用上真实记忆/图谱数据。

| 序号 | 任务 | 说明 | 产出 |
|------|------|------|------|
| **1.1** | **创作 API** | 新增 `POST /api/creator/run`（或类似），入参：`mode`(create/continue/polish/chat)、`input`、可选 `project_id` 等 | 后端统一入口，支持流式返回 |
| **1.2** | **路由到现有引擎** | 根据 `mode` 调用 `ReactNovelCreator` 对应能力（含 create_plan、create_chapter、续写、润色等） | 复用现有创作逻辑，接口化 |
| **1.3** | **记忆 & 图谱 API** | `GET /api/memory/entities`、`GET /api/memory/graph`（节点+边）、`GET /api/memory/recents`；可选 `GET /api/memory/note/:id` 用于「点击查看记忆」 | 数据来自 semantic_mesh，或 UniMem  when 启用 |
| **1.4** | **前端接真接口** | 创作页请求 `/api/creator/run` 替代纯 `/api/chat`；记忆列表/图谱/最近检索改用上述 memory API；点击节点调 `note/:id` | 端到端可演示真实创作+记忆 |

**优先级**：1.1 ≈ 1.3 > 1.2 > 1.4。先有 API 契约，再实现路由与前端对接。

**P0 实施记录**（已落地）：
- **创作 API**：`POST /api/creator/run`，入参 `mode`（create/continue/polish/chat）、`input`、`project_id`；非流式 JSON 返回。
- **记忆 API**：`GET /api/memory/entities`、`/api/memory/graph`、`/api/memory/recents`、`/api/memory/note/<id>`，数据来自 `semantic_mesh/mesh.json`。
- **后端**：`api/creator_handlers.py`、`api/memory_handlers.py`；Flask 在 `api_flask.py` 中挂载上述路由。
- **前端**：创作页 create/continue/polish 走 `/api/creator/run`，chat 仍走 `/api/chat` 流式；记忆列表/图谱/最近检索拉取真实 API；图谱节点点击请求 `note/:id`，抽屉展示详情与关联。

**阶段一打通情况检查**（按 ROADMAP 逐项核对）：

| 任务 | 要求 | 检查结果 | 说明 |
|------|------|----------|------|
| **1.1 创作 API** | `POST /api/creator/run`，入参 mode/input/project_id，支持流式返回 | ✅ 已实现 | `api_flask.py` 挂载 `/api/creator/run`；入参齐全；当前为**非流式** JSON 返回（与「支持流式」为可选差异） |
| **1.2 路由到现有引擎** | 按 mode 调用 ReactNovelCreator（create_plan、create_chapter、续写、润色等） | ✅ 已实现 | `creator_handlers.py`：create→`run_create`（create_novel_plan），continue→`run_continue`（create_chapter + 加载 mesh），polish→`run_polish`，chat→`run_chat`；均复用现有引擎 |
| **1.3 记忆 & 图谱 API** | entities / graph / recents / note/:id，数据来自 semantic_mesh 或 UniMem | ✅ 已实现 | `memory_handlers.py` 全部实现；数据来自 `outputs/<project_id>/semantic_mesh/mesh.json`；get_note 返回 id/label/type/brief/body/related |
| **1.4 前端接真接口** | 创作用 `/api/creator/run`，记忆/图谱/最近用 memory API，节点点击调 note/:id | ✅ 已实现 | `creator.tsx`：create/continue/polish 用 `/api/creator/run`，chat 用 `/api/chat` 流式；memoryOpen 时拉 entities/graph/recents（带 project_id）；记忆列表项与 2D/3D 图节点点击均请求 `/api/memory/note/<id>` 并 setSelectedNode，抽屉展示详情与关联 |

**结论**：阶段一四项任务均已打通；唯一与 ROADMAP 描述的差异为创作 API 当前为**非流式**返回，若需「流式返回」可在 1.1 上做增量（如 SSE 或 WebSocket）。

**运行与验证**：后端需在 **seeme** 虚拟环境（conda）下运行。启动：`conda activate seeme`，在 `src` 目录执行 `python api_flask.py`（默认端口 5200）。验证创作/记忆 API 是否加载：`conda run -n seeme python -c "from api_flask import app, _CREATOR_MEMORY_AVAILABLE; print('Creator/Memory:', _CREATOR_MEMORY_AVAILABLE)"`（在 `src` 下执行）。前端 `config/config.ts` 中 `API_URL` 需指向后端地址（本地联调可为 `http://localhost:5200`）。

**前端能否看到「创作 + 记忆更新」的完整流程？**

| 能力 | 现状 | 说明 |
|------|------|------|
| 创作步骤可见 | ⚠️ 仅演示 | 编排区播放的是**固定顺序动画**（planner→memory→writer→editor→qa），非后端真实步骤；后端 create/continue 为单次请求，未推送「正在写大纲」「正在写第 N 章」等中间状态 |
| 创作结果可见 | ✅ 有 | 最终大纲摘要或章节正文在对话区展示 |
| 记忆更新可见 | ✅ 已改善 | 创作/续写**成功后若记忆面板已打开**会**自动刷新** entities/graph/recents（`creator.tsx` 中 `fetchMemory()`，创作成功且 `memoryOpen` 时调用），用户无需关开面板即可看到新记忆 |

若要在页面上进一步「看到整个流程」的**步骤**（非仅结果）：  
- **中期**：阶段二编排事件 + 流式/WS 推送后，可展示真实步骤（正在写大纲、正在写第 N 章、正在更新记忆等）。

**近期记忆改进（UniMem，为 P1 2.3 / P2 打基础）**：

| 改进项 | 说明 |
|--------|------|
| 编排层 API | `recall_for_agent`、`retain_for_agent`、`context_for_agent`，供决策编排 Agent / 任务 Agent 统一使用 |
| 重要性评分 | recall 重排序：时间衰减 + 访问次数 + 会话/任务匹配，可配置 `retrieval.importance_weight`、`importance_decay_days` |
| 会话级 FoA/DA | 当 `context.session_id` 存在时，FoA/DA 优先按会话检索（Redis 用 session key，内存按 metadata 过滤） |
| retain 写 session_id | 存储时把 `context.session_id` 写入 `memory.metadata`，便于会话检索与重要性匹配 |

详见 `src/unimem/README.md`「编排层记忆 API」「记忆重要性评分」「会话级 FoA/DA」小节。2.3 做 UniMem 贯通时可直接复用上述 API。

---

***REMOVED******REMOVED******REMOVED*** 阶段二：编排可观测 & UniMem 贯通（P1）— 建议 2–3 周

**目标**：工作流「像游戏一样」可观测；记忆体系统一到 UniMem（可选）并支持图+向量。

| 序号 | 任务 | 说明 | 产出 |
|------|------|------|------|
| **2.1** | **编排事件** | 创作 pipeline 各步骤（大纲→写手→记忆→润色→质检）emit 开始/结束/失败事件 | 便于 SSE/WebSocket 推送 |
| **2.2** | **事件推送 API** | 如 `GET /api/creator/stream` 或 WebSocket：流式文本 + 编排事件（当前 step、done、error） | 前端工作流面板驱动真实状态 |
| **2.3** | **UniMem 为可选记忆后端** | 配置启用时，memory API 可合并 UniMem 与 semantic_mesh；Retain 写创作结果，Recall 供检索 | 语义网格保留为「创作专用图」，UniMem 作长期记忆 |
| **2.4** | **图谱数据融合** | `graph` API 支持 semantic_mesh + UniMem 图（若可实现），前端 2D/3D 图可展示真实混合图 | 记忆图与真实数据一致 |

**优先级**：2.1 ≈ 2.2 > 2.3 > 2.4。先可观测，再丰富记忆源。

**P1 实施检查清单与接口草案（2.1 / 2.2）**：

| 任务 | 检查项 | 接口/约定草案 |
|------|--------|----------------|
| **2.1 编排事件** | 创作 pipeline 各步骤在开始/结束/失败时 emit 事件 | 事件 payload 建议：`{ "type": "step_start" \| "step_done" \| "step_error", "step": "plan" \| "write" \| "memory" \| "polish" \| "qa", "data"?: { ... }, "ts": ISO8601 }`；在 `ReactNovelCreator` 或调用链中插入 emit 点 |
| **2.2 事件推送 API** | 前端能收到流式文本 + 编排事件，驱动工作流面板 | 方案 A：`GET /api/creator/stream?mode=...&input=...` 返回 SSE，每行一个 JSON 事件或文本块。方案 B：WebSocket 订阅同一会话，服务端在 pipeline 执行时 push 事件。前端：监听 stream/WS，根据 `step` 更新编排区状态（高亮当前 step、done/error 样式） |

落地顺序建议：先 2.1（在现有 create/continue 路径上加 emit），再 2.2（新增 stream 或 WS 路由并让前端接上）。

**P1 2.1 / 2.2 实施记录**（已落地）：

| 任务 | 产出 | 说明 |
|------|------|------|
| **2.1 编排事件** | ✅ | `api/orchestration_events.py`：`emit_step_start` / `emit_step_done` / `emit_step_error`；`ReactNovelCreator.create_novel_plan` 与 `create_chapter` 在 plan / memory / write 步骤开始/结束/失败时调用；`creator_handlers.run_create` / `run_continue` / `run` 支持 `on_event` 并传入 creator |
| **2.2 事件推送 API** | ✅ | `POST /api/creator/stream`：body 同 `/api/creator/run`（mode、input、project_id 等），返回 SSE；每条 `data: { "type": "step_start" \| "step_done" \| "step_error", "step": "plan" \| "memory" \| "write", "data": {...}, "ts": ISO8601 }`，最后一条 `type: "stream_end"` 含 code、message、content；仅支持 mode=create 或 continue |

前端对接（已落地）：创作页单次「生成大纲」「写一章」改为请求 `POST /api/creator/stream`（`fetchCreatorStream` + fetch ReadableStream），根据 `step_start` / `step_done` / `step_error` 更新编排区（`stepToAgentKey` 映射 plan→planner、memory→memory、write→writer），收到 `stream_end` 后展示最终 content 并刷新项目/章节列表；批量「写 N 章」仍走 submit + 轮询。

**P1 2.3 / 2.4 实施记录**（已落地）：

| 任务 | 产出 | 说明 |
|------|------|------|
| **2.3 UniMem 为可选记忆后端** | ✅ | 默认启用（`UNIMEM_ENABLED=0` 可关闭）；`memory_handlers._get_unimem()` 懒加载 UniMem（可配 `UNIMEM_STORAGE/GRAPH/VECTOR_BACKEND`）；创作大纲成功调用 `retain_plan_to_unimem(project_id, plan_summary)`，续写成功调用 `retain_chapter_to_unimem(project_id, chapter_number, content)`；`get_entities` / `get_graph` / `get_recents` / `get_note` 启用时合并 UniMem 数据（recall_for_agent + project_id） |
| **2.4 图谱数据融合** | ✅ | `get_graph` 在启用 UniMem 时追加 recall 结果为节点（id 前缀 `unimem_`，source=UniMem），并用 `memory.links` 生成边；`get_note` 对 `unimem_` 节点从 UniMem（neo4j.get_memory）取详情与 related |

启用方式：默认开启；可选设置 `UNIMEM_ENABLED=0` 关闭。后端写入：默认均为 `memory`（仅内存，进程退出即丢）；**要让 Qdrant / Neo4j 有内容**，需设置 `UNIMEM_STORAGE_BACKEND=redis`、`UNIMEM_GRAPH_BACKEND=neo4j`、`UNIMEM_VECTOR_BACKEND=qdrant`，并确保 Redis / Neo4j / Qdrant 已启动；`memory_handlers._get_unimem()` 会按上述环境变量构建 config 并传给 UniMem，使 LayeredStorageAdapter 的 FoA/DA 用 Redis、LTM 用 Neo4j，AtomLinkAdapter 用 Qdrant 写入向量；可选 `UNIMEM_QDRANT_HOST`、`UNIMEM_QDRANT_PORT`、`UNIMEM_COLLECTION_NAME`。

**P1 贯通下 UniMem 存的记忆有哪些？**

| 来源 | 何时写入 | 内容 | metadata 标识 |
|------|----------|------|----------------|
| **创作 API（P1 2.3）** | create 成功 | 大纲摘要（最多 8000 字） | source=creator_plan, project_id, role=creator |
| **创作 API（P1 2.3）** | continue 成功 | 章节前 500 字摘要 | source=creator_chapter, project_id, chapter_number, role=writer |
| **ReactNovelCreator 内嵌** | create_chapter 完成后（enable_unimem=True） | 整章正文 | chapter_number, title, summary, word_count, novel_title |
| 其他 | 过程记忆、视频脚本、学习流水线、Puppeteer unimem_retain、Reflect 等 | 各异 | 各流程自定 |

前端/记忆 API 启用 UniMem 时：entities、graph、recents 会合并上述记忆（recall 按 project_id）；图谱中 UniMem 节点 id 前缀为 `unimem_`，source=UniMem。

---

***REMOVED******REMOVED******REMOVED*** 阶段三：Agent & Memory 升级（P2）— 建议 3–4 周

**目标**：编排可扩展、可演进的 DAG；记忆支持 RAG、图增强、跨会话。

| 序号 | 任务 | 说明 | 产出 |
|------|------|------|------|
| **3.1** | **DAG 编排** | 将创作流程抽象为 DAG（如 LangGraph / 自研），节点=步骤，边=依赖；支持分支、条件、后续扩展 human-in-the-loop | 替代单 ReAct 黑盒，便于增删步骤 |
| **3.2** | **RAG over 已写内容** | 续写/润色时，对已有章节 + 语义网格做检索，注入上下文 | 长文一致性、前后呼应 |
| **3.3** | **记忆图增强** | 时序边、来源标注、置信度等；可选与 UniMem 原子笔记 / AtomLink 打通 | 图谱更可解释、可追溯 |
| **3.4** | **项目级持久化** | 项目（小说）为一级实体；支持创建/加载/切换；每项目独立 semantic_mesh + 可选 UniMem 空间 | 前端项目选择、「继续创作」加载既有项目 |

**优先级**：3.1 > 3.4 > 3.2 > 3.3。先确立 DAG 与项目模型，再深化检索与图。

---

***REMOVED******REMOVED******REMOVED*** 阶段四：稳定性与成本（P3）— 持续

**目标**：可回归、可监控、成本可控。

| 序号 | 任务 | 说明 |
|------|------|------|
| **4.1** | **质量基线 & 回归** | 固定若干「标杆小说」流程，做一致性、风格等指标；CI 回归创作 pipeline + memory API |
| **4.2** | **模型路由与缓存** | 按任务类型选模型（如提纲用便宜模型，终稿用强模型）；对重复检索、相同上下文做缓存 |
| **4.3** | **可观测与告警** | 链路日志、耗时、Token 用量；失败率、慢请求告警 |

---

***REMOVED******REMOVED*** 三、建议实施顺序（甘特式）

```
周 1–2    [P0] 创作 API + 记忆/图谱 API 设计与实现
周 2–3    [P0] 前端对接真实 API，替换 mock，实现「创作→记忆→图谱」闭环
周 3–4    [P1] 编排事件 + 流式/WS 推送，工作流面板接真实步骤
周 4–5    [P1] UniMem 与 semantic_mesh 融合，图谱 API 支持混合数据
周 5–8    [P2] DAG 编排抽象、项目持久化、RAG、图增强（按优先级穿插）
后续      [P3] 回归、缓存、观测与成本优化
```

---

***REMOVED******REMOVED*** 四、与 Agent / Memory 趋势的对应

| 趋势 | Creator 对应 |
|------|----------------|
| **多智能体 & DAG 编排** | 阶段二事件推送 + 阶段三 DAG；工作流可观测、可扩展 |
| **图+向量混合记忆** | 语义网格（图）+ UniMem（向量/图）；阶段二、三打通并开放 API |
| **长期记忆与个性化** | UniMem Retain/Recall/Reflect；项目级记忆、跨会话 |
| **可观测与可控** | 编排事件、步骤状态、图谱与检索结果在前端可见可点 |
| **RAG 与检索增强** | 阶段三 RAG over 章节 + 网格，提升续写/润色质量 |

---

***REMOVED******REMOVED*** 五、风险与依赖

- **UniMem 依赖**：Redis、Neo4j、Qdrant 等。若暂不部署，可仅用 semantic_mesh 完成 P0/P1 记忆与图谱，UniMem 作为可选增强。
- **前端工作量**：若 1.4、2.2 改动较大，可与后端 API 并行，用 mock 先定契约再替换。
- **DAG 选型**：LangGraph 等成熟方案 vs 自研。建议先用小规模自研 DAG 验证创作流程，再考虑引入 LangGraph。

---

***REMOVED******REMOVED*** 六、总结

1. **先闭环再升级**：P0 打通「创作 API + 记忆/图谱 API + 前端」是当前最高优先级。  
2. **编排可观测**：P1 编排事件与推送让「工作流像游戏」落地，并为后续 DAG 打基础。  
3. **记忆分层**：语义网格负责创作一致性，UniMem 负责长期记忆与检索；通过统一 API 对外。  
4. **渐进式增强**：DAG、RAG、图增强、项目持久化在闭环稳定后按 P2 顺序推进，持续对齐 Agent 与 Memory 方向。

可按实际人力与依赖落地情况，微调各阶段周期与任务顺序；若需要，我可以把某一段拆成更细的 TODO（含接口草案、文件改动点等）。
