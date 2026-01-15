"""
测试优化功能：增强实体提取和 UniMem 集成
"""
import logging
from pathlib import Path
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from novel_creation.react_novel_creator import ReactNovelCreator

def test_enhanced_extraction():
    """测试增强实体提取"""
    print("=" * 70)
    print("测试 1: 增强实体提取")
    print("=" * 70)
    
    creator = ReactNovelCreator(
        novel_title="测试小说_增强提取",
        enable_context_offloading=False,  ***REMOVED*** 关闭上下文卸载以加快测试
        enable_creative_context=True,
        enable_enhanced_extraction=True,  ***REMOVED*** 启用增强提取
        enable_unimem=False  ***REMOVED*** 先测试实体提取
    )
    
    ***REMOVED*** 创建一个测试章节
    test_content = """
    公元2023年，深秋的北京，国家会议中心。
    
    林风站在落地窗前，望着窗外金黄色的银杏叶在秋风中飘落。作为《科技前沿》杂志的首席记者，他已经报道过无数次科技会议。
    
    "林记者，会议还有十分钟开始。"助理小陈轻声提醒。
    
    林风点点头，调整了一下胸前的工作证。他看到了苏雨博士，一个天才物理学家，正在检查她的实验设备。
    
    在会场外，陈局长正在和一群科学家讨论时空旅行的可能性。突然，一个神秘的影子出现在角落，没有人注意到他的存在。
    
    林风拿出一本古老的日记，封面上写着"时空旅者的日记"。他翻开第一页，看到了令人震惊的内容。
    """
    
    ***REMOVED*** 手动创建章节进行测试
    from novel_creation.react_novel_creator import NovelChapter
    test_chapter = NovelChapter(
        chapter_number=1,
        title="测试章节",
        content=test_content,
        summary="测试实体提取"
    )
    
    ***REMOVED*** 测试实体提取
    print("\n开始提取实体...")
    entities = creator._extract_entities_from_chapter(test_chapter)
    
    print(f"\n提取结果：")
    print(f"  实体总数: {len(entities)}")
    
    ***REMOVED*** 按类型分组
    entity_types = {}
    for entity in entities:
        etype = entity.type.value if hasattr(entity.type, 'value') else str(entity.type)
        entity_types[etype] = entity_types.get(etype, 0) + 1
        print(f"  - {etype}: {entity.name} (置信度方法: {entity.metadata.get('extraction_method', 'unknown')})")
    
    print(f"\n实体类型分布: {entity_types}")
    
    ***REMOVED*** 检查是否有增强提取的实体
    enhanced_count = sum(1 for e in entities if e.metadata.get('extraction_method') != 'basic')
    print(f"增强提取的实体: {enhanced_count}/{len(entities)}")
    
    return len(entities), enhanced_count


