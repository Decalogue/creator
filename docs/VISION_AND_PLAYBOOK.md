# Creator + EverMemOS 愿景与执行清单

本文档对齐「基于 EverMemOS 提升 Creator、沉淀技术、冲比赛与后续规划」的整体方向，并与 [EVERMEMOS_INTEGRATION.md](EVERMEMOS_INTEGRATION.md)、[VIDEO_DEMO.md](VIDEO_DEMO.md)（参赛与视频指南）配合使用。

---

## 一、愿景三则

1. **基于 EverMemOS 提升 Creator 的综合创作能力，争取比赛获奖**  
   - 记忆写入：大纲、章节摘要、本章实体、润色、对话。  
   - 记忆检索：在规划前 / 续写前 / 润色 / 对话时注入云端记忆；**有计划地开展跨章、长跨度检索验证**，积累可展示的案例与素材。

2. **以问题驱动改进，在打磨 Creator 的同时把可复用记忆架构沉淀到 UniMem**  
   - 将使用中的卡点与问题视为改进方向，结合 EverMemOS API 与论文理解其设计，反哺 query 与参数。  
   - 维护「改进方向 / 问题清单」（见下），记录具体 query、返回质量与问题，用于优化 query 设计。  
   - 将 EverMemOS 的检索策略、写入粒度、去重与融合、跨会话/跨章设计抽象为可复用记忆架构，在 UniMem 侧做文档或模块级对应（如 recall/retain 与 search/add 的映射）。

3. **若比赛获奖，申请面试加入 EverMind 团队，专注记忆方向的科研与落地**  
   - 把比赛作品做成「记忆增强创作」的完整案例（数据流、检索如何影响创作、遇到的问题与改进），作为面试与作品集材料。

---

## 二、改进方向 / 问题清单（模板）

在真实多章创作与检索测试中，把**优点 / 缺点**和具体 query、返回质量记下来，用于优化 Creator 的 query 设计，并当比赛展示素材（长跨度记忆、一致性）。

| 时间 | 场景 | query / 参数 | 返回条数 | 优点 | 缺点 | 备注（可贴 1–2 条摘录） |
|------|------|--------------|----------|------|------|--------------------------|
| 例：2/6 续写第3章前 | 续写前检索 | 前文 情节 人物 大纲 本章摘要 角色, top_k=5 | 5 | 能带到林渊、玄灵大陆 | — | 摘录略 |
| （可填） | 跨章人物 | 主角 人物 角色 成长 变化 | | | | |
| （可填） | 伏笔 | 伏笔 铺垫 悬念 回收 | | | | |
| （可填） | 长线设定 | 世界观 设定 规则 体系 | | | | |

- **记录方式**：  
  - 用脚本跑几类检索并自动落日志（见下一节），再在本文档或 `retrieval_notes.md` 中补「优点/缺点」与典型摘录。  
  - 或直接在「检索测试与记录」跑完后，把当次结果贴到上表对应行。

---

## 三、检索测试与记录（刻意几类检索）

为验证**跨章人物、伏笔、长线设定**等长跨度记忆，并积累比赛展示素材，建议在写完多章后定期跑一轮「几类检索」并记录结果。

### 3.1 三类预设 query（可调）

| 类型 | 建议 query | 用途 |
|------|------------|------|
| **跨章人物** | 主角 人物 角色 成长 变化 关系 | 检验人物设定与弧光是否被召回 |
| **伏笔** | 伏笔 铺垫 悬念 回收 线索 | 检验伏笔/悬念类记忆是否可被检索 |
| **长线设定** | 世界观 设定 规则 体系 玄灵 大陆 | 检验设定类记忆的跨章召回 |

### 3.2 如何跑并记录（已整合进创作流程）

- **前端**：打开记忆列表 → 在「云端记忆（EverMemOS）」标题右侧点击 **「跑检索测试」**，即对当前项目跑三类 query、结果**追加到同一 JSONL 日志**，并在本页展示本次三条的条数与摘录预览。
- **脚本**：在项目 `src` 目录下执行 `python -m scripts.evermemos_retrieval_demo 玄灵科学家 --top-k 8`，与前端共用同一套逻辑和默认日志路径，适合命令行或 CI。
- **日志路径**：默认 `src/scripts/evermemos_retrieval_log.jsonl`（JSON Lines：每行一次 run 的一条 query 结果）。
- **日志字段**：`timestamp`、`project_id`、`query_type`、`query`、`top_k`、`result_count`、`excerpts`。可事后在表格或 `retrieval_notes.md` 中为当次 run 补「优点/缺点」和典型摘录。
- **比赛展示**：从日志中挑选「跨章人物 / 伏笔 / 长线设定」各 1–2 条高质量召回样例，用于视频或 README，体现长跨度记忆与一致性。

### 3.3 与 Creator 日常检索的关系

- **创作流程内**：规划前 / 续写前 / 润色 / 对话仍用现有 query（见 [EVERMEMOS_INTEGRATION.md](EVERMEMOS_INTEGRATION.md)），不依赖本脚本。  
- **本脚本**：专门用于「刻意测试几类检索 + 记录」，用于调优和展示，不改变现有 API 或前端逻辑。

---

## 四、API / 论文 → UniMem 沉淀（要点）

- **EverMemOS 侧**：add / get / search / delete；search 的 RetrieveMemRequest（query、user_id/group_id、memory_types、retrieve_method、top_k、时间范围等）；返回 memories、scores、total_count、has_more。  
- **对应到 UniMem**：  
  - 概念映射：EverMemOS 的「事件/情节/前瞻/原子事实」与 UniMem 的 memory/context 可做一层抽象对应（谁负责长期、谁负责作品内、如何混合）。  
  - 检索策略：keyword / vector / hybrid / rrf / agentic 与 UniMem 的 recall 策略可对比记录（何时用语义、何时用关键词、何时融合）。  
  - 写入粒度：大纲 / 章节摘要 / 本章实体 / 润色/对话 的划分，可作为「记忆写入粒度」的参考，在 UniMem 侧文档或配置中保留同一套划分思路。  
- 具体沉淀形式：在 UniMem 的 README 或 `docs/` 下增加「与 EverMemOS 的对应关系」「记忆层设计说明」等小节，随 Creator 与比赛推进逐步补全。

---

## 五、推荐执行顺序（结合本 playbook）

1. **多章创作**：用 Creator 正常写 3–5 章以上，保证云端有摘要 + 实体。  
2. **跑检索 demo**：执行 `python -m scripts.evermemos_retrieval_demo <project_id> --top-k 8`，查看三类 query 的返回。  
3. **填改进清单**：把当次「优点/缺点」、典型摘录填进第二节表格或 `retrieval_notes.md`。  
4. **调 query / 参数**：根据缺点或有问题 case 调整 Creator 内 query 或 memory_types/retrieve_method（必要时在 memory_handlers 或 api_EverMemOS 层加可选参数）。  
5. **比赛材料**：从日志与表格中选出跨章人物、伏笔、长线设定的好例子，用于视频与 README。

---

*主文档已统一放在 `docs/`，本 playbook 与 EVERMEMOS_INTEGRATION、VIDEO_DEMO 同目录。*
