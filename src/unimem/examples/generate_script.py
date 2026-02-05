"""
短剧剧本生成脚本

使用 ScriptAdapter 生成50集短剧剧本
流程：大纲 -> 分集大纲 -> 分镜脚本 -> 完整剧本
"""

import json
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from unimem.adapters.script_adapter import ScriptAdapter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    从文本中提取 JSON，支持多种格式（增强版）
    
    尝试多种方法：
    1. 查找 { ... } 块
    2. 移除 markdown 代码块标记
    3. 修复常见的 JSON 格式问题
    4. 尝试部分提取（即使部分损坏）
    """
    # 方法1: 查找 markdown 代码块
    if "```json" in text:
        json_start = text.find("```json") + 7
        json_end = text.find("```", json_start)
        if json_end > json_start:
            text = text[json_start:json_end].strip()
    elif "```" in text:
        json_start = text.find("```") + 3
        json_end = text.find("```", json_start)
        if json_end > json_start:
            text = text[json_start:json_end].strip()
    
    # 方法2: 查找第一个 { 到最后一个 } 之间的内容
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    if first_brace >= 0 and last_brace > first_brace:
        text = text[first_brace:last_brace + 1]
    
    # 方法3: 修复常见的 JSON 问题
    try:
        # 移除控制字符（除了换行和制表符）
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', '', text)
        # 修复单引号为双引号（在键名和字符串值中）
        text = re.sub(r"'(\w+)':", r'"\1":', text)
        text = re.sub(r":\s*'([^']*)'", r': "\1"', text)
        # 修复尾随逗号
        text = re.sub(r',\s*}', '}', text)
        text = re.sub(r',\s*]', ']', text)
        # 修复缺失的引号（在键名中）
        text = re.sub(r'(\w+):', r'"\1":', text)
        # 修复未转义的换行符
        text = text.replace('\n', '\\n').replace('\r', '\\r')
        
        return json.loads(text)
    except json.JSONDecodeError as e:
        # 方法4: 尝试部分提取 - 找到 episode_outlines 数组
        try:
            # 查找 "episode_outlines" 数组
            outlines_start = text.find('"episode_outlines"')
            if outlines_start >= 0:
                array_start = text.find('[', outlines_start)
                if array_start >= 0:
                    # 尝试提取数组内容
                    bracket_count = 0
                    array_end = array_start
                    for i in range(array_start, len(text)):
                        if text[i] == '[':
                            bracket_count += 1
                        elif text[i] == ']':
                            bracket_count -= 1
                            if bracket_count == 0:
                                array_end = i + 1
                                break
                    
                    if array_end > array_start:
                        array_text = text[array_start:array_end]
                        # 尝试解析数组
                        outlines = json.loads(array_text)
                        return {"episode_outlines": outlines}
        except:
            pass
        
        # 方法5: 尝试逐行修复
        try:
            lines = text.split('\n')
            fixed_lines = []
            for line in lines:
                # 跳过注释行
                if line.strip().startswith('//') or line.strip().startswith('#'):
                    continue
                # 修复常见的行内问题
                line = re.sub(r',\s*$', '', line)  # 移除行尾逗号
                fixed_lines.append(line)
            fixed_text = '\n'.join(fixed_lines)
            return json.loads(fixed_text)
        except:
            pass
        
        logger.debug(f"JSON extraction failed after all attempts: {e}")
        return None
    except Exception as e:
        logger.debug(f"JSON extraction failed: {e}")
        return None


def generate_script_outline(adapter: ScriptAdapter, theme: str = "都市悬疑") -> str:
    """生成故事大纲"""
    logger.info("="*60)
    logger.info("步骤1: 生成故事大纲")
    logger.info("="*60)
    
    prompt = f"""请创作一个{theme}题材的50集短剧故事大纲。

要求：
1. 甜宠主题：要有甜蜜的恋爱元素，男女主角的互动要有甜度
2. 适合短剧的快节奏叙事
3. 每集3-5分钟，50集总时长约150-250分钟
4. 要有明确的主线和副线（可以是误会、追求、宠溺等）
5. 人物关系要有甜宠感，男主要有宠溺属性，女主要有可爱或独立特质
6. 适合短视频平台的观看习惯，每集要有甜宠亮点
7. 可以包含：霸道总裁、青梅竹马、契约婚姻、校园恋爱等甜宠元素

