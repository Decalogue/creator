***REMOVED*** REFLECT功能增强 - 经验提取

***REMOVED******REMOVED*** 改进时间
2026-01-08

***REMOVED******REMOVED*** 改进目标
增强REFLECT功能，使其能够从多轮对话和反馈中提取可复用的EXPERIENCE类型记忆。

***REMOVED******REMOVED*** 已完成的改进

***REMOVED******REMOVED******REMOVED*** ✅ 1. 增强REFLECT提示词
**文件**: `operation_adapter.py` - `_build_reflect_prompt`

**改进内容**:
- 添加了提取经验模式的明确指令
- 要求LLM识别可复用的、通用的、经过验证的最佳实践
- 使用【新经验】标记来标识经验模式

***REMOVED******REMOVED******REMOVED*** ✅ 2. 实现经验提取方法
**文件**: `operation_adapter.py`

**新增方法**:
- `_extract_experiences()`: 从REFLECT答案中提取经验记忆
- `_refine_experience()`: 使用LLM提炼经验，确保是可复用的通用模式
- `_extract_implicit_experience()`: 从答案中隐式提取经验（无明确标记时）

**特点**:
- 支持显式标记提取（【新经验】）
- 支持隐式提取（从包含"应该"、"建议"等关键词的句子中提取）
- 自动提炼经验为通用模式

***REMOVED******REMOVED******REMOVED*** ✅ 3. 更新REFLECT流程
**文件**: `operation_adapter.py` - `reflect`方法

**改进**:
- 在REFLECT结果中添加`new_experiences`字段
- 同时提取新观点和新经验

**文件**: `core.py` - `reflect`方法

**改进**:
- 处理并存储新提取的经验记忆
- 确保经验记忆有正确的source标识
- 记录经验提取统计信息

***REMOVED******REMOVED*** 使用方式

***REMOVED******REMOVED******REMOVED*** 在REFLECT答案中明确标记经验
```
答案：...（回答内容）

【新经验】
在短视频脚本创作中，用户反馈"开场不够吸引"时，应该：
1. 使用悬念或反转开头
2. 前3秒内抛出核心冲突或问题
3. 避免平铺直叙，增加视觉冲击
```

***REMOVED******REMOVED******REMOVED*** 隐式提取经验
当REFLECT任务描述包含"经验"、"模式"、"策略"、"最佳实践"、"总结"等关键词时，系统会自动从答案中提取包含经验模式的句子。

***REMOVED******REMOVED*** 预期效果

***REMOVED******REMOVED******REMOVED*** 短期
- ✅ REFLECT操作能够提取EXPERIENCE类型记忆
- ✅ 经验记忆包含正确的source标识（`reflect_experience`）
- ✅ 经验记忆保存到Neo4j和向量存储

***REMOVED******REMOVED******REMOVED*** 中期
- 📈 EXPERIENCE类型记忆占比提升（目标：20%+）
- 📈 从多轮对话中积累可复用经验
- 📈 系统能够自动识别和复用成功模式

***REMOVED******REMOVED******REMOVED*** 长期
- 🎯 形成经验知识库
- 🎯 跨任务经验共享
- 🎯 自动避免重复错误

***REMOVED******REMOVED*** 代码修改清单

1. `operation_adapter.py`:
   - 修改`reflect()`方法，添加经验提取
   - 修改`_build_reflect_prompt()`，添加经验提取指令
   - 新增`_extract_experiences()`方法
   - 新增`_refine_experience()`方法
   - 新增`_extract_implicit_experience()`方法

2. `core.py`:
   - 修改`reflect()`方法，处理new_experiences
   - 确保经验记忆有正确的source标识

***REMOVED******REMOVED*** 注意事项

1. **经验vs观点**: 
   - 经验（EXPERIENCE）：可复用的通用模式，适用于类似场景
   - 观点（OPINION）：对特定情况的看法或信念

2. **提炼机制**: 
   - 系统会使用LLM进一步提炼经验，确保是通用模式而非具体事件
   - 如果提炼失败，会使用原始文本（经过清理）

3. **置信度**: 
   - 显式标记的经验：置信度0.8
   - 隐式提取的经验：置信度0.7

***REMOVED******REMOVED*** 测试建议

1. 运行包含"经验"、"模式"关键词的REFLECT操作
2. 检查是否成功提取EXPERIENCE类型记忆
3. 验证经验记忆是否正确保存到Neo4j
4. 检查经验记忆的source字段是否为`reflect_experience`
