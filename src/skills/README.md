***REMOVED*** Skills 系统使用指南

***REMOVED******REMOVED*** 简介

基于 Anthropic Skills 设计的技能系统，实现渐进式披露机制。Skills 是一个包含"说明文档、脚本和资源"的文件夹，提供可重复调用的专业 SOP（标准操作程序）+ 说明书，由模型按需加载。

**核心特点**：
- **渐进式披露**：按需加载，节省 token
- **自动选择**：根据触发词和标签自动选择相关 Skills
- **模块化**：每个 Skill 是独立的文件夹
- **标准化**：统一的 SKILL.md 格式

***REMOVED******REMOVED*** 核心概念

***REMOVED******REMOVED******REMOVED*** 渐进式披露机制

每个 Skill 包含三层内容，按需加载到上下文窗口：

| 层级 | 内容 | 加载时机 | Token 数量 |
|------|------|----------|-----------|
| 1 | SKILL.md 元数据 (YAML) | 始终加载 | ~100 |
| 2 | SKILL.md 主体 (Markdown) | 触发时加载 | <5k |
| 3+ | 绑定的文本文件、脚本和数据 | 按需调用 | 无限制* |

***REMOVED******REMOVED*** 目录结构

```
skills/
├── __init__.py          ***REMOVED*** 模块导出
├── skill.py             ***REMOVED*** Skill 类定义
├── manager.py          ***REMOVED*** Skill Manager
├── example.py          ***REMOVED*** 使用示例
├── test.py             ***REMOVED*** 测试代码
├── calculator/          ***REMOVED*** Calculator Skill
│   ├── SKILL.md        ***REMOVED*** 核心文件（元数据 + 主体）
│   ├── examples.md     ***REMOVED*** 资源文件（第三层）
│   └── calculator.py   ***REMOVED*** 脚本文件（第三层）
└── weather/            ***REMOVED*** Weather Skill
    ├── SKILL.md
    ├── cities.md
    └── weather_api.md
```

***REMOVED******REMOVED*** 快速开始（5 分钟上手）

***REMOVED******REMOVED******REMOVED*** 1. 导入模块

```python
from skills import default_manager
```

***REMOVED******REMOVED******REMOVED*** 2. 列出所有 Skills

```python
skills = default_manager.list_skills()
print(skills)  ***REMOVED*** ['calculator', 'weather']
```

***REMOVED******REMOVED******REMOVED*** 3. 获取 Skill 元数据（第一层）

```python
calculator = default_manager.get_skill('calculator')
metadata = calculator.metadata

print(metadata.name)        ***REMOVED*** calculator
print(metadata.description) ***REMOVED*** 执行数学计算...
print(metadata.tags)        ***REMOVED*** ['math', 'calculation', 'calculator']
print(metadata.triggers)   ***REMOVED*** ['计算', '算', '数学', ...]
```

***REMOVED******REMOVED******REMOVED*** 4. 渐进式加载

```python
***REMOVED*** 第一层：元数据（~100 tokens，始终加载）
context_level1 = calculator.get_context(level=1)

***REMOVED*** 第二层：主体内容（<5k tokens，触发时加载）
context_level2 = calculator.get_context(level=2)

***REMOVED*** 第三层：所有资源（无限制，按需加载）
context_level3 = calculator.get_context(level=3)
```

***REMOVED******REMOVED******REMOVED*** 5. 根据查询选择 Skills

```python
query = "帮我计算 10 * 5 + 20"
selected_skills = default_manager.select_skills(query)
***REMOVED*** 返回: [<Skill: calculator>]

***REMOVED*** 获取相关 Skills 的上下文
context = default_manager.get_context_for_query(query, level=2)
```

***REMOVED******REMOVED******REMOVED*** 6. 运行示例

```bash
cd /root/data/AI/creator/src

***REMOVED*** 运行完整示例
python -m skills.example

***REMOVED*** 或直接运行
python skills/example.py

***REMOVED*** 运行测试
python -m skills.test
```

***REMOVED******REMOVED*** SKILL.md 格式

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

***REMOVED*** Skill 名称

***REMOVED******REMOVED*** 功能描述

详细的功能说明...

***REMOVED******REMOVED*** 使用方法

使用说明...

***REMOVED******REMOVED*** 相关资源

- `resource1.md`: 资源说明
- `script.py`: 脚本说明
```

***REMOVED******REMOVED*** 详细使用指南

***REMOVED******REMOVED******REMOVED*** 基本使用

```python
from skills import default_manager

***REMOVED*** 列出所有 Skills
skills = default_manager.list_skills()
print(skills)  ***REMOVED*** ['calculator', 'weather']

***REMOVED*** 获取 Skill
calculator = default_manager.get_skill('calculator')

***REMOVED*** 获取元数据（第一层，轻量级）
metadata = calculator.metadata
print(metadata.name)  ***REMOVED*** calculator
print(metadata.description)  ***REMOVED*** 执行数学计算...

***REMOVED*** 加载主体内容（第二层）
body = calculator.load_body()

***REMOVED*** 加载资源文件（第三层）
examples = calculator.load_resource('examples.md')
```

***REMOVED******REMOVED******REMOVED*** 根据查询选择 Skills

```python
***REMOVED*** 根据用户查询自动选择相关 Skills
query = "帮我计算 10 * 5 + 20"
selected_skills = default_manager.select_skills(query)
***REMOVED*** 返回: [<Skill: calculator>]

