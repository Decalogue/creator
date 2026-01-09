"""
根据创作 idea 生成前5章内容

使用创作助手的多层级生成流程：
简介 -> 大纲 -> 摘要 -> 章节
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from unimem.adapters.novel_adapter import NovelAdapter
from unimem.memory_types import Memory, Entity
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_creative_idea(idea_file: Path):
    """加载创作 idea"""
    with open(idea_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_outline_from_synopsis(idea: dict, adapter: NovelAdapter):
    """从简介生成大纲"""
    logger.info("="*50)
    logger.info("步骤1: 从简介生成故事大纲")
    logger.info("="*50)
    
    synopsis = idea.get('opening_scene', '') + "\n\n" + idea.get('background', '')
    
    outline = adapter.generate_from_hierarchy(
        synopsis=synopsis,
        target_level="outline",
        context_memories=[]
    )
    
    logger.info("✅ 大纲生成完成")
    return outline


def generate_summaries_from_outline(outline: str, adapter: NovelAdapter, num_chapters: int = 5):
    """从大纲生成章节摘要"""
    logger.info("\n" + "="*50)
    logger.info(f"步骤2: 从大纲生成前{num_chapters}章摘要")
    logger.info("="*50)
    
    summaries = adapter.generate_from_hierarchy(
        synopsis=outline,
        target_level="summary",
        context_memories=[]
    )
    
    ***REMOVED*** 解析摘要（可能是 JSON 或文本）
    try:
        summaries_json = json.loads(summaries)
        if isinstance(summaries_json, dict) and 'summaries' in summaries_json:
            return summaries_json['summaries']
        elif isinstance(summaries_json, list):
            return summaries_json
    except:
        ***REMOVED*** 如果不是 JSON，按行分割
        if isinstance(summaries, str):
            summary_list = [s.strip() for s in summaries.split('\n') if s.strip()]
            return summary_list[:num_chapters]
    
    return [summaries] if summaries else []


def build_enhanced_prompt_with_feedback(original_prompt: str, validation_result: dict, attempt: int) -> str:
    """
    根据校验反馈构建增强的 prompt
    
    将 issues 和 suggestions 转化为具体的生成指导
    
    Args:
        original_prompt: 原始 prompt
        validation_result: 校验结果（包含 issues, suggestions, coverage）
        attempt: 当前尝试次数
        
    Returns:
        增强后的 prompt
    """
    issues = validation_result.get('issues', [])
    suggestions = validation_result.get('suggestions', [])
    coverage = validation_result.get('coverage', {})
    
    feedback_section = "\n\n【重要：根据上一版生成结果的反馈，请特别注意以下要求】\n"
    
    ***REMOVED*** 1. 明确指出需要避免的问题
    if issues:
        feedback_section += "\n【需要避免的问题】\n"
        for i, issue in enumerate(issues[:5], 1):  ***REMOVED*** 最多5个问题
            feedback_section += f"{i}. {issue}\n"
        feedback_section += "\n请确保生成的内容避免上述问题。\n"
    
    ***REMOVED*** 2. 提供具体的改进建议
    if suggestions:
        feedback_section += "\n【改进方向】\n"
        for i, suggestion in enumerate(suggestions[:5], 1):  ***REMOVED*** 最多5条建议
            feedback_section += f"{i}. {suggestion}\n"
        feedback_section += "\n请在生成时充分考虑并体现上述改进建议。\n"
    
    ***REMOVED*** 3. 根据各维度评分提供针对性指导
    if coverage:
        feedback_section += "\n【各维度要求】\n"
        if coverage.get('plot_coverage', 1.0) < 0.8:
            feedback_section += "- 请确保完整涵盖预期摘要的核心情节，不要遗漏重要情节点\n"
        if coverage.get('character_consistency', 1.0) < 0.8:
            feedback_section += "- 请严格遵循创作设定中的人物性格和行为特征\n"
        if coverage.get('setting_consistency', 1.0) < 0.8:
            feedback_section += "- 请确保世界观、背景设定与创作设定完全一致\n"
        if coverage.get('style_consistency', 1.0) < 0.8:
            feedback_section += "- 请保持与创作设定要求的写作风格一致\n"
    
    feedback_section += f"\n这是第 {attempt} 次生成尝试，请务必解决上述问题，生成更符合要求的内容。\n"
    
    return original_prompt + feedback_section


def validate_generated_chapter(chapter_content: str, expected_summary: str, idea: dict, adapter: NovelAdapter) -> dict:
    """
    反向结构化校验：对生成的章节进行结构化分析，并与预期摘要对比
    
    Returns:
        {
            'accuracy_score': float,  ***REMOVED*** 准确度评分 0-1
            'validation_result': dict,  ***REMOVED*** 详细校验结果
            'issues': list,  ***REMOVED*** 发现的问题
            'suggestions': list  ***REMOVED*** 优化建议
        }
    """
    if not adapter.is_available():
        return {'accuracy_score': 0.5, 'validation_result': {}, 'issues': [], 'suggestions': []}
    
    try:
        ***REMOVED*** 1. 对生成内容进行反向结构化分析
        logger.info("  进行反向结构化分析...")
        generated_analysis = adapter._analyze_content(
            chapter_content[:2000],  ***REMOVED*** 限制长度
            is_creative_content=True
        )
        
        ***REMOVED*** 2. 对预期摘要进行结构化分析
        expected_analysis = adapter._analyze_content(
            expected_summary,
            is_creative_content=True
        )
        
        ***REMOVED*** 3. 对比分析
        logger.info("  进行对比校验...")
        from unimem.chat import ark_deepseek_v3_2
        
        comparison_prompt = f"""请对比以下两段内容的结构化分析结果，评估生成内容是否符合预期要求。

