"""
立即开始创作：使用优化后的系统
"""
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from novel_creation.react_novel_creator import ReactNovelCreator


def create_novel():
    """立即开始创作"""
    print("=" * 70)
    print("小说创作系统 - 开始创作")
    print("=" * 70)
    print()
    
    # 创作配置
    novel_title = "我的第一部优化小说"
    genre = "科幻"
    theme = "时间旅行与平行世界的探索"
    target_chapters = 3
    words_per_chapter = 2000
    
    print("创作配置：")
    print(f"  标题: {novel_title}")
    print(f"  类型: {genre}")
    print(f"  主题: {theme}")
    print(f"  章节数: {target_chapters} 章")
    print(f"  每章字数: {words_per_chapter} 字")
    print()
    
    print("=" * 70)
    print("初始化创作器...")
    print("=" * 70)
    
    # 创建创作器（启用所有优化功能）
    creator = ReactNovelCreator(
        novel_title=novel_title,
        enable_context_offloading=True,
        enable_creative_context=True,
        enable_enhanced_extraction=True,  # 启用增强实体提取
        enable_unimem=False,  # 不使用 UniMem（可选）
        enable_quality_check=True  # 启用质量检查
    )
    
    print("✅ 创作器初始化成功")
    print()
    print("优化功能状态：")
    print(f"  ✅ 增强实体提取: {creator.enable_enhanced_extraction}")
    print(f"  ✅ 质量检查: {creator.enable_quality_check}")
    print(f"  ✅ 创作上下文: {creator.enable_creative_context}")
    print()
    
    print("=" * 70)
    print("开始创作...")
    print("=" * 70)
    print()
    
    try:
        # 创作小说
        result = creator.create_novel(
            genre=genre,
            theme=theme,
            target_chapters=target_chapters,
            words_per_chapter=words_per_chapter,
            start_from_chapter=1
        )
        
        print()
        print("=" * 70)
        print("✅ 创作完成！")
        print("=" * 70)
        print()
        print(f"小说标题: {result['novel_title']}")
        print(f"总章节数: {result['total_chapters']}")
        print(f"总字数: {result['total_words']:,} 字")
        print(f"输出目录: {result['output_dir']}")
        print()
        
        # 显示优化效果
        import json
        metadata_file = Path(result['output_dir']) / "metadata.json"
        if metadata_file.exists():
            metadata = json.loads(metadata_file.read_text(encoding='utf-8'))
            
            print("优化效果统计：")
            print()
            
            # 增强提取效果
            enhanced = metadata.get('enhanced_extraction', {})
            if enhanced.get('enabled'):
                print(f"✅ 增强实体提取:")
                print(f"   方法: {enhanced.get('method', 'N/A')}")
            
            # 创作上下文效果
            creative = metadata.get('creative_context', {})
            if creative.get('enabled'):
                entities_count = creative.get('entities_count', 0)
                relations_count = creative.get('relations_count', 0)
                chapters = metadata.get('total_chapters', 1)
                entities_per_chapter = entities_count / chapters if chapters > 0 else 0
                
                print(f"✅ 创作上下文:")
                print(f"   实体总数: {entities_count}")
                print(f"   关系总数: {relations_count}")
                print(f"   平均实体数/章: {entities_per_chapter:.1f}")
                print(f"   目标: 5+ 实体/章")
                print(f"   状态: {'✅ 达标' if entities_per_chapter >= 5 else '⚠️  未达标'}")
            
            # 质量检查效果
            quality = metadata.get('quality_check', {})
            if quality.get('enabled'):
                total_issues = quality.get('total_issues', 0)
                high_severity = quality.get('high_severity_chapters', 0)
                
                print(f"✅ 质量检查:")
                print(f"   发现问题: {total_issues} 个")
                print(f"   严重问题章节: {high_severity} 个")
                if total_issues == 0:
                    print(f"   状态: ✅ 未发现问题")
                elif high_severity == 0:
                    print(f"   状态: ⚠️  有轻微问题")
                else:
                    print(f"   状态: ⚠️  有严重问题")
        
        print()
        print("=" * 70)
        print("创作成功完成！")
        print("=" * 70)
        print()
        print(f"📁 完整小说: {result['output_dir']}/{novel_title}_完整版.txt")
        print(f"📊 元数据: {result['output_dir']}/metadata.json")
        print(f"🧠 语义网格: {result['output_dir']}/semantic_mesh/mesh.json")
        print()
        
        return result
        
    except KeyboardInterrupt:
        print("\n\n创作已中断")
        return None
    except Exception as e:
        print(f"\n\n❌ 创作失败: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    create_novel()
