# VideoAdapter 最大化利用 UniMem 优势指南

## 概述

`VideoAdapter` 已深度集成 UniMem，充分利用 UniMem 的语义检索、记忆存储和跨任务学习能力，实现更智能、更个性化的短视频文案生成。

## UniMem 集成优势

### 1. 语义检索历史创作
- **功能**：自动从 UniMem 中检索相关的历史脚本和创作经验
- **优势**：避免重复创作，复用成功模式，保持风格一致性

### 2. 记忆存储和关联
- **功能**：将每次生成的脚本存储到 UniMem，建立记忆网络
- **优势**：积累创作历史，支持跨任务学习和经验总结

### 3. 跨任务风格学习
- **功能**：从历史记忆中提取用户偏好和成功的创作模式
- **优势**：实现个性化定制，越用越懂用户

### 4. 记忆演化优化
- **功能**：通过 UniMem 的 REFLECT 操作总结和优化创作经验
- **优势**：持续改进，形成创作知识库

## 使用方法

### 基础使用（独立模式）

```python
from unimem.adapters import VideoAdapter

# 创建适配器（独立模式，不连接 UniMem）
adapter = VideoAdapter(config={})

# 解析 Word 文档
doc_data = adapter.parse_word_document("user_memories.docx")

# 生成脚本（不使用 UniMem）
script = adapter.generate_video_script(
    task_memories=doc_data["task_memories"],
    general_memories=doc_data["general_memories"],
    video_type="ecommerce",
    platform="douyin",
    use_unimem_retrieval=False,  # 禁用 UniMem 检索
    store_to_unimem=False  # 不存储到 UniMem
)
```

### 高级使用（UniMem 集成模式）

```python
from unimem import UniMem
from unimem.adapters import VideoAdapter

# 1. 初始化 UniMem
unimem = UniMem(config={})

# 2. 创建适配器（传入 UniMem 实例）
adapter = VideoAdapter(
    config={},
    unimem_instance=unimem  # 关键：传入 UniMem 实例
)

# 3. 解析 Word 文档
doc_data = adapter.parse_word_document("user_memories.docx")

# 4. 生成脚本（充分利用 UniMem）
script = adapter.generate_video_script(
    task_memories=doc_data["task_memories"],
    modification_memories=doc_data["modification_memories"],
    general_memories=doc_data["general_memories"],
    user_preferences=doc_data["user_preferences"],
    product_info=doc_data["product_info"],
    shot_materials=doc_data["shot_materials"],
    video_type="ecommerce",
    platform="douyin",
    duration_seconds=60,
    use_unimem_retrieval=True,  # 启用 UniMem 检索
    store_to_unimem=True  # 存储到 UniMem
)

# 5. 脚本已自动存储到 UniMem，可通过 memory_id 检索
if "unimem_memory_id" in script:
    print(f"脚本已存储，memory_id: {script['unimem_memory_id']}")
```

## UniMem 功能详解

### 1. 历史创作检索 (`enrich_memories_from_unimem`)

**工作原理**：
- 使用任务记忆和视频类型构建查询
- 通过 UniMem 的 `recall` 操作进行语义检索
- 检索相关的历史脚本、成功模式和用户偏好

**检索内容**：
- 历史相关脚本：相似的视频脚本和文案
- 成功创作模式：被验证有效的创作经验
- 用户风格偏好：从历史记忆中提取的风格特点

**优势**：
```python
# 自动检索历史电商推广脚本
enriched = adapter.enrich_memories_from_unimem(
    task_memories=["推广新品手机", "突出性价比"],
    video_type="ecommerce",
    top_k=10
)

# 结果包含：
# - historical_scripts: 历史相似的手机推广脚本
# - successful_patterns: 成功的推广模式
# - user_style_preferences: 用户的表达偏好
```

### 2. 脚本存储 (`store_script_to_unimem`)

**工作原理**：
- 将生成的脚本转换为 `Experience` 对象
- 使用 UniMem 的 `retain` 操作存储
- 自动建立与其他记忆的关联

