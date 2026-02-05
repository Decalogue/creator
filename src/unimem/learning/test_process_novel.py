"""
测试小说处理功能

处理单本小说，验证提取功能是否正常
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from unimem.learning.novel_processor import NovelProcessor

def test_process_huaqian():
    """测试处理《花千骨》"""
    filepath = "/root/data/AI/creator/src/data/小说/小说_1/电子书合集_10万+小说合集_12000本小说_TOP100-言情篇_No.11 仙侠奇缘之花千骨.txt"
    
    print("=" * 60)
    print("测试小说处理功能")
    print("=" * 60)
    
    processor = NovelProcessor()
    
    print(f"\n处理文件: {filepath}")
    result = processor.process_novel(filepath)
    
    if result:
        print(f"\n✓ 处理成功!")
        print(f"\n【元数据】")
        metadata = result.get("metadata", {})
        print(f"  标题: {metadata.get('title')}")
        print(f"  分类: {metadata.get('category')}")
        
        print(f"\n【结构信息】")
        structure = result.get("structure", {})
        print(f"  总长度: {structure.get('total_length'):,} 字符")
        print(f"  章节数: {structure.get('chapter_count')}")
        
        if structure.get("chapters"):
            print(f"  前3章标题:")
            for i, ch in enumerate(structure["chapters"][:3], 1):
                print(f"    {i}. {ch['title'][:50]}")
        
        print(f"\n【情节节点】")
        plot_points = result.get("plot_points", [])
        print(f"  找到 {len(plot_points)} 个情节节点")
        if plot_points:
            print(f"  前3个节点:")
            for i, point in enumerate(plot_points[:3], 1):
                print(f"    {i}. 类型: {', '.join(point.get('types', []))}")
                print(f"       位置: {point.get('position', 0):.2%}")
                print(f"       内容: {point.get('paragraph', '')[:100]}...")
        
        print(f"\n【人物信息】")
        characters = result.get("characters", [])
        print(f"  找到 {len(characters)} 个主要人物:")
        for i, char in enumerate(characters[:5], 1):
            print(f"    {i}. {char['name']} (出现 {char['frequency']} 次)")
        
        print(f"\n【节奏特征】")
        rhythm = result.get("rhythm", {})
        print(f"  平均章节长度: {rhythm.get('avg_chapter_length', 0):,.0f} 字")
        print(f"  章节数: {rhythm.get('chapter_count')}")
        print(f"  总长度: {rhythm.get('total_length', 0):,} 字")
        
        # 保存结果
        output_file = "/tmp/test_huaqian_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存到: {output_file}")
        
    else:
        print("✗ 处理失败")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_process_huaqian()

