***REMOVED*** LLM模型配置说明

***REMOVED******REMOVED*** 配置依据

基于实际对比测试结果（10章测试），系统采用混合模型策略，为不同任务选择最适合的模型。

***REMOVED******REMOVED*** 测试结果摘要

| 指标 | Gemini 3 Flash | DeepSeek V3.2 | 胜者 |
|------|----------------|---------------|------|
| 字数控制差异 | 27.1% | 135.9% | ✅ Gemini |
| 平均每章问题数 | 1.30个 | 2.40个 | ✅ Gemini |
| 重写改善率 | 60.0% | 57.1% | ✅ Gemini |

***REMOVED******REMOVED*** 当前配置

***REMOVED******REMOVED******REMOVED*** 1. 章节生成
- **模型**：`gemini_3_flash`（默认）
- **原因**：
  - 字数控制更准确（差异27.1% vs 135.9%）
  - 初始质量问题更少（1.30 vs 2.40个/章）
  - 需要重写的章节更少（50% vs 70%）
- **配置方式**：
  - 环境变量：`export NOVEL_LLM_MODEL=gemini_3_flash`
  - 代码参数：`ReactNovelCreator(llm_client=gemini_3_flash)`

***REMOVED******REMOVED******REMOVED*** 2. 重写机制
- **模型**：使用章节生成相同的模型（`gemini_3_flash`）
- **原因**：
  - 重写改善率更高（60.0% vs 57.1%）
  - 平均重写轮数相当（2.60 vs 2.57）
- **实现**：通过 `self.agent.run()` 调用，自动使用传入的 `llm_client`

***REMOVED******REMOVED******REMOVED*** 3. 悬念评估
- **模型**：`deepseek_v3_2`（固定）
- **原因**：
  - 更适合深度理解和分析任务
  - 能够准确识别深层悬疑元素
- **实现**：`_calculate_suspense_score()` 方法中固定使用

***REMOVED******REMOVED******REMOVED*** 4. 实体提取
- **模型**：多模型投票（`gemini_3_flash` + `deepseek_v3_2`）
- **原因**：
  - 两个模型互补，提高提取精度
  - 投票机制确保95%+的准确率
- **实现**：`MultiModelEntityExtractor` 类

***REMOVED******REMOVED******REMOVED*** 5. 质量检查
- **方法**：基于规则的检查系统
- **说明**：不直接使用LLM，通过规则检查一致性、连贯性、风格等问题

***REMOVED******REMOVED*** 配置变更历史

***REMOVED******REMOVED******REMOVED*** 2026-01-21
- **变更**：默认章节生成模型从 `deepseek_v3_2` 改为 `gemini_3_flash`
- **依据**：LLM对比测试结果
- **影响文件**：
  - `test_quality_optimizations.py`
  - `test_50_100_chapters.py`
  - `README.md`

***REMOVED******REMOVED*** 使用建议

1. **默认配置**：直接使用，无需修改（已优化为最佳配置）
2. **自定义配置**：可通过环境变量 `NOVEL_LLM_MODEL` 临时切换
3. **评估任务**：不建议修改悬念评估和质量评估的模型配置
4. **实体提取**：保持多模型投票，确保高精度

***REMOVED******REMOVED*** 性能对比

详细对比报告请参考：`outputs/LLM对比测试_comparison_report.txt`