请以 JSON 格式返回结果：
{{
    "title": "短剧标题",
    "genre": "题材类型",
    "theme": "主题",
    "main_storyline": "主要故事线",
    "main_characters": [
        {{
            "name": "角色名",
            "role": "角色定位",
            "characteristics": "角色特点"
        }}
    ],
    "conflicts": ["冲突1", "冲突2", ...],
    "plot_structure": {{
        "act1": "第一幕：开端（1-15集）",
        "act2": "第二幕：发展（16-35集）",
        "act3": "第三幕：高潮与结局（36-50集）"
    }},
    "key_turning_points": ["转折点1", "转折点2", ...],
    "target_audience": "目标受众"
}}"""
    
    try:
        from unimem.chat import ark_deepseek_v3_2
        messages = [
            {"role": "system", "content": "你是一个专业的短剧剧本创作助手，擅长创作适合短视频平台的短剧故事大纲。请始终以有效的 JSON 格式返回结果。"},
            {"role": "user", "content": prompt}
        ]
        
        _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=2048)
        result = adapter._parse_json_response(response_text)
        
        if result:
            logger.info("✅ 故事大纲生成完成")
            return json.dumps(result, ensure_ascii=False, indent=2)
        else:
            logger.warning("大纲生成失败，尝试手动提取 JSON...")
            # 尝试更宽松的 JSON 提取
            result = extract_json_from_text(response_text)
            if result:
                logger.info("✅ 通过手动提取成功解析大纲")
                return json.dumps(result, ensure_ascii=False, indent=2)
            
            logger.warning("使用甜宠主题默认大纲")
            return json.dumps({
                "title": "甜宠短剧",
                "genre": "甜宠",
                "theme": "甜蜜恋爱",
                "main_storyline": "一个普通女孩与霸道总裁的甜蜜恋爱故事，从误会到相知，从相知到相爱，最终收获幸福。",
                "main_characters": [
                    {
                        "name": "女主角",
                        "role": "普通女孩，善良独立",
                        "characteristics": "可爱、坚强、有自己的梦想"
                    },
                    {
                        "name": "男主角",
                        "role": "霸道总裁",
                        "characteristics": "高冷外表下隐藏温柔，对女主角宠溺有加"
                    }
                ],
                "conflicts": ["身份差距", "误会", "第三者介入"],
                "plot_structure": {
                    "act1": "第一幕：相遇与误会（1-15集）",
                    "act2": "第二幕：相知与心动（16-35集）",
                    "act3": "第三幕：相爱与幸福（36-50集）"
                },
                "key_turning_points": ["初次相遇", "误会解除", "表白", "在一起"],
                "target_audience": "18-35岁女性观众"
            }, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"生成故事大纲失败: {e}")
        return ""


def generate_episode_outlines(adapter: ScriptAdapter, outline: Dict[str, Any], num_episodes: int = 50) -> List[Dict[str, Any]]:
    """
    生成分集大纲（增强版：带重试机制和完整性检查）
    """
    logger.info("="*60)
    logger.info(f"步骤2: 生成{num_episodes}集分集大纲")
    logger.info("="*60)
    
    # 将大纲转换为文本
    outline_text = f"""
标题：{outline.get('title', '')}
题材：{outline.get('genre', '')}
主题：{outline.get('theme', '')}
主要故事线：{outline.get('main_storyline', '')}
主要角色：{json.dumps(outline.get('main_characters', [])[:5], ensure_ascii=False)}
核心冲突：{json.dumps(outline.get('conflicts', [])[:5], ensure_ascii=False)}
剧情结构：
{outline.get('plot_structure', {}).get('act1', '')}
{outline.get('plot_structure', {}).get('act2', '')}
{outline.get('plot_structure', {}).get('act3', '')}
关键转折点：{json.dumps(outline.get('key_turning_points', [])[:5], ensure_ascii=False)}
"""
    
    # 分批生成（每次生成5集，降低出错概率）
    all_outlines = []
    batch_size = 5
    max_retries = 3  # 每批次最多重试3次
    failed_batches = []  # 记录失败的批次
    
    for batch_start in range(0, num_episodes, batch_size):
        batch_end = min(batch_start + batch_size, num_episodes)
        batch_num = batch_start // batch_size + 1
        total_batches = (num_episodes + batch_size - 1) // batch_size
        
        logger.info(f"\n生成第 {batch_start+1}-{batch_end} 集大纲（批次 {batch_num}/{total_batches}）...")
        
        prompt = f"""请根据以下故事大纲，生成第{batch_start+1}到第{batch_end}集的分集大纲。

故事大纲：
{outline_text}

要求：
1. 每集要有完整的情节单元
2. 保持节奏紧凑，每集有高潮点
3. 每集时长控制在3-5分钟
4. 分集之间要有连贯性和悬念
5. 第{batch_start+1}集要吸引观众，第{batch_end}集要有悬念
6. **重要：必须生成完整的 {batch_end - batch_start} 集，每集都要有 episode_num、title、summary、key_scenes、main_conflict、climax、hook、ending_hook 字段**