【预期摘要的结构化分析】
关键词: {', '.join(expected_analysis.get('keywords', [])[:10])}
上下文: {expected_analysis.get('context', '')}
创作维度: {json.dumps(expected_analysis.get('creative_dimensions', {}), ensure_ascii=False)}

【生成章节的结构化分析】
关键词: {', '.join(generated_analysis.get('keywords', [])[:10])}
上下文: {generated_analysis.get('context', '')}
创作维度: {json.dumps(generated_analysis.get('creative_dimensions', {}), ensure_ascii=False)}

【创作设定要求】
- 作品类型: {idea.get('genre', '')}
- 主要人物: {json.dumps([c.get('name') for c in idea.get('main_characters', [])[:3]], ensure_ascii=False)}
- 核心冲突: {idea.get('core_conflict', '')[:200]}

请评估：
1. 生成内容是否涵盖了预期摘要的核心情节？
2. 生成内容是否符合创作设定（人物、世界观、风格）？
3. 是否存在明显偏差或遗漏？

请以 JSON 格式返回结果：
{{
    "accuracy_score": 0.0-1.0,  // 准确度评分
    "coverage": {{
        "plot_coverage": 0.0-1.0,  // 情节覆盖度
        "character_consistency": 0.0-1.0,  // 人物一致性
        "setting_consistency": 0.0-1.0,  // 设定一致性
        "style_consistency": 0.0-1.0  // 风格一致性
    }},
    "issues": [
        "问题1描述",
        "问题2描述"
    ],
    "suggestions": [
        "优化建议1",
        "优化建议2"
    ]
}}"""
        
        messages = [
            {"role": "system", "content": "你是一个专业的内容质量评估助手，擅长对比分析文本内容是否符合预期要求。请始终以有效的 JSON 格式返回结果。"},
            {"role": "user", "content": comparison_prompt}
        ]
        
        _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=1024)
        validation_result = adapter._parse_json_response(response_text)
        
        if validation_result:
            accuracy_score = validation_result.get('accuracy_score', 0.5)
            logger.info(f"  ✅ 校验完成，准确度评分: {accuracy_score:.2f}")
            return {
                'accuracy_score': accuracy_score,
                'validation_result': validation_result,
                'issues': validation_result.get('issues', []),
                'suggestions': validation_result.get('suggestions', []),
                'coverage': validation_result.get('coverage', {})
            }
        else:
            logger.warning("  校验结果解析失败")
            return {'accuracy_score': 0.5, 'validation_result': {}, 'issues': [], 'suggestions': []}
            
    except Exception as e:
        logger.error(f"  校验过程出错: {e}")
        return {'accuracy_score': 0.5, 'validation_result': {}, 'issues': [], 'suggestions': []}


def generate_chapter_from_summary(summary: str, idea: dict, chapter_num: int, adapter: NovelAdapter, context_memories: list, enable_validation: bool = True, validation_threshold: float = 0.7, max_retries: int = 2):
    """
    从摘要生成完整章节（带反向结构化校验）
    
    Args:
        summary: 章节摘要
        idea: 创作设定
        chapter_num: 章节编号
        adapter: 适配器
        context_memories: 上下文记忆
        enable_validation: 是否启用校验
        validation_threshold: 校验阈值（低于此值会重新生成）
        max_retries: 最大重试次数
    """
    logger.info(f"\n生成第 {chapter_num} 章...")
    
    ***REMOVED*** 如果有前章节的校验反馈，加入指导
    previous_feedback = ""
    if 'validation_feedback' in idea and idea['validation_feedback']:
        ***REMOVED*** 获取前章节的反馈（特别是最近一章）
        recent_feedback = idea['validation_feedback'][-1]
        if recent_feedback.get('chapter') < chapter_num:
            previous_feedback = "\n\n【参考：前章节的改进建议】\n"
            if recent_feedback.get('suggestions'):
                previous_feedback += "以下建议来自前章节的校验反馈，请在生成时参考：\n"
                for i, sug in enumerate(recent_feedback['suggestions'], 1):
                    previous_feedback += f"{i}. {sug}\n"
    
    ***REMOVED*** 构建章节生成 prompt（包含创作 idea 的上下文）
    chapter_prompt = f"""请根据以下摘要和创作设定，生成完整的第{chapter_num}章内容。

