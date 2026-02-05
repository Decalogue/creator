#!/usr/bin/env python3
"""
创作100章小说 - 基于"长期优化验证"主题的全新创作
保持相同的世界观和主题，但创作全新的故事，结局留有悬念
根据番茄小说内容创作规范进行创作

运行：在 src 目录下执行 python scripts/novel/create_100_chapters_novel.py
"""

import sys
import logging
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from task.novel.react_novel_creator import ReactNovelCreator
from llm.chat import kimi_k2

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_100_chapters_novel():
    """创作100章小说"""
    novel_title = "完美之墙"
    genre = "科幻"
    theme = "AI优化、智能学习、人性探索、自由意志、长期连贯性、悬念结局。创作要求：1) 内容健康积极，避免低俗色情、未成年人负面导向、血腥暴力、敏感政治话题，符合番茄小说内容创作规范；2) 语言通俗易懂，避免复杂科学术语和专业名词，用简单直白的语言表达，保证绝大多数人都能看得爽，即使涉及科技概念也要用生活化的比喻和描述"
    target_chapters = 100
    words_per_chapter = 2048

    logger.info("=" * 60)
    logger.info(f"开始创作小说: {novel_title}")
    logger.info(f"类型: {genre}")
    logger.info(f"主题: {theme}")
    logger.info(f"目标章节: {target_chapters}")
    logger.info(f"每章字数: {words_per_chapter}")
    logger.info("=" * 60)

    creator = ReactNovelCreator(
        novel_title=novel_title,
        enable_context_offloading=True,
        enable_creative_context=True,
        enable_enhanced_extraction=True,
        enable_quality_check=True,
        llm_client=kimi_k2,
    )

    try:
        result = creator.create_novel(
            genre=genre,
            theme=theme,
            target_chapters=target_chapters,
            words_per_chapter=words_per_chapter,
            start_from_chapter=1,
            use_progressive=True,
        )
        logger.info("=" * 60)
        logger.info("小说创作完成！")
        logger.info(f"输出目录: {creator.output_dir}")
        logger.info("=" * 60)
        return result
    except Exception as e:
        logger.error(f"创作过程中出现错误: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    create_100_chapters_novel()