请以 JSON 格式返回结果（确保格式正确，不要有语法错误）：
{{
    "episode_outlines": [
        {{
            "episode_num": {batch_start+1},
            "title": "分集标题",
            "summary": "分集摘要（100-150字）",
            "key_scenes": ["场景1", "场景2", "场景3"],
            "main_conflict": "核心冲突",
            "climax": "高潮点",
            "hook": "吸引观众的钩子",
            "ending_hook": "结尾悬念"
        }},
        {{
            "episode_num": {batch_start+2},
            ...
        }}
    ]
}}"""
        
        # 重试机制
        batch_success = False
        for attempt in range(max_retries):
            try:
                from unimem.chat import ark_deepseek_v3_2
                messages = [
                    {"role": "system", "content": "你是一个专业的短剧剧本创作助手，擅长创作分集大纲。请始终以有效的、完整的 JSON 格式返回结果，确保所有字段都存在。"},
                    {"role": "user", "content": prompt}
                ]
                
                _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=4096)
                
                # 保存原始响应（用于调试）
                if attempt == 0:
                    debug_file = Path(__file__).parent.parent.parent / 'data' / f'debug_batch_{batch_start+1}_{batch_end}.txt'
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(response_text)
                
                result = adapter._parse_json_response(response_text)
                
                # 如果解析失败，尝试手动提取
                if not result:
                    if attempt < max_retries - 1:
                        logger.warning(f"第 {batch_start+1}-{batch_end} 集 JSON 解析失败（尝试 {attempt+1}/{max_retries}），尝试手动提取...")
                    else:
                        logger.warning(f"第 {batch_start+1}-{batch_end} 集 JSON 解析失败，尝试手动提取...")
                    result = extract_json_from_text(response_text)
                
                if result and "episode_outlines" in result:
                    batch_outlines = result["episode_outlines"]
                    
                    # 验证批次完整性
                    expected_episodes = set(range(batch_start + 1, batch_end + 1))
                    actual_episodes = set(ep.get('episode_num', 0) for ep in batch_outlines)
                    
                    if len(batch_outlines) == batch_end - batch_start and expected_episodes == actual_episodes:
                        all_outlines.extend(batch_outlines)
                        logger.info(f"✅ 第 {batch_start+1}-{batch_end} 集大纲生成完成（{len(batch_outlines)} 集）")
                        batch_success = True
                        break
                    else:
                        missing = expected_episodes - actual_episodes
                        logger.warning(f"⚠️ 批次不完整：期望 {len(expected_episodes)} 集，实际 {len(batch_outlines)} 集，缺失: {missing}")
                        if attempt < max_retries - 1:
                            logger.info(f"  重试中... ({attempt+2}/{max_retries})")
                            import time
                            time.sleep(2)
                            continue
                else:
                    if attempt < max_retries - 1:
                        logger.warning(f"第 {batch_start+1}-{batch_end} 集大纲生成失败（尝试 {attempt+1}/{max_retries}），响应文本: {response_text[:200]}...")
                        import time
                        time.sleep(2)
                        continue
                    else:
                        logger.error(f"第 {batch_start+1}-{batch_end} 集大纲生成失败，响应文本: {response_text[:200]}...")
                
            except Exception as e:
                logger.error(f"生成第 {batch_start+1}-{batch_end} 集大纲失败（尝试 {attempt+1}/{max_retries}）: {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2)
                    continue
        
        if not batch_success:
            failed_batches.append((batch_start + 1, batch_end))
            logger.error(f"❌ 第 {batch_start+1}-{batch_end} 集大纲生成失败，已重试 {max_retries} 次")
        
        # 添加延迟避免 API 限流
        import time
        if batch_end < num_episodes:
            time.sleep(2)
    
    # 完整性检查和补生成
    logger.info(f"\n📊 完整性检查：已生成 {len(all_outlines)}/{num_episodes} 集")
    
    if len(all_outlines) < num_episodes:
        missing_episodes = check_and_fill_missing_outlines(
            adapter, outline, all_outlines, num_episodes, outline_text
        )
        all_outlines.extend(missing_episodes)
        all_outlines.sort(key=lambda x: x.get('episode_num', 0))
    
    logger.info(f"\n✅ 所有分集大纲生成完成，共 {len(all_outlines)} 集")
    
    # 最终验证
    final_check = verify_outlines_completeness(all_outlines, num_episodes)
    if not final_check:
        logger.error(f"❌ 完整性验证失败：仍有缺失集数")
    else:
        logger.info(f"✅ 完整性验证通过：所有 {num_episodes} 集均已生成")
    
    return all_outlines


def check_and_fill_missing_outlines(adapter: ScriptAdapter, outline: Dict[str, Any], 
                                   existing_outlines: List[Dict[str, Any]], 
                                   num_episodes: int, outline_text: str) -> List[Dict[str, Any]]:
    """
    检查并补生成缺失的分集大纲
    """
    expected = set(range(1, num_episodes + 1))
    actual = set(ep.get('episode_num', 0) for ep in existing_outlines)
    missing = sorted(list(expected - actual))
    
    if not missing:
        return []
    
    logger.warning(f"⚠️ 发现缺失集数: {missing}，开始补生成...")
    
    filled_outlines = []
    
    # 将缺失的集数分组（每组最多5集）
    batch_size = 5
    for i in range(0, len(missing), batch_size):
        missing_batch = missing[i:i+batch_size]
        batch_start = missing_batch[0]
        batch_end = missing_batch[-1]
        
        logger.info(f"补生成第 {batch_start}-{batch_end} 集大纲...")
        
        prompt = f"""请根据以下故事大纲，生成第{batch_start}到第{batch_end}集的分集大纲。

故事大纲：
{outline_text}

要求：
1. 每集要有完整的情节单元
2. 保持节奏紧凑，每集有高潮点
3. 每集时长控制在3-5分钟
4. 分集之间要有连贯性和悬念
5. **重要：必须生成完整的 {len(missing_batch)} 集，每集都要有 episode_num、title、summary、key_scenes、main_conflict、climax、hook、ending_hook 字段**

