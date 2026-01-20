***REMOVED*** 基于 ReAct 的中长篇小说创作系统

***REMOVED******REMOVED*** 概述

利用结合了 Cursor 和 Manus 思路的 ReAct 系统进行中长篇小说创作，充分利用以下特性：

- **工具动态发现**：Agent 可以主动查找工具文档
- **上下文缩减**：自动管理上下文，避免溢出
- **分层行动空间**：灵活使用 L1/L2/L3 工具
- **多 Agent 协作**：可选的多 Agent 协作模式

***REMOVED******REMOVED*** 设计思路

***REMOVED******REMOVED******REMOVED*** 1. 分章节创作

将长篇小说分解为多个章节，每章独立创作，降低上下文压力。

***REMOVED******REMOVED******REMOVED*** 2. 上下文管理

- 每章完成后进行 Compaction，保留关键信息
- 使用章节摘要确保前后章节连贯性
- 每5章进行一次上下文压缩

***REMOVED******REMOVED******REMOVED*** 3. 渐进式创作

支持边写边改，迭代优化。可以：
- 从任意章节开始续写
- 修改已有章节
- 调整大纲

***REMOVED******REMOVED*** 使用方法

***REMOVED******REMOVED******REMOVED*** 基本使用

```python
from novel_creation import ReactNovelCreator

***REMOVED*** 创建小说创作器
creator = ReactNovelCreator(
    novel_title="时空旅者的日记",
    enable_context_offloading=True
)

***REMOVED*** 创作小说
result = creator.create_novel(
    genre="科幻",
    theme="时间旅行、平行世界、人性探索",
    target_chapters=20,
    words_per_chapter=3000,
    start_from_chapter=1
)
```

***REMOVED******REMOVED******REMOVED*** 分步创作

```python
***REMOVED*** 1. 创建大纲
plan = creator.create_novel_plan(
    genre="科幻",
    theme="时间旅行",
    target_chapters=20,
    words_per_chapter=3000
)

***REMOVED*** 2. 创作单个章节
chapter = creator.create_chapter(
    chapter_number=1,
    chapter_title="第一章：起点",
    chapter_summary="主角发现时间旅行的秘密",
    target_words=3000
)

***REMOVED*** 3. 继续创作下一章
next_chapter = creator.create_chapter(
    chapter_number=2,
    chapter_title="第二章：第一次旅行",
    chapter_summary="主角进行第一次时间旅行",
    previous_chapters_summary=chapter.summary,  ***REMOVED*** 传递前面章节摘要
    target_words=3000
)
```

***REMOVED******REMOVED*** 输出结构

```
novel_creation/outputs/{novel_title}/
├── novel_plan.json          ***REMOVED*** 小说大纲
├── metadata.json            ***REMOVED*** 元数据
├── {novel_title}_完整版.txt ***REMOVED*** 完整小说
├── chapters/                ***REMOVED*** 章节文件
│   ├── chapter_001.txt
│   ├── chapter_001_meta.json
│   ├── chapter_002.txt
│   └── ...
├── summaries/               ***REMOVED*** 章节摘要
└── drafts/                  ***REMOVED*** 草稿
```

***REMOVED******REMOVED*** 特性

***REMOVED******REMOVED******REMOVED*** 1. 字数控制（基于番茄小说爆款数据统计）

- **目标字数**：2048字（完美落点）
- **允许范围**：1500-3000字
- **上限控制**：使用 `max_new_tokens` 在生成时控制长度
- **智能截断**：超过3000字时自动截断，保留核心情节

***REMOVED******REMOVED******REMOVED*** 2. 情节节奏控制

每章按照以下节奏结构创作：
- **开头（约25%）**：快速进入情节，引入本章核心冲突
- **发展（约40%）**：展开情节，推进冲突，展现人物
- **高潮（约25%）**：冲突达到顶点或出现转折
- **结尾（约10%）**：自然过渡，为下一章埋下伏笔

***REMOVED******REMOVED******REMOVED*** 3. 对话质量优化

- **对话占比**：20-40%（确保平衡）
- **对话功能**：推进情节、展现人物、制造冲突、提供信息
- **对话风格**：保持角色语言风格一致
- **对话技巧**：避免信息转储，使用潜台词，结合动作描写

