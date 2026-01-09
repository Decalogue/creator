#!/usr/bin/env python3
"""
基于新模板创建5份差异化的短视频需求文档

使用新的智能填充模板，创建5个不同场景的需求文档。
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def create_diverse_doc(output_path: str, scenario: dict) -> str:
    """
    基于新模板格式创建差异化的需求文档
    
    Args:
        output_path: 输出文件路径
        scenario: 场景配置字典
        
    Returns:
        创建的文档路径
    """
    doc = Document()
    
    # 标题
    title = doc.add_heading('短视频创作需求模板', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 说明（新模板格式）
    doc.add_paragraph('请根据以下说明填写相应内容，所有内容都是可选的，根据需要填写即可。')
    doc.add_paragraph('💡 提示：建议填写尽可能详细的信息，以便生成更符合您需求的视频剧本。')
    doc.add_paragraph()
    
    # 1. 视频基本信息
    doc.add_heading('一、视频基本信息', level=1)
    doc.add_paragraph('视频类型（必填，从以下选项选择其一）：')
    doc.add_paragraph('  - ecommerce（电商推广）', style='List Bullet')
    doc.add_paragraph('  - ip_building（个人IP打造）', style='List Bullet')
    doc.add_paragraph('  - knowledge（知识分享）', style='List Bullet')
    doc.add_paragraph('  - vlog（生活Vlog）', style='List Bullet')
    doc.add_paragraph('  - media（自媒体内容）', style='List Bullet')
    doc.add_paragraph(f'视频类型: {scenario["video_type"]}')
    doc.add_paragraph()
    
    doc.add_paragraph('目标平台（必填，从以下选项选择其一）：')
    doc.add_paragraph('  - douyin（抖音）', style='List Bullet')
    doc.add_paragraph('  - xiaohongshu（小红书）', style='List Bullet')
    doc.add_paragraph('  - tiktok（TikTok国际）', style='List Bullet')
    doc.add_paragraph('  - youtube（YouTube）', style='List Bullet')
    doc.add_paragraph(f'目标平台: {scenario["platform"]}')
    doc.add_paragraph()
    
    doc.add_paragraph(f'目标时长（秒，可选，默认60秒）: {scenario.get("duration", 60)}')
    doc.add_paragraph()
    
    # 2. 当前任务需求
    doc.add_heading('二、当前任务需求', level=1)
    doc.add_paragraph('请详细描述本次视频创作的具体需求，每行一条：')
    for req in scenario.get("task_memories", []):
        doc.add_paragraph(req)
    doc.add_paragraph()
    
    # 3. 修改需求（可选）
    doc.add_heading('三、修改需求（可选）', level=1)
    doc.add_paragraph('如果在已有脚本基础上进行修改，请填写修改要求：')
    for mod in scenario.get("modification_memories", []):
        doc.add_paragraph(mod)
    if not scenario.get("modification_memories"):
        doc.add_paragraph('（首次生成，无需填写）')
    doc.add_paragraph()
    
    # 4. 通用记忆总结（可选）
    doc.add_heading('四、通用记忆总结（可选）', level=1)
    doc.add_paragraph('跨任务的用户偏好和通用风格偏好，这些会应用到所有视频创作：')
    for mem in scenario.get("general_memories", []):
        doc.add_paragraph(mem)
    doc.add_paragraph()
    
    # 5. 用户偏好设置
    doc.add_heading('五、用户偏好设置（可选）', level=1)
    doc.add_paragraph('请使用"键: 值"的格式填写，例如：')
    for key, value in scenario.get("user_preferences", {}).items():
        doc.add_paragraph(f'{key}: {value}')
    doc.add_paragraph()
    
    # 6. 商品信息（仅电商题材需要）
    if scenario.get("product_info"):
        doc.add_heading('六、商品信息（仅电商题材需要）', level=1)
        doc.add_paragraph('请使用"键: 值"的格式填写，例如：')
        for key, value in scenario["product_info"].items():
            doc.add_paragraph(f'{key}: {value}')
        doc.add_paragraph()
    
    # 7. 镜头素材（新格式，动态生成）
    doc.add_heading('七、镜头素材', level=1)
    doc.add_paragraph('请描述可用的镜头素材，每行一个镜头，使用"键: 值"格式或直接描述：')
    doc.add_paragraph('💡 提示：镜头素材越详细，生成的剧本越精准。建议包括：产品展示、使用场景、细节特写、对比效果等。')
    
    shot_materials = scenario.get("shot_materials", [])
    if shot_materials:
        for shot in shot_materials:
            doc.add_paragraph(shot)
    else:
        # 根据视频类型生成默认镜头建议
        if scenario["video_type"] == "ecommerce":
            default_shots = [
                "镜头1: 产品整体展示（全景，展示产品全貌）",
                "镜头2: 产品特写（细节展示，突出卖点）",
                "镜头3: 使用场景展示（实际应用场景）",
                "镜头4: 对比效果（使用前后对比）",
                "镜头5: 用户反应镜头（惊喜/满意表情）",
                "镜头6: 产品细节特写（材质/做工细节）"
            ]
        elif scenario["video_type"] == "knowledge":
            default_shots = [
                "镜头1: 标题和讲师介绍（开场，建立权威性）",
                "镜头2: 核心概念展示（动画/图示，可视化解释）",
                "镜头3: 实例演示（实际操作，真实案例）",
                "镜头4: 重点知识点标注（强调关键信息）",
                "镜头5: 总结和回顾（结尾，关键点回顾）"
            ]
        else:
            default_shots = [
                "镜头1: 开场镜头（吸引注意，建立情境）",
                "镜头2: 主要内容展示（核心内容呈现）",
                "镜头3: 细节特写（重点内容强调）",
                "镜头4: 结尾总结（收尾，引导行动）"
            ]
        
        for shot in default_shots[:scenario.get("duration", 60) // 10]:
            doc.add_paragraph(shot)
    
    doc.add_paragraph()
    
    # 保存文档
    doc.save(output_path)
    return output_path


def main():
    """主函数：创建5份差异化的需求文档"""
    
    # 定义5个差异化场景
    scenarios = [
        {
            "id": "scenario_1",
            "name": "电商-美妆-小红书-简单",
            "video_type": "ecommerce",
            "platform": "xiaohongshu",
            "duration": 45,
            "task_memories": [
                "推广新品口红",
                "突出持久度和显色度",
                "目标受众：年轻女性",
                "风格：清新自然"
            ],
            "modification_memories": [],
            "general_memories": [
                "喜欢用生活化语言",
                "偏好真实体验分享",
                "避免过度美颜滤镜"
            ],
            "user_preferences": {
                "风格偏好": "清新自然",
                "语气偏好": "亲切友好",
                "平台偏好": "小红书"
            },
            "product_info": {
                "产品名称": "春季限定口红",
                "核心卖点": "12小时持久，色彩饱满",
                "价格区间": "100-150元"
            },
            "shot_materials": [
                "镜头1: 产品整体展示（口红外观，包装设计）",
                "镜头2: 产品特写（膏体细节，色彩展示）",
                "镜头3: 试色过程（自然光线下的试色效果）",
                "镜头4: 持久度测试（时间轴展示12小时后的效果）",
                "镜头5: 多色号展示（不同色号的对比）",
                "镜头6: 日常妆容搭配（不同场合的妆容效果）"
            ]
        },
        {
            "id": "scenario_2",
            "name": "教育-编程-抖音-中等",
            "video_type": "knowledge",
            "platform": "douyin",
            "duration": 90,
            "task_memories": [
                "Python编程入门教学",
                "讲解变量和数据类型",
                "目标受众：编程初学者",
                "风格：通俗易懂，循序渐进"
            ],
            "modification_memories": [],
            "general_memories": [
                "喜欢循序渐进的教学方式",
                "偏好实际案例演示",
                "避免过于理论化"
            ],
            "user_preferences": {
                "风格偏好": "专业但易懂",
                "语气偏好": "耐心细致",
                "平台偏好": "抖音"
            },
            "product_info": {},
            "shot_materials": [
                "镜头1: 课程标题和讲师介绍（Python编程入门）",
                "镜头2: 代码演示屏幕录制（变量和数据类型示例）",
                "镜头3: 实际运行效果展示（代码执行结果）",
                "镜头4: 重点知识点标注（关键概念强调）",
                "镜头5: 实例演示（贴近实际应用场景的案例）",
                "镜头6: 注释说明展示（代码注释详解）",
                "镜头7: 练习题展示（巩固练习，互动环节）",
                "镜头8: 总结和回顾（本节重点回顾）"
            ]
        },
        {
            "id": "scenario_3",
            "name": "娱乐-搞笑-抖音-简单",
            "video_type": "ecommerce",
            "platform": "douyin",
            "duration": 30,
            "task_memories": [
                "搞笑日常段子",
                "展示生活中的小趣事",
                "目标受众：年轻人",
                "风格：轻松幽默"
            ],
            "modification_memories": [],
            "general_memories": [
                "喜欢真实生活场景",
                "偏好自然表演",
                "避免过度夸张"
            ],
            "user_preferences": {
                "风格偏好": "轻松幽默",
                "语气偏好": "自然随意",
                "平台偏好": "抖音"
            },
            "product_info": {},
            "shot_materials": [
                "镜头1: 开场悬念（吸引注意，制造好奇心）",
                "镜头2: 日常场景（建立情境，生活化场景）",
                "镜头3: 意外情况发生（转折点，剧情推进）",
                "镜头4: 反应镜头（情绪表达，表情动作）",
                "镜头5: 反转或笑点（高潮，制造惊喜）"
            ]
        },
        {
            "id": "scenario_4",
            "name": "电商-服装-淘宝-复杂",
            "video_type": "ecommerce",
            "platform": "douyin",
            "duration": 60,
            "task_memories": [
                "推广春季连衣裙",
                "突出面料质感和上身效果",
                "目标受众：25-35岁女性",
                "风格：优雅知性",
                "需要多角度展示",
                "强调适用场景（职场、约会、休闲）"
            ],
            "modification_memories": [],
            "general_memories": [
                "喜欢详细展示细节",
                "偏好真实上身效果",
                "避免过度修图"
            ],
            "user_preferences": {
                "风格偏好": "优雅知性",
                "语气偏好": "专业推荐",
                "平台偏好": "淘宝"
            },
            "product_info": {
                "产品名称": "春季气质连衣裙",
                "核心卖点": "面料舒适，版型修身，多场景适用",
                "价格区间": "200-300元",
                "颜色": "米白色、浅蓝色",
                "尺码": "S-XL"
            },
            "shot_materials": [
                "镜头1: 产品整体展示（连衣裙全貌，版型展示）",
                "镜头2: 面料细节特写（材质质感，手感展示）",
                "镜头3: 上身效果展示（多角度上身效果）",
                "镜头4: 多场景穿搭演示（职场、约会、休闲等场景）",
                "镜头5: 细节做工展示（缝线、纽扣、拉链等细节）",
                "镜头6: 身材包容性展示（不同身材的穿着效果）",
                "镜头7: 搭配建议（配饰、鞋包等搭配演示）"
            ]
        },
        {
            "id": "scenario_5",
            "name": "知识-科技-抖音-复杂",
            "video_type": "knowledge",
            "platform": "douyin",
            "duration": 120,
            "task_memories": [
                "AI技术科普",
                "讲解GPT模型原理",
                "目标受众：对AI感兴趣的用户",
                "风格：专业但不晦涩",
                "需要平衡专业性和通俗性",
                "避免过于技术化的术语"
            ],
            "modification_memories": [],
            "general_memories": [
                "喜欢用类比解释复杂概念",
                "偏好实际应用案例",
                "避免过于抽象的理论"
            ],
            "user_preferences": {
                "风格偏好": "专业但易懂",
                "语气偏好": "深入浅出",
                "平台偏好": "抖音"
            },
            "product_info": {},
            "shot_materials": [
                "镜头1: 标题和讲师介绍（AI技术科普）",
                "镜头2: 生动例子引入（降低理解门槛的类比）",
                "镜头3: 核心概念可视化（GPT模型原理图示）",
                "镜头4: 实际应用案例（贴近生活的AI应用）",
                "镜头5: 重点知识点标注（专业术语解释）",
                "镜头6: 类比说明展示（用通俗语言解释复杂概念）",
                "镜头7: 未来发展趋势（引发思考的互动环节）",
                "镜头8: 总结和回顾（引导观众思考AI未来发展）"
            ]
        }
    ]
    
    # 创建输出目录
    output_dir = Path("/tmp/test_docs_new_template")
    output_dir.mkdir(exist_ok=True)
    
    print("=" * 70)
    print("基于新模板创建5份差异化的需求文档")
    print("=" * 70)
    print()
    
    created_files = []
    
    for scenario in scenarios:
        output_path = output_dir / f"{scenario['id']}.docx"
        try:
            create_diverse_doc(str(output_path), scenario)
            created_files.append(str(output_path))
            print(f"✅ 已创建: {scenario['name']}")
            print(f"   文件: {output_path}")
            print(f"   类型: {scenario['video_type']} | 平台: {scenario['platform']} | 时长: {scenario['duration']}秒")
            print(f"   镜头数: {len(scenario.get('shot_materials', []))}")
            print()
        except Exception as e:
            print(f"❌ 创建失败: {scenario['name']} - {e}")
            print()
    
    print("=" * 70)
    print(f"完成！共创建 {len(created_files)} 份文档")
    print(f"输出目录: {output_dir}")
    print("=" * 70)
    
    return created_files


if __name__ == "__main__":
    main()
