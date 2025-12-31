"""
测试分集大纲生成脚本

只测试大纲生成，不生成完整剧本
确保能稳定产出50集
"""

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from unimem.adapters.script_adapter import ScriptAdapter
from unimem.examples.generate_script import generate_script_outline, generate_episode_outlines

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """测试大纲生成"""
    logger.info("="*60)
    logger.info("测试：分集大纲生成（目标：稳定产出50集）")
    logger.info("="*60)
    
    ***REMOVED*** 初始化适配器
    config = {
        'local_model_path': '/root/data/AI/pretrain/multilingual-e5-small',
        'qdrant_url': 'http://localhost:6333',
        'collection_name': 'script_creation'
    }
    
    adapter = ScriptAdapter(config)
    if not adapter.is_available():
        logger.error("适配器初始化失败")
        return
    
    logger.info("✅ 适配器初始化成功")
    
    ***REMOVED*** 1. 生成故事大纲
    theme = "甜宠"
    logger.info(f"\n选择主题: {theme}")
    
    outline_json = generate_script_outline(adapter, theme)
    if not outline_json:
        logger.error("故事大纲生成失败，退出")
        return
    
    outline = json.loads(outline_json)
    logger.info(f"✅ 故事大纲生成完成")
    logger.info(f"   标题: {outline.get('title', '')}")
    logger.info(f"   类型: {outline.get('genre', '')}")
    
    ***REMOVED*** 保存大纲
    data_dir = Path(__file__).parent.parent.parent / 'data'
    outline_file = data_dir / 'test_script_outline.json'
    with open(outline_file, 'w', encoding='utf-8') as f:
        json.dump(outline, f, ensure_ascii=False, indent=2)
    logger.info(f"大纲已保存到: {outline_file}")
    
    ***REMOVED*** 2. 生成分集大纲（50集）
    logger.info("\n" + "="*60)
    logger.info("开始生成50集分集大纲...")
    logger.info("="*60)
    
    episode_outlines = generate_episode_outlines(adapter, outline, num_episodes=50)
    
    if not episode_outlines:
        logger.error("❌ 分集大纲生成失败")
        return
    
    ***REMOVED*** 3. 验证完整性
    logger.info("\n" + "="*60)
    logger.info("完整性验证")
    logger.info("="*60)
    
    expected = set(range(1, 51))
    actual = set(ep.get('episode_num', 0) for ep in episode_outlines)
    missing = sorted(list(expected - actual))
    
    logger.info(f"期望集数: 50 集")
    logger.info(f"实际集数: {len(episode_outlines)} 集")
    
    if missing:
        logger.error(f"❌ 缺失集数: {missing}")
        logger.error(f"❌ 测试失败：未能稳定产出50集")
        return
    else:
        logger.info(f"✅ 所有50集均已生成")
    
    ***REMOVED*** 4. 保存结果
    outlines_file = data_dir / 'test_script_episode_outlines.json'
    with open(outlines_file, 'w', encoding='utf-8') as f:
        json.dump({"episode_outlines": episode_outlines}, f, ensure_ascii=False, indent=2)
    logger.info(f"分集大纲已保存到: {outlines_file}")
    
    ***REMOVED*** 5. 统计信息
    logger.info("\n" + "="*60)
    logger.info("生成统计")
    logger.info("="*60)
    logger.info(f"总集数: {len(episode_outlines)} 集")
    logger.info(f"完整性: ✅ 通过")
    
    ***REMOVED*** 显示前5集和后5集
    logger.info(f"\n前5集:")
    for ep in episode_outlines[:5]:
        logger.info(f"  第{ep.get('episode_num', 0)}集: {ep.get('title', '')}")
    
    logger.info(f"\n后5集:")
    for ep in episode_outlines[-5:]:
        logger.info(f"  第{ep.get('episode_num', 0)}集: {ep.get('title', '')}")
    
    logger.info("\n✅ 测试通过：大纲生成稳定产出50集！")


if __name__ == "__main__":
    main()

