# Creator 创作助手 + EverMemOS 参赛集成方案

本文档描述如何将 **Creator 创作助手** 与 **EverMemOS 官方 API** 整合，用于参赛（如 Memory Genesis 2026 Agent + Memory 赛道），并保留 UniMem 在作品内图谱与检索上的优势。

**EverMemOS Cloud 官方 API 文档**：[Introduction](https://docs.evermind.ai/api-reference/introduction)；[Search memories](https://docs.evermind.ai/api-reference/memory-controller/search-memories)。`api_EverMemOS.search_memory` 已支持 top_k、retrieve_method、memory_types、start_time/end_time、radius。

## 目标

- **参赛要求**：使用 EverMemOS 官方云 API 作为记忆层（add / get / search / delete）。
- **应用形态**：Creator 作为主应用，具备大纲创作、章节续写、润色、对话等能力。
- **记忆分工**：EverMemOS 负责用户级/项目级长期记忆；UniMem + semantic_mesh 负责单作品内实体关系、章节结构。

## 架构概览

```
用户 / 前端 → Creator API (Flask) → creator_handlers (create / continue / polish / chat)
  → 创作成功事件 → retain_plan_to_evermemos / retain_chapter_to_evermemos → api_EverMemOS (add_memory)
```

检索增强（已接入）：规划前、续写前、润色、对话前按 project 召回并注入 prompt；前端「云端记忆」区块展示 EverMemOS 检索结果（GET /api/memory/evermemos）。

## 配置

| 环境变量 | 说明 |
|----------|------|
| `EVERMEMOS_API_KEY` | EverMemOS 云 API Key（必填才启用云端记忆） |
| `EVERMEMOS_ENABLED` | 设为 `1`/`true` 时启用双写与检索 |

## 数据映射

- **sender**：必填 UUID；创作助手使用固定 UUID（`uuid5(NAMESPACE_DNS, "creator.evermemos")`）。
- **group_id**：设为 `project_id`（书名），检索时按 group_id 查。
- **message 格式**：`message_id`、`create_time`（ISO8601）、`sender`、`sender_name`（可选）、`group_id`、`content`。

## 实现要点

1. **api_EverMemOS.py**：官方 API 封装；search_memory / search_memory_result。
2. **memory_handlers.py**：retain_plan/chapter/polish/chat_to_evermemos；recall_from_evermemos(project_id, query, top_k, memory_types)。
3. **creator_handlers.py**：create/continue 前 recall 并注入；polish/chat 在提供 project_id 时 recall 注入并在成功后 retain。
4. **API**：GET /api/memory/evermemos?project_id=&query=&top_k=10。
5. **前端**：记忆面板「云端记忆」区块；未配置时显示配置说明。

## UniMem 与 EverMemOS 分工说明

主路径记忆 = **本地 mesh（必选）** + **可选 UniMem 图谱** + **可选 EverMemOS 云端**：mesh 管实体/关系结构，EverMemOS 管摘要与跨章叙事细节，职责不重叠。

| 层级 | 存储 | 职责 | 典型用途 |
|------|------|------|----------|
| **本地结构** | semantic_mesh（mesh.json）；可选 UniMem（Redis/Neo4j/Qdrant） | 实体、关系、图谱结构 | 作品内人名/关系/设定一致性、图谱展示 |
| **云端叙事** | EverMemOS 云 API | 摘要、情节、关键细节点（数字、术语、一次性事件） | 跨章连贯、长程召回（≥21 章）、规划/续写/润色/对话前检索 |

双写策略：创作事件同时写 EverMemOS 与本地 mesh（及可选 UniMem），互不替代。当前默认仅 mesh + EverMemOS 即可跑通主路径；UniMem 为可选扩展。

## 参赛提交

- 应用入口：Creator 前端 + 后端（/api/creator/stream、/api/creator/run 等）。
- 记忆层：配置 EVERMEMOS_API_KEY 后自动写入 EverMemOS；检索在规划/续写前或对话中调用 search_memory 增强上下文。

**三赛道策略与执行清单**：见 [VIDEO_DEMO.md](VIDEO_DEMO.md)。
