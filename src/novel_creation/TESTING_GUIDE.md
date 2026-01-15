***REMOVED*** 小说创作系统测试指南

***REMOVED******REMOVED*** 🎯 测试目标

验证从 idea 到完整小说的端到端流程，确保系统能够稳定运行并产出高质量作品。

***REMOVED******REMOVED*** 📋 测试计划

***REMOVED******REMOVED******REMOVED*** 阶段一：基础功能验证（5章短篇）

**目标**：验证核心流程是否正常工作

```bash
***REMOVED*** 基础测试（5章，每章2000字）
python novel_creation/test_full_novel_creation.py \
    --title "测试小说" \
    --genre "科幻" \
    --theme "时间旅行" \
    --chapters 5 \
    --words 2000
```

**检查点**：
- ✅ 创作器初始化成功
- ✅ 大纲生成成功
- ✅ 所有章节创作完成
- ✅ 完整小说文件生成
- ✅ 元数据保存成功
- ✅ 语义网格生成（如果启用）

***REMOVED******REMOVED******REMOVED*** 阶段二：中等长度测试（10章）

**目标**：验证系统在中等长度作品中的稳定性

```bash
***REMOVED*** 中等长度测试（10章，每章3000字）
python novel_creation/test_full_novel_creation.py \
    --title "中等长度测试" \
    --genre "玄幻" \
    --theme "修仙与飞升" \
    --chapters 10 \
    --words 3000
```

**检查点**：
- ✅ 上下文管理是否有效
- ✅ 章节连贯性是否保持
- ✅ 实体提取是否持续有效
- ✅ 质量检查是否发现问题

***REMOVED******REMOVED******REMOVED*** 阶段三：长篇小说测试（20章）

**目标**：验证系统在长篇小说创作中的稳定性

```bash
***REMOVED*** 长篇小说测试（20章，每章3000字）
python novel_creation/test_full_novel_creation.py \
    --title "长篇小说测试" \
    --genre "都市" \
    --theme "职场与成长" \
    --chapters 20 \
    --words 3000
```

**检查点**：
- ✅ 上下文压缩是否有效
- ✅ 长期连贯性是否保持
- ✅ 性能是否稳定
- ✅ 是否有内存泄漏

***REMOVED******REMOVED******REMOVED*** 阶段四：超长篇小说测试（50章）

**目标**：验证系统在超长篇小说创作中的极限能力

```bash
***REMOVED*** 超长篇小说测试（50章，每章3000字）
python novel_creation/test_full_novel_creation.py \
    --title "超长篇小说测试" \
    --genre "历史" \
    --theme "王朝兴衰" \
    --chapters 50 \
    --words 3000
```

**检查点**：
- ✅ 系统是否能完成超长创作
- ✅ 上下文管理策略是否有效
- ✅ 质量是否保持稳定

***REMOVED******REMOVED*** 🔍 测试检查清单

***REMOVED******REMOVED******REMOVED*** 功能检查

- [ ] 创作器初始化成功
- [ ] 大纲生成成功
- [ ] 所有章节创作完成
- [ ] 完整小说文件生成
- [ ] 元数据保存成功
- [ ] 语义网格生成（如果启用）

***REMOVED******REMOVED******REMOVED*** 质量检查

- [ ] 章节连贯性
- [ ] 角色一致性
- [ ] 情节逻辑性
- [ ] 风格一致性
- [ ] 实体提取效果

***REMOVED******REMOVED******REMOVED*** 性能检查

- [ ] 创作速度
- [ ] 内存使用
- [ ] 上下文管理效率
- [ ] 错误处理能力

***REMOVED******REMOVED*** 📊 测试结果记录

***REMOVED******REMOVED******REMOVED*** 测试记录表

| 测试阶段 | 章节数 | 每章字数 | 总字数 | 耗时 | 状态 | 问题 |
|---------|--------|---------|--------|------|------|------|
| 阶段一 | 5 | 2000 | 10000 | - | - | - |
| 阶段二 | 10 | 3000 | 30000 | - | - | - |
| 阶段三 | 20 | 3000 | 60000 | - | - | - |
| 阶段四 | 50 | 3000 | 150000 | - | - | - |

***REMOVED******REMOVED******REMOVED*** 问题记录

记录测试过程中发现的问题：

1. **问题描述**
   - 发现时间：
   - 测试阶段：
   - 严重程度：
   - 复现步骤：
   - 修复状态：

***REMOVED******REMOVED*** 🚀 快速开始

***REMOVED******REMOVED******REMOVED*** 运行基础测试

```bash
cd /root/data/AI/creator/src
python novel_creation/test_full_novel_creation.py
```

***REMOVED******REMOVED******REMOVED*** 自定义测试参数

```bash
python novel_creation/test_full_novel_creation.py \
    --title "我的小说" \
    --genre "科幻" \
    --theme "时间旅行" \
    --chapters 5 \
    --words 2000
```

***REMOVED******REMOVED*** 📝 注意事项

1. **LLM 配置**：确保 LLM 配置正确，有足够的额度
2. **时间成本**：长篇小说创作需要较长时间，建议分阶段测试
3. **资源消耗**：注意 Token 消耗和成本控制
4. **错误处理**：测试过程中如遇错误，记录详细信息

***REMOVED******REMOVED*** 🔧 故障排查

***REMOVED******REMOVED******REMOVED*** 常见问题

1. **创作器初始化失败**
   - 检查 LLM 配置
   - 检查依赖是否安装

2. **章节创作失败**
   - 检查 LLM 调用是否正常
   - 检查上下文是否溢出

3. **文件生成失败**
   - 检查输出目录权限
   - 检查磁盘空间

***REMOVED******REMOVED*** 📈 下一步

测试完成后，根据结果：
1. 修复发现的问题
2. 优化性能瓶颈
3. 增强质量检查
4. 完善用户体验
