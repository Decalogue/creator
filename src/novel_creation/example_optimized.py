"""
优化后的小说创作示例
展示如何使用所有优化功能
"""
import logging
from pathlib import Path
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from novel_creation.react_novel_creator import ReactNovelCreator


def example_basic_creation():
    """示例1：基础创作（推荐配置）"""
    print("=" * 70)
    print("示例1：基础创作（推荐配置）")
    print("=" * 70)
    
    creator = ReactNovelCreator(
        novel_title="示例小说_基础",
        enable_context_offloading=True,
        enable_creative_context=True,
        enable_enhanced_extraction=True,  ***REMOVED*** 启用增强实体提取
        enable_unimem=False,  ***REMOVED*** 可选：需要 UniMem 服务
        enable_quality_check=True  ***REMOVED*** 启用质量检查
    )
    
    ***REMOVED*** 创作小说
    result = creator.create_novel(
        genre="科幻",
        theme="时间旅行、平行世界",
        target_chapters=3,  ***REMOVED*** 示例：只创作3章
        words_per_chapter=1000,  ***REMOVED*** 示例：每章1000字
        start_from_chapter=1
    )
    
    print(f"\n✅ 创作完成！")
    print(f"   章节数: {result['total_chapters']}")
    print(f"   总字数: {result['total_words']:,}")
    print(f"   输出目录: {result['output_dir']}")
    
    return creator, result


def example_step_by_step():
    """示例2：分步创作"""
    print("\n" + "=" * 70)
    print("示例2：分步创作")
    print("=" * 70)
    
    creator = ReactNovelCreator(
        novel_title="示例小说_分步",
        enable_enhanced_extraction=True,
        enable_quality_check=True
    )
    
    ***REMOVED*** 1. 创建大纲
    print("\n1. 创建大纲...")
    plan = creator.create_novel_plan(
        genre="奇幻",
        theme="魔法世界、冒险",
        target_chapters=3,
        words_per_chapter=1000
    )
    print(f"✅ 大纲创建成功，共 {len(plan.get('chapter_outline', []))} 章")
    
    ***REMOVED*** 2. 逐章创作
    print("\n2. 逐章创作...")
    previous_summary = ""
    
    for i, chapter_info in enumerate(plan.get('chapter_outline', [])[:3], 1):
        print(f"\n创作第{chapter_info['chapter_number']}章：{chapter_info['title']}...")
        
        chapter = creator.create_chapter(
            chapter_number=chapter_info['chapter_number'],
            chapter_title=chapter_info['title'],
            chapter_summary=chapter_info['summary'],
            previous_chapters_summary=previous_summary,
            target_words=1000
        )
        
        print(f"✅ 完成，字数: {len(chapter.content)}")
        
        ***REMOVED*** 检查质量问题
        quality = chapter.metadata.get('quality_check', {})
        if quality.get('total_issues', 0) > 0:
            print(f"⚠️  发现问题: {quality['total_issues']} 个")
            for issue in quality['issues'][:2]:  ***REMOVED*** 显示前2个
                print(f"   - [{issue['severity']}] {issue['description'][:50]}...")
        else:
            print("✅ 质量检查通过")
        
        ***REMOVED*** 更新摘要
        if previous_summary:
            previous_summary += f"\n\n第{chapter.chapter_number}章：{chapter.title}\n{chapter.summary}"
        else:
            previous_summary = f"第{chapter.chapter_number}章：{chapter.title}\n{chapter.summary}"
    
    ***REMOVED*** 3. 保存
    creator._generate_full_novel()
    creator._save_metadata()
    
    print(f"\n✅ 分步创作完成！输出目录: {creator.output_dir}")
    
    return creator


