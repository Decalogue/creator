"""
测试创作助手增强功能

验证 atom_link_adapter.py 中新增的创作助手功能：
1. 创作维度分析
2. 多层级结构化
3. 检索奖励机制
4. 生成流程
5. 自动优化
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from unimem.adapters.atom_link_adapter import AtomLinkAdapter
from unimem.types import Memory, Entity
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_creative_dimensions_analysis():
    """测试创作维度分析"""
    logger.info("=== 测试创作维度分析 ===")
    
    config = {
        'local_model_path': '/root/data/AI/pretrain/multilingual-e5-small',
        'qdrant_host': 'localhost',
        'qdrant_port': 6333,
        'collection_name': 'test_creative'
    }
    
    adapter = AtomLinkAdapter(config)
    adapter.initialize()
    
    ***REMOVED*** 测试创作内容分析
    creative_content = """
    令狐冲是华山派的大弟子，性格豪放不羁，喜欢喝酒。他在思过崖上遇到了风清扬，
    学习了独孤九剑。后来因为救了任我行，被逐出师门。他与任盈盈相识，最终结为夫妻。
    """
    
    analysis = adapter._analyze_content(creative_content, is_creative_content=True)
    
    logger.info(f"关键词: {analysis.get('keywords', [])}")
    logger.info(f"上下文: {analysis.get('context', '')}")
    logger.info(f"标签: {analysis.get('tags', [])}")
    
    if "creative_dimensions" in analysis:
        dims = analysis["creative_dimensions"]
        logger.info(f"创作维度:")
        logger.info(f"  类型: {dims.get('genre', 'N/A')}")
        logger.info(f"  风格: {dims.get('writing_style', 'N/A')}")
        logger.info(f"  人物: {dims.get('characters', [])}")
        logger.info(f"  场景: {dims.get('scenes', [])}")
        logger.info(f"  事件: {dims.get('events', [])}")
    
    assert "keywords" in analysis
    assert "context" in analysis
    logger.info("✅ 创作维度分析测试通过\n")


def test_structure_hierarchy():
    """测试多层级结构化"""
    logger.info("=== 测试多层级结构化 ===")
    
    config = {
        'local_model_path': '/root/data/AI/pretrain/multilingual-e5-small',
        'qdrant_host': 'localhost',
        'qdrant_port': 6333,
        'collection_name': 'test_creative'
    }
    
    adapter = AtomLinkAdapter(config)
    adapter.initialize()
    
    ***REMOVED*** 模拟章节内容
    chapters = [
        "令狐冲在思过崖上遇到了风清扬，学习了独孤九剑。",
        "令狐冲因为救了任我行，被逐出师门。",
        "令狐冲与任盈盈相识，最终结为夫妻。"
    ]
    
    ***REMOVED*** 测试章节 -> 摘要
    result = adapter.structure_content_hierarchy(chapters, level="summary")
    logger.info(f"摘要结果: {result.get('summaries', [])}")
    assert "summaries" in result or "metadata" in result
    logger.info("✅ 多层级结构化测试通过\n")


def test_retrieve_with_reward():
    """测试检索奖励机制"""
    logger.info("=== 测试检索奖励机制 ===")
    
    config = {
        'local_model_path': '/root/data/AI/pretrain/multilingual-e5-small',
        'qdrant_host': 'localhost',
        'qdrant_port': 6333,
        'collection_name': 'test_creative'
    }
    
    adapter = AtomLinkAdapter(config)
    adapter.initialize()
    
    ***REMOVED*** 创建一些测试记忆
    original_contents = [
        "令狐冲在思过崖上遇到了风清扬，学习了独孤九剑。",
        "令狐冲因为救了任我行，被逐出师门。",
        "令狐冲与任盈盈相识，最终结为夫妻。"
    ]
    
    for i, content in enumerate(original_contents):
        memory = adapter.construct_atomic_note(
            content=content,
            timestamp=datetime.now(),
            entities=[],
            generate_summary=False,
            is_creative_content=True
        )
        adapter.add_memory_to_vector_store(memory)
    
    ***REMOVED*** 使用摘要检索原内容
    query = "令狐冲学习剑法"
    results = adapter.retrieve_with_reward(query, original_contents, top_k=3)
    
    logger.info(f"检索到 {len(results)} 个结果")
    for i, result in enumerate(results):
        logger.info(f"结果 {i+1}:")
        logger.info(f"  奖励: {result['reward']:.3f}")
        logger.info(f"  内容: {result['memory'].content[:50]}...")
    
    assert len(results) > 0
    assert all("reward" in r for r in results)
    logger.info("✅ 检索奖励机制测试通过\n")


def test_generate_from_hierarchy():
    """测试生成流程"""
    logger.info("=== 测试生成流程 ===")
    
    config = {
        'local_model_path': '/root/data/AI/pretrain/multilingual-e5-small',
        'qdrant_host': 'localhost',
        'qdrant_port': 6333,
        'collection_name': 'test_creative'
    }
    
    adapter = AtomLinkAdapter(config)
    adapter.initialize()
    
    ***REMOVED*** 测试简介 -> 大纲
    synopsis = "这是一个关于令狐冲的武侠故事，讲述了他从华山派弟子到江湖侠客的成长历程。"
    
    outline = adapter.generate_from_hierarchy(synopsis, target_level="outline")
    logger.info(f"生成的大纲: {outline[:200]}...")
    
    assert len(outline) > 0
    logger.info("✅ 生成流程测试通过\n")


def test_optimize_prompt():
    """测试自动优化"""
    logger.info("=== 测试自动优化 ===")
    
    config = {
        'local_model_path': '/root/data/AI/pretrain/multilingual-e5-small',
        'qdrant_host': 'localhost',
        'qdrant_port': 6333,
        'collection_name': 'test_creative'
    }
    
    adapter = AtomLinkAdapter(config)
    adapter.initialize()
    
    input_text = "请生成一个关于令狐冲的故事章节"
    execution_result = "生成的内容过于简短，缺少细节描写"
    current_prompt = "请生成故事章节"
    
    result = adapter.optimize_prompt_and_context(input_text, execution_result, current_prompt)
    
    logger.info(f"优化后的 prompt: {result.get('optimized_prompt', '')[:200]}...")
    logger.info(f"分析结果: {result.get('analysis', {})}")
    
    assert "optimized_prompt" in result
    assert "analysis" in result
    logger.info("✅ 自动优化测试通过\n")


if __name__ == "__main__":
    try:
        test_creative_dimensions_analysis()
        test_structure_hierarchy()
        test_retrieve_with_reward()
        test_generate_from_hierarchy()
        test_optimize_prompt()
        
        logger.info("=" * 50)
        logger.info("✅ 所有创作助手功能测试通过！")
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)

