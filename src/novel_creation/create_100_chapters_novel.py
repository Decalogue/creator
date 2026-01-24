***REMOVED***!/usr/bin/env python3
"""
创作100章小说 - 基于"长期优化验证"主题的全新创作
保持相同的世界观和主题，但创作全新的故事，结局留有悬念
根据番茄小说内容创作规范进行创作
"""

import sys
import os
import logging
from pathlib import Path

***REMOVED*** 设置环境变量：只使用 kimi_k2 进行实体提取，不使用 gemini_3_flash
os.environ["USE_SINGLE_MODEL_EXTRACTION"] = "1"

***REMOVED*** 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent.parent))  ***REMOVED*** 添加src目录到路径

from novel_creation.react_novel_creator import ReactNovelCreator
from llm.chat import kimi_k2

***REMOVED*** 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_100_chapters_novel():
    """创作100章小说"""
    
    ***REMOVED*** 小说基本信息（基于30章测试的主题，但创作全新故事）
    ***REMOVED*** 小说名：针对番茄小说网受众，选择更有冲击力和画面感的标题
    ***REMOVED*** 候选标题分析：
    ***REMOVED*** 1. 《完美之墙》- 来自30章测试第1章标题，有画面感，暗示完美背后的危机，最有吸引力
    ***REMOVED*** 2. 《逻辑死锁》- 直接点题，有科技感，暗示困境
    ***REMOVED*** 3. 《优化陷阱》- 暗示完美优化的危险
    ***REMOVED*** 4. 《验证者》- 比《验证》更有角色感
    ***REMOVED*** 5. 《验证》- 简洁但可能对番茄受众吸引力不够
    ***REMOVED*** 最终选择：《完美之墙》- 最有画面感和吸引力，符合番茄小说受众喜好
    novel_title = "完美之墙"
    genre = "科幻"
    ***REMOVED*** 主题：结合番茄小说内容创作规范，确保内容健康、积极，避免低俗、敏感内容
    ***REMOVED*** 强调：AI优化、智能学习、人性探索、自由意志、悬念结局
    ***REMOVED*** 避免：低俗色情、未成年人负面导向、血腥暴力、敏感政治话题
    ***REMOVED*** 语言要求：通俗易懂，避免复杂科学术语，保证绝大多数人都能看得爽
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
    
    ***REMOVED*** 创建小说创作器
    creator = ReactNovelCreator(
        novel_title=novel_title,
        enable_context_offloading=True,
        enable_creative_context=True,
        enable_enhanced_extraction=True,
        enable_quality_check=True,
        llm_client=kimi_k2  ***REMOVED*** 使用Kimi K2作为主模型
    )
    
    ***REMOVED*** 创作小说（使用渐进式大纲，因为章节数>=50）
    try:
        result = creator.create_novel(
            genre=genre,
            theme=theme,
            target_chapters=target_chapters,
            words_per_chapter=words_per_chapter,
            start_from_chapter=1,
            use_progressive=True  ***REMOVED*** 强制使用渐进式大纲
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
