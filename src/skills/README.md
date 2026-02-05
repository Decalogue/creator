# skills — 技能/能力层（创作相关）

## 简介

基于 Anthropic Skills 设计的技能系统，实现渐进式披露机制，**主要服务于 Creator 创作流程**：提供可重复调用的 SOP（标准操作程序）、风格说明、创作规范等，由编排层或创作助手按需加载，与 `tools` 互补（tools 侧重可执行工具调用，skills 侧重文档与流程说明）。

**核心特点**：
- **渐进式披露**：按需加载，节省 token
- **自动选择**：根据触发词和标签自动选择相关 Skills
- **模块化**：每个 Skill 是独立文件夹
- **标准化**：统一的 SKILL.md 格式

## 核心概念

### 渐进式披露机制

每个 Skill 包含三层内容，按需加载到上下文窗口：

| 层级 | 内容 | 加载时机 | Token 数量 |
|------|------|----------|-----------|
| 1 | SKILL.md 元数据 (YAML) | 始终加载 | ~100 |
| 2 | SKILL.md 主体 (Markdown) | 触发时加载 | <5k |
| 3+ | 绑定的文本文件、脚本和数据 | 按需调用 | 无限制* |

## 目录结构

```
skills/
├── __init__.py          # 模块导出
├── skill.py             # Skill 类定义
├── manager.py           # Skill Manager
├── example.py           # 使用示例
├── test.py              # 测试代码
├── chapter_creation_sop/ # 内置：章节创作规范
│   └── SKILL.md         # 必需：元数据 + 主体
└── <your_skill>/        # 创作相关 Skill（自行添加）
    ├── SKILL.md         # 必需：元数据 + 主体
    └── ...              # 可选：资源文件
```

**内置 Skill**：`chapter_creation_sop`（章节创作规范），见下方「内置 Skills」；可按需添加更多创作相关 Skill（如短剧节奏、对话 SOP 等）。

## 快速开始（5 分钟上手）

### 1. 导入模块

```python
from skills import default_manager
```

### 2. 列出所有 Skills

```python
skills = default_manager.list_skills()
print(skills)  # 例如 []，添加创作相关 Skill 后为 ['节奏规范', '对话SOP', ...]
```

### 3. 获取 Skill 元数据（第一层）

```python
skill = default_manager.get_skill('your_skill_name')  # 创作相关 Skill 名称
if skill:
    metadata = skill.metadata
    print(metadata.name, metadata.description, metadata.tags, metadata.triggers)
```

### 4. 渐进式加载

```python
skill = default_manager.get_skill('your_skill_name')
if skill:
    context_level1 = skill.get_context(level=1)   # 元数据
    context_level2 = skill.get_context(level=2)   # 主体
    context_level3 = skill.get_context(level=3)   # 含资源
```

### 5. 根据查询选择 Skills

```python
query = "本章对话占比与节奏要求"
selected_skills = default_manager.select_skills(query, max_skills=3)
context = default_manager.get_context_for_query(query, level=2)
```

### 6. 运行示例

```bash
cd /root/data/AI/creator/src

# 运行完整示例
python -m skills.example

# 或直接运行
python skills/example.py

# 运行测试
python -m skills.test
```

## SKILL.md 格式

每个 Skill 必须包含 `SKILL.md` 文件，格式如下：

```markdown
---
name: skill_name
description: Skill 描述
version: 1.0.0
author: 作者名
tags:
  - tag1
  - tag2
triggers:
  - 触发词1
  - 触发词2
---

# Skill 名称

## 功能描述

详细的功能说明...

## 使用方法

使用说明...

## 相关资源

- `resource1.md`: 资源说明
- `script.py`: 脚本说明
```

## 详细使用指南

### 基本使用

```python
from skills import default_manager

# 列出所有 Skills（添加创作相关 Skill 后会有内容）
skills = default_manager.list_skills()
print(skills)

# 获取 Skill
skill = default_manager.get_skill('your_skill_name')  # 创作相关 Skill 名称
if skill:
    metadata = skill.metadata
    print(metadata.name, metadata.description)
    body = skill.load_body()
    resources = skill.list_resources()
```

### 根据查询选择 Skills

```python
query = "本章对话占比与节奏要求"
selected_skills = default_manager.select_skills(query, max_skills=3)
context = default_manager.get_context_for_query(query, level=2)
```

### 渐进式加载

```python
skill = default_manager.get_skill('your_skill_name')

# 第一层：只加载元数据（~100 tokens）
context_level1 = skill.get_context(level=1)

# 第二层：加载主体内容（<5k tokens）
context_level2 = skill.get_context(level=2)

# 第三层：加载所有资源（无限制）
context_level3 = skill.get_context(level=3)
```

### 与创作流程集成

```python
from skills import default_manager

def get_creation_context(user_query: str) -> str:
    """根据创作相关查询获取 Skill 上下文，供编排层或创作助手注入"""
    selected = default_manager.select_skills(user_query, max_skills=3)
    return default_manager.get_context_for_query(user_query, level=2)

# 示例：获取「对话占比与节奏」相关规范
context = get_creation_context("本章对话占比与节奏要求")
# 将 context 加入 system 或 user 消息后调用 LLM
```

## 内置 Skills

### 内置 Skill：章节创作规范

