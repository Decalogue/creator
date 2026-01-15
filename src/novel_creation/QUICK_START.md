***REMOVED*** 小说创作系统 - 快速开始指南

***REMOVED******REMOVED*** 🚀 快速开始

***REMOVED******REMOVED******REMOVED*** 1. 基础使用

```python
from novel_creation.react_novel_creator import ReactNovelCreator

***REMOVED*** 创建创作器（启用所有优化功能）
creator = ReactNovelCreator(
    novel_title="我的小说",
    enable_enhanced_extraction=True,  ***REMOVED*** 增强实体提取
    enable_quality_check=True  ***REMOVED*** 质量检查
)

***REMOVED*** 创作完整小说
result = creator.create_novel(
    genre="科幻",
    theme="时间旅行、平行世界",
    target_chapters=10,
    words_per_chapter=3000
)

print(f"创作完成！共 {result['total_chapters']} 章，{result['total_words']} 字")
print(f"输出目录：{result['output_dir']}")
```

***REMOVED******REMOVED******REMOVED*** 2. 分步创作

```python
***REMOVED*** 1. 创建大纲
plan = creator.create_novel_plan(
    genre="科幻",
    theme="时间旅行",
    target_chapters=10,
    words_per_chapter=3000
)

***REMOVED*** 2. 逐章创作
previous_summary = ""
for chapter_info in plan['chapter_outline']:
    chapter = creator.create_chapter(
        chapter_number=chapter_info['chapter_number'],
        chapter_title=chapter_info['title'],
        chapter_summary=chapter_info['summary'],
        previous_chapters_summary=previous_summary,
        target_words=3000
    )
    
    ***REMOVED*** 检查质量问题
    quality = chapter.metadata.get('quality_check', {})
    if quality.get('total_issues', 0) > 0:
        print(f"⚠️ 第{chapter.chapter_number}章发现问题：{quality['total_issues']}个")
        for issue in quality['issues'][:3]:  ***REMOVED*** 显示前3个问题
            print(f"  - {issue['description']}")
    
    ***REMOVED*** 更新摘要
    if previous_summary:
        previous_summary += f"\n\n第{chapter.chapter_number}章：{chapter.title}\n{chapter.summary}"
    else:
        previous_summary = f"第{chapter.chapter_number}章：{chapter.title}\n{chapter.summary}"
```

***REMOVED******REMOVED******REMOVED*** 3. 使用统一编排器

```python
from novel_creation.unified_orchestrator import ReActOrchestrator, HybridOrchestrator

***REMOVED*** ReAct 编排器
orchestrator = ReActOrchestrator(
    novel_title="我的小说",
    enable_creative_context=True,
    enable_unimem=True  ***REMOVED*** 可选：需要 UniMem
)

chapter = orchestrator.create_chapter(
    chapter_number=1,
    chapter_title="第一章",
    chapter_summary="主角发现时间旅行的秘密",
    target_words=3000
)

***REMOVED*** 混合编排器（自动选择编排方式）
hybrid = HybridOrchestrator(novel_title="我的小说")

chapter = hybrid.create_chapter(
    chapter_number=1,
    chapter_title="第一章",
    chapter_summary="主角进行激烈的战斗",  ***REMOVED*** 包含"战斗"，会选择 Puppeteer（如果可用）
    target_words=3000
)
```

***REMOVED******REMOVED*** 📋 配置选项

***REMOVED******REMOVED******REMOVED*** ReactNovelCreator 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `novel_title` | str | 必需 | 小说标题 |
| `output_dir` | Path | None | 输出目录（默认：outputs/{novel_title}） |
| `enable_context_offloading` | bool | True | 启用上下文卸载 |
| `enable_creative_context` | bool | True | 启用创作上下文系统（语义网格） |
| `enable_enhanced_extraction` | bool | True | 启用增强实体提取（LLM 辅助） |
| `enable_unimem` | bool | False | 启用 UniMem 长期记忆 |
| `enable_quality_check` | bool | True | 启用质量检查 |

***REMOVED******REMOVED******REMOVED*** 推荐配置

