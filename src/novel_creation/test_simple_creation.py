***REMOVED***!/usr/bin/env python3
"""
简化的小说创作测试
只测试基本功能，不依赖 LLM 实际生成内容
"""
import sys
import logging
from pathlib import Path

***REMOVED*** 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

***REMOVED*** 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from novel_creation import ReactNovelCreator, NovelChapter


def test_with_mock_content():
    """使用模拟内容测试创作流程"""
    print("=" * 70)
    print("简化小说创作测试（使用模拟内容）")
    print("=" * 70)
    print()
    
    ***REMOVED*** 创建小说创作器
    creator = ReactNovelCreator(
        novel_title="测试小说_模拟",
        enable_context_offloading=True,
        enable_creative_context=True
    )
    
    print(f"✅ Novel Creator 初始化成功")
    print(f"   创作上下文系统: {'启用' if creator.enable_creative_context else '禁用'}")
    print()
    
    ***REMOVED*** 创建模拟大纲
    print("=" * 70)
    print("步骤1: 创建模拟大纲")
    print("=" * 70)
    print()
    
    plan = {
        "background": "一个关于时间旅行的科幻故事",
        "characters": [
            {"name": "主角", "description": "一个年轻的时空旅者"}
        ],
        "chapter_outline": [
            {
                "chapter_number": 1,
                "title": "第一章：起点",
                "summary": "主角发现时间旅行的秘密"
            },
            {
                "chapter_number": 2,
                "title": "第二章：第一次旅行",
                "summary": "主角进行第一次时间旅行"
            },
            {
                "chapter_number": 3,
                "title": "第三章：代价",
                "summary": "主角发现时间旅行的代价"
            }
        ],
        "main_plot": "主角通过时间旅行探索不同的人生可能性",
        "key_plot_points": ["发现日记", "第一次旅行", "发现代价"]
    }
    
    ***REMOVED*** 保存大纲
    plan_file = creator.output_dir / "novel_plan.json"
    import json
    plan_file.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    creator.metadata.update({
        "genre": "科幻",
        "theme": "时间旅行",
        "target_chapters": 3,
        "words_per_chapter": 500,
        "plan": plan
    })
    
    print("✅ 模拟大纲创建成功")
    print(f"   章节数: {len(plan['chapter_outline'])}")
    print()
    
    ***REMOVED*** 使用模拟内容创作章节
    print("=" * 70)
    print("步骤2: 创作章节（使用模拟内容）")
    print("=" * 70)
    print()
    
    mock_chapters = [
        '''主角"李维"站在古老的图书馆前，手中握着一本破旧的日记。日记的封面上写着"时空旅者的日记"几个字。他翻开第一页，上面写着："如果你能看到这些文字，说明你已经被选中了。"李维感到一阵眩晕，周围的景象开始模糊。当他再次睁开眼睛时，发现自己站在一个完全不同的地方。这是一个充满未来科技的城市，天空中飘着蓝色的云。''',
        '''李维意识到自己已经穿越到了另一个时间线。在这个世界里，他是一个成功的企业家，拥有巨大的财富和地位。但是，他感到内心空虚。他遇到了另一个自己，那个自己告诉他："每个选择都有代价，你无法逃避。"李维开始思考，是否应该继续这种旅行。''',
        '''李维发现，每次时间旅行都会消耗他的生命力。他的身体开始变得虚弱，记忆也开始混乱。他意识到，如果继续下去，他可能会永远迷失在时间的长河中。最终，他决定回到原点，接受自己的现实生活。他合上日记，决定不再使用它。'''
    ]
    
    previous_summary = ""
    
    for i, (chapter_info, mock_content) in enumerate(zip(plan['chapter_outline'], mock_chapters)):
        print(f"【创作第{i+1}章】")
        print(f"   标题: {chapter_info['title']}")
        
        ***REMOVED*** 创建章节对象（使用模拟内容）
        chapter = NovelChapter(
            chapter_number=chapter_info["chapter_number"],
            title=chapter_info["title"],
            content=mock_content,
            summary=chapter_info["summary"],
            metadata={
                "target_words": 500,
                "actual_words": len(mock_content),
            }
        )
        
        ***REMOVED*** 保存章节
        creator._save_chapter(chapter)
        
        ***REMOVED*** 生成章节摘要
        chapter.summary = creator._generate_chapter_summary(chapter)
        
        ***REMOVED*** 处理创作上下文
        if creator.enable_creative_context:
            creator._process_chapter_with_creative_context(chapter)
        
        ***REMOVED*** 添加到列表
        creator.chapters.append(chapter)
        
        print(f"   ✅ 第{i+1}章处理完成")
        print(f"   字数: {len(chapter.content)} 字")
        print(f"   内容预览: {chapter.content[:80]}...")
        
        if creator.enable_creative_context:
            print(f"   语义网格实体数: {len(creator.semantic_mesh.entities)}")
            print(f"   语义网格关系数: {len(creator.semantic_mesh.relations)}")
            
            ***REMOVED*** 查询关联记忆
            chapter_entity_id = f"chapter_{chapter.chapter_number:03d}"
            related = creator.get_related_memories(chapter_entity_id, max_results=3)
            if related:
                print(f"   关联记忆: {len(related)} 个")
                for entity in related[:2]:
                    print(f"     - {entity.name} ({entity.type.value})")
        
        print()
        
        ***REMOVED*** 更新前面章节摘要
        if previous_summary:
            previous_summary += f"\n\n第{chapter.chapter_number}章：{chapter.title}\n{chapter.summary}"
        else:
            previous_summary = f"第{chapter.chapter_number}章：{chapter.title}\n{chapter.summary}"
    
    ***REMOVED*** 更新元数据
    creator.metadata["total_chapters"] = len(creator.chapters)
    creator.metadata["total_words"] = sum(len(c.content) for c in creator.chapters)
    
    ***REMOVED*** 生成完整小说
    print("=" * 70)
    print("步骤3: 生成完整小说")
    print("=" * 70)
    print()
    
    creator._generate_full_novel()
    creator._save_metadata()
    
    print("✅ 完整小说生成成功")
    print()
    
    ***REMOVED*** 检查输出文件
    print("=" * 70)
    print("步骤4: 检查输出文件")
    print("=" * 70)
    print()
    
    output_dir = creator.output_dir
    
    files_to_check = [
        ("novel_plan.json", "小说大纲"),
        ("metadata.json", "元数据"),
        (f"{creator.novel_title}_完整版.txt", "完整小说"),
    ]
    
    for filename, desc in files_to_check:
        file_path = output_dir / filename
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"   ✅ {desc}: {filename} ({size} bytes)")
        else:
            print(f"   ❌ {desc}: {filename} (不存在)")
    
    ***REMOVED*** 检查章节文件
    chapters_dir = output_dir / "chapters"
    if chapters_dir.exists():
        chapter_files = list(chapters_dir.glob("chapter_*.txt"))
        chapter_meta_files = list(chapters_dir.glob("chapter_*_meta.json"))
        print(f"   ✅ 章节文件: {len(chapter_files)} 个 .txt, {len(chapter_meta_files)} 个 .json")
    
    ***REMOVED*** 检查语义网格
    if creator.enable_creative_context:
        mesh_dir = output_dir / "semantic_mesh"
        if mesh_dir.exists():
            mesh_file = mesh_dir / "mesh.json"
            if mesh_file.exists():
                size = mesh_file.stat().st_size
                print(f"   ✅ 语义网格: mesh.json ({size} bytes)")
                print(f"      实体数: {len(creator.semantic_mesh.entities)}")
                print(f"      关系数: {len(creator.semantic_mesh.relations)}")
                
                ***REMOVED*** 显示实体列表
                print(f"   【实体列表】")
                for entity_id, entity in list(creator.semantic_mesh.entities.items())[:5]:
                    print(f"     - {entity.name} ({entity.type.value})")
                if len(creator.semantic_mesh.entities) > 5:
                    print(f"     ... 还有 {len(creator.semantic_mesh.entities) - 5} 个实体")
    
    ***REMOVED*** 总结
    print()
    print("=" * 70)
    print("测试总结")
    print("=" * 70)
    print()
    print(f"✅ 小说创作测试完成")
    print(f"   输出目录: {output_dir}")
    print(f"   章节数: {len(creator.chapters)}")
    print(f"   总字数: {creator.metadata.get('total_words', 0)}")
    
    if creator.enable_creative_context:
        print(f"   语义网格实体数: {len(creator.semantic_mesh.entities)}")
        print(f"   语义网格关系数: {len(creator.semantic_mesh.relations)}")
        print(f"   订阅者数: {len(creator.memory_bus.subscriptions)}")
    
    print()
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    success = test_with_mock_content()
    sys.exit(0 if success else 1)
