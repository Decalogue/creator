# EverMemOS 项目通读摘要

本文档为通读 EverMemOS 官方仓库及文档/架构图后的学习总结，便于与 Creator 项目对照或后续集成。

---

## 一、定位与愿景

- **EverMemOS**：面向对话式 AI 的**长期记忆操作系统**，为智能体提供「活的、持续进化的历史」。
- **核心主张**：不止「记忆」，更是「前瞻」（More than memory — it's foresight）；强调记忆提取的**准确度**与**逻辑一致性**，受**人脑记忆形成**启发。
- **部署形态**：云服务（EverMemOS Cloud，两行 API 即可用）+ 开源自建（Docker Compose、MongoDB/ES/Milvus/Redis、Python 3.10+、uv、≥4GB 内存）。

---

## 二、受生物启发的三阶段模型

| 阶段 | 大脑对应 | 功能简述 |
|------|----------|----------|
| **1. 情景轨迹构建** | 海马 + 内嗅皮层 | 将连续对话切分为**记忆单元（MemCell）**，含完整对话、关键事实、时间等 |
| **2. 语义整合** | 新皮层 | 将相关 MemCell 归类为**主题记忆场景（MemScene）**，并更新**用户画像** |
| **3. 重构式回忆** | 前额叶与海马协同 | 根据当前问题在 MemScene 引导下**智能检索**，只选取推理所需记忆参与生成 |

---

## 三、系统流程（Encoding → Consolidation → Retrieval）

- **Phase I**：对话历史 + 新对话 → 切分 → MemCell、Episode、Atomic Facts、Foresight。
- **Phase II**：MemScene Pool → 相似度与增量聚类 → MemBase、用户画像。
- **Phase III**：Chat/Reasoning Query → Scene Match、Recall Foresight/Profile/Episode → 记忆增强的 Agent。

---

## 四、开源实现：六层架构

1. Agentic Layer；2. Memory Layer；3. Retrieval Layer（Milvus/ES、混合 RRF、Agentic）；4. Business Layer；5. Infrastructure Layer；6. Core Framework。技术栈：FastAPI、Python 3.10+、uv；MongoDB、ES、Milvus、Redis。

---

## 五、核心概念

- **MemCell**：原子记忆单元。**Episode**：情节记忆。**MemScene**：语义整合后的场景。**Profile**：用户画像。**Foresight**：前瞻。记忆类型：episodic_memory、profile、preferences、relationships 等。

---

## 六、API 与使用方式

- **云服务（Creator 侧已用）**：`src/api_EverMemOS.py` 使用 EverMemOS 云 API，提供 memory.add、memory.get、memory.search、memory.delete，与 config.EVERMEMOS_API_KEY 配合。
- **开源版 REST**：Base `http://localhost:8001/api/v1/memories`，POST/GET/DELETE memories、GET search 等。

---

## 七、检索策略

轻量模式（BM25 + 向量 + RRF）与 Agentic 模式（LLM 查询扩展、多轮检索）；Rerank 可选。

---

## 八、与 Creator 的关系

- **当前**：Creator 通过 `src/api_EverMemOS.py` 使用 **EverMemOS 云服务** 做记忆的增删查。
- **可选**：自建时可将 api_EverMemOS 的 base URL 指向自建实例，统一 user_id/group_id 与 project_id 映射。

---

## 九、文档与入口

| 文档 | 说明 |
|------|------|
| Creator 参赛集成 | [EVERMEMOS_INTEGRATION.md](EVERMEMOS_INTEGRATION.md) |
| 参赛与视频指南 | [VIDEO_DEMO.md](VIDEO_DEMO.md) |
| 愿景与执行清单 | [VISION_AND_PLAYBOOK.md](VISION_AND_PLAYBOOK.md) |

*参见 [EVERMEMOS_INTEGRATION.md](EVERMEMOS_INTEGRATION.md) 了解当前 Creator 侧整合方案。*
