#!/usr/bin/env python3
"""
测试质量优化功能
包括：字数控制、质量问题、节奏和悬念优化
"""
import sys
import os
import argparse
import logging
from pathlib import Path
from typing import Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from novel_creation.react_novel_creator import ReactNovelCreator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_quality_optimizations(
    novel_title: str,
    genre: str,
    theme: str,
    target_chapters: int,
    words_per_chapter: int = 2048,
    test_title: Optional[str] = None
) -> None:
    """
    测试质量优化功能
    
    Args:
        novel_title: 小说标题（用于创作内容）
        genre: 小说类型
        theme: 主题
        target_chapters: 目标章节数
        words_per_chapter: 每章目标字数
        test_title: 测试标题（用于输出目录，如果为None则使用novel_title）
    """
    logger.info("=" * 80)
    logger.info("开始测试质量优化功能")
    logger.info("=" * 80)
    
    # 确定测试标题（用于输出目录）
    if test_title is None:
        test_title = novel_title
    
    logger.info(f"测试标题: {test_title}")
    logger.info(f"小说标题: {novel_title}")
    logger.info(f"类型: {genre}, 主题: {theme}")
    logger.info(f"目标章节数: {target_chapters}, 每章目标字数: {words_per_chapter}")
    logger.info("")
    
    # 选择LLM客户端（可通过环境变量或参数控制）
    import os
    llm_model = os.getenv("NOVEL_LLM_MODEL", "deepseek_v3_2")  # 默认使用deepseek_v3_2
    
    if llm_model == "gemini_3_flash":
        from llm.chat import gemini_3_flash
        llm_client = gemini_3_flash
        logger.info(f"使用LLM模型: gemini_3_flash")
    else:
        from llm.chat import deepseek_v3_2
        llm_client = deepseek_v3_2
        logger.info(f"使用LLM模型: deepseek_v3_2")
    
    # 创建创作器（使用test_title作为输出目录，novel_title作为小说标题）
    creator = ReactNovelCreator(
        novel_title=novel_title,  # 小说标题用于创作内容
        output_dir=f"novel_creation/outputs/{test_title}",  # 测试标题用于输出目录
        enable_quality_check=True,
        enable_creative_context=True,
        llm_client=llm_client
    )
    
    try:
        # 创作小说
        result = creator.create_novel(
            genre=genre,
            theme=theme,
            target_chapters=target_chapters,
            words_per_chapter=words_per_chapter,
            use_progressive=target_chapters >= 50
        )
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("测试完成！")
        logger.info("=" * 80)
        
        # 输出质量统计
        quality_tracker = creator.metadata.get("quality_tracker", {})
        quality_history = quality_tracker.get("chapter_quality_history", [])
        
        if quality_history:
            logger.info("")
            logger.info("📊 质量统计:")
            logger.info(f"  总章节数: {len(quality_history)}")
            
            # 字数控制统计
            avg_word_control = sum(m.get("word_control_score", 0) for m in quality_history) / len(quality_history)
            avg_words = sum(m.get("word_count", 0) for m in quality_history) / len(quality_history)
            target_words = quality_history[0].get("target_words", words_per_chapter)
            
            logger.info(f"  平均字数控制得分: {avg_word_control:.2f} (满分1.0)")
            logger.info(f"  平均字数: {avg_words:.0f}字 (目标: {target_words}字)")
            
            # 质量问题统计
            total_issues = sum(m.get("quality_issues", 0) for m in quality_history)
            avg_issues = total_issues / len(quality_history)
            logger.info(f"  平均质量问题数: {avg_issues:.2f}个/章")
            
            # 阶段性质量检查
            periodic_checks = creator.metadata.get("periodic_quality_checks", [])
            if periodic_checks:
                logger.info("")
                logger.info("📈 阶段性质量检查:")
                for check in periodic_checks:
                    scores = check.get("scores", {})
                    overall = scores.get("overall", 0)
                    rhythm = scores.get("plot_rhythm", 0)
                    suspense = scores.get("suspense", 0)
                    logger.info(f"  {check.get('chapter_range', 'N/A')}: 综合{overall:.2f}, 节奏{rhythm:.2f}, 悬念{suspense:.2f}")
        
        logger.info("")
        logger.info(f"✅ 输出目录: {creator.output_dir}")
        
    except KeyboardInterrupt:
        logger.warning("用户中断测试")
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    import random
    
    # 创意小说标题和主题库
    creative_novels = [
        {
            "title": "时间碎片收集者",
            "genre": "科幻",
            "theme": "时间旅行、平行世界、记忆碎片、寻找真相"
        },
        {
            "title": "梦境交易所",
            "genre": "奇幻",
            "theme": "梦境与现实交织、情感交易、记忆买卖、意识觉醒"
        },
        {
            "title": "遗忘图书馆",
            "genre": "悬疑",
            "theme": "失忆症、图书馆、隐藏记忆、真相探索"
        },
        {
            "title": "情绪调色师",
            "genre": "都市奇幻",
            "theme": "情绪可视化、色彩魔法、心理治愈、情感共鸣"
        },
        {
            "title": "星尘旅人",
            "genre": "科幻",
            "theme": "星际旅行、文明探索、宇宙奥秘、生命意义"
        },
        {
            "title": "镜像世界",
            "genre": "奇幻",
            "theme": "平行世界、镜像人生、身份互换、命运选择"
        },
        {
            "title": "声音的囚徒",
            "genre": "悬疑",
            "theme": "听觉超能力、声音记忆、真相追寻、心理悬疑"
        },
        {
            "title": "记忆编织者",
            "genre": "奇幻",
            "theme": "记忆编织、时间线修复、因果循环、命运改写"
        },
        {
            "title": "量子纠缠",
            "genre": "科幻",
            "theme": "量子物理、意识上传、虚拟现实、存在本质"
        },
        {
            "title": "影子契约",
            "genre": "奇幻",
            "theme": "影子交易、能力交换、代价与收获、人性考验"
        }
    ]
    
    parser = argparse.ArgumentParser(description="测试质量优化功能")
    parser.add_argument("--title", type=str, default=None, help="测试标题（用于输出目录，默认随机生成）")
    parser.add_argument("--novel-title", type=str, default=None, help="小说标题（用于创作内容，默认随机生成）")
    parser.add_argument("--genre", type=str, default=None, help="小说类型（默认随机生成）")
    parser.add_argument("--theme", type=str, default=None, help="主题（默认随机生成）")
    parser.add_argument("--chapters", type=int, default=20, help="目标章节数")
    parser.add_argument("--words", type=int, default=2048, help="每章目标字数")
    parser.add_argument("--random", action="store_true", help="强制随机选择创意小说（即使指定了其他参数）")
    
    args = parser.parse_args()
    
    # 如果指定了--random或所有参数都未指定，随机选择一个创意小说
    if args.random or (args.novel_title is None and args.genre is None and args.theme is None):
        selected = random.choice(creative_novels)
        novel_title = args.novel_title or selected["title"]
        genre = args.genre or selected["genre"]
        theme = args.theme or selected["theme"]
        logger.info(f"🎲 随机选择创意小说: 《{novel_title}》({genre} - {theme})")
    else:
        # 使用用户指定的参数，缺失的用默认值
        novel_title = args.novel_title or "创意小说"
        genre = args.genre or "都市"
        theme = args.theme or "系统文、打脸装逼"
    
    # 测试标题默认使用小说标题
    test_title = args.title or novel_title
    
    test_quality_optimizations(
        novel_title=novel_title,
        genre=genre,
        theme=theme,
        target_chapters=args.chapters,
        words_per_chapter=args.words,
        test_title=test_title
    )
