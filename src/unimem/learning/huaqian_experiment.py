"""
《花千骨》深度实验脚本

基于章节结构、时序信息和目录，探索动态编排和记忆系统的潜力
"""

import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from unimem.core import UniMem
from unimem.learning.huaqian_deep_analysis import HuaqianDeepAnalyzer
from unimem.types import Experience, Context, MemoryType, MemoryLayer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="《花千骨》深度实验")
    parser.add_argument("--filepath", type=str,
                       default="/root/data/AI/creator/src/data/小说/小说_1/电子书合集_10万+小说合集_12000本小说_TOP100-言情篇_No.11 仙侠奇缘之花千骨.txt",
                       help="小说文件路径")
    parser.add_argument("--store", action="store_true", default=True,
                       help="是否存储到记忆系统")
    parser.add_argument("--output", type=str, default="results/huaqian_analysis.json",
                       help="输出JSON文件路径")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("《花千骨》深度分析实验")
    print("=" * 70)
    
    ***REMOVED*** 1. 初始化分析器
    print("\n【步骤 1】加载和解析小说...")
    analyzer = HuaqianDeepAnalyzer(args.filepath)
    analyzer.load_and_parse()
    
    print(f"✓ 解析完成: {len(analyzer.volumes)} 卷, {len(analyzer.chapters)} 章")
    
    ***REMOVED*** 2. 分析动态编排模式
    print("\n【步骤 2】分析动态编排模式...")
    orchestration_patterns = analyzer.analyze_dynamic_orchestration_patterns()
    
    print(f"✓ 卷转换模式: {len(orchestration_patterns['volume_transitions'])} 个")
    print(f"✓ 章节序列: {len(orchestration_patterns['chapter_sequences'])} 个")
    print(f"✓ 推进模式: {len(orchestration_patterns['progression_patterns'])} 个")
    print(f"✓ 节奏模式: {len(orchestration_patterns['pacing_patterns'])} 个")
    
    ***REMOVED*** 3. 提取记忆模式
    print("\n【步骤 3】提取记忆模式...")
    memory_patterns = analyzer.extract_memory_patterns()
    
    print(f"✓ 提取了 {len(memory_patterns)} 个记忆模式")
    
    ***REMOVED*** 3.5. 使用 ReMe 启发的多面蒸馏提取（新增）
    print("\n【步骤 3.5】ReMe 启发的多面蒸馏提取...")
    try:
        reme_experiences = analyzer.extract_with_reme_inspiration()
        print(f"✓ 成功模式: {len(reme_experiences['success'])} 个")
        print(f"✓ 失败模式: {len(reme_experiences['failure'])} 个")
        print(f"✓ 比较性洞察: {len(reme_experiences['comparison'])} 个")
    except Exception as e:
        logger.warning(f"ReMe 提取失败: {e}", exc_info=True)
        reme_experiences = {"success": [], "failure": [], "comparison": []}
    
    ***REMOVED*** 4. 生成编排洞察
    print("\n【步骤 4】生成编排洞察...")
    insights = analyzer.generate_orchestration_insights()
    
    print(f"✓ Agent选择模式: {len(insights['agent_selection_patterns'])} 个")
    print(f"✓ 工具使用模式: {len(insights['tool_usage_patterns'])} 个")
    
    ***REMOVED*** 5. 存储到记忆系统
    if args.store:
        print("\n【步骤 5】存储模式到记忆系统...")
        unimem = UniMem(
            storage_backend="redis",
            graph_backend="neo4j",
            vector_backend="qdrant"
        )
        
        ***REMOVED*** 导出记忆项
        memory_items = analyzer.export_for_memory_system()
        
        stored_count = 0
        total_items = len(memory_items)
        ***REMOVED*** 限制存储数量，避免实验时间过长
        max_items = min(20, total_items)  ***REMOVED*** 先存储前20个，足够验证流程
        print(f"  准备存储 {max_items}/{total_items} 个记忆项...")
        for idx, item in enumerate(memory_items[:max_items], 1):
            try:
                memory = unimem.retain(
                    experience=Experience(
                        content=item["content"],
                        timestamp=datetime.now(),
                        metadata=item.get("metadata", {})
                    ),
                    context=Context(
                        session_id="huaqian_experiment",
                        user_id="system",
                        metadata={
                            "source": "huaqian_novel",
                            "experiment": True
                        }
                    ),
                )
                success = memory is not None
                
                if success:
                    stored_count += 1
                    if idx % 5 == 0:
                        print(f"  进度: {idx}/{max_items} (已存储 {stored_count} 个)")
                    
            except Exception as e:
                logger.error(f"存储失败 ({idx}/{max_items}): {e}", exc_info=True)
        
        print(f"✓ 已存储 {stored_count}/{max_items} 个模式到记忆系统")
    
    ***REMOVED*** 6. 保存分析结果
    print("\n【步骤 6】保存分析结果...")
    results = {
        "metadata": {
            "novel": "仙侠奇缘之花千骨",
            "analysis_time": datetime.now().isoformat(),
            "volumes_count": len(analyzer.volumes),
            "chapters_count": len(analyzer.chapters),
        },
        "structure": {
            "volumes": [
                {
                    "volume_number": vol["volume_number"],
                    "title": vol["volume_title"],
                    "chapter_count": len(vol["chapters"]),
                }
                for vol in analyzer.volumes
            ],
            "chapters": [
                {
                    "chapter_number": ch["chapter_number"],
                    "volume_number": ch["volume_number"],
                    "title": ch["chapter_title"],
                    "word_count": ch.get("meta_word_count", 0),
                    "update_time": ch.get("update_time"),
                }
                for ch in analyzer.chapters[:20]  ***REMOVED*** 前20章
            ]
        },
        "orchestration_patterns": orchestration_patterns,
        "memory_patterns": memory_patterns[:30],  ***REMOVED*** 前30个
        "insights": insights,
    }
    
    ***REMOVED*** 保存到文件
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"✓ 结果已保存到: {output_path}")
    
    ***REMOVED*** 7. 输出关键洞察
    print("\n" + "=" * 70)
    print("关键洞察总结")
    print("=" * 70)
    
    print("\n【卷结构分析】")
    for vol in analyzer.volumes[:3]:
        print(f"  卷{vol['volume_number']}: {vol['volume_title']}")
        print(f"    章节数: {len(vol['chapters'])}")
        print(f"    主题: {analyzer._infer_theme(vol)}")
    
    print("\n【时序分析】")
    if analyzer.timeline:
        avg_interval = sum(
            (analyzer.timeline[i+1]["update_time"] - analyzer.timeline[i]["update_time"]).total_seconds() / 3600
            for i in range(min(10, len(analyzer.timeline) - 1))
        ) / max(min(10, len(analyzer.timeline) - 1), 1)
        print(f"  平均更新间隔: {avg_interval:.1f} 小时")
        print(f"  最早: {analyzer.timeline[0]['update_time']}")
        print(f"  最晚: {analyzer.timeline[-1]['update_time']}")
    
    print("\n【编排建议】")
    if insights["agent_selection_patterns"]:
        print(f"  发现 {len(insights['agent_selection_patterns'])} 个Agent选择模式")
        for pattern in insights["agent_selection_patterns"][:5]:
            print(f"    - {pattern['chapter'][:30]}... → {', '.join(pattern['recommended_agents'])}")
    
    print("\n" + "=" * 70)
    print("实验完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()

