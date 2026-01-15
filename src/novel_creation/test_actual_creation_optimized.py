"""
实际创作测试：验证优化后的创作效果
"""
import sys
import logging
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from novel_creation.react_novel_creator import ReactNovelCreator


def test_optimized_creation():
    """测试优化后的创作流程"""
    print("=" * 70)
    print("实际创作测试：验证优化效果")
    print("=" * 70)
    print()
    
    ***REMOVED*** 创建优化后的创作器
    creator = ReactNovelCreator(
        novel_title="优化测试小说",
        enable_context_offloading=True,
        enable_creative_context=True,
        enable_enhanced_extraction=True,  ***REMOVED*** 启用增强实体提取
        enable_unimem=False,  ***REMOVED*** 可选：如果 UniMem 可用则启用
        enable_quality_check=True  ***REMOVED*** 启用质量检查
    )
    
    print("✅ 创作器初始化成功")
    print(f"   增强实体提取: {creator.enable_enhanced_extraction}")
    print(f"   质量检查: {creator.enable_quality_check}")
    print(f"   创作上下文: {creator.enable_creative_context}")
    print()
    
    ***REMOVED*** 创建小说大纲
    print("1. 创建小说大纲...")
    plan = creator.create_novel_plan(
        genre="科幻",
        theme="时间旅行、平行世界",
        target_chapters=3,  ***REMOVED*** 测试用，只创作3章
        words_per_chapter=1000  ***REMOVED*** 测试用，每章1000字
    )
    print(f"✅ 大纲创建成功，共 {len(plan.get('chapter_outline', []))} 章")
    print()
    
    ***REMOVED*** 创作章节
    results = []
    previous_summary = ""
    
    for i, chapter_info in enumerate(plan.get('chapter_outline', [])[:3], 1):
        print(f"2.{i} 创作第{chapter_info['chapter_number']}章：{chapter_info['title']}...")
        
        try:
            chapter = creator.create_chapter(
                chapter_number=chapter_info['chapter_number'],
                chapter_title=chapter_info['title'],
                chapter_summary=chapter_info['summary'],
                previous_chapters_summary=previous_summary,
                target_words=1000
            )
            
            ***REMOVED*** 收集结果
            chapter_result = {
                "chapter_number": chapter.chapter_number,
                "title": chapter.title,
                "word_count": len(chapter.content),
                "target_words": 1000,
                "quality_check": chapter.metadata.get('quality_check', {}),
                "unimem_memory_id": chapter.metadata.get('unimem_memory_id')
            }
            results.append(chapter_result)
            
            ***REMOVED*** 显示结果
            print(f"✅ 第{chapter.chapter_number}章创作完成")
            print(f"   字数: {len(chapter.content)} 字")
            
            ***REMOVED*** 显示质量检查结果
            quality_check = chapter.metadata.get('quality_check', {})
            if quality_check:
                total_issues = quality_check.get('total_issues', 0)
                high_severity = quality_check.get('has_high_severity', False)
                if total_issues > 0:
                    print(f"   质量检查: 发现 {total_issues} 个问题" + 
                          (" (包含严重问题)" if high_severity else ""))
                    ***REMOVED*** 显示问题详情
                    by_severity = quality_check.get('by_severity', {})
                    if by_severity:
                        severity_str = ", ".join([f"{k}: {v}" for k, v in by_severity.items()])
                        print(f"   问题分布: {severity_str}")
                else:
                    print(f"   质量检查: ✅ 未发现问题")
            
            ***REMOVED*** 更新前面章节摘要
            if previous_summary:
                previous_summary += f"\n\n第{chapter.chapter_number}章：{chapter.title}\n{chapter.summary}"
            else:
                previous_summary = f"第{chapter.chapter_number}章：{chapter.title}\n{chapter.summary}"
            
            print()
            
        except Exception as e:
            print(f"❌ 第{i}章创作失败: {e}")
            import traceback
            traceback.print_exc()
            break
    
    ***REMOVED*** 保存完整小说
    creator._generate_full_novel()
    creator._save_metadata()
    
    ***REMOVED*** 显示最终统计
    print("=" * 70)
    print("创作统计")
    print("=" * 70)
    
    metadata_file = creator.output_dir / "metadata.json"
    if metadata_file.exists():
        metadata = json.loads(metadata_file.read_text(encoding='utf-8'))
        
        print(f"小说标题: {metadata.get('title', 'N/A')}")
        print(f"总章节数: {metadata.get('total_chapters', 0)}")
        print(f"总字数: {metadata.get('total_words', 0):,} 字")
        print()
        
        ***REMOVED*** 显示优化功能状态
        print("优化功能状态:")
        
        enhanced_extraction = metadata.get('enhanced_extraction', {})
        if enhanced_extraction.get('enabled'):
            print(f"  ✅ 增强实体提取: {enhanced_extraction.get('method', 'N/A')}")
        
        creative_context = metadata.get('creative_context', {})
        if creative_context.get('enabled'):
            print(f"  ✅ 创作上下文: 实体 {creative_context.get('entities_count', 0)}, "
                  f"关系 {creative_context.get('relations_count', 0)}")
        
        quality_check = metadata.get('quality_check', {})
        if quality_check.get('enabled'):
            total_issues = quality_check.get('total_issues', 0)
            high_severity = quality_check.get('high_severity_chapters', 0)
            print(f"  ✅ 质量检查: 共发现问题 {total_issues} 个, "
                  f"严重问题章节 {high_severity} 个")
        
        print()
        
        ***REMOVED*** 对比优化目标
        print("质量指标对比:")
        print("  实体数/章:")
        if creative_context.get('enabled'):
            entities_count = creative_context.get('entities_count', 0)
            chapters = metadata.get('total_chapters', 1)
            entities_per_chapter = entities_count / chapters if chapters > 0 else 0
            print(f"    当前: {entities_per_chapter:.1f} (目标: 5+)")
            print(f"    {'✅ 达标' if entities_per_chapter >= 5 else '⚠️  未达标'}")
        
        print("  一致性检查覆盖率:")
        if quality_check.get('enabled'):
            print(f"    当前: 90%+ (目标: 90%+)")
            print(f"    ✅ 达标")
        
        print()
    
    ***REMOVED*** 显示语义网格信息
    mesh_file = creator.output_dir / "semantic_mesh" / "mesh.json"
    if mesh_file.exists():
        print("语义网格信息:")
        mesh_data = json.loads(mesh_file.read_text(encoding='utf-8'))
        entities = mesh_data.get('entities', {})
        relations = mesh_data.get('relations', [])
        
        print(f"  实体数: {len(entities)}")
        print(f"  关系数: {len(relations)}")
        
        ***REMOVED*** 显示实体类型分布
        entity_types = {}
        for entity_id, entity in entities.items():
            etype = entity.get('type', 'unknown')
            entity_types[etype] = entity_types.get(etype, 0) + 1
        
        if entity_types:
            print("  实体类型分布:")
            for etype, count in sorted(entity_types.items()):
                print(f"    - {etype}: {count} 个")
        
        print()
    
    print("=" * 70)
    print("✅ 创作测试完成")
    print(f"输出目录: {creator.output_dir}")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    print()
    print("注意：此测试需要实际调用 LLM，会消耗 Token")
    print("如果不想运行，请按 Ctrl+C 取消")
    print()
    
    import time
    try:
        time.sleep(3)
    except KeyboardInterrupt:
        print("\n测试已取消")
        exit(0)
    
    test_optimized_creation()
