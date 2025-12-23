# Skills 系统

基于 Anthropic Skills 设计的技能系统，实现渐进式披露机制。

## 核心概念

### Skills 是什么？

Skills 是一个包含"说明文档、脚本和资源"的文件夹，提供可重复调用的专业 SOP（标准操作程序）+ 说明书，由模型按需加载。

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
├── calculator/          # Calculator Skill
│   ├── SKILL.md         # 核心文件（元数据 + 主体）
│   ├── examples.md      # 资源文件（第三层）
│   └── calculator.py    # 脚本文件（第三层）
└── weather/             # Weather Skill
    ├── SKILL.md
    ├── cities.md
    └── weather_api.md
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

## 使用方法

### 基本使用

```python
from skills import default_manager

# 列出所有 Skills
skills = default_manager.list_skills()
print(skills)  # ['calculator', 'weather']

# 获取 Skill
calculator = default_manager.get_skill('calculator')

# 获取元数据（第一层，轻量级）
metadata = calculator.metadata
print(metadata.name)  # calculator
print(metadata.description)  # 执行数学计算...

# 加载主体内容（第二层）
body = calculator.load_body()

# 加载资源文件（第三层）
examples = calculator.load_resource('examples.md')
```

### 根据查询选择 Skills

```python
# 根据用户查询自动选择相关 Skills
query = "帮我计算 10 * 5 + 20"
selected_skills = default_manager.select_skills(query)
# 返回: [<Skill: calculator>]

# 获取相关 Skills 的上下文（用于传递给 LLM）
context = default_manager.get_context_for_query(query, level=2)
```

### 渐进式加载

```python
skill = default_manager.get_skill('calculator')

# 第一层：只加载元数据（~100 tokens）
context_level1 = skill.get_context(level=1)

# 第二层：加载主体内容（<5k tokens）
context_level2 = skill.get_context(level=2)

# 第三层：加载所有资源（无限制）
context_level3 = skill.get_context(level=3)
```

## 与 LLM 集成

```python
from skills import default_manager
from llm.chat import ark_deepseek_v3_2

def chat_with_skills(user_query: str):
    # 1. 根据查询选择相关 Skills
    selected_skills = default_manager.select_skills(user_query)
    
    # 2. 获取 Skills 上下文（第二层：主体内容）
    skills_context = default_manager.get_context_for_query(user_query, level=2)
    
    # 3. 构建消息
    messages = [
        {
            "role": "system",
            "content": f"你是一个 AI 助手，可以使用以下 Skills：\n\n{skills_context}"
        },
        {
            "role": "user",
            "content": user_query
        }
    ]
    
    # 4. 调用 LLM
    response = ark_deepseek_v3_2(messages)
    return response
```

## 创建新 Skill

1. 在 `skills/` 目录下创建新文件夹（如 `my_skill/`）
2. 创建 `SKILL.md` 文件，包含元数据和主体内容
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
