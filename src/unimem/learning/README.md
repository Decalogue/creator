***REMOVED*** 小说模式学习模块

***REMOVED******REMOVED*** 概述

从大量优质小说中提取创作模式，并存储到记忆系统中，用于改进动态编排和创作质量。

***REMOVED******REMOVED*** 功能

1. **小说数据处理**：提取结构、情节、人物、节奏等特征
2. **模式提取**：识别情节类型、节奏模式、人物关系等
3. **记忆存储**：将提取的模式存储到 UniMem LTM 层

***REMOVED******REMOVED*** 使用方法

***REMOVED******REMOVED******REMOVED*** 批量学习模式

```bash
***REMOVED*** 处理所有小说（默认目录）
cd /root/data/AI/creator/src
python -m unimem.learning.batch_learn_novels \
    --novel_dir /root/data/AI/creator/src/data/小说 \
    --store \
    --output results/novel_patterns.json

***REMOVED*** 限制处理数量（用于测试）
python -m unimem.learning.batch_learn_novels \
    --novel_dir /root/data/AI/creator/src/data/小说 \
    --limit 10 \
    --store \
    --output results/novel_patterns_test.json
```

***REMOVED******REMOVED******REMOVED*** 单独处理一本小说

```python
from unimem.core import UniMem
from unimem.learning.novel_processor import NovelProcessor

***REMOVED*** 初始化
unimem = UniMem()
processor = NovelProcessor(unimem_instance=unimem)

***REMOVED*** 处理单本小说
result = processor.process_novel("/path/to/novel.txt")

***REMOVED*** 存储模式
processor.store_patterns_to_memory(result)
```

***REMOVED******REMOVED*** 提取的模式类型

***REMOVED******REMOVED******REMOVED*** 1. 情节模式 (Plot Patterns)
- 打脸情节
- 装逼情节
- 反转情节
- 高潮情节
- 情感情节
- 冲突情节

***REMOVED******REMOVED******REMOVED*** 2. 节奏模式 (Rhythm Patterns)
- 平均章节长度
- 章节数量
- 总字数
- 章节长度分布

***REMOVED******REMOVED******REMOVED*** 3. 人物模式 (Character Patterns)
- 主要人物列表
- 人物出现频率
- 人物关系

***REMOVED******REMOVED******REMOVED*** 4. 结构模式 (Structure Patterns)
- 章节划分
- 章节标题格式
- 整体结构

***REMOVED******REMOVED*** 数据格式

***REMOVED******REMOVED******REMOVED*** 输入
- TXT 格式小说文件
- 支持 UTF-8 编码
- 自动检测章节标题

***REMOVED******REMOVED******REMOVED*** 输出
```json
{
  "metadata": {
    "title": "花千骨",
    "category": "仙侠",
    "filename": "..."
  },
  "structure": {
    "chapters": [...],
    "chapter_count": 50,
    "total_length": 1000000
  },
  "plot_points": [...],
  "characters": [...],
  "rhythm": {...}
}
```

***REMOVED******REMOVED*** 注意事项

1. **处理速度**：大规模处理可能需要较长时间，建议分批处理
2. **内存占用**：每本小说会加载到内存，注意内存使用
3. **编码问题**：自动处理编码错误，但可能丢失部分内容
4. **存储容量**：大量模式会占用较多存储空间

***REMOVED******REMOVED*** 后续优化方向

1. 使用 NER 模型提取更准确的人物信息
2. 使用情感分析识别情感节点
3. 使用文本分类识别情节类型
4. 提取更复杂的模式（如人物关系网络、情节发展轨迹）