| Skill 名称 | 说明 | 触发词示例 |
|------------|------|------------|
| **章节创作规范** | 单章创作的 SOP：字数（2048/1500～3000）、节奏（25%/40%/25%/10%）、对话占比（20%～40%）与一致性要点，与 `task/novel` 配置对齐 | 写本章、续写、字数、节奏、对话占比、章节创作 |

**使用方法**（在 `src` 目录下执行）：

```python
from skills import default_manager

# 按创作任务选择并获取上下文（推荐）
query = "写本章，注意字数与节奏"
selected = default_manager.select_skills(query, max_skills=3)
context = default_manager.get_context_for_query(query, level=2)
# 将 context 注入 system 或 user 后调用 LLM

# 或直接按名称获取
skill = default_manager.get_skill("章节创作规范")
if skill:
    level1 = skill.get_context(level=1)   # 仅元数据
    level2 = skill.get_context(level=2)   # 元数据 + 主体（SOP 全文）
```

**运行示例与测试**：

```bash
cd src
python -m skills.example    # 列出 Skills、渐进式披露、按查询选择
python -m skills.test       # 单元测试（含本章创作规范相关断言）
```

### 添加更多 Skill

在 `skills/` 下新建子目录并放入 `SKILL.md`，例如：

- 短剧节奏规范、每集时长与悬念节奏
- 对话质量 SOP（占比、心理活动上限等）
- 世界观/角色一致性检查清单

## API 参考

### SkillManager（Skill 管理器）

- `scan_skills() -> None`: 扫描 Skills 目录，加载所有 Skills 的元数据
- `list_skills() -> List[str]`: 列出所有可用的 Skill 名称
- `get_skill(name: str) -> Optional[Skill]`: 获取指定的 Skill
- `get_metadata(name: str) -> Optional[SkillMetadata]`: 获取 Skill 的元数据（第一层，轻量级）
- `get_all_metadata() -> List[SkillMetadata]`: 获取所有 Skills 的元数据列表（用于模型选择）
- `select_skills(query: str, max_skills: int = 5) -> List[Skill]`: 根据查询选择相关的 Skills
- `get_context_for_query(query: str, level: int = 2) -> str`: 根据查询获取相关 Skills 的上下文
- `reload_skill(name: str) -> None`: 重新加载指定的 Skill

### Skill 类

- `metadata: SkillMetadata`: 获取元数据（第一层）
- `name: str`: Skill 名称
- `description: str`: Skill 描述
- `load_body() -> str`: 加载 SKILL.md 的主体内容（第二层，触发时加载）
- `load_resource(filename: str) -> str`: 加载资源文件（第三层，按需加载）
- `list_resources() -> List[str]`: 列出所有可用的资源文件
- `get_context(level: int = 1) -> str`: 获取指定层级的上下文内容
- `estimate_tokens(level: int = 1) -> int`: 估算指定层级的 token 数量

### SkillMetadata（元数据）

- `name: str`: Skill 名称
- `description: str`: Skill 描述
- `version: str`: 版本号
- `author: Optional[str]`: 作者
- `tags: List[str]`: 标签列表
- `triggers: List[str]`: 触发关键词列表

## 创建新 Skill

1. 在 `skills/` 目录下创建新文件夹（如 `my_skill/`）
2. 创建 `SKILL.md` 文件，包含元数据和主体内容：

```markdown
---
name: my_skill
description: 我的 Skill 描述
version: 1.0.0
tags:
  - tag1
  - tag2
triggers:
  - 触发词1
  - 触发词2
---

# My Skill

## 功能描述

详细的功能说明...

## 使用方法

使用说明...
```

3. 可选：添加资源文件（脚本、数据、文档等）
4. 重新扫描：`default_manager.scan_skills()`

## 优势

1. **模块化**：每个 Skill 是独立的文件夹，易于管理
2. **渐进式加载**：按需加载，节省 token
3. **可发现性**：通过触发词和标签自动选择相关 Skills
4. **可扩展性**：轻松添加新 Skills 和资源文件
5. **标准化**：统一的 SKILL.md 格式

## 注意事项

1. 每个 Skill 目录必须包含 `SKILL.md` 文件
2. YAML front matter 必须正确格式
3. 资源文件路径相对于 Skill 目录
4. 建议每个 Skill 的元数据保持在 ~100 tokens 以内
5. 主体内容建议控制在 <5k tokens
6. 触发词和标签应该准确反映 Skill 的功能，以便自动选择

## 与创作流程的关系

- **定位**：与 `tools` 互补。tools 提供可执行工具（计算、查询、文档检索等），skills 提供 SOP、风格指南、创作规范等文档与资源，供编排层或创作助手按需注入上下文。
- **扩展**：新增创作相关 Skill（如「短剧节奏规范」「对话质量 SOP」等）时，在 `skills/` 下新建目录、编写 `SKILL.md` 与资源文件，由 `default_manager` 扫描即可被 `select_skills` / `get_context_for_query` 使用。

## 下一步

1. 查看 `example.py` 学习用法
2. 运行 `python -m skills.example` 查看示例
3. 运行 `python -m skills.test` 验证功能
4. 在 `skills/` 下新建目录、编写 `SKILL.md` 与资源文件，添加创作相关 Skill