***REMOVED******REMOVED******REMOVED*** 4. 上下文管理

- 自动使用 Context Offloading 管理上下文
- 每章完成后生成摘要，用于后续章节连贯性
- 每5章进行一次上下文压缩
- **分层摘要系统**：最近章节摘要、阶段摘要、关键节点摘要

***REMOVED******REMOVED******REMOVED*** 5. 章节连贯性

- 使用前面章节的摘要保持连贯性
- 自动检查人物性格一致性
- 保持情节逻辑连贯
- **实体管理系统**：实体重要性评分、分层传递、多模型投票提取（精度95%+）

***REMOVED******REMOVED******REMOVED*** 6. 质量监控

- **单章质量检查**：每章完成后自动检查角色一致性、世界观一致性、时间线一致性
- **阶段性质量检查**：每10章进行一次综合质量评估
  - 连贯性得分
  - 人物一致性得分
  - 情节节奏得分
  - 世界观一致性得分
  - 悬念得分
  - 综合评分（低于0.7时触发警告）

***REMOVED******REMOVED******REMOVED*** 7. 渐进式大纲（100+章节）

- **整体大纲**：100-200章的整体故事框架
- **阶段大纲**：每20章一个阶段，详细规划
- **章节大纲**：每章的具体内容摘要
- 支持动态生成阶段大纲，避免一次性生成所有章节大纲

***REMOVED******REMOVED******REMOVED*** 8. 灵活创作

- 支持从任意章节开始续写
- 支持修改已有章节
- 支持调整大纲

***REMOVED******REMOVED*** 与 UniMem 的集成（未来）

当前版本不使用 UniMem，但设计上已考虑未来集成：

- 章节内容可以存储到 UniMem
- 人物信息可以存储到 UniMem
- 情节线索可以存储到 UniMem
- 使用 UniMem 检索相关章节和人物信息

***REMOVED******REMOVED*** 示例

运行示例脚本：

```bash
python novel_creation/example.py
```

***REMOVED******REMOVED*** 优化功能

***REMOVED******REMOVED******REMOVED*** Phase 1: 基础优化（已完成 ✅）

1. **字数控制**：基于番茄小说爆款数据统计，目标2048字，上限3000字
2. **实体管理系统**：实体重要性评分、分层传递、多模型投票提取
3. **渐进式大纲**：三层次大纲（整体、阶段、章节），支持100+章节
4. **分层摘要**：最近章节摘要、阶段摘要、关键节点摘要

***REMOVED******REMOVED******REMOVED*** Phase 2: 质量优化（已完成 ✅）

1. **情节节奏控制**：开头25%、发展40%、高潮25%、结尾10%
2. **对话质量优化**：对话占比20-40%，确保对话推进情节
3. **阶段性质量检查**：每10章自动评估综合质量（连贯性、人物一致性、节奏、世界观、悬念）

***REMOVED******REMOVED******REMOVED*** Phase 3: 高级优化（进行中 🔄）

1. **质量指标追踪**：持续追踪所有质量指标
2. **大纲动态调整**：根据实际创作情况调整后续大纲
3. **自适应生成策略**：根据质量反馈调整生成策略

***REMOVED******REMOVED*** 测试结果

***REMOVED******REMOVED******REMOVED*** 阶段性质量检查示例（12章测试）

```json
{
  "chapter_range": "第1-10章",
  "scores": {
    "coherence": 1.00,
    "character_consistency": 1.00,
    "plot_rhythm": 0.60,
    "worldview_consistency": 1.00,
    "suspense": 0.80,
    "overall": 0.90
  },
  "needs_attention": false
}
```

**评分说明**：
- 综合评分 0.90（优秀）
- 连贯性、人物一致性、世界观一致性均为满分
- 节奏得分 0.60（需要改进，章节长度变化较小）
- 悬念得分 0.80（良好）

***REMOVED******REMOVED*** 注意事项

1. **LLM 配置**：确保 `react.py` 中的 LLM 配置正确
2. **上下文长度**：长篇小说创作时注意上下文长度管理
3. **创作质量**：系统自动进行质量检查，每10章生成质量报告
4. **资源消耗**：长篇小说创作需要较多 Token，注意成本控制
5. **字数控制**：虽然目标2048字，但实际可能在2500-3000字之间（符合番茄小说统计建议）