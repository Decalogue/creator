# Skills 系统快速开始

## 5 分钟上手

### 1. 导入模块

```python
from skills import default_manager
```

### 2. 列出所有 Skills

```python
skills = default_manager.list_skills()
print(skills)  # ['calculator', 'weather']
```

### 3. 获取 Skill 元数据（第一层）

```python
calculator = default_manager.get_skill('calculator')
metadata = calculator.metadata

print(metadata.name)        # calculator
print(metadata.description) # 执行数学计算...
print(metadata.tags)        # ['math', 'calculation', 'calculator']
print(metadata.triggers)   # ['计算', '算', '数学', ...]
```

### 4. 渐进式加载

```python
# 第一层：元数据（~100 tokens，始终加载）
context_level1 = calculator.get_context(level=1)

# 第二层：主体内容（<5k tokens，触发时加载）
context_level2 = calculator.get_context(level=2)

# 第三层：所有资源（无限制，按需加载）
context_level3 = calculator.get_context(level=3)
```

### 5. 根据查询选择 Skills

```python
query = "帮我计算 10 * 5 + 20"
selected_skills = default_manager.select_skills(query)
# 返回: [<Skill: calculator>]

# 获取相关 Skills 的上下文
context = default_manager.get_context_for_query(query, level=2)
```

### 6. 与 LLM 集成

```python
from skills import default_manager
from llm.chat import ark_deepseek_v3_2

def chat_with_skills(user_query: str):
    # 选择相关 Skills
    skills_context = default_manager.get_context_for_query(user_query, level=2)
    
    # 构建消息
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
    
    # 调用 LLM
    _, response = ark_deepseek_v3_2(messages)
    return response

# 使用
result = chat_with_skills("帮我计算 25 * 8 + 100")
```

## 创建新 Skill

1. 在 `skills/` 目录下创建新文件夹（如 `my_skill/`）
2. 创建 `SKILL.md` 文件：

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

## 运行示例

```bash
# 运行基础示例
python skills/example.py

# 运行测试
python skills/test_skills.py
```

## 核心概念

- **渐进式披露**：按需加载，节省 token
- **自动选择**：根据触发词和标签自动选择相关 Skills
- **模块化**：每个 Skill 是独立的文件夹
- **标准化**：统一的 SKILL.md 格式