def test_unimem_integration():
    """测试 UniMem 集成"""
    print("\n" + "=" * 70)
    print("测试 2: UniMem 集成")
    print("=" * 70)
    
    try:
        creator = ReactNovelCreator(
            novel_title="测试小说_UniMem",
            enable_context_offloading=False,
            enable_creative_context=True,
            enable_enhanced_extraction=True,
            enable_unimem=True  ***REMOVED*** 启用 UniMem
        )
        
        if not creator.unimem:
            print("⚠️  UniMem 未初始化，跳过测试")
            return False
        
        print("✅ UniMem 已成功初始化")
        
        ***REMOVED*** 创建一个测试章节并存储
        from novel_creation.react_novel_creator import NovelChapter
        test_chapter = NovelChapter(
            chapter_number=1,
            title="测试章节",
            content="这是一个测试章节的内容。主角林风是一名记者。",
            summary="测试 UniMem 存储"
        )
        
        print("\n存储章节到 UniMem...")
        creator._store_chapter_to_unimem(test_chapter)
        
        if test_chapter.metadata.get('unimem_memory_id'):
            print(f"✅ 章节已存储，Memory ID: {test_chapter.metadata['unimem_memory_id']}")
        else:
            print("⚠️  未获取到 Memory ID")
            return False
        
        ***REMOVED*** 测试检索
        print("\n测试从 UniMem 检索...")
        memories = creator._retrieve_unimem_memories(1, "测试章节摘要")
        if memories:
            print(f"✅ 检索成功，获得记忆:\n{memories[:200]}...")
        else:
            print("⚠️  未检索到相关记忆（可能是首次存储）")
        
        return True
        
    except Exception as e:
        print(f"❌ UniMem 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_integration():
    """测试完整集成（创建完整章节）"""
    print("\n" + "=" * 70)
    print("测试 3: 完整集成测试")
    print("=" * 70)
    print("注意：此测试需要 LLM 调用，可能会消耗 Token")
    
    try:
        creator = ReactNovelCreator(
            novel_title="测试小说_完整集成",
            enable_context_offloading=True,
            enable_creative_context=True,
            enable_enhanced_extraction=True,
            enable_unimem=False  ***REMOVED*** 可选：启用 UniMem
        )
        
        ***REMOVED*** 创建大纲
        print("\n1. 创建小说大纲...")
        plan = creator.create_novel_plan(
            genre="科幻",
            theme="时间旅行",
            target_chapters=2,
            words_per_chapter=500  ***REMOVED*** 短章节用于测试
        )
        print(f"✅ 大纲创建成功，共 {len(plan.get('chapter_outline', []))} 章")
        
        ***REMOVED*** 创建第一章
        print("\n2. 创建第一章...")
        chapter1 = creator.create_chapter(
            chapter_number=1,
            chapter_title=plan['chapter_outline'][0]['title'],
            chapter_summary=plan['chapter_outline'][0]['summary'],
            target_words=500
        )
        print(f"✅ 第一章创建成功，字数: {len(chapter1.content)}")
        
        ***REMOVED*** 检查实体提取结果
        if creator.enable_creative_context and creator.semantic_mesh:
            entities = creator.semantic_mesh.get_all_entities()
            relations = creator.semantic_mesh.get_all_relations()
            print(f"\n实体提取结果:")
            print(f"  实体数: {len(entities)}")
            print(f"  关系数: {len(relations)}")
            
            ***REMOVED*** 显示实体类型分布
            entity_types = {}
            for entity in entities:
                etype = entity.type.value if hasattr(entity.type, 'value') else str(entity.type)
                entity_types[etype] = entity_types.get(etype, 0) + 1
            
            print(f"  实体类型分布: {entity_types}")
        
        ***REMOVED*** 保存元数据
        creator._save_metadata()
        
        ***REMOVED*** 检查元数据
        metadata_file = creator.output_dir / "metadata.json"
        if metadata_file.exists():
            metadata = json.loads(metadata_file.read_text(encoding='utf-8'))
            print(f"\n元数据:")
            print(f"  增强提取: {metadata.get('enhanced_extraction', {}).get('enabled', False)}")
            print(f"  创作上下文: {metadata.get('creative_context', {}).get('enabled', False)}")
            if metadata.get('creative_context', {}).get('enabled'):
                print(f"  实体数: {metadata.get('creative_context', {}).get('entities_count', 0)}")
                print(f"  关系数: {metadata.get('creative_context', {}).get('relations_count', 0)}")
        
        print(f"\n✅ 完整集成测试成功")
        print(f"输出目录: {creator.output_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ 完整集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("=" * 70)
    print("小说创作系统优化功能测试")
    print("=" * 70)
    
    results = {}
    
    ***REMOVED*** 测试 1: 增强实体提取
    try:
        entity_count, enhanced_count = test_enhanced_extraction()
        results['enhanced_extraction'] = {
            'success': True,
            'entity_count': entity_count,
            'enhanced_count': enhanced_count
        }
    except Exception as e:
        print(f"❌ 增强实体提取测试失败: {e}")
        results['enhanced_extraction'] = {'success': False, 'error': str(e)}
    
    ***REMOVED*** 测试 2: UniMem 集成
    results['unimem'] = {
        'success': test_unimem_integration()
    }
    
    ***REMOVED*** 测试 3: 完整集成（可选，需要 LLM）
    user_input = input("\n是否运行完整集成测试（需要 LLM 调用）？(y/n): ")
    if user_input.lower() == 'y':
        results['full_integration'] = {
            'success': test_full_integration()
        }
    else:
        print("跳过完整集成测试")
    
    ***REMOVED*** 总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result.get('success') else "❌ 失败"
        print(f"{test_name}: {status}")
        if 'entity_count' in result:
            print(f"  实体数: {result['entity_count']}, 增强提取: {result['enhanced_count']}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