请以 JSON 格式返回结果：
{{
    "episode_outlines": [
        {{
            "episode_num": {batch_start},
            "title": "分集标题",
            "summary": "分集摘要（100-150字）",
            "key_scenes": ["场景1", "场景2", "场景3"],
            "main_conflict": "核心冲突",
            "climax": "高潮点",
            "hook": "吸引观众的钩子",
            "ending_hook": "结尾悬念"
        }},
        ...
    ]
}}"""
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                from unimem.chat import ark_deepseek_v3_2
                messages = [
                    {"role": "system", "content": "你是一个专业的短剧剧本创作助手，擅长创作分集大纲。请始终以有效的、完整的 JSON 格式返回结果。"},
                    {"role": "user", "content": prompt}
                ]
                
                _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=4096)
                result = adapter._parse_json_response(response_text)
                
                if not result:
                    result = extract_json_from_text(response_text)
                
                if result and "episode_outlines" in result:
                    batch_outlines = result["episode_outlines"]
                    filled_outlines.extend(batch_outlines)
                    logger.info(f"✅ 补生成完成：第 {batch_start}-{batch_end} 集（{len(batch_outlines)} 集）")
                    break
                else:
                    if attempt < max_retries - 1:
                        logger.warning(f"补生成失败（尝试 {attempt+1}/{max_retries}），重试中...")
                        import time
                        time.sleep(2)
            except Exception as e:
                logger.error(f"补生成第 {batch_start}-{batch_end} 集失败（尝试 {attempt+1}/{max_retries}）: {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2)
        
        import time
        time.sleep(2)
    
    return filled_outlines


def verify_outlines_completeness(outlines: List[Dict[str, Any]], num_episodes: int) -> bool:
    """
    验证分集大纲的完整性
    """
    expected = set(range(1, num_episodes + 1))
    actual = set(ep.get('episode_num', 0) for ep in outlines)
    missing = sorted(list(expected - actual))
    
    if missing:
        logger.error(f"❌ 完整性验证失败：缺失集数 {missing}")
        return False
    
    logger.info(f"✅ 完整性验证通过：所有 {num_episodes} 集均已生成")
    return True


def validate_generated_script(script_content: str, expected_outline: Dict[str, Any], outline: Dict[str, Any], adapter: ScriptAdapter) -> dict:
    """
    反向结构化校验：对生成的剧本进行结构化分析，并与预期分集大纲对比
    
    Returns:
        {
            'accuracy_score': float,  # 准确度评分 0-1
            'validation_result': dict,  # 详细校验结果
            'issues': list,  # 发现的问题
            'suggestions': list  # 优化建议
        }
    """
    if not adapter.is_available():
        return {'accuracy_score': 0.5, 'validation_result': {}, 'issues': [], 'suggestions': []}
    
    try:
        # 1. 对生成剧本进行反向结构化分析
        logger.info("  进行反向结构化分析...")
        generated_analysis = adapter._analyze_script_content(
            script_content[:2000]  # 限制长度
        )
        
        # 2. 对预期分集大纲进行结构化分析
        expected_summary = expected_outline.get('summary', '')
        expected_analysis = adapter._analyze_script_content(
            expected_summary
        )
        
        # 3. 对比分析
        logger.info("  进行对比校验...")
        from unimem.chat import ark_deepseek_v3_2
        
        comparison_prompt = f"""请对比以下两段内容的结构化分析结果，评估生成剧本是否符合预期要求。

【预期分集大纲的结构化分析】
关键词: {', '.join(expected_analysis.get('keywords', [])[:10])}
上下文: {expected_analysis.get('context', '')}
剧本维度: {json.dumps(expected_analysis.get('script_dimensions', {}), ensure_ascii=False)}

【生成剧本的结构化分析】
关键词: {', '.join(generated_analysis.get('keywords', [])[:10])}
上下文: {generated_analysis.get('context', '')}
剧本维度: {json.dumps(generated_analysis.get('script_dimensions', {}), ensure_ascii=False)}

【创作设定要求】
- 作品类型: {outline.get('genre', '')}
- 主要人物: {json.dumps([c.get('name') for c in outline.get('main_characters', [])[:3]], ensure_ascii=False)}
- 主题: {outline.get('theme', '')[:200]}

【预期分集大纲要求】
- 标题: {expected_outline.get('title', '')}
- 核心冲突: {expected_outline.get('main_conflict', '')}
- 关键场景: {json.dumps(expected_outline.get('key_scenes', [])[:5], ensure_ascii=False)}
- 高潮点: {expected_outline.get('climax', '')}

请评估：
1. 生成剧本是否涵盖了预期分集大纲的核心情节？
2. 生成剧本是否符合创作设定（人物、世界观、风格）？
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


