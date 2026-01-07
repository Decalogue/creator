"""
测试 ReMe 启发的提取器

验证多面蒸馏提取功能
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from unimem.learning.huaqian_deep_analysis import HuaqianDeepAnalyzer
from unimem.learning.reme_inspired_extractor import RemeInspiredExtractor

def test_reme_extraction():
    """测试 ReMe 启发的提取"""
    print("=" * 70)
    print("测试 ReMe 启发的多面蒸馏提取")
    print("=" * 70)
    
    # 1. 加载小说数据
    filepath = "/root/data/AI/creator/src/data/小说/小说_1/电子书合集_10万+小说合集_12000本小说_TOP100-言情篇_No.11 仙侠奇缘之花千骨.txt"
    
    print("\n【步骤 1】加载和解析小说...")
    analyzer = HuaqianDeepAnalyzer(filepath)
    analyzer.load_and_parse()
    print(f"✓ 解析完成: {len(analyzer.volumes)} 卷, {len(analyzer.chapters)} 章")
    
    # 2. 使用 ReMe 启发的提取
    print("\n【步骤 2】ReMe 启发的多面蒸馏提取...")
    reme_experiences = analyzer.extract_with_reme_inspiration()
    
    print(f"\n✓ 提取结果:")
    print(f"  成功模式: {len(reme_experiences['success'])} 个")
    print(f"  失败模式: {len(reme_experiences['failure'])} 个")
    print(f"  比较性洞察: {len(reme_experiences['comparison'])} 个")
    
    # 3. 显示示例
    if reme_experiences['success']:
        print(f"\n【成功模式示例】")
        example = reme_experiences['success'][0]
        print(f"  场景: {example['scenario']}")
        print(f"  内容: {example['content'][:80]}...")
        print(f"  置信度: {example['confidence']:.2f}")
        print(f"  成功分数: {example['success_score']:.2f}")
    
    if reme_experiences['failure']:
        print(f"\n【失败模式示例】")
        example = reme_experiences['failure'][0]
        print(f"  场景: {example['scenario']}")
        print(f"  内容: {example['content'][:80]}...")
        print(f"  失败次数: {example['failure_count']}")
    
    if reme_experiences['comparison']:
        print(f"\n【比较性洞察示例】")
        example = reme_experiences['comparison'][0]
        print(f"  场景: {example['scenario']}")
        print(f"  内容: {example['content'][:80]}...")
        print(f"  置信度: {example['confidence']:.2f}")
    
    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)
    
    return reme_experiences

if __name__ == "__main__":
    test_reme_extraction()