**高质量创作（推荐）**：
```python
creator = ReactNovelCreator(
    novel_title="我的小说",
    enable_context_offloading=True,
    enable_creative_context=True,
    enable_enhanced_extraction=True,
    enable_unimem=True,  ***REMOVED*** 需要 UniMem 服务
    enable_quality_check=True
)
```

**快速创作（节省 Token）**：
```python
creator = ReactNovelCreator(
    novel_title="我的小说",
    enable_context_offloading=False,
    enable_creative_context=True,
    enable_enhanced_extraction=False,  ***REMOVED*** 使用基础提取
    enable_unimem=False,
    enable_quality_check=False
)
```

**平衡模式（默认）**：
```python
creator = ReactNovelCreator(
    novel_title="我的小说",
    ***REMOVED*** 使用默认配置即可
)
```

***REMOVED******REMOVED*** 📊 输出结构

```
outputs/{novel_title}/
├── novel_plan.json          ***REMOVED*** 小说大纲
├── metadata.json            ***REMOVED*** 元数据（包含优化功能状态）
├── {novel_title}_完整版.txt ***REMOVED*** 完整小说
├── chapters/                ***REMOVED*** 章节文件
│   ├── chapter_001.txt
│   ├── chapter_001_meta.json
│   ├── chapter_002.txt
│   └── ...
├── summaries/               ***REMOVED*** 章节摘要
│   ├── chapter_001_summary.txt
│   └── ...
├── semantic_mesh/           ***REMOVED*** 语义网格（如果启用）
│   └── mesh.json
└── drafts/                  ***REMOVED*** 草稿
```

***REMOVED******REMOVED******REMOVED*** 查看创作结果

```python
import json
from pathlib import Path

***REMOVED*** 读取元数据
metadata_file = Path("outputs/我的小说/metadata.json")
metadata = json.loads(metadata_file.read_text(encoding='utf-8'))

print(f"标题: {metadata['title']}")
print(f"章节数: {metadata['total_chapters']}")
print(f"总字数: {metadata['total_words']:,}")

***REMOVED*** 查看优化功能状态
print("\n优化功能:")
print(f"  增强提取: {metadata.get('enhanced_extraction', {}).get('enabled', False)}")
print(f"  创作上下文: {metadata.get('creative_context', {}).get('enabled', False)}")
if metadata.get('creative_context', {}).get('enabled'):
    cc = metadata['creative_context']
    print(f"    实体数: {cc.get('entities_count', 0)}")
    print(f"    关系数: {cc.get('relations_count', 0)}")

quality = metadata.get('quality_check', {})
print(f"  质量检查: {quality.get('enabled', False)}")
if quality.get('enabled'):
    print(f"    发现问题: {quality.get('total_issues', 0)} 个")
    print(f"    严重问题章节: {quality.get('high_severity_chapters', 0)} 个")
```

***REMOVED******REMOVED*** 🔍 质量检查

***REMOVED******REMOVED******REMOVED*** 查看章节质量问题

```python
***REMOVED*** 创作后自动检查
chapter = creator.create_chapter(...)

***REMOVED*** 查看检查结果
quality = chapter.metadata.get('quality_check', {})
if quality:
    print(f"发现问题: {quality.get('total_issues', 0)} 个")
    
    ***REMOVED*** 按严重程度分类
    by_severity = quality.get('by_severity', {})
    print(f"  严重: {by_severity.get('high', 0)}")
    print(f"  中等: {by_severity.get('medium', 0)}")
    print(f"  轻微: {by_severity.get('low', 0)}")
    
    ***REMOVED*** 查看问题详情
    for issue in quality.get('issues', [])[:5]:  ***REMOVED*** 前5个问题
        print(f"\n[{issue['severity'].upper()}] {issue['type']}")
        print(f"  描述: {issue['description']}")
        print(f"  位置: {issue['location']}")
        if issue.get('suggestion'):
            print(f"  建议: {issue['suggestion']}")
```

***REMOVED******REMOVED******REMOVED*** 手动质量检查

```python
from novel_creation.quality_checker import check_chapter_quality

result = check_chapter_quality(
    chapter_content="章节内容...",
    chapter_number=1,
    previous_chapters=[],  ***REMOVED*** 前面章节列表
    novel_plan=None  ***REMOVED*** 可选：小说大纲
)

print(f"发现问题: {result['total_issues']} 个")
for issue in result['issues']:
    print(f"  - {issue['description']}")
```