def build_enhanced_prompt_with_feedback(original_prompt: str, validation_result: dict, attempt: int) -> str:
    """
    根据校验反馈构建增强的 prompt（用于剧本生成）
    
    将 issues 和 suggestions 转化为具体的生成指导
    """
    issues = validation_result.get('issues', [])
    suggestions = validation_result.get('suggestions', [])
    coverage = validation_result.get('coverage', {})
    
    feedback_section = "\n\n【重要：根据上一版生成结果的反馈，请特别注意以下要求】\n"
    
    # 1. 明确指出需要避免的问题
    if issues:
        feedback_section += "\n【需要避免的问题】\n"
        for i, issue in enumerate(issues[:5], 1):
            feedback_section += f"{i}. {issue}\n"
        feedback_section += "\n请确保生成的内容避免上述问题。\n"
    
    # 2. 提供具体的改进建议
    if suggestions:
        feedback_section += "\n【改进方向】\n"
        for i, suggestion in enumerate(suggestions[:5], 1):
            feedback_section += f"{i}. {suggestion}\n"
        feedback_section += "\n请在生成时充分考虑并体现上述改进建议。\n"
    
    # 3. 根据各维度评分提供针对性指导
    if coverage:
        feedback_section += "\n【各维度要求】\n"
        if coverage.get('plot_coverage', 1.0) < 0.8:
            feedback_section += "- 请确保完整涵盖预期分集大纲的核心情节，不要遗漏重要情节点\n"
        if coverage.get('character_consistency', 1.0) < 0.8:
            feedback_section += "- 请严格遵循创作设定中的人物性格和行为特征\n"
        if coverage.get('setting_consistency', 1.0) < 0.8:
            feedback_section += "- 请确保世界观、背景设定与创作设定完全一致\n"
        if coverage.get('style_consistency', 1.0) < 0.8:
            feedback_section += "- 请保持与创作设定要求的剧本风格一致\n"
    
    feedback_section += f"\n这是第 {attempt} 次生成尝试，请务必解决上述问题，生成更符合要求的内容。\n"
    
    return original_prompt + feedback_section


