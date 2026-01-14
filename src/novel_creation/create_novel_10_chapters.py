***REMOVED***!/usr/bin/env python3
"""
实际小说创作：创作前10章
每章长度：2000-3000字（番茄小说风格）
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

from novel_creation import ReactNovelCreator


def create_novel_10_chapters():
    """创作前10章小说"""
    print("=" * 70)
    print("开始创作小说 - 前10章")
    print("=" * 70)
    print()
    
    ***REMOVED*** 创建小说创作器（启用所有功能）
    creator = ReactNovelCreator(
        novel_title="时空旅者的日记",
        enable_context_offloading=True,
        enable_creative_context=True
    )
    
    print(f"✅ Novel Creator 初始化成功")
    print(f"   小说标题: {creator.novel_title}")
    print(f"   输出目录: {creator.output_dir}")
    print(f"   创作上下文系统: {'启用' if creator.enable_creative_context else '禁用'}")
    print()
    
    ***REMOVED*** 创建小说大纲（10章）
    print("=" * 70)
    print("步骤1: 创建小说大纲（10章）")
    print("=" * 70)
    print()
    
    try:
        plan = creator.create_novel_plan(
            genre="科幻",
            theme="时间旅行、平行世界、人性探索、时空管理局",
            target_chapters=10,
            words_per_chapter=2500  ***REMOVED*** 每章2500字（番茄小说风格）
        )
        
        print("✅ 小说大纲创建成功")
        print(f"   背景设定: {plan.get('background', 'N/A')[:150]}...")
        print(f"   主要角色: {len(plan.get('characters', []))} 个")
        print(f"   章节大纲: {len(plan.get('chapter_outline', []))} 章")
        print()
        
        ***REMOVED*** 显示角色信息
        if plan.get('characters'):
            print("【主要角色】")
            for char in plan.get('characters', [])[:5]:
                print(f"   - {char.get('name', 'N/A')}: {char.get('description', '')[:80]}...")
            print()
        
    except Exception as e:
        print(f"❌ 创建大纲失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    ***REMOVED*** 创作前10章
    print("=" * 70)
    print("步骤2: 创作前10章")
    print("=" * 70)
    print()
    
    previous_summary = ""
    successful_chapters = 0
    
    for i in range(10):
        chapter_info = plan.get("chapter_outline", [])[i] if i < len(plan.get("chapter_outline", [])) else {
            "chapter_number": i + 1,
            "title": f"第{i+1}章",
            "summary": "待创作"
        }
        
        print(f"【创作第{i+1}章】")
        print(f"   标题: {chapter_info.get('title', f'第{i+1}章')}")
        print(f"   摘要: {chapter_info.get('summary', '')[:100]}...")
        print()
        
        try:
            chapter = creator.create_chapter(
                chapter_number=chapter_info["chapter_number"],
                chapter_title=chapter_info.get("title", f"第{i+1}章"),
                chapter_summary=chapter_info.get("summary", ""),
                previous_chapters_summary=previous_summary,
                target_words=2500  ***REMOVED*** 目标2500字
            )
            
            actual_words = len(chapter.content)
            print(f"   ✅ 第{i+1}章创作完成")
            print(f"   字数: {actual_words} 字")
            print(f"   目标: 2500 字")
            print(f"   完成度: {actual_words/2500*100:.1f}%")
            print(f"   内容预览: {chapter.content[:150]}...")
            
            ***REMOVED*** 检查创作上下文系统
            if creator.enable_creative_context:
                print(f"   【创作上下文】")
                print(f"   语义网格实体数: {len(creator.semantic_mesh.entities)}")
                print(f"   语义网格关系数: {len(creator.semantic_mesh.relations)}")
            
            print()
            
            ***REMOVED*** 更新前面章节摘要（用于后续章节的连贯性）
            if previous_summary:
                previous_summary += f"\n\n第{chapter.chapter_number}章：{chapter.title}\n{chapter.summary}"
            else:
                previous_summary = f"第{chapter.chapter_number}章：{chapter.title}\n{chapter.summary}"
            
            successful_chapters += 1
            
        except Exception as e:
            print(f"   ❌ 第{i+1}章创作失败: {e}")
            import traceback
            traceback.print_exc()
            print()
            continue
    
    ***REMOVED*** 生成完整小说
    print("=" * 70)
    print("步骤3: 生成完整小说")
    print("=" * 70)
    print()
    
    try:
        creator._generate_full_novel()
        creator._save_metadata()
        
        print("✅ 完整小说生成成功")
        print(f"   成功创作章节数: {successful_chapters}/10")
        print(f"   总字数: {creator.metadata.get('total_words', 0)} 字")
        print()
        
    except Exception as e:
        print(f"❌ 生成完整小说失败: {e}")
        import traceback
        traceback.print_exc()
    
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
            print(f"   ✅ {desc}: {filename} ({size:,} bytes)")
        else:
            print(f"   ❌ {desc}: {filename} (不存在)")
    
    ***REMOVED*** 检查章节文件
    chapters_dir = output_dir / "chapters"
    if chapters_dir.exists():
        chapter_files = list(chapters_dir.glob("chapter_*.txt"))
        chapter_meta_files = list(chapters_dir.glob("chapter_*_meta.json"))
        print(f"   ✅ 章节文件: {len(chapter_files)} 个 .txt, {len(chapter_meta_files)} 个 .json")
        
        ***REMOVED*** 显示每章字数统计
        if chapter_files:
            print()
            print("   【章节字数统计】")
            for cf in sorted(chapter_files):
                content = cf.read_text(encoding='utf-8')
                word_count = len(content)
                print(f"     {cf.stem}: {word_count:,} 字")
    
    ***REMOVED*** 检查语义网格
    if creator.enable_creative_context:
        mesh_dir = output_dir / "semantic_mesh"
        if mesh_dir.exists():
            mesh_file = mesh_dir / "mesh.json"
            if mesh_file.exists():
                size = mesh_file.stat().st_size
                print()
                print(f"   ✅ 语义网格: mesh.json ({size:,} bytes)")
                print(f"      实体数: {len(creator.semantic_mesh.entities)}")
                print(f"      关系数: {len(creator.semantic_mesh.relations)}")
                
                ***REMOVED*** 统计实体类型
                entity_types = {}
                for entity in creator.semantic_mesh.entities.values():
                    etype = entity.type.value
                    entity_types[etype] = entity_types.get(etype, 0) + 1
                
                print(f"   【实体类型分布】")
                for etype, count in sorted(entity_types.items()):
                    print(f"     - {etype}: {count} 个")
    
    ***REMOVED*** 总结
    print()
    print("=" * 70)
    print("创作总结")
    print("=" * 70)
    print()
    print(f"✅ 小说创作完成")
    print(f"   输出目录: {output_dir}")
    print(f"   成功创作章节数: {successful_chapters}/10")
    print(f"   总字数: {creator.metadata.get('total_words', 0):,} 字")
    print(f"   平均每章: {creator.metadata.get('total_words', 0) // max(successful_chapters, 1):,} 字")
    
    if creator.enable_creative_context:
        print(f"   语义网格实体数: {len(creator.semantic_mesh.entities)}")
        print(f"   语义网格关系数: {len(creator.semantic_mesh.relations)}")
    
    print()
    print("=" * 70)
    
    return successful_chapters == 10


if __name__ == "__main__":
    success = create_novel_10_chapters()
    sys.exit(0 if success else 1)
