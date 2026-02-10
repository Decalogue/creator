# API 层

提供 RESTful 接口：创作（creator_handlers）、记忆/图谱（memory_handlers）、编排事件等。

## 记忆抽象实现（B.2）

主路径记忆由 **memory_handlers** 实现，统一抽象为：mesh 读写 + UniMem 可选适配器 + EverMemOS 可选云记忆。

### 数据分层

| 层级 | 存储 | 说明 |
|------|------|------|
| **主存储** | semantic_mesh/mesh.json | 按 project 读写，实体与关系；read_mesh / write_mesh |
| **UniMem 适配器** | Redis/Neo4j/Qdrant（可选） | UNIMEM_ENABLED=1 时，retain 写入、get_entities/graph 合并 recall |
| **EverMemOS** | 云端 API（可选） | EVERMEMOS_ENABLED 且配置 API_KEY 时，retain/recall 与云端同步 |

### 入口

- **mesh**：`read_mesh(project_id)`、`write_mesh(project_id, mesh_data)`
- **recall**：`recall_for_mode(project_id, mode, chapter_number?)` 按模式检索（create/continue/polish/chat）
- **retain**：`retain_plan`、`retain_chapter`、`retain_chapter_entities`、`retain_polish`、`retain_chat`
- **云端列表**：`list_from_evermemos(project_id, limit)` 按 group_id 拉取该项目下全部云端记忆（不依赖 query），与 recall 返回格式一致，用于前端「云端记忆」列表、重启后可靠展示。

所有记忆相关 API 的 `project_id` 在 Flask 层经 `normalize_project_id` 规范化（含去掉「（当前）」后缀），与创作/续写侧一致。

**创作与记忆拆分加载**（`api_flask`）：先单独导入 `api.creator_handlers`（run、get_project_chapters），再单独导入 `api.memory_handlers`。仅当 creator 失败时续写/stream 返回「创作服务未就绪」；记忆失败时实体/图谱/云端等走 fallback，续写仍可进行（creator_handlers 内对 memory 调用已 try/except 跳过）。

**记忆只读 fallback**：当 `api.memory_handlers` 未加载时，`api_flask` 仍从本地 `project_dir(pid)/semantic_mesh/mesh.json` 提供实体/图谱/最近/节点详情；云端记忆在 fallback 下通过单独导入 `api_EverMemOS` 按 group_id 拉列表，保证「作品列表正常但记忆看不到」时可展示本地 mesh 与云端列表。

**章节列表**：`GET /api/creator/chapters?project_id=xxx` 由 `creator_handlers.get_project_chapters` 提供；CREATOR 未就绪时由 `api_flask._fallback_chapters` 从本地 `novel_plan.json` + `chapters/` 目录读取。支持顶层 `chapter_outline`、无 outline 时从 `phases[].chapters` 合并；若大纲条数少于 `novel_plan.json` 中的 `target_chapters`（如渐进式只生成了首阶段），会补齐到 `target_chapters`，保证「共 N 章，已写 M 章」显示正确。无 `novel_plan.json` 时仅从 `chapters/chapter_*.txt` 推断。

**续写是否注入云端记忆**：`run_continue(..., use_evermemos_context=True)`；`POST /api/creator/run` 与 `POST /api/creator/stream` 的 body 支持 `use_evermemos_context`（默认 true）。为 false 时续写仅使用本地 mesh + 大纲摘要，不调用 EverMemOS recall，便于对比测试章节重叠等问题。

**EverMemOS 本地记录与清空**：每次 `add_memory` 使用的 `message_id` 会追加到该项目目录下的 `evermemos_ids.json`。清空云端记忆时优先按该文件逐条调用 `delete`，无需先 `get_memory`；无本地记录时（历史项目）回退为按 group_id 拉取后删除。`scope=all` 时先按各项目本地记录删除，再按 user 拉取并删除剩余。

UniMem 与 EverMemOS 通过上述 retain/recall 入口透明接入，主路径仅依赖抽象接口。

## 编排事件契约（B.4）

创作 pipeline 各步骤通过 `on_event` 回调发出事件，供 SSE 推送、前端工作流展示。

### step 类型（CREATOR_STEPS）

| step | 说明 |
|------|------|
| plan | 大纲生成 |
| memory | 记忆/检索 |
| write | 章节创作 |
| polish | 润色 |
| qa | 质量检查 |

### 事件类型与 payload

| type | 说明 | payload 结构 |
|------|------|-------------|
| step_start | 步骤开始 | `{ type, step, data?, ts }` |
| step_done | 步骤完成 | `{ type, step, data?, ts }` |
| step_error | 步骤失败 | `{ type, step, data: { error }, ts }` |
| stream_end | 流结束（api_flask 发出） | `{ type, code, message, content?, ... }` |

### 使用

```python
from api.orchestration_events import emit_step_start, emit_step_done, emit_step_error, CREATOR_STEPS

# 步骤开始
emit_step_start("plan", {"target_chapters": 20}, on_event)

# 步骤完成
emit_step_done("plan", {"summary": "大纲生成完成"}, on_event)

# 步骤失败
emit_step_error("plan", e, on_event)
```
