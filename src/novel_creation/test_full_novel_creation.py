"""
完整小说创作流程测试脚本

测试从 idea 到完整小说的端到端流程
"""
import sys
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from novel_creation.react_novel_creator import ReactNovelCreator

logger = logging.getLogger(__name__)


def test_full_novel_creation(
    novel_title: str = "测试小说",
    genre: str = "科幻",
    theme: str = "时间旅行与平行世界",
    target_chapters: int = 5,
    words_per_chapter: int = 2000
):
    """
    测试完整小说创作流程
    
    Args:
        novel_title: 小说标题
        genre: 小说类型
        theme: 主题
        target_chapters: 目标章节数
        words_per_chapter: 每章目标字数
    """
    print("=" * 70)
    print("完整小说创作流程测试")
    print("=" * 70)
    print()
    print(f"📖 小说标题: {novel_title}")
    print(f"📚 类型: {genre}")
    print(f"🎯 主题: {theme}")
    print(f"📑 章节数: {target_chapters} 章")
    print(f"📝 每章字数: {words_per_chapter} 字")
    print()
    
    # 创建创作器（启用所有优化功能）
    print("=" * 70)
    print("初始化创作器...")
    print("=" * 70)
    
    try:
        creator = ReactNovelCreator(
            novel_title=novel_title,
            enable_context_offloading=True,
            enable_creative_context=True,
            enable_enhanced_extraction=True,
            enable_unimem=False,  # 先不使用 UniMem
            enable_quality_check=True
        )
        print("✅ 创作器初始化成功")
        print()
        print("优化功能状态：")
        # 检查属性是否存在
        if hasattr(creator, '_enable_context_offloading'):
            print(f"  ✅ 上下文卸载: {creator._enable_context_offloading}")
        if hasattr(creator, 'enable_creative_context'):
            print(f"  ✅ 创作上下文: {creator.enable_creative_context}")
        if hasattr(creator, 'enable_enhanced_extraction'):
            print(f"  ✅ 增强实体提取: {creator.enable_enhanced_extraction}")
        if hasattr(creator, 'enable_quality_check'):
            print(f"  ✅ 质量检查: {creator.enable_quality_check}")
        print()
    except Exception as e:
        print(f"❌ 创作器初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # 开始创作
    print("=" * 70)
    print("开始创作...")
    print("=" * 70)
    print()
    
    start_time = datetime.now()
    
    try:
        result = creator.create_novel(
            genre=genre,
            theme=theme,
            target_chapters=target_chapters,
            words_per_chapter=words_per_chapter,
            start_from_chapter=1
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print()
        print("=" * 70)
        print("✅ 创作完成！")
        print("=" * 70)
        print()
        print(f"📖 小说标题: {result['novel_title']}")
        print(f"📑 总章节数: {result['total_chapters']}")
        print(f"📝 总字数: {result['total_words']:,} 字")
        print(f"⏱️  耗时: {duration:.1f} 秒")
        print(f"📁 输出目录: {result['output_dir']}")
        print()
        
        # 显示优化效果
        _show_optimization_results(result['output_dir'])
        
        return result
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 创作已中断")
        return None
    except Exception as e:
        print(f"\n\n❌ 创作失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def _show_optimization_results(output_dir: str):
    """显示优化效果统计"""
    import json
    
    metadata_file = Path(output_dir) / "metadata.json"
    if not metadata_file.exists():
        print("⚠️ 元数据文件不存在")
        return
    
    try:
        metadata = json.loads(metadata_file.read_text(encoding='utf-8'))
        
        print("=" * 70)
        print("优化效果统计")
        print("=" * 70)
        print()
        
        # 增强提取效果
        enhanced = metadata.get('enhanced_extraction', {})
        if enhanced.get('enabled'):
            print("✅ 增强实体提取:")
            print(f"   方法: {enhanced.get('method', 'N/A')}")
            print()
        
        # 创作上下文效果
        creative = metadata.get('creative_context', {})
        if creative.get('enabled'):
            entities_count = creative.get('entities_count', 0)
            relations_count = creative.get('relations_count', 0)
            chapters = metadata.get('total_chapters', 1)
            entities_per_chapter = entities_count / chapters if chapters > 0 else 0
            
            print("✅ 创作上下文:")
            print(f"   实体总数: {entities_count}")
            print(f"   关系总数: {relations_count}")
            print(f"   平均实体数/章: {entities_per_chapter:.1f}")
            print(f"   目标: 5+ 实体/章")
            print(f"   状态: {'✅ 达标' if entities_per_chapter >= 5 else '⚠️  未达标'}")
            print()
        
        # 质量检查效果
        quality = metadata.get('quality_check', {})
        if quality.get('enabled'):
            total_issues = quality.get('total_issues', 0)
            high_severity = quality.get('high_severity_chapters', 0)
            
            print("✅ 质量检查:")
            print(f"   发现问题: {total_issues} 个")
            print(f"   严重问题章节: {high_severity} 个")
            if total_issues == 0:
                print(f"   状态: ✅ 未发现问题")
            elif high_severity == 0:
                print(f"   状态: ⚠️  有轻微问题")
            else:
                print(f"   状态: ⚠️  有严重问题")
            print()
        
        # 文件输出
        print("=" * 70)
        print("输出文件")
        print("=" * 70)
        print()
        print(f"📄 完整小说: {output_dir}/{metadata.get('novel_title', '小说')}_完整版.txt")
        print(f"📊 元数据: {output_dir}/metadata.json")
        print(f"📋 大纲: {output_dir}/novel_plan.json")
        if creative.get('enabled'):
            print(f"🧠 语义网格: {output_dir}/semantic_mesh/mesh.json")
        print()
        
    except Exception as e:
        print(f"⚠️ 读取元数据失败: {e}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='完整小说创作流程测试')
    parser.add_argument('--title', type=str, default='测试小说', help='小说标题')
    parser.add_argument('--genre', type=str, default='科幻', help='小说类型')
    parser.add_argument('--theme', type=str, default='时间旅行与平行世界', help='主题')
    parser.add_argument('--chapters', type=int, default=5, help='章节数')
    parser.add_argument('--words', type=int, default=2000, help='每章字数')
    
    args = parser.parse_args()
    
    result = test_full_novel_creation(
        novel_title=args.title,
        genre=args.genre,
        theme=args.theme,
        target_chapters=args.chapters,
        words_per_chapter=args.words
    )
    
    if result:
        print("=" * 70)
        print("🎉 测试成功完成！")
        print("=" * 70)
        return 0
    else:
        print("=" * 70)
        print("❌ 测试失败")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