def generate_full_script(adapter: ScriptAdapter, episode_outline: Dict[str, Any], outline: Dict[str, Any], context_memories: List = None, enable_validation: bool = True, validation_threshold: float = 0.7, max_retries: int = 2) -> tuple:
    """
    生成完整剧本（带上下文和反向结构化校验）
    
    Args:
        adapter: 适配器
        episode_outline: 分集大纲
        outline: 故事大纲
        context_memories: 上下文记忆（前几集的记忆）
        enable_validation: 是否启用校验
        validation_threshold: 校验阈值
        max_retries: 最大重试次数
        
    Returns:
        (script_content, validation_result)
    """
    episode_num = episode_outline.get('episode_num', 1)
    logger.info(f"\n生成第 {episode_num} 集完整剧本...")
    
    # 构建上下文信息
    context_text = ""
    if context_memories:
        context_text = "\n\n【前集上下文】\n"
        for mem in context_memories[:3]:  # 使用最近3集的记忆
            context_text += f"- {mem.content[:200]}\n"
            if mem.metadata and mem.metadata.get("script_dimensions"):
                dims = mem.metadata["script_dimensions"]
                if dims.get("scenes"):
                    context_text += f"  场景: {', '.join(dims['scenes'][:2])}\n"
                if dims.get("characters"):
                    context_text += f"  人物: {', '.join(dims['characters'][:2])}\n"
    
    # 如果有前集的校验反馈，加入指导
    previous_feedback = ""
    if 'validation_feedback' in outline and outline['validation_feedback']:
        recent_feedback = outline['validation_feedback'][-1]
        if recent_feedback.get('episode') < episode_num:
            previous_feedback = "\n\n【参考：前集的改进建议】\n"
            if recent_feedback.get('suggestions'):
                previous_feedback += "以下建议来自前集的校验反馈，请在生成时参考：\n"
                for i, sug in enumerate(recent_feedback['suggestions'], 1):
                    previous_feedback += f"{i}. {sug}\n"
    
    # 如果有前集的自动优化反馈，加入指导
    if 'optimization_feedback' in outline and outline['optimization_feedback']:
        recent_opt_feedback = outline['optimization_feedback'][-1]
        if recent_opt_feedback.get('episode') < episode_num:
            if not previous_feedback:
                previous_feedback = "\n\n【参考：前集的自动优化建议】\n"
            else:
                previous_feedback += "\n【参考：前集的自动优化建议】\n"
            
            if recent_opt_feedback.get('suggestions'):
                previous_feedback += "以下建议来自前集的自动优化分析：\n"
                for i, sug in enumerate(recent_opt_feedback['suggestions'], 1):
                    previous_feedback += f"{i}. {sug}\n"
            
            # 添加剧本特定的优化建议
            script_specific = recent_opt_feedback.get('script_specific', {})
            if script_specific:
                if script_specific.get('shot_design'):
                    previous_feedback += f"\n分镜设计建议: {script_specific['shot_design']}\n"
                if script_specific.get('dialogue_style'):
                    previous_feedback += f"对话风格建议: {script_specific['dialogue_style']}\n"
                if script_specific.get('rhythm_control'):
                    previous_feedback += f"节奏控制建议: {script_specific['rhythm_control']}\n"
    
    # 构建初始生成 prompt
    initial_prompt = f"""请根据以下分集大纲和创作设定，生成第{episode_num}集的完整短剧剧本。

创作设定：
- 作品类型: {outline.get('genre', '')}
- 主题: {outline.get('theme', '')}
- 主要角色: {json.dumps(outline.get('main_characters', [])[:3], ensure_ascii=False)}

分集大纲：
- 标题: {episode_outline.get('title', '')}
- 摘要: {episode_outline.get('summary', '')}
- 关键场景: {json.dumps(episode_outline.get('key_scenes', []), ensure_ascii=False)}
- 核心冲突: {episode_outline.get('main_conflict', '')}
- 高潮点: {episode_outline.get('climax', '')}
- 结尾悬念: {episode_outline.get('ending_hook', '')}
{context_text}
{previous_feedback}
要求：
1. 使用标准剧本格式
2. 每集时长控制在3-5分钟（约2000-3000字）
3. 包含场景、人物、对话、动作
4. 对话要自然、有张力，符合甜宠风格
5. 场景描述要视觉化
6. 要有明确的镜头语言提示
7. 开头要有吸引观众的钩子
8. 结尾要有悬念
9. 与前集保持情节连贯性

请以标准剧本格式返回，格式如下：

【第{episode_num}集：{episode_outline.get('title', '')}】

【场景1：地点 - 时间】
[镜头：全景/中景/近景/特写]
[画面描述]
[人物动作]

人物A: [对话内容]

人物B: [对话内容]

[动作描述]

【场景2：地点 - 时间】
..."""
    
    # 生成前：使用 optimize_script_prompt 优化初始 prompt（仅第一集或每5集优化一次）
    shot_script_prompt = initial_prompt
    if episode_num == 1 or episode_num % 5 == 0:
        logger.info(f"  🔧 生成前自动优化 prompt（第 {episode_num} 集）...")
        try:
            optimization_result = adapter.optimize_script_prompt(
                input_text=f"分集大纲：{episode_outline.get('summary', '')}\n关键场景：{json.dumps(episode_outline.get('key_scenes', []), ensure_ascii=False)}",
                execution_result="",  # 首次生成，无执行结果
                current_prompt=initial_prompt
            )
            
            if optimization_result.get('optimized_prompt'):
                shot_script_prompt = optimization_result['optimized_prompt']
                logger.info(f"  ✅ Prompt 已优化（基于短剧剧本特殊需求）")
                
                # 记录优化建议到上下文
                if optimization_result.get('optimized_context', {}).get('script_specific'):
                    script_specific = optimization_result['optimized_context']['script_specific']
                    if script_specific.get('shot_design'):
                        logger.info(f"  💡 分镜设计建议: {script_specific['shot_design'][:100]}...")
                    if script_specific.get('dialogue_style'):
                        logger.info(f"  💡 对话风格建议: {script_specific['dialogue_style'][:100]}...")
            else:
                logger.info(f"  ℹ️  未获得优化建议，使用原始 prompt")
        except Exception as e:
            logger.warning(f"  ⚠️  Prompt 优化过程出错: {e}，使用原始 prompt")
            shot_script_prompt = initial_prompt
    
    for attempt in range(max_retries + 1):
        try:
            from unimem.chat import ark_deepseek_v3_2
            messages = [
                {"role": "system", "content": "你是一个专业的短剧剧本创作助手，擅长创作标准格式的短剧剧本。请保持节奏紧凑、对话自然、视觉化描述，符合甜宠风格。"},
                {"role": "user", "content": shot_script_prompt}
            ]
            
            _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=2048)
            
            # 清理响应文本
            script = response_text.strip()
            if script.startswith("```"):
                lines = script.split('\n')
                script = '\n'.join([line for line in lines if not line.strip().startswith('```')])
            
            # 反向结构化校验
            validation_result = None
            if enable_validation:
                validation_result = validate_generated_script(
                    script, episode_outline, outline, adapter
                )
                
                accuracy_score = validation_result.get('accuracy_score', 0.5)
                
                if accuracy_score < validation_threshold and attempt < max_retries:
                    logger.warning(f"  ⚠️ 准确度评分 {accuracy_score:.2f} 低于阈值 {validation_threshold}，尝试重新生成...")
                    
                    # 使用 issues 和 suggestions 指导重新生成
                    enhanced_prompt = build_enhanced_prompt_with_feedback(
                        original_prompt=shot_script_prompt,
                        validation_result=validation_result,
                        attempt=attempt + 1
                    )
                    shot_script_prompt = enhanced_prompt
                    logger.info(f"  📝 已根据校验反馈优化 prompt（第 {attempt + 1} 次尝试）")
                    continue
                else:
                    logger.info(f"  ✅ 校验通过，准确度评分: {accuracy_score:.2f}")
                    if validation_result.get('issues'):
                        logger.info(f"  ⚠️ 发现 {len(validation_result['issues'])} 个问题（但不影响使用）")
                        # 记录 issues 和 suggestions 供后续集参考
                        if validation_result.get('suggestions'):
                            logger.info(f"  💡 生成 {len(validation_result['suggestions'])} 条优化建议（已记录）")
                            if 'validation_feedback' not in outline:
                                outline['validation_feedback'] = []
                            outline['validation_feedback'].append({
                                'episode': episode_num,
                                'issues': validation_result.get('issues', [])[:3],
                                'suggestions': validation_result.get('suggestions', [])[:3]
                            })
            
            # 生成后：使用 optimize_script_prompt 分析结果并优化后续 prompt（每集都分析，但仅记录优化建议）
            if script and adapter.is_available():
                try:
                    logger.info(f"  🔧 生成后自动分析并优化（用于指导后续集）...")
                    post_optimization = adapter.optimize_script_prompt(
                        input_text=f"分集大纲：{episode_outline.get('summary', '')}",
                        execution_result=script[:1000],  # 使用生成结果的前1000字进行分析
                        current_prompt=shot_script_prompt
                    )
                    
                    # 将优化建议存储到 outline 中，供后续集参考
                    if post_optimization.get('analysis', {}).get('suggestions'):
                        if 'optimization_feedback' not in outline:
                            outline['optimization_feedback'] = []
                        outline['optimization_feedback'].append({
                            'episode': episode_num,
                            'suggestions': post_optimization['analysis'].get('suggestions', [])[:3],
                            'script_specific': post_optimization.get('optimized_context', {}).get('script_specific', {})
                        })
                        logger.info(f"  ✅ 已记录优化建议供后续集参考")
                except Exception as e:
                    logger.warning(f"  ⚠️  生成后优化分析出错: {e}（不影响生成）")
            
            logger.info(f"✅ 第 {episode_num} 集剧本生成完成 ({len(script)} 字)")
            return script, validation_result
            
        except Exception as e:
            logger.error(f"生成第 {episode_num} 集剧本失败: {e}")
            if attempt < max_retries:
                logger.info(f"  重试中... ({attempt + 1}/{max_retries})")
                import time
                time.sleep(1)
                continue
            return "", None
    
    return "", None


