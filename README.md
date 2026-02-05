# Creator — 创作助手

基于多智能体编排与记忆系统的创作助手。

---

## 已实现（DONE）

| 层级 / 入口 | 说明 |
|-------------|------|
| **编排层** | `orchestrator/react`（ReAct） |
| **创作层** | `task.novel`（ReactNovelCreator） |
| **记忆与上下文** | UniMem、`context`（semantic_mesh） |
| **API 入口** | `api_flask` → `api/creator_handlers`、`api/memory_handlers` |
| **能力扩展** | `tools`、`skills` 聚焦创作 |

## 计划中（TODO）

由 **Agentic RL 推理模型** 实现：动态选 Agent、提取记忆、综合优化决策路径与记忆系统。

对应能力点：

- **动态编排**：按状态实时选 Agent，不依赖固定流程
- **自适应学习**：用强化学习优化协作模式
- **环状协作**：涌现「反复打磨」式协作
- **记忆管理**：压缩、更新、重组记忆
- **成本优化**：平衡质量与成本，学习高效策略

---

## 相关文档

| 文档 | 说明 |
|------|------|
| 本页 | 项目总览 |
| [docs/ROADMAP.md](docs/ROADMAP.md) | 研发路线图与阶段规划 |
| [src/README.md](src/README.md) | 模块说明与主路径/支线划分 |
| [Instructions/工程原则.md](Instructions/工程原则.md) | 工程原则与规范 |