def example_check_results():
    """示例3：查看创作结果"""
    print("\n" + "=" * 70)
    print("示例3：查看创作结果")
    print("=" * 70)
    
    ***REMOVED*** 假设已经创作完成，查看结果
    output_dir = Path("novel_creation/outputs/示例小说_基础")
    
    if not output_dir.exists():
        print("⚠️  请先运行示例1创建小说")
        return
    
    ***REMOVED*** 读取元数据
    metadata_file = output_dir / "metadata.json"
    if metadata_file.exists():
        metadata = json.loads(metadata_file.read_text(encoding='utf-8'))
        
        print("\n📊 创作统计:")
        print(f"   标题: {metadata.get('title', 'N/A')}")
        print(f"   章节数: {metadata.get('total_chapters', 0)}")
        print(f"   总字数: {metadata.get('total_words', 0):,} 字")
        
        ***REMOVED*** 优化功能状态
        print("\n🔧 优化功能状态:")
        
        enhanced = metadata.get('enhanced_extraction', {})
        if enhanced.get('enabled'):
            print(f"   ✅ 增强实体提取: {enhanced.get('method', 'N/A')}")
        
        creative = metadata.get('creative_context', {})
        if creative.get('enabled'):
            print(f"   ✅ 创作上下文:")
            print(f"      实体数: {creative.get('entities_count', 0)}")
            print(f"      关系数: {creative.get('relations_count', 0)}")
        
        quality = metadata.get('quality_check', {})
        if quality.get('enabled'):
            print(f"   ✅ 质量检查:")
            print(f"      发现问题: {quality.get('total_issues', 0)} 个")
            print(f"      严重问题章节: {quality.get('high_severity_chapters', 0)} 个")
        
        ***REMOVED*** 语义网格
        mesh_file = output_dir / "semantic_mesh" / "mesh.json"
        if mesh_file.exists():
            print("\n🧠 语义网格:")
            mesh_data = json.loads(mesh_file.read_text(encoding='utf-8'))
            entities = mesh_data.get('entities', {})
            relations = mesh_data.get('relations', [])
            
            print(f"   实体数: {len(entities)}")
            print(f"   关系数: {len(relations)}")
            
            ***REMOVED*** 实体类型分布
            entity_types = {}
            for entity_id, entity in entities.items():
                etype = entity.get('type', 'unknown')
                entity_types[etype] = entity_types.get(etype, 0) + 1
            
            if entity_types:
                print("   实体类型分布:")
                for etype, count in sorted(entity_types.items()):
                    print(f"     - {etype}: {count} 个")


def example_quality_check():
    """示例4：质量检查"""
    print("\n" + "=" * 70)
    print("示例4：质量检查")
    print("=" * 70)
    
    from novel_creation.quality_checker import check_chapter_quality
    
    ***REMOVED*** 测试章节内容
    chapter_content = """
    公元2023年，北京。
    
    林风站在窗前，看到了苏雨。
    "你好，苏语。"林风说道。
    
    在遥远的未来，机器人统治了地球。
    """
    
    ***REMOVED*** 前面章节
    previous_chapters = [
        {
            "number": 1,
            "content": "林风是一名记者，遇到了苏雨博士。",
            "summary": "第一章介绍"
        }
    ]
    
    ***REMOVED*** 执行质量检查
    result = check_chapter_quality(
        chapter_content=chapter_content,
        chapter_number=2,
        previous_chapters=previous_chapters,
        novel_plan=None
    )
    
    print(f"\n发现问题: {result['total_issues']} 个")
    
    if result['total_issues'] > 0:
        print("\n问题详情:")
        for i, issue in enumerate(result['issues'], 1):
            print(f"\n{i}. [{issue['severity'].upper()}] {issue['type']}")
            print(f"   描述: {issue['description']}")
            print(f"   位置: {issue['location']}")
            if issue.get('suggestion'):
                print(f"   建议: {issue['suggestion']}")
    else:
        print("✅ 未发现问题")


def main():
    """运行所有示例"""
    print("=" * 70)
    print("优化后的小说创作系统 - 使用示例")
    print("=" * 70)
    print()
    print("注意：")
    print("1. 示例1和示例2会实际调用 LLM，需要消耗 Token")
    print("2. 示例3和示例4不需要 LLM，可以安全运行")
    print()
    
    import time
    print("3秒后开始运行示例（按 Ctrl+C 取消）...")
    try:
        time.sleep(3)
    except KeyboardInterrupt:
        print("\n示例已取消")
        return
    
    ***REMOVED*** 运行示例（可以根据需要选择）
    try:
        ***REMOVED*** 示例1：基础创作（需要 LLM）
        ***REMOVED*** creator, result = example_basic_creation()
        
        ***REMOVED*** 示例2：分步创作（需要 LLM）
        ***REMOVED*** creator = example_step_by_step()
        
        ***REMOVED*** 示例3：查看结果（不需要 LLM）
        example_check_results()
        
        ***REMOVED*** 示例4：质量检查（不需要 LLM）
        example_quality_check()
        
        print("\n" + "=" * 70)
        print("✅ 示例运行完成")
        print("=" * 70)
        print("\n提示：取消示例1和示例2的注释可以测试完整创作流程")
        
    except Exception as e:
        print(f"\n❌ 示例运行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
