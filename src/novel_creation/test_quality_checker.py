"""
测试质量检查器功能
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from novel_creation.quality_checker import QualityChecker, check_chapter_quality
from novel_creation.react_novel_creator import ReactNovelCreator


def test_basic_quality_check():
    """测试基础质量检查"""
    print("=" * 70)
    print("测试 1: 基础质量检查")
    print("=" * 70)
    
    checker = QualityChecker(llm_client=None)
    
    ***REMOVED*** 测试章节内容
    chapter_content = """
    公元2023年，北京国家会议中心。
    
    林风站在落地窗前，望着窗外金黄色的银杏叶在秋风中飘落。作为《科技前沿》杂志的首席记者，他已经报道过无数次科技会议。
    
    "林记者，会议还有十分钟开始。"助理小陈轻声提醒。
    
    林风点点头，调整了一下胸前的工作证。他看到了苏雨博士，一个天才物理学家，正在检查她的实验设备。
    
    在会场外，陈局长正在和一群科学家讨论时空旅行的可能性。突然，一个神秘的影子出现在角落，没有人注意到他的存在。
    
    林风拿出一本古老的日记，封面上写着"时空旅者的日记"。他翻开第一页，看到了令人震惊的内容。
    """
    
    ***REMOVED*** 创建前面章节（模拟）
    previous_chapters = [
        {
            "number": 0,
            "content": "第一章已经介绍了主角林风是一名记者。",
            "summary": "第一章简介"
        }
    ]
    
    issues = checker.check_chapter(
        chapter_content=chapter_content,
        chapter_number=2,
        previous_chapters=previous_chapters,
        novel_plan=None
    )
    
    print(f"\n发现问题数: {len(issues)}")
    
    if issues:
        print("\n问题详情:")
        for issue in issues:
            print(f"  [{issue.severity.value.upper()}] {issue.issue_type.value}: {issue.description}")
            if issue.suggestion:
                print(f"    建议: {issue.suggestion}")
    else:
        print("✅ 未发现问题")
    
    return len(issues)


def test_character_consistency():
    """测试角色一致性检查"""
    print("\n" + "=" * 70)
    print("测试 2: 角色一致性检查")
    print("=" * 70)
    
    checker = QualityChecker(llm_client=None)
    
    ***REMOVED*** 测试：角色名称相似但不一致
    chapter_content = """
    林风站在窗前，看到了苏雨。
    "苏语，你好吗？"林风问道。
    """
    
    previous_chapters = [
        {
            "number": 1,
            "content": "林风遇到了苏雨博士。",
            "summary": "第一章"
        }
    ]
    
    issues = checker.check_character_consistency(
        chapter_content=chapter_content,
        chapter_number=2,
        previous_chapters=previous_chapters
    )
    
    print(f"\n发现问题数: {len(issues)}")
    
    for issue in issues:
        print(f"  [{issue.severity.value.upper()}] {issue.description}")
        print(f"    位置: {issue.location}")
        if issue.suggestion:
            print(f"    建议: {issue.suggestion}")
    
    return len(issues)


def test_worldview_consistency():
    """测试世界观一致性检查"""
    print("\n" + "=" * 70)
    print("测试 3: 世界观一致性检查")
    print("=" * 70)
    
    checker = QualityChecker(llm_client=None)
    
    ***REMOVED*** 测试：前面章节没有魔法，但本章出现魔法
    chapter_content = """
    林风念动咒语，施展了一个强大的魔法。
    魔法阵在空气中闪烁，释放出强大的魔力。
    这是一个禁咒级别的魔法，足以摧毁整个城市。
    """
    
    previous_chapters = [
        {
            "number": 1,
            "content": "这是一个科幻世界，只有科技没有魔法。",
            "summary": "第一章介绍世界观"
        }
    ]
    
    issues = checker.check_worldview_consistency(
        chapter_content=chapter_content,
        chapter_number=2,
        previous_chapters=previous_chapters
    )
    
    print(f"\n发现问题数: {len(issues)}")
    
    for issue in issues:
        print(f"  [{issue.severity.value.upper()}] {issue.description}")
        if issue.suggestion:
            print(f"    建议: {issue.suggestion}")
    
    return len(issues)


def test_coherence():
    """测试连贯性检查"""
    print("\n" + "=" * 70)
    print("测试 4: 连贯性检查")
    print("=" * 70)
    
    checker = QualityChecker(llm_client=None)
    
    ***REMOVED*** 测试：章节间缺乏衔接
    chapter_content = """
    在遥远的未来，机器人统治了地球。
    人类被迫生活在火星上。
    """
    
    previous_chapters = [
        {
            "number": 1,
            "content": "林风是一名记者，正在北京报道科技会议。",
            "summary": "第一章"
        }
    ]
    
    issues = checker.check_coherence(
        chapter_content=chapter_content,
        chapter_number=2,
        previous_chapters=previous_chapters
    )
    
    print(f"\n发现问题数: {len(issues)}")
    
    for issue in issues:
        print(f"  [{issue.severity.value.upper()}] {issue.description}")
        if issue.suggestion:
            print(f"    建议: {issue.suggestion}")
    
    return len(issues)


def test_integration_with_creator():
    """测试与 ReactNovelCreator 的集成"""
    print("\n" + "=" * 70)
    print("测试 5: 与 ReactNovelCreator 集成")
    print("=" * 70)
    
    try:
        creator = ReactNovelCreator(
            novel_title="测试质量检查",
            enable_context_offloading=False,
            enable_creative_context=True,
            enable_enhanced_extraction=True,
            enable_unimem=False,
            enable_quality_check=True  ***REMOVED*** 启用质量检查
        )
        
        print("✅ ReactNovelCreator 初始化成功")
        print(f"   质量检查: {creator.enable_quality_check}")
        print(f"   质量检查器: {'已初始化' if creator.quality_checker else '未初始化'}")
        
        ***REMOVED*** 测试质量检查方法
        from novel_creation.react_novel_creator import NovelChapter
        
        test_chapter = NovelChapter(
            chapter_number=1,
            title="测试章节",
            content="这是测试内容。",
            summary="测试"
        )
        
        result = creator._check_chapter_quality(test_chapter, None)
        print(f"\n✅ 质量检查方法执行成功")
        print(f"   发现问题: {result.get('total_issues', 0)} 个")
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("=" * 70)
    print("质量检查器功能测试")
    print("=" * 70)
    
    results = {}
    
    ***REMOVED*** 测试 1: 基础质量检查
    results['basic_check'] = test_basic_quality_check()
    
    ***REMOVED*** 测试 2: 角色一致性
    results['character'] = test_character_consistency()
    
    ***REMOVED*** 测试 3: 世界观一致性
    results['worldview'] = test_worldview_consistency()
    
    ***REMOVED*** 测试 4: 连贯性
    results['coherence'] = test_coherence()
    
    ***REMOVED*** 测试 5: 集成测试
    results['integration'] = test_integration_with_creator()
    
    ***REMOVED*** 总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    
    for test_name, result in results.items():
        if isinstance(result, bool):
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test_name}: {status}")
        else:
            print(f"{test_name}: 发现问题 {result} 个")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