创作设定：
- 作品类型: {idea.get('genre', '')}
- 写作风格: {idea.get('writing_style', '')}
- 主要人物: {json.dumps(idea.get('main_characters', [])[:3], ensure_ascii=False)}
- 核心冲突: {idea.get('core_conflict', '')}
- 独特设定: {idea.get('unique_setting', '')}

章节摘要：
{summary}
{previous_feedback}
要求：
1. 章节长度控制在 2000-3000 字左右
2. 保持与创作设定的风格一致
3. 包含场景描写、人物对话、情节推进
4. 为下一章埋下伏笔
5. 使用古典白话文风格，符合历史武侠小说的语言特色

请直接返回章节内容，不要包含标题或其他格式："""
    
    for attempt in range(max_retries + 1):
        try:
            from unimem.chat import ark_deepseek_v3_2
            messages = [
                {"role": "system", "content": "你是一个专业的武侠小说创作助手，擅长根据设定和摘要生成完整的章节内容。请保持风格一致性和情节连贯性。"},
                {"role": "user", "content": chapter_prompt}
            ]
            
            _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=4096)
            
            ***REMOVED*** 清理响应文本
            chapter_content = response_text.strip()
            if chapter_content.startswith("```"):
                ***REMOVED*** 移除 markdown 代码块标记
                lines = chapter_content.split('\n')
                chapter_content = '\n'.join([line for line in lines if not line.strip().startswith('```')])
            
            ***REMOVED*** 反向结构化校验
            validation_result = None
            if enable_validation:
                validation_result = validate_generated_chapter(
                    chapter_content, summary, idea, adapter
                )
                
                accuracy_score = validation_result.get('accuracy_score', 0.5)
                
                if accuracy_score < validation_threshold and attempt < max_retries:
                    logger.warning(f"  ⚠️ 准确度评分 {accuracy_score:.2f} 低于阈值 {validation_threshold}，尝试重新生成...")
                    
                    ***REMOVED*** 使用 issues 和 suggestions 指导重新生成
                    enhanced_prompt = build_enhanced_prompt_with_feedback(
                        original_prompt=chapter_prompt,
                        validation_result=validation_result,
                        attempt=attempt + 1
                    )
                    chapter_prompt = enhanced_prompt
                    logger.info(f"  📝 已根据校验反馈优化 prompt（第 {attempt + 1} 次尝试）")
                    continue
                else:
                    logger.info(f"  ✅ 校验通过，准确度评分: {accuracy_score:.2f}")
                    if validation_result.get('issues'):
                        logger.info(f"  ⚠️ 发现 {len(validation_result['issues'])} 个问题（但不影响使用）")
                        ***REMOVED*** 即使通过，也记录 issues 和 suggestions 供后续章节参考
                        if validation_result.get('suggestions'):
                            logger.info(f"  💡 生成 {len(validation_result['suggestions'])} 条优化建议（已记录）")
                            ***REMOVED*** 将重要的问题和建议存储到 idea 的 metadata 中，供后续章节参考
                            if 'validation_feedback' not in idea:
                                idea['validation_feedback'] = []
                            idea['validation_feedback'].append({
                                'chapter': chapter_num,
                                'issues': validation_result.get('issues', [])[:3],  ***REMOVED*** 只保留最重要的3个
                                'suggestions': validation_result.get('suggestions', [])[:3]  ***REMOVED*** 只保留最重要的3条
                            })
            
            logger.info(f"✅ 第 {chapter_num} 章生成完成 ({len(chapter_content)} 字)")
            return chapter_content, validation_result
            
        except Exception as e:
            logger.error(f"生成第 {chapter_num} 章失败: {e}")
            if attempt < max_retries:
                logger.info(f"  重试中... ({attempt + 1}/{max_retries})")
                continue
            return "", None
    
    return "", None


def generate_chapters(idea: dict, adapter: NovelAdapter, num_chapters: int = 5, enable_validation: bool = True, validation_threshold: float = 0.7, validate_first_n: int = 3):
    """
    生成前N章内容（支持反向结构化校验）
    
    Args:
        idea: 创作设定
        adapter: 适配器
        num_chapters: 章节数量
        enable_validation: 是否启用校验
        validation_threshold: 校验阈值（0-1）
        validate_first_n: 前N章必须校验（其余章节可选）
    """
    logger.info("="*60)
    logger.info(f"开始生成《{idea.get('title', '')}》前 {num_chapters} 章")
    if enable_validation:
        logger.info(f"校验模式: 前 {validate_first_n} 章强制校验，阈值 {validation_threshold}")
    logger.info("="*60)
    
    ***REMOVED*** 1. 生成大纲
    outline = generate_outline_from_synopsis(idea, adapter)
    
    ***REMOVED*** 保存大纲
    outline_file = Path(__file__).parent.parent.parent / 'data' / 'xuemolu_outline.json'
    with open(outline_file, 'w', encoding='utf-8') as f:
        json.dump({"outline": outline}, f, ensure_ascii=False, indent=2)
    logger.info(f"大纲已保存到: {outline_file}")
    
    ***REMOVED*** 2. 生成章节摘要
    summaries = generate_summaries_from_outline(outline, adapter, num_chapters)
    
    if not summaries:
        logger.warning("未能生成章节摘要，使用默认摘要")
        summaries = [f"第{i}章摘要" for i in range(1, num_chapters + 1)]
    
    ***REMOVED*** 保存摘要
    summaries_file = Path(__file__).parent.parent.parent / 'data' / 'xuemolu_summaries.json'
    with open(summaries_file, 'w', encoding='utf-8') as f:
        json.dump({"summaries": summaries}, f, ensure_ascii=False, indent=2)
    logger.info(f"章节摘要已保存到: {summaries_file}")
    
    ***REMOVED*** 3. 生成各章节内容（逐章生成，每章单独保存）
    data_dir = Path(__file__).parent.parent.parent / 'data'
    
    ***REMOVED*** 创建保存目录
    novel_dir = data_dir / 'novel'
    novel_dir.mkdir(exist_ok=True)
    logger.info(f"章节保存目录: {novel_dir}")
    
    chapters = []
    context_memories = []  ***REMOVED*** 用于累积上下文
    
    for i, summary in enumerate(summaries[:num_chapters], 1):
        ***REMOVED*** 决定是否启用校验：前N章强制校验，其余章节可选
        should_validate = enable_validation and (i <= validate_first_n)
        
        chapter_content, validation_result = generate_chapter_from_summary(
            summary=summary,
            idea=idea,
            chapter_num=i,
            adapter=adapter,
            context_memories=context_memories,
            enable_validation=should_validate,
            validation_threshold=validation_threshold
        )
        
        if chapter_content:
            chapter_data = {
                'chapter_num': i,
                'title': f"第{i}章",
                'summary': summary,
                'content': chapter_content,
                'word_count': len(chapter_content)
            }
            
            ***REMOVED*** 添加校验结果
            if validation_result:
                chapter_data['validation'] = {
                    'accuracy_score': validation_result.get('accuracy_score', 0),
                    'coverage': validation_result.get('coverage', {}),
                    'issues': validation_result.get('issues', []),
                    'suggestions': validation_result.get('suggestions', [])
                }
            
            chapters.append(chapter_data)
            
            ***REMOVED*** 立即保存单章到文件
            chapter_file = novel_dir / f"chapter_{i:02d}.json"
            with open(chapter_file, 'w', encoding='utf-8') as f:
                json.dump(chapter_data, f, ensure_ascii=False, indent=2)
            
            ***REMOVED*** 同时保存纯文本版本
            chapter_txt_file = novel_dir / f"chapter_{i:02d}.txt"
            with open(chapter_txt_file, 'w', encoding='utf-8') as f:
                f.write(f"第{i}章：{chapter_data['title']}\n")
                f.write("="*60 + "\n\n")
                f.write(chapter_content)
            
            logger.info(f"  ✅ 第 {i} 章完成 ({len(chapter_content)} 字) - 已保存到 {chapter_file.name}")
            
            ***REMOVED*** 将生成的章节内容存储为记忆，用于后续章节的上下文
            if adapter.is_available():
                memory = adapter.construct_atomic_note(
                    content=chapter_content[:1000],  ***REMOVED*** 只存储部分内容作为上下文
                    timestamp=datetime.now(),
                    entities=[],
                    generate_summary=False,
                    is_creative_content=True
                )
                context_memories.append(memory)
                if len(context_memories) > 3:  ***REMOVED*** 只保留最近3章作为上下文
                    context_memories = context_memories[-3:]
        
        ***REMOVED*** 添加延迟避免 API 限流
        import time
        time.sleep(1)
    
    return chapters


def save_chapters(chapters: list, idea: dict, output_file: Path):
    """
    保存章节汇总到文件
    
    注意：各章节已单独保存到 data/novel/ 目录，此函数用于保存汇总文件。
    """
    output_data = {
        'novel_info': {
            'title': idea.get('title', ''),
            'genre': idea.get('genre', ''),
            'background': idea.get('background', ''),
            'core_conflict': idea.get('core_conflict', ''),
            'total_chapters': len(chapters),
            'generated_chapters': len(chapters)
        },
        'chapters': chapters,
        'generation_time': datetime.now().isoformat()
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"\n✅ 章节汇总已保存到: {output_file}")
    
    ***REMOVED*** 同时生成纯文本版本
    txt_file = output_file.with_suffix('.txt')
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(f"{idea.get('title', '')}\n")
        f.write("="*60 + "\n\n")
        for ch in chapters:
            f.write(f"{ch['title']}\n")
            f.write("-"*60 + "\n\n")
            f.write(ch['content'])
            f.write("\n\n" + "="*60 + "\n\n")
    
    logger.info(f"✅ 纯文本汇总版本已保存到: {txt_file}")


def main():
    ***REMOVED*** 初始化适配器
    config = {
        'local_model_path': '/root/data/AI/pretrain/multilingual-e5-small',
        'qdrant_host': 'localhost',
        'qdrant_port': 6333,
        'collection_name': 'xuemolu_creation'
    }
    
    adapter = NovelAdapter(config)
    adapter.initialize()
    
    ***REMOVED*** 加载创作 idea
    idea_file = Path(__file__).parent.parent.parent / 'data' / 'new_idea.json'
    logger.info(f"加载创作 idea: {idea_file}")
    idea = load_creative_idea(idea_file)
    
    logger.info(f"作品标题: {idea.get('title', '')}")
    logger.info(f"作品类型: {idea.get('genre', '')}")
    
    ***REMOVED*** 生成前5章（启用校验，前3章强制校验，阈值0.7）
    chapters = generate_chapters(
        idea, 
        adapter, 
        num_chapters=5,
        enable_validation=True,  ***REMOVED*** 启用校验
        validation_threshold=0.7,  ***REMOVED*** 准确度阈值
        validate_first_n=3  ***REMOVED*** 前3章强制校验
    )
    
    ***REMOVED*** 保存章节汇总（所有章节已单独保存，这里保存汇总）
    data_dir = Path(__file__).parent.parent.parent / 'data'
    output_file = data_dir / 'xuemolu_chapters.json'
    save_chapters(chapters, idea, output_file)
    
    ***REMOVED*** 打印统计信息
    logger.info("\n" + "="*60)
    logger.info("生成统计")
    logger.info("="*60)
    logger.info(f"总章节数: {len(chapters)}")
    total_words = sum(ch.get('word_count', 0) for ch in chapters)
    logger.info(f"总字数: {total_words:,} 字")
    logger.info(f"平均每章: {total_words // len(chapters) if chapters else 0} 字")
    logger.info(f"单章文件已保存到: {data_dir / 'novel'}/")
    
    ***REMOVED*** 打印校验统计
    validated_chapters = [ch for ch in chapters if 'validation' in ch]
    if validated_chapters:
        logger.info(f"\n校验统计:")
        logger.info(f"  校验章节数: {len(validated_chapters)}")
        avg_accuracy = sum(ch['validation'].get('accuracy_score', 0) for ch in validated_chapters) / len(validated_chapters)
        logger.info(f"  平均准确度: {avg_accuracy:.2f}")
        for ch in validated_chapters:
            score = ch['validation'].get('accuracy_score', 0)
            logger.info(f"    第{ch['chapter_num']}章: {score:.2f}")
    
    logger.info("\n✅ 所有任务完成！")


if __name__ == "__main__":
    main()

