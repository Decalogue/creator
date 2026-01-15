"""
快速验证脚本：测试优化功能的核心逻辑
不依赖实际 LLM 调用，只验证代码路径和结构
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging
logging.basicConfig(level=logging.WARNING)  # 减少日志输出

def test_enhanced_extractor_structure():
    """测试增强实体提取器的结构"""
    print("=" * 70)
    print("测试 1: 增强实体提取器结构")
    print("=" * 70)
    
    try:
        from novel_creation.enhanced_entity_extractor import EnhancedEntityExtractor, EntityExtractionResult
        from llm.chat import deepseek_v3_2
        
        # 初始化（不实际调用 LLM）
        extractor = EnhancedEntityExtractor(llm_client=None, use_ner=False)
        print("✅ 增强实体提取器初始化成功")
        
        # 测试基础提取（不调用 LLM）
        test_text = """
        林风站在落地窗前，看到了苏雨博士和陈局长。
        "你好，林记者。"苏雨说道。
        他们正在国家会议中心讨论时空旅行的问题。
        """
        
        result = extractor._extract_with_rules(test_text, chapter_number=1)
        print(f"✅ 基础提取测试成功，提取到 {len(result['entities'])} 个实体")
        
        # 检查实体类型
        entity_types = {}
        for entity in result['entities']:
            etype = str(entity.type)
            entity_types[etype] = entity_types.get(etype, 0) + 1
            print(f"   - {etype}: {entity.name}")
        
        print(f"\n实体类型分布: {entity_types}")
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_react_creator_initialization():
    """测试 ReactNovelCreator 的初始化"""
    print("\n" + "=" * 70)
    print("测试 2: ReactNovelCreator 初始化")
    print("=" * 70)
    
    try:
        from novel_creation.react_novel_creator import ReactNovelCreator
        
        # 测试启用增强提取
        creator1 = ReactNovelCreator(
            novel_title="测试1",
            enable_context_offloading=False,
            enable_creative_context=False,
            enable_enhanced_extraction=True,
            enable_unimem=False
        )
        print("✅ 启用增强提取的初始化成功")
        print(f"   增强提取: {creator1.enable_enhanced_extraction}")
        print(f"   实体提取器: {'已初始化' if creator1.entity_extractor else '未初始化'}")
        
        # 测试启用 UniMem（不实际连接）
        try:
            creator2 = ReactNovelCreator(
                novel_title="测试2",
                enable_context_offloading=False,
                enable_creative_context=False,
                enable_enhanced_extraction=False,
                enable_unimem=True  # 可能失败，但不应该报错
            )
            print("✅ 启用 UniMem 的初始化完成（可能未实际连接）")
            print(f"   UniMem: {creator2.enable_unimem}")
            print(f"   UniMem 实例: {'已初始化' if creator2.unimem else '未初始化（正常）'}")
        except Exception as e:
            print(f"⚠️  UniMem 初始化失败（预期，可能未安装）: {type(e).__name__}")
        
        # 测试完整配置
        creator3 = ReactNovelCreator(
            novel_title="测试3",
            enable_context_offloading=True,
            enable_creative_context=True,
            enable_enhanced_extraction=True,
            enable_unimem=False
        )
        print("✅ 完整配置初始化成功")
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_entity_extraction_methods():
    """测试实体提取方法"""
    print("\n" + "=" * 70)
    print("测试 3: 实体提取方法")
    print("=" * 70)
    
    try:
        from novel_creation.react_novel_creator import ReactNovelCreator, NovelChapter
        
        creator = ReactNovelCreator(
            novel_title="测试提取",
            enable_context_offloading=False,
            enable_creative_context=True,
            enable_enhanced_extraction=True,
            enable_unimem=False
        )
        
        # 创建测试章节
        test_content = """
        公元2023年，北京国家会议中心。
        
        林风看到了苏雨博士，她正在检查实验设备。
        "林记者，会议马上开始。"苏雨说道。
        
        陈局长走了过来，他们开始讨论时空旅行的问题。
        在角落，一个神秘的影子静静观察着一切。
        """
        
        test_chapter = NovelChapter(
            chapter_number=1,
            title="测试章节",
            content=test_content,
            summary="测试实体提取"
        )
        
        # 测试基础提取方法
        print("测试基础提取方法...")
        basic_entities = creator._extract_entities_basic(test_chapter)
        print(f"✅ 基础提取成功，提取到 {len(basic_entities)} 个实体")
        
        # 测试增强提取方法（会回退到基础）
        print("测试增强提取方法（无 LLM，应回退到基础）...")
        entities = creator._extract_entities_from_chapter(test_chapter)
        print(f"✅ 增强提取成功，提取到 {len(entities)} 个实体")
        
        # 显示实体详情
        print("\n提取的实体:")
        for entity in entities:
            etype = entity.type.value if hasattr(entity.type, 'value') else str(entity.type)
            method = entity.metadata.get('extraction_method', 'unknown')
            print(f"  - {etype}: {entity.name} (方法: {method})")
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_unified_orchestrator():
    """测试统一编排器"""
    print("\n" + "=" * 70)
    print("测试 4: 统一编排器")
    print("=" * 70)
    
    try:
        from novel_creation.unified_orchestrator import (
            ReActOrchestrator,
            HybridOrchestrator
        )
        
        # 测试 ReAct 编排器
        print("测试 ReAct 编排器...")
        orchestrator1 = ReActOrchestrator(
            novel_title="测试编排",
            enable_creative_context=True,
            enable_unimem=False
        )
        print("✅ ReAct 编排器初始化成功")
        
        # 测试混合编排器
        print("测试混合编排器...")
        orchestrator2 = HybridOrchestrator(
            novel_title="测试混合",
            react_config={},
            puppeteer_config=None
        )
        print("✅ 混合编排器初始化成功")
        
        # 测试编排方式选择
        test_summary1 = "本章包含大量对话和心理描写"
        test_summary2 = "本章包含激烈的战斗和行动"
        
        choice1 = orchestrator2._select_orchestrator(test_summary1)
        choice2 = orchestrator2._select_orchestrator(test_summary2)
        
        print(f"✅ 编排方式选择:")
        print(f"   摘要1（对话）: {choice1}")
        print(f"   摘要2（行动）: {choice2}")
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("=" * 70)
    print("小说创作系统优化功能 - 快速验证")
    print("=" * 70)
    print()
    
    results = {}
    
    # 测试 1: 增强提取器结构
    results['extractor_structure'] = test_enhanced_extractor_structure()
    
    # 测试 2: ReactNovelCreator 初始化
    results['creator_init'] = test_react_creator_initialization()
    
    # 测试 3: 实体提取方法
    results['extraction_methods'] = test_entity_extraction_methods()
    
    # 测试 4: 统一编排器
    results['orchestrator'] = test_unified_orchestrator()
    
    # 总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️  部分测试失败，请检查错误信息")
    
    print("=" * 70)


if __name__ == "__main__":
    main()