**存储内容**：
- 脚本摘要和预览
- 任务需求和视频类型
- 平台和时长信息

**优势**：
```python
# 自动存储，后续可检索
memory_id = adapter.store_script_to_unimem(
    script_data=script,
    task_memories=["推广新品手机"],
    video_type="ecommerce",
    platform="douyin"
)

# 后续可通过 memory_id 或语义检索找到这个脚本
```

### 3. 跨任务学习

**场景示例**：

```python
# 第一次创作：电商推广视频
script1 = adapter.generate_video_script(
    task_memories=["推广新品手机"],
    video_type="ecommerce",
    use_unimem_retrieval=True,
    store_to_unimem=True
)

# 第二次创作：相同类型，自动学习第一次的经验
script2 = adapter.generate_video_script(
    task_memories=["推广新品耳机"],  # 类似的产品
    video_type="ecommerce",
    use_unimem_retrieval=True,  # 自动检索 script1 相关的经验
    store_to_unimem=True
)
```

**学习效果**：
- 自动复用第一次的成功模式
- 保持风格一致性
- 避免重复错误

## 最佳实践

### 1. 初始化 UniMem 实例

```python
# 推荐：使用配置文件
from unimem import UniMem
from unimem.config import UniMemConfig

config = UniMemConfig.from_file("unimem_config.yaml")
unimem = UniMem(config=config.to_dict())

# 传入 VideoAdapter
adapter = VideoAdapter(unimem_instance=unimem)
```

### 2. Word 文档结构建议

为了最大化利用 UniMem，建议 Word 文档包含：

```
# 当前任务需求
- 推广新品手机
- 突出性价比和拍照功能
- 目标受众：年轻人

# 修改需求（可选）
- 增加情感共鸣
- 调整语气更轻松

# 通用记忆总结
- 喜欢用生活化语言
- 避免使用"姐妹们"等称呼
- 偏好真实体验分享

# 用户偏好
风格偏好: 真诚自然
平台偏好: 抖音
语气偏好: 像朋友分享

# 商品信息（电商题材）
产品名称: 新品手机
核心卖点: 性价比、拍照
目标价格: 2000-3000元

# 镜头素材
镜头1: 产品特写
镜头2: 使用场景
...
```

### 3. 定期使用 REFLECT 优化

```python
from unimem.memory_types import Task, Context

# 定期总结创作经验
updated_memories = unimem.reflect(
    memories=[...],  # 最近生成的脚本记忆
    task=Task("总结电商推广视频的成功模式"),
    context=Context()
)
```

### 4. 利用检索优化脚本

```python
# 生成脚本前，先检索相关经验
related_scripts = unimem.recall(
    query="电商推广手机 成功案例",
    top_k=5
)

# 将这些经验作为任务记忆的一部分
task_memories = [
    "推广新品手机",
    *[s.memory.content[:100] for s in related_scripts]  # 加入历史经验
]
```

## 性能优化

### 1. 控制检索数量
```python
# 根据需求调整 top_k
enriched = adapter.enrich_memories_from_unimem(
    task_memories=task_memories,
    video_type=video_type,
    top_k=5  # 少量检索，提高速度
)
```

### 2. 选择性启用功能
```python
# 如果不需要历史学习，可以禁用
script = adapter.generate_video_script(
    ...,
    use_unimem_retrieval=False,  # 禁用检索
    store_to_unimem=True  # 只存储，不检索
)
```

### 3. 批量处理
```python
# 批量生成脚本，共享 UniMem 连接
for task in tasks:
    script = adapter.generate_video_script(
        task_memories=task,
        use_unimem_retrieval=True,
        store_to_unimem=True
    )
```

## 总结

通过深度集成 UniMem，`VideoAdapter` 实现了：

1. **智能检索**：自动从历史记忆中学习
2. **持续积累**：每次创作都成为后续创作的参考
3. **风格一致**：跨任务保持用户偏好
4. **经验复用**：避免重复创作，提高效率

**关键点**：传入 `unimem_instance` 参数，即可启用所有 UniMem 优势功能！

