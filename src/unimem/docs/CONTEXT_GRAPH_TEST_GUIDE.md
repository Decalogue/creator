# Context Graph 综合测试指南

## 测试目标

这是一个全面的Context Graph功能测试框架，旨在：

1. **验证Context Graph机制**：测试reasoning、decision_trace、先例搜索等核心功能
2. **多轮交互优化**：模拟真实的创作流程（生成->反馈->优化->REFLECT）
3. **系统进化**：从测试结果中提取经验模式，不断优化系统

## 测试场景设计

### 场景1: 电商-美妆-小红书（简单需求）
- **复杂度**: 简单
- **特点**: 基础电商推广，3轮反馈优化
- **验证点**: 基础决策痕迹捕获、reasoning提取

### 场景2: 教育-编程-抖音（中等复杂度）
- **复杂度**: 中等
- **特点**: 知识分享类，需要平衡专业性和通俗性
- **验证点**: 多轮优化、经验提取

### 场景3: 娱乐-搞笑-抖音（简单）
- **复杂度**: 简单
- **特点**: 轻松幽默风格
- **验证点**: 风格记忆、快速优化

### 场景4: 电商-服装-淘宝（复杂需求）
- **复杂度**: 复杂
- **特点**: 多角度展示、多场景应用，4轮反馈
- **验证点**: 复杂决策上下文、先例搜索

### 场景5: 知识-科技-抖音（高复杂度）
- **复杂度**: 复杂
- **特点**: 专业内容通俗化，4轮反馈
- **验证点**: 深度优化、经验模式提取

## 测试流程

每个场景都会执行以下步骤：

### 步骤1: 创建Word需求文档
- 自动生成符合格式的Word文档
- 包含任务需求、商品信息、镜头素材等

### 步骤2: 解析文档
- 使用LLM解析Word文档
- 提取任务记忆、商品信息等

### 步骤3: 搜索先例
- 使用`search_precedents`方法
- 基于决策上下文搜索相似历史决策
- **验证**: 先例搜索功能是否正常

### 步骤4: 生成初始剧本
- 调用`generate_script`生成初始剧本
- 自动存储到UniMem
- **验证**: 
  - reasoning是否正确提取
  - decision_trace是否正确捕获
  - DecisionEvent节点是否创建

### 步骤5: 多轮反馈优化
- 根据场景配置执行多轮反馈
- 每轮：存储反馈 -> 提取修改需求 -> 优化脚本
- **验证**:
  - 反馈记忆的reasoning提取
  - 决策痕迹的累积
  - 优化效果的提升

### 步骤6: REFLECT操作
- 收集所有相关记忆
- 执行REFLECT操作
- **验证**:
  - 是否提取到新经验
  - 经验的reasoning是否完整

### 步骤7: 验证Context Graph功能
- **验证项**:
  1. reasoning字段覆盖率（目标>80%）
  2. decision_trace字段覆盖率（目标>80%）
  3. DecisionEvent节点创建（目标>0）
  4. 先例搜索功能（目标能找到先例）

## 运行测试

### 方法1: 使用启动脚本（推荐）

```bash
cd /root/data/AI/creator/src/unimem/examples
./run_context_graph_test.sh
```

### 方法2: 直接运行Python脚本

```bash
cd /root/data/AI/creator/src
conda activate myswift  # 或 seeme
export PYTHONPATH=/root/data/AI/creator/src:$PYTHONPATH
python3 unimem/examples/comprehensive_context_graph_test.py
```

## 测试结果

测试完成后会生成以下文件：

### 1. 测试结果JSON
- 文件名: `context_graph_test_results_YYYYMMDD_HHMMSS.json`
- 内容: 所有测试场景的详细结果
  - 每个步骤的执行状态
  - 记忆ID列表
  - 决策事件列表
  - reasoning提取情况
  - 先例搜索结果
  - 错误信息

### 2. 进化报告JSON
- 文件名: `context_graph_test_evolution_YYYYMMDD_HHMMSS.json`
- 内容: 系统进化分析
  - 公共模式识别
  - 决策理由模式
  - 系统优化建议
  - 下一步行动

### 3. 运行日志
- 文件名: `context_graph_test_YYYYMMDD_HHMMSS.log`
- 内容: 完整的运行日志

## 结果分析

### 关键指标

1. **Reasoning覆盖率**
   - 目标: >80%
   - 含义: 有多少记忆包含决策理由
   - 改进: 如果<80%，需要增强REFLECT提示词

2. **Decision_trace覆盖率**
   - 目标: >80%
   - 含义: 有多少记忆包含决策痕迹
   - 改进: 如果<80%，检查context.metadata捕获逻辑

3. **DecisionEvent节点数**
   - 目标: >0
   - 含义: 是否成功创建决策事件节点
   - 改进: 如果=0，检查decision_trace是否正确传递

4. **先例搜索成功率**
   - 目标: 能找到相似先例（如果已有历史数据）
   - 含义: 先例搜索功能是否正常
   - 改进: 如果找不到，降低搜索阈值或优化算法

### 经验模式提取

测试框架会自动：
1. 从Neo4j查询所有experience类型记忆
2. 分析决策理由模式
3. 提取公共创作原则
4. 生成系统优化建议

## 系统进化

每次测试后，系统会：

1. **提取经验模式**
   - 从REFLECT操作中提取的经验记忆
   - 分析决策理由的常见模式
   - 总结创作原则

2. **优化建议**
   - 基于覆盖率指标提出改进建议
   - 识别系统瓶颈
   - 推荐下一步优化方向

3. **持续改进**
   - 多次运行测试，积累更多数据
   - 基于经验数据优化系统参数
   - 建立创作原则库

## 自定义测试场景

你可以修改`comprehensive_context_graph_test.py`中的`_generate_diverse_scenarios`方法，添加自己的测试场景：

```python
scenarios.append({
    "id": "scenario_custom",
    "name": "自定义场景",
    "video_type": "ecommerce",
    "platform": "douyin",
    "duration": 60,
    "complexity": "medium",
    "task_memories": [
        "你的任务需求1",
        "你的任务需求2",
    ],
    "product_info": {
        "产品名称": "你的产品",
    },
    "feedbacks": [
        {"round": 1, "feedback": "第一轮反馈"},
        {"round": 2, "feedback": "第二轮反馈"},
    ]
})
```

## 注意事项

1. **运行时间**: 完整测试需要15-30分钟（取决于LLM响应速度）
2. **资源要求**: 需要连接Redis、Neo4j、Qdrant
3. **数据积累**: 第一次运行可能找不到先例，这是正常的
4. **错误处理**: 测试框架会捕获错误并继续执行，不会因单个场景失败而中断

## 预期效果

运行测试后，你应该看到：

1. ✅ 5个测试场景全部执行完成
2. ✅ 每个场景都创建了记忆和决策事件
3. ✅ Reasoning覆盖率>80%
4. ✅ Decision_trace覆盖率>80%
5. ✅ 提取到经验记忆
6. ✅ 找到相似先例（如果有历史数据）

## 下一步

测试完成后，你可以：

1. **查看结果文件**: 分析测试结果，了解系统表现
2. **优化系统**: 根据改进建议优化系统参数
3. **运行更多测试**: 积累更多数据，提升系统能力
4. **建立原则库**: 基于提取的经验建立创作原则库

---

**开始测试，见证Context Graph的强大能力！** 🚀
