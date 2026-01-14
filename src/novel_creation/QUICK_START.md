***REMOVED*** 快速开始

***REMOVED******REMOVED*** 最简单的使用方式

```python
from novel_creation import ReactNovelCreator

***REMOVED*** 创建小说创作器
creator = ReactNovelCreator(novel_title="我的小说")

***REMOVED*** 一键创作（会自动创建大纲并开始创作）
result = creator.create_novel(
    genre="科幻",
    theme="时间旅行",
    target_chapters=10,  ***REMOVED*** 先创作10章测试
    words_per_chapter=2000
)

print(f"创作完成！共{result['total_chapters']}章，{result['total_words']}字")
print(f"输出目录：{result['output_dir']}")
```

***REMOVED******REMOVED*** 分步创作（推荐）

```python
from novel_creation import ReactNovelCreator

creator = ReactNovelCreator(novel_title="我的小说")

***REMOVED*** 步骤1：创建大纲
plan = creator.create_novel_plan(
    genre="科幻",
    theme="时间旅行",
    target_chapters=20,
    words_per_chapter=3000
)

***REMOVED*** 步骤2：创作第一章
chapter1 = creator.create_chapter(
    chapter_number=1,
    chapter_title=plan['chapter_outline'][0]['title'],
    chapter_summary=plan['chapter_outline'][0]['summary'],
    target_words=3000
)

***REMOVED*** 步骤3：继续创作后续章节
for i in range(1, 20):
    chapter_info = plan['chapter_outline'][i]
    chapter = creator.create_chapter(
        chapter_number=i+1,
        chapter_title=chapter_info['title'],
        chapter_summary=chapter_info['summary'],
        previous_chapters_summary=chapter1.summary,  ***REMOVED*** 传递前面章节摘要
        target_words=3000
    )
```

***REMOVED******REMOVED*** 运行示例

```bash
cd /root/data/AI/creator/src
python novel_creation/example.py
```
