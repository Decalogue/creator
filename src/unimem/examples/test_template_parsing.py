"""
测试 Word 模板解析功能

用于验证从 Word 模板中提取参数的准确性
"""

import sys
import json
from pathlib import Path

***REMOVED*** 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from unimem.adapters import VideoAdapter


def test_template_creation():
    """测试模板创建"""
    print("="*60)
    print("测试 1: 创建 Word 模板")
    print("="*60)
    
    adapter = VideoAdapter()
    template_path = "test_video_script_template.docx"
    
    try:
        adapter.create_word_template(template_path)
        print(f"✓ 模板创建成功: {template_path}")
        return template_path
    except Exception as e:
        print(f"✗ 模板创建失败: {e}")
        return None


def test_parameter_extraction(doc_path: str):
    """测试参数提取逻辑"""
    print("\n" + "="*60)
    print("测试 2: 参数提取逻辑说明")
    print("="*60)
    
    adapter = VideoAdapter()
    
    if not Path(doc_path).exists():
        print(f"✗ 文档不存在: {doc_path}")
        print("  请先填写模板并保存到此路径")
        return None
    
    print(f"\n正在解析文档: {doc_path}")
    print("\n提取方式说明：")
    print("-" * 60)
    
    print("\n1. 视频类型 (video_type):")
    print("   方式：关键词匹配")
    print("   逻辑：在包含'视频类型'的行中查找 'ecommerce', 'ip_building', 'knowledge', 'vlog', 'media'")
    print("   示例：'视频类型: ecommerce' → 'ecommerce'")
    
    print("\n2. 目标平台 (platform):")
    print("   方式：关键词匹配")
    print("   逻辑：在包含'目标平台'的行中查找 'douyin', 'xiaohongshu', 'tiktok', 'youtube'")
    print("   示例：'目标平台: douyin' → 'douyin'")
    
    print("\n3. 目标时长 (duration_seconds):")
    print("   方式：正则表达式提取数字")
    print("   逻辑：使用 re.findall(r'\\d+', line) 提取第一个数字")
    print("   示例：'目标时长: 60秒' → 60")
    print("   示例：'目标时长（秒）: 60' → 60")
    
    print("\n4. 章节识别（任务需求、修改需求等）:")
    print("   方式：关键词匹配 + 章节号识别")
    print("   逻辑：")
    print("   - 识别章节标题（'一、', '二、' 或关键词 '当前任务', '修改需求' 等）")
    print("   - 设置 current_section 状态")
    print("   - 后续行内容归类到对应章节")
    
    print("\n5. 键值对解析（用户偏好、商品信息）:")
    print("   方式：字符串分割")
    print("   逻辑：使用 ':' 或 '：' 分割，提取键和值")
    print("   示例：'风格偏好: 真诚自然' → {'风格偏好': '真诚自然'}")
    
    print("\n6. 镜头素材:")
    print("   方式：JSON 解析或键值对分割")
    print("   逻辑：")
    print("   - 先尝试 JSON 解析")
    print("   - 失败则使用键值对分割")
    print("   - 否则作为描述文本")
    
    print("\n" + "-" * 60)
    print("\n开始解析...")
    
    try:
        result = adapter.parse_word_document(doc_path)
        
        print("\n" + "="*60)
        print("解析结果：")
        print("="*60)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        print("\n" + "="*60)
        print("提取到的参数：")
        print("="*60)
        print(f"视频类型: {result.get('video_type')}")
        print(f"目标平台: {result.get('platform')}")
        print(f"目标时长: {result.get('duration_seconds')}秒")
        print(f"任务需求数量: {len(result.get('task_memories', []))}")
        print(f"修改需求数量: {len(result.get('modification_memories', []))}")
        print(f"通用记忆数量: {len(result.get('general_memories', []))}")
        print(f"用户偏好字段数: {len(result.get('user_preferences', {}))}")
        print(f"商品信息字段数: {len(result.get('product_info', {}))}")
        print(f"镜头素材数量: {len(result.get('shot_materials', []))}")
        
        return result
        
    except Exception as e:
        print(f"\n✗ 解析失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主函数"""
    print("\n")
    print("="*60)
    print("Word 模板参数提取测试")
    print("="*60)
    
    ***REMOVED*** 1. 创建模板
    template_path = test_template_creation()
    
    if not template_path:
        return
    
    ***REMOVED*** 2. 等待用户填写
    print(f"\n请填写模板: {template_path}")
    print("填写完成后，按回车继续测试解析...")
    input()
    
    ***REMOVED*** 3. 测试解析
    result = test_parameter_extraction(template_path)
    
    if result:
        print("\n✓ 测试完成！解析成功。")
    else:
        print("\n✗ 测试失败！请检查文档格式。")
    
    print(f"\n提示：模板文件位于: {Path(template_path).absolute()}")


if __name__ == "__main__":
    main()

