"""
批量学习小说模式的脚本

从小说数据集中提取模式并存储到记忆系统
"""

import sys
import os
import json
import argparse
import logging
from pathlib import Path

***REMOVED*** 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from unimem.core import UniMem
from unimem.learning.novel_processor import NovelProcessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="批量学习小说模式")
    parser.add_argument("--novel_dir", type=str, 
                       default="/root/data/AI/creator/src/data/小说",
                       help="小说目录路径")
    parser.add_argument("--limit", type=int, default=None,
                       help="处理数量限制（用于测试）")
    parser.add_argument("--output", type=str, default=None,
                       help="输出JSON文件路径（保存处理结果）")
    parser.add_argument("--store", action="store_true", default=True,
                       help="是否存储到记忆系统")
    parser.add_argument("--config", type=str, default=None,
                       help="UniMem配置文件路径")
    
    args = parser.parse_args()
    
    ***REMOVED*** 初始化 UniMem
    logger.info("初始化 UniMem...")
    unimem = UniMem(
        storage_backend="redis",
        graph_backend="neo4j",
        vector_backend="qdrant",
        config_file=args.config
    )
    
    ***REMOVED*** 创建处理器
    processor = NovelProcessor(unimem_instance=unimem)
    
    ***REMOVED*** 批量处理
    logger.info(f"开始批量处理小说目录: {args.novel_dir}")
    results = processor.batch_process(
        novel_dir=args.novel_dir,
        limit=args.limit,
        store_to_memory=args.store
    )
    
    ***REMOVED*** 保存结果
    if args.output:
        logger.info(f"保存处理结果到: {args.output}")
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        ***REMOVED*** 保存统计信息
        stats = {
            "total_processed": len(results),
            "total_chapters": sum(r["structure"].get("chapter_count", 0) for r in results),
            "total_plot_points": sum(len(r.get("plot_points", [])) for r in results),
            "novels": [
                {
                    "title": r["metadata"].get("title"),
                    "chapters": r["structure"].get("chapter_count", 0),
                    "plot_points": len(r.get("plot_points", [])),
                }
                for r in results
            ]
        }
        
        stats_file = args.output.replace(".json", "_stats.json")
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        logger.info(f"统计信息已保存到: {stats_file}")
    
    logger.info("批量学习完成！")


if __name__ == "__main__":
    main()

