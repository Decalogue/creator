# 短视频剧本生成示例使用指南

## 概述

`generate_video_script.py` 是一个完整的短视频剧本生成示例，演示了如何：
1. 创建 Word 模板供用户填写
2. 解析用户填写的 Word 文档
3. 利用 UniMem 检索历史记忆
4. 生成个性化短视频剧本
5. 支持用户反馈不断优化

## 功能特性

### 1. Word 模板生成
- 自动创建标准化的 Word 模板
- 包含所有必要的字段和说明
- 用户只需填写内容即可

### 2. 智能文档解析
- 自动识别视频类型、平台、时长等基本信息
- 提取任务需求、修改需求、通用记忆等
- 支持键值对格式的用户偏好和商品信息

### 3. UniMem 深度集成
- 自动检索相关的历史创作
- 提取成功的创作模式
- 学习用户的风格偏好
- 将每次生成的剧本存储到 UniMem

### 4. 交互式优化
- 支持多轮反馈优化
- 自动提取修改需求
- 持续改进剧本质量

## 使用方法

### 方式一：命令行模式

#### 1. 创建 Word 模板

```bash
cd /root/data/AI/creator/src/unimem/examples
python generate_video_script.py --template --template-path video_script_template.docx
```

#### 2. 填写模板

打开生成的 `video_script_template.docx`，按照说明填写：
- 视频基本信息（类型、平台、时长）
- 当前任务需求
- 修改需求（如有）
- 通用记忆总结
- 用户偏好设置
- 商品信息（电商题材需要）
- 镜头素材

#### 3. 生成剧本

```bash
python generate_video_script.py --doc video_script_template.docx --output my_script.json
```

### 方式二：交互式模式（推荐）

```bash
python generate_video_script.py --interactive
# 或
python generate_video_script.py -i
```

交互式模式流程：
1. 自动创建模板（如果不存在）
2. 提示输入 Word 文档路径
3. 解析文档并显示结果
4. 生成初始剧本
5. 支持多轮反馈优化
6. 每次优化后保存新版本

## Word 模板字段说明

### 一、视频基本信息（必填）

- **视频类型**：从以下选项选择
  - `ecommerce`（电商推广）
  - `ip_building`（个人IP打造）
  - `knowledge`（知识分享）
  - `vlog`（生活Vlog）
  - `media`（自媒体内容）

- **目标平台**：从以下选项选择
  - `douyin`（抖音）
  - `xiaohongshu`（小红书）
  - `tiktok`（TikTok国际）
  - `youtube`（YouTube）

- **目标时长**：数字，单位秒（默认60秒）

### 二、当前任务需求

详细描述本次视频创作的具体需求，每行一条，例如：
- 推广新品手机
- 突出性价比和拍照功能
- 目标受众：年轻人

### 三、修改需求（可选）

如果在已有脚本基础上进行修改，填写修改要求。

### 四、通用记忆总结（可选）

跨任务的用户偏好和通用风格偏好，例如：
- 喜欢用生活化语言
- 避免使用"姐妹们"等称呼
- 偏好真实体验分享

### 五、用户偏好设置（可选）

使用"键: 值"格式，例如：
- 风格偏好: 真诚自然
- 平台偏好: 抖音
- 语气偏好: 像朋友分享

### 六、商品信息（仅电商题材）

使用"键: 值"格式，例如：
- 产品名称: 新品手机
- 核心卖点: 性价比、拍照
- 目标价格: 2000-3000元

### 七、镜头素材

描述可用的镜头素材，每行一个，例如：
- 镜头1: 产品特写，展示手机外观
- 镜头2: 使用场景，年轻人拍照

## 示例：完整工作流程

### 1. 创建模板

```bash
python generate_video_script.py --template
```

### 2. 填写模板