def main():
    """主函数"""
    # 初始化适配器
    config = {
        'local_model_path': '/root/data/AI/pretrain/multilingual-e5-small',
        'qdrant_host': 'localhost',
        'qdrant_port': 6333,
        'collection_name': 'script_creation'
    }
    
    adapter = ScriptAdapter(config)
    adapter.initialize()
    
    # 选择主题
    data_dir = Path(__file__).parent.parent.parent / 'data'
    test_outline_file = data_dir / 'test_script_outline.json'
    test_outlines_file = data_dir / 'test_script_episode_outlines.json'
    
    # 优先使用测试通过的大纲
    if test_outline_file.exists() and test_outlines_file.exists():
        logger.info("✅ 使用测试通过的大纲文件...")
        with open(test_outline_file, 'r', encoding='utf-8') as f:
            outline = json.load(f)
        with open(test_outlines_file, 'r', encoding='utf-8') as f:
            outlines_data = json.load(f)
            episode_outlines = outlines_data.get('episode_outlines', [])
        
        logger.info(f"作品标题: {outline.get('title', '')}")
        logger.info(f"题材类型: {outline.get('genre', '')}")
        logger.info(f"分集大纲: {len(episode_outlines)} 集（已加载）")
        
        # 验证完整性
        if len(episode_outlines) < 50:
            logger.warning(f"⚠️ 分集大纲不完整：只有 {len(episode_outlines)}/50 集，将重新生成")
            episode_outlines = None
    else:
        episode_outlines = None
    
    # 如果没有测试大纲，则生成新的大纲
    if episode_outlines is None:
        theme = "甜宠"
        logger.info(f"选择主题: {theme}")
        
        # 1. 生成故事大纲
        outline_json = generate_script_outline(adapter, theme)
        if not outline_json:
            logger.error("故事大纲生成失败，退出")
            return
        
        outline = json.loads(outline_json)
        logger.info(f"作品标题: {outline.get('title', '')}")
        logger.info(f"题材类型: {outline.get('genre', '')}")
        
        # 保存大纲
        outline_file = data_dir / 'script_outline.json'
        with open(outline_file, 'w', encoding='utf-8') as f:
            json.dump(outline, f, ensure_ascii=False, indent=2)
        logger.info(f"大纲已保存到: {outline_file}")
        
        # 2. 生成分集大纲（50集）
        episode_outlines = generate_episode_outlines(adapter, outline, num_episodes=50)
    
    if not episode_outlines:
        logger.error("分集大纲生成失败，退出")
        return
    
    # 最终完整性验证
    if len(episode_outlines) < 50:
        logger.error(f"❌ 分集大纲不完整：只有 {len(episode_outlines)}/50 集，退出")
        return
    
    # 保存分集大纲
    outlines_file = data_dir / 'script_episode_outlines.json'
    with open(outlines_file, 'w', encoding='utf-8') as f:
        json.dump({"episode_outlines": episode_outlines}, f, ensure_ascii=False, indent=2)
    logger.info(f"分集大纲已保存到: {outlines_file}")
    
    # 验证保存的文件
    with open(outlines_file, 'r', encoding='utf-8') as f:
        saved_data = json.load(f)
        saved_count = len(saved_data.get('episode_outlines', []))
        logger.info(f"✅ 验证：保存的文件包含 {saved_count} 集")
    
    # 3. 生成完整剧本（逐集生成，每集使用上下文和反向结构化校验）
    num_episodes_to_generate = len(episode_outlines)
    logger.info(f"\n生成全部 {num_episodes_to_generate} 集完整剧本（逐集生成，带上下文和校验）...")
    logger.info(f"校验模式: 前 5 集强制校验，阈值 0.7")
    
    # 创建保存目录
    script_dir = data_dir / 'script'
    script_dir.mkdir(exist_ok=True)
    logger.info(f"剧本保存目录: {script_dir}")
    
    scripts = []
    context_memories = []  # 用于累积上下文记忆
    validate_first_n = 5  # 前5集强制校验
    
    # 逐集生成（不使用批次）
    for i, ep_outline in enumerate(episode_outlines, 1):
        episode_num = ep_outline.get('episode_num', i)
        
        # 决定是否启用校验：前N集强制校验，其余章节可选
        should_validate = episode_num <= validate_first_n
        
        script, validation_result = generate_full_script(
            adapter=adapter,
            episode_outline=ep_outline,
            outline=outline,
            context_memories=context_memories,
            enable_validation=should_validate,
            validation_threshold=0.7,
            max_retries=2
        )
        
        if script:
            script_data = {
                "episode_num": episode_num,
                "title": ep_outline.get('title', f'第{episode_num}集'),
                "outline": ep_outline,
                "script": script,
                "word_count": len(script)
            }
            
            # 添加校验结果
            if validation_result:
                script_data['validation'] = {
                    'accuracy_score': validation_result.get('accuracy_score', 0),
                    'coverage': validation_result.get('coverage', {}),
                    'issues': validation_result.get('issues', []),
                    'suggestions': validation_result.get('suggestions', [])
                }
            
            scripts.append(script_data)
            
            # 立即保存单集剧本到文件
            episode_file = script_dir / f"episode_{episode_num:02d}.json"
            with open(episode_file, 'w', encoding='utf-8') as f:
                json.dump(script_data, f, ensure_ascii=False, indent=2)
            
            # 同时保存纯文本版本
            episode_txt_file = script_dir / f"episode_{episode_num:02d}.txt"
            with open(episode_txt_file, 'w', encoding='utf-8') as f:
                f.write(f"第{episode_num}集：{script_data['title']}\n")
                f.write("="*60 + "\n\n")
                f.write(script)
            
            logger.info(f"  ✅ 第 {episode_num} 集完成 ({len(script)} 字) - 已保存到 {episode_file.name}")
            
            # 将生成的剧本内容存储为记忆，用于后续集的上下文
            if adapter.is_available():
                memory = adapter.construct_script_note(
                    content=script[:1000],  # 只存储部分内容作为上下文
                    timestamp=datetime.now(),
                    entities=[],
                    generate_summary=False
                )
                context_memories.append(memory)
                if len(context_memories) > 3:  # 只保留最近3集作为上下文
                    context_memories = context_memories[-3:]
        
        # 添加延迟避免 API 限流
        import time
        if i < num_episodes_to_generate:
            time.sleep(1)
    
    # 保存完整剧本汇总（所有集数已单独保存，这里保存汇总）
    scripts_file = data_dir / 'script_episodes.json'
    scripts_data = {
        "novel_info": {
            "title": outline.get('title', ''),
            "genre": outline.get('genre', ''),
            "theme": outline.get('theme', ''),
            "total_episodes": num_episodes_to_generate,
            "generated_episodes": len(scripts)
        },
        "episodes": scripts
    }
    with open(scripts_file, 'w', encoding='utf-8') as f:
        json.dump(scripts_data, f, ensure_ascii=False, indent=2)
    logger.info(f"完整剧本汇总已保存到: {scripts_file}")
    
    # 生成纯文本汇总版本
    txt_file = data_dir / 'script_episodes.txt'
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(f"{outline.get('title', '短剧剧本')}\n")
        f.write("="*60 + "\n\n")
        for script_data in scripts:
            f.write(f"第{script_data['episode_num']}集：{script_data['title']}\n")
            f.write("-"*60 + "\n\n")
            f.write(script_data['script'])
            f.write("\n\n")
    logger.info(f"纯文本汇总版本已保存到: {txt_file}")
    logger.info(f"单集剧本文件已保存到: {script_dir}/")
    
    # 打印统计信息
    logger.info("\n" + "="*60)
    logger.info("生成统计")
    logger.info("="*60)
    logger.info(f"总集数: 50 集")
    logger.info(f"分集大纲: {len(episode_outlines)} 集")
    logger.info(f"完整剧本: {len(scripts)} 集")
    if scripts:
        total_words = sum(s.get('word_count', 0) for s in scripts)
        logger.info(f"总字数: {total_words:,} 字")
        logger.info(f"平均每集: {total_words // len(scripts) if scripts else 0} 字")
    
    logger.info("\n✅ 所有任务完成！")


if __name__ == "__main__":
    main()