***REMOVED*** 获取相关 Skills 的上下文（用于传递给 LLM）
context = default_manager.get_context_for_query(query, level=2)
```

***REMOVED******REMOVED******REMOVED*** 渐进式加载

```python
skill = default_manager.get_skill('calculator')

***REMOVED*** 第一层：只加载元数据（~100 tokens）
context_level1 = skill.get_context(level=1)

***REMOVED*** 第二层：加载主体内容（<5k tokens）
context_level2 = skill.get_context(level=2)

***REMOVED*** 第三层：加载所有资源（无限制）
context_level3 = skill.get_context(level=3)
```

***REMOVED******REMOVED******REMOVED*** 与 LLM 集成

```python
from skills import default_manager
from llm.chat import ark_deepseek_v3_2

def chat_with_skills(user_query: str):
    ***REMOVED*** 1. 根据查询选择相关 Skills
    selected_skills = default_manager.select_skills(user_query)
    
    ***REMOVED*** 2. 获取 Skills 上下文（第二层：主体内容）
    skills_context = default_manager.get_context_for_query(user_query, level=2)
    
    ***REMOVED*** 3. 构建消息
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
    
    ***REMOVED*** 4. 调用 LLM
    _, response = ark_deepseek_v3_2(messages)
    return response

***REMOVED*** 使用示例
result = chat_with_skills("帮我计算 25 * 8 + 100")
print(result)
```

***REMOVED******REMOVED*** 内置 Skills

***REMOVED******REMOVED******REMOVED*** 1. Calculator Skill（计算器）

- **Skill 名**: `calculator`
- **功能**: 执行数学计算，支持基本运算和复杂表达式
- **标签**: `math`, `calculation`, `calculator`
- **触发词**: `计算`, `算`, `数学`, `加减乘除`, `calculator`, `calculate`

**资源文件**:
- `examples.md`: 更多计算示例
- `calculator.py`: Python 实现脚本

***REMOVED******REMOVED******REMOVED*** 2. Weather Skill（天气查询）

- **Skill 名**: `weather`
- **功能**: 查询指定城市的天气信息
- **标签**: `weather`, `天气`, `forecast`, `预报`
- **触发词**: `天气`, `温度`, `预报`, `weather`, `temperature`, `forecast`

**资源文件**:
- `cities.md`: 支持的城市列表
- `weather_api.md`: 天气 API 使用说明

***REMOVED******REMOVED*** API 参考

***REMOVED******REMOVED******REMOVED*** SkillManager（Skill 管理器）

- `scan_skills() -> None`: 扫描 Skills 目录，加载所有 Skills 的元数据
- `list_skills() -> List[str]`: 列出所有可用的 Skill 名称
- `get_skill(name: str) -> Optional[Skill]`: 获取指定的 Skill
- `get_metadata(name: str) -> Optional[SkillMetadata]`: 获取 Skill 的元数据（第一层，轻量级）
- `get_all_metadata() -> List[SkillMetadata]`: 获取所有 Skills 的元数据列表（用于模型选择）
- `select_skills(query: str, max_skills: int = 5) -> List[Skill]`: 根据查询选择相关的 Skills
- `get_context_for_query(query: str, level: int = 2) -> str`: 根据查询获取相关 Skills 的上下文
- `reload_skill(name: str) -> None`: 重新加载指定的 Skill

***REMOVED******REMOVED******REMOVED*** Skill 类

- `metadata: SkillMetadata`: 获取元数据（第一层）
- `name: str`: Skill 名称
- `description: str`: Skill 描述
- `load_body() -> str`: 加载 SKILL.md 的主体内容（第二层，触发时加载）
- `load_resource(filename: str) -> str`: 加载资源文件（第三层，按需加载）
- `list_resources() -> List[str]`: 列出所有可用的资源文件
- `get_context(level: int = 1) -> str`: 获取指定层级的上下文内容
- `estimate_tokens(level: int = 1) -> int`: 估算指定层级的 token 数量

***REMOVED******REMOVED******REMOVED*** SkillMetadata（元数据）

- `name: str`: Skill 名称
- `description: str`: Skill 描述
- `version: str`: 版本号
- `author: Optional[str]`: 作者
- `tags: List[str]`: 标签列表
- `triggers: List[str]`: 触发关键词列表

***REMOVED******REMOVED*** 创建新 Skill

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

***REMOVED*** My Skill

***REMOVED******REMOVED*** 功能描述

详细的功能说明...

***REMOVED******REMOVED*** 使用方法

使用说明...
```

3. 可选：添加资源文件（脚本、数据、文档等）
4. 重新扫描：`default_manager.scan_skills()`

***REMOVED******REMOVED*** 优势

1. **模块化**：每个 Skill 是独立的文件夹，易于管理
2. **渐进式加载**：按需加载，节省 token
3. **可发现性**：通过触发词和标签自动选择相关 Skills
4. **可扩展性**：轻松添加新 Skills 和资源文件
5. **标准化**：统一的 SKILL.md 格式

***REMOVED******REMOVED*** 注意事项

1. 每个 Skill 目录必须包含 `SKILL.md` 文件
2. YAML front matter 必须正确格式
3. 资源文件路径相对于 Skill 目录
4. 建议每个 Skill 的元数据保持在 ~100 tokens 以内
5. 主体内容建议控制在 <5k tokens
6. 触发词和标签应该准确反映 Skill 的功能，以便自动选择

***REMOVED******REMOVED*** 下一步

1. 查看 `example.py` 学习更多用法和完整示例
2. 运行 `python -m skills.example` 查看所有示例
3. 运行 `python -m skills.test` 验证功能
4. 参考现有 Skills 实现创建自己的 Skill