打开 `video_script_template.docx`，填写：
```
一、视频基本信息
视频类型: ecommerce
目标平台: douyin
目标时长: 60

二、当前任务需求
推广新品手机
突出性价比和拍照功能
目标受众：年轻人

五、用户偏好设置
风格偏好: 真诚自然
语气偏好: 像朋友分享

六、商品信息
产品名称: 新品手机
核心卖点: 性价比、拍照

七、镜头素材
镜头1: 产品特写，展示手机外观
镜头2: 使用场景，年轻人拍照
```

### 3. 生成剧本（交互式）

```bash
python generate_video_script.py -i
```

输入提示时：
- 直接回车使用默认模板路径
- 或输入你填写的文档路径

### 4. 查看生成结果

生成的剧本包含：
- `script`: 完整文案
- `segments`: 分段详情（序号、分类、景别、文案、画面）
- `editing_script`: 剪辑脚本
- `summary`: 摘要信息
- `unimem_memory_id`: UniMem 记忆ID（用于后续检索）

### 5. 优化剧本

根据生成的剧本，提供反馈，例如：
```
开场不够吸引人，需要更有悬念
中间部分要更突出拍照功能
结尾的号召力不够
```

系统会：
1. 自动提取修改需求
2. 存储反馈到 UniMem
3. 优化并重新生成剧本
4. 保存优化后的版本

## UniMem 优势体现

### 自动学习历史经验

当你第二次生成类似主题的视频时，系统会自动：
- 检索上次的成功经验
- 复用有效的创作模式
- 保持风格一致性

### 持续积累知识库

每次生成的剧本和用户反馈都会：
- 存储到 UniMem
- 建立记忆关联
- 形成可检索的知识库

### 个性化定制

通过通用记忆总结，系统会：
- 记住你的风格偏好
- 应用到所有视频创作
- 越用越懂你

## 输出文件说明

- `video_script_template.docx`: Word 模板文件
- `generated_script.json`: 初始生成的剧本
- `generated_script_optimized_v1.json`: 第一次优化后的剧本
- `generated_script_optimized_v2.json`: 第二次优化后的剧本
- ...（每次优化都会保存新版本）

## 代码示例

### 基本使用

```python
from unimem import UniMem
from unimem.adapters import VideoAdapter

# 初始化
unimem = UniMem(config={})
adapter = VideoAdapter(unimem_instance=unimem)

# 创建模板
adapter.create_word_template("template.docx")

# 解析文档
doc_data = adapter.parse_word_document("filled_template.docx")

# 生成剧本
script = adapter.generate_video_script(
    task_memories=doc_data["task_memories"],
    video_type=doc_data["video_type"],
    platform=doc_data["platform"],
    duration_seconds=doc_data["duration_seconds"],
    use_unimem_retrieval=True,
    store_to_unimem=True
)
```

### 优化使用

```python
# 提取用户反馈
modifications = adapter.extract_modification_memories_from_conversation(
    "开场不够吸引人，需要更有悬念"
)

# 优化剧本
optimized = adapter.optimize_script_for_editing(
    script_data=script,
    feedback="开场不够吸引人"
)
```

## 注意事项

1. **Word 文档格式**：必须使用 `.docx` 格式
2. **必填字段**：视频类型和目标平台是必填的
3. **UniMem 配置**：如需使用 UniMem 功能，确保已正确配置数据库连接
4. **模板结构**：建议使用生成的模板，确保解析准确性

## 故障排除

### 问题：模板创建失败

**原因**：缺少 `python-docx` 库

**解决**：
```bash
pip install python-docx
```

### 问题：解析结果为空

**原因**：Word 文档格式不符合模板结构

**解决**：
- 使用生成的模板文件
- 确保章节标题正确（一、二、三等）
- 不要删除模板中的示例文字结构

### 问题：UniMem 功能不可用

**原因**：UniMem 未初始化或配置错误

**解决**：
- 检查 UniMem 配置
- 如果不使用 UniMem，设置 `use_unimem_retrieval=False` 和 `store_to_unimem=False`

## 更多信息

- 查看 `VIDEO_ADAPTER_UNIMEM_USAGE.md` 了解 UniMem 集成详情
- 查看 `video_adapter.py` 源码了解实现细节

