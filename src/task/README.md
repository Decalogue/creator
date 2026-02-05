# task — 任务层

按创作/业务类型分子包，与 config 领域对应。

| 子包 | 说明 |
|------|------|
| **novel** | 小说创作（原 novel_creation）：ReAct 创作、质检、实体提取等。 |

## 使用

```python
from task import ReactNovelCreator, NovelChapter
# 或
from task.novel import ReactNovelCreator, NovelChapter
```

详见各子目录 README（如 `task/novel/README.md`）。