***REMOVED******REMOVED*** 🧠 语义网格记忆

***REMOVED******REMOVED******REMOVED*** 查看语义网格

```python
import json
from pathlib import Path

***REMOVED*** 读取语义网格
mesh_file = Path("outputs/我的小说/semantic_mesh/mesh.json")
mesh_data = json.loads(mesh_file.read_text(encoding='utf-8'))

***REMOVED*** 查看实体
entities = mesh_data.get('entities', {})
print(f"实体总数: {len(entities)}")

***REMOVED*** 按类型统计
entity_types = {}
for entity_id, entity in entities.items():
    etype = entity.get('type', 'unknown')
    entity_types[etype] = entity_types.get(etype, 0) + 1

for etype, count in sorted(entity_types.items()):
    print(f"  {etype}: {count} 个")

***REMOVED*** 查看关系
relations = mesh_data.get('relations', [])
print(f"\n关系总数: {len(relations)}")
for rel in relations[:5]:  ***REMOVED*** 前5个关系
    print(f"  {rel.get('source_id')} --{rel.get('relation_type')}--> {rel.get('target_id')}")
```

***REMOVED******REMOVED******REMOVED*** 查询相关记忆

```python
***REMOVED*** 使用创作者的方法
related = creator.get_related_memories("chapter_001", max_results=5)
for entity in related:
    print(f"{entity.name} ({entity.type.value}): {entity.content[:100]}...")
```

***REMOVED******REMOVED*** 📈 性能优化建议

***REMOVED******REMOVED******REMOVED*** 1. 减少 LLM 调用

```python
***REMOVED*** 禁用增强提取（使用基础规则提取）
creator = ReactNovelCreator(
    novel_title="我的小说",
    enable_enhanced_extraction=False  ***REMOVED*** 节省 Token
)
```

***REMOVED******REMOVED******REMOVED*** 2. 批量处理

```python
***REMOVED*** 一次性创作多个章节，而不是逐章调用
result = creator.create_novel(
    genre="科幻",
    theme="时间旅行",
    target_chapters=10,
    words_per_chapter=3000
)
```

***REMOVED******REMOVED******REMOVED*** 3. 使用上下文卸载

```python
***REMOVED*** 启用上下文卸载（默认启用）
creator = ReactNovelCreator(
    novel_title="我的小说",
    enable_context_offloading=True  ***REMOVED*** 自动管理上下文长度
)
```

***REMOVED******REMOVED*** ⚠️ 常见问题

***REMOVED******REMOVED******REMOVED*** 1. UniMem 初始化失败

**问题**：`UniMem 初始化失败`

**解决**：
- 检查 UniMem 服务是否可用
- 或者设置 `enable_unimem=False`（系统会优雅降级）

***REMOVED******REMOVED******REMOVED*** 2. 实体提取失败

**问题**：`LLM 提取失败`

**解决**：
- 检查 LLM 配置
- 系统会自动回退到基础规则提取

***REMOVED******REMOVED******REMOVED*** 3. 质量检查报告过多问题

**问题**：质量检查发现很多问题

**解决**：
- 检查是否是真的问题（可能是误报）
- 可以调整质量检查的阈值
- 或者设置 `enable_quality_check=False`

***REMOVED******REMOVED*** 📚 更多资源

- `docs/NOVEL_CREATION_ANALYSIS_AND_OPTIMIZATION.md` - 详细分析和优化方案
- `docs/NOVEL_OPTIMIZATION_QUICK_REFERENCE.md` - 快速参考
- `docs/OPTIMIZATION_FINAL_SUMMARY.md` - 最终总结
- `test_quick_validation.py` - 快速验证脚本
- `test_actual_creation_optimized.py` - 实际创作测试

***REMOVED******REMOVED*** 🎯 下一步

1. **开始创作**：使用上述代码示例开始创作你的第一篇小说
2. **查看结果**：检查输出目录中的章节和元数据
3. **优化调整**：根据结果调整参数和配置
4. **持续改进**：根据创作效果持续优化

祝你创作愉快！🎉
