***REMOVED*** Puppeteer 与 UniMem 集成测试

***REMOVED******REMOVED*** 快速开始

***REMOVED******REMOVED******REMOVED*** 前置条件

1. **启动 UniMem 服务**
   ```bash
   cd /root/data/AI/creator/src
   python -m unimem.service.server
   ```
   
   或者使用启动脚本：
   ```bash
   ./unimem/scripts/start_unimem_service.sh
   ```

2. **确保后端服务运行**
   - Redis（端口 6379）
   - Neo4j（端口 7474）
   - Qdrant（端口 6333）

3. **激活 conda 环境**
   ```bash
   conda activate seeme
   ```

***REMOVED******REMOVED******REMOVED*** 运行测试

```bash
cd /root/data/AI/creator/src/puppeteer
python tests/test_unimem_integration.py
```

***REMOVED******REMOVED*** 测试内容

测试脚本会执行以下测试：

1. **UniMem 服务连接**
   - 检查服务是否运行
   - 验证健康检查端点

2. **UniMem 工具注册**
   - 检查三个工具是否已注册
   - 验证工具模块导入

3. **GraphReasoningWithMemory 组件**
   - 测试组件导入
   - 测试组件初始化

4. **Reasoning_Agent_With_Memory 组件**
   - 测试组件导入
   - 验证组件结构

5. **UniMem 工具执行**
   - 测试 retain 工具
   - 测试 recall 工具

6. **提示词文件**
   - 检查文件是否存在
   - 验证 JSON/JSONL 格式

***REMOVED******REMOVED*** 预期结果

如果所有测试通过（包括 UniMem 服务运行），你会看到：

```
============================================================
测试总结
============================================================
服务连接: ✓ 通过
工具注册: ✓ 通过
GraphReasoningWithMemory: ✓ 通过
Reasoning_Agent_With_Memory: ✓ 通过
工具执行: ✓ 通过
提示词文件: ✓ 通过

总计: 6/6 通过

🎉 所有测试通过！
```

如果 UniMem 服务未运行，部分测试会失败，但组件结构测试应该通过。

***REMOVED******REMOVED*** 故障排除

***REMOVED******REMOVED******REMOVED*** 问题 1：UniMem 服务未运行

**错误信息**：
```
✗ 无法连接到 UniMem 服务 (http://localhost:9622)
```

**解决方案**：
1. 启动 UniMem 服务
2. 等待服务完全启动
3. 检查服务日志

***REMOVED******REMOVED******REMOVED*** 问题 2：模块导入错误

**错误信息**：
```
ModuleNotFoundError: No module named 'tools.base.register'
```

**解决方案**：
- 确保在 `puppeteer` 目录下运行测试
- 检查 Python 路径设置

***REMOVED******REMOVED******REMOVED*** 问题 3：后端服务未运行

**错误信息**：
```
Connection refused
```

**解决方案**：
1. 检查 Redis：`redis-cli ping`
2. 检查 Neo4j：查看服务状态
3. 检查 Qdrant：`curl http://localhost:6333/health`

***REMOVED******REMOVED*** 测试说明

***REMOVED******REMOVED******REMOVED*** 组件测试

组件测试主要验证：
- 模块可以正常导入
- 类可以正常实例化
- 基本功能结构正确

***REMOVED******REMOVED******REMOVED*** 集成测试

集成测试需要 UniMem 服务运行，验证：
- 工具可以正常调用
- 记忆可以正常存储和检索
- 组件可以正常协作

***REMOVED******REMOVED*** 下一步

测试通过后，可以：
1. 使用 `tasks/novel_with_memory.py` 运行完整任务
2. 查看集成使用指南：`puppeteer/docs/unimem_integration_usage.md`
3. 根据需要调整提示词和配置

