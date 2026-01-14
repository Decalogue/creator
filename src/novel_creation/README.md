# 基于 ReAct 的中长篇小说创作系统

## 概述

利用结合了 Cursor 和 Manus 思路的 ReAct 系统进行中长篇小说创作，充分利用以下特性：

- **工具动态发现**：Agent 可以主动查找工具文档
- **上下文缩减**：自动管理上下文，避免溢出
- **分层行动空间**：灵活使用 L1/L2/L3 工具
- **多 Agent 协作**：可选的多 Agent 协作模式

## 设计思路

### 1. 分章节创作

将长篇小说分解为多个章节，每章独立创作，降低上下文压力。

### 2. 上下文管理

- 每章完成后进行 Compaction，保留关键信息
- 使用章节摘要确保前后章节连贯性
- 每5章进行一次上下文压缩

### 3. 渐进式创作

支持边写边改，迭代优化。可以：
- 从任意章节开始续写
- 修改已有章节
- 调整大纲

## 使用方法

### 基本使用

```python
from novel_creation import ReactNovelCreator

# 创建小说创作器
creator = ReactNovelCreator(
    novel_title="时空旅者的日记",
    enable_context_offloading=True
)

# 创作小说
result = creator.create_novel(
    genre="科幻",
    theme="时间旅行、平行世界、人性探索",
    target_chapters=20,
    words_per_chapter=3000,
    start_from_chapter=1
)
```

### 分步创作

```python
# 1. 创建大纲
plan = creator.create_novel_plan(
    genre="科幻",
    theme="时间旅行",
    target_chapters=20,
    words_per_chapter=3000
)

# 2. 创作单个章节
chapter = creator.create_chapter(
    chapter_number=1,
    chapter_title="第一章：起点",
    chapter_summary="主角发现时间旅行的秘密",
    target_words=3000
)

# 3. 继续创作下一章
next_chapter = creator.create_chapter(
    chapter_number=2,
    chapter_title="第二章：第一次旅行",
    chapter_summary="主角进行第一次时间旅行",
    previous_chapters_summary=chapter.summary,  # 传递前面章节摘要
    target_words=3000
)
```

## 输出结构

```
novel_creation/outputs/{novel_title}/
├── novel_plan.json          # 小说大纲
├── metadata.json            # 元数据
├── {novel_title}_完整版.txt # 完整小说
├── chapters/                # 章节文件
│   ├── chapter_001.txt
│   ├── chapter_001_meta.json
│   ├── chapter_002.txt
│   └── ...
├── summaries/               # 章节摘要
└── drafts/                  # 草稿
```

## 特性

### 1. 上下文管理

- 自动使用 Context Offloading 管理上下文
- 每章完成后生成摘要，用于后续章节连贯性
- 每5章进行一次上下文压缩

### 2. 章节连贯性

- 使用前面章节的摘要保持连贯性
- 自动检查人物性格一致性
- 保持情节逻辑连贯

### 3. 灵活创作

- 支持从任意章节开始续写
- 支持修改已有章节
- 支持调整大纲

## 与 UniMem 的集成（未来）

当前版本不使用 UniMem，但设计上已考虑未来集成：

- 章节内容可以存储到 UniMem
- 人物信息可以存储到 UniMem
- 情节线索可以存储到 UniMem
- 使用 UniMem 检索相关章节和人物信息

## 示例

运行示例脚本：

```bash
python novel_creation/example.py
```

## 注意事项

1. **LLM 配置**：确保 `react.py` 中的 LLM 配置正确
2. **上下文长度**：长篇小说创作时注意上下文长度管理
3. **创作质量**：可以通过调整提示词和迭代次数提升质量
4. **资源消耗**：长篇小说创作需要较多 Token，注意成本控制
