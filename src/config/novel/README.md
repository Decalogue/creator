# config/novel — 小说创作配置与 prompt

小说创作相关配置与 prompt 模板，供 `task.novel` 使用，集中管理便于调整与复用。

## 模块

- **defaults.py**：默认字数、节奏系数、对话占比、token 限制等常量。
- **prompts.py**：实体提取、JSON 修复、对话质量要求等 prompt 模板。

## 使用

```python
from config.novel import (
    DEFAULT_TARGET_WORDS,
    MIN_TOKEN_LIMIT,
    POSITION_ADJUSTMENTS,
    get_entity_extraction_prompt,
    DIALOGUE_QUALITY_INSTRUCTION,
)
```

## 依赖

- 无外部依赖，仅标准库；被 `task.novel` 引用。
