***REMOVED*** Puppeteer 与 UniMem 集成测试

***REMOVED******REMOVED*** 快速开始

***REMOVED******REMOVED******REMOVED*** 前置条件

1. **启动 UniMem 服务**
   ```bash
   cd /root/data/AI/creator/src
   ./unimem/scripts/start_unimem_service.sh
   ```
   
   或者直接运行：
   ```bash
   python -m unimem.service.server
   ```

2. **确保后端服务运行**
   - Redis（FoA/DA）
   - Neo4j（Graph/LTM）
   - Qdrant（Vector）

3. **激活 conda 环境**
   ```bash
   conda activate seeme
   ```

***REMOVED******REMOVED******REMOVED*** 运行测试

**方式 1：使用测试脚本（推荐）**
```bash
cd /root/data/AI/creator/src
./puppeteer/examples/run_integration_test.sh
```

**方式 2：直接运行 Python 脚本**
```bash
cd /root/data/AI/creator/src/puppeteer
python examples/test_unimem_integration.py
```

***REMOVED******REMOVED*** 测试内容

测试脚本会执行以下测试：

1. **服务连接测试**
   - 检查 UniMem 服务是否运行
   - 验证健康检查端点

2. **工具注册测试**
   - 检查 UniMem 工具是否已注册
   - 验证三个工具：retain, recall, reflect

3. **基本操作测试**
   - 测试存储记忆
   - 测试检索记忆
   - 验证记忆内容

4. **工具执行测试**
   - 测试通过工具接口存储记忆
   - 测试通过工具接口检索记忆

5. **模拟任务测试**
   - 模拟完整的任务流程
   - 任务开始时检索记忆
   - Agent 执行时存储记忆
   - 任务完成后处理

***REMOVED******REMOVED*** 预期结果

如果所有测试通过，你会看到：

```
============================================================
测试总结
============================================================
服务连接: ✓ 通过
工具注册: ✓ 通过
基本操作: ✓ 通过
工具执行: ✓ 通过
模拟任务: ✓ 通过

总计: 5/5 通过

🎉 所有测试通过！
```

***REMOVED******REMOVED*** 故障排除

***REMOVED******REMOVED******REMOVED*** 问题 1：UniMem 服务未运行

**错误信息**：
```
✗ 无法连接到 UniMem 服务 (http://localhost:9622)
```

**解决方案**：
1. 检查服务是否启动：
   ```bash
   curl http://localhost:9622/unimem/health
   ```

2. 启动服务：
   ```bash
   cd /root/data/AI/creator/src
   python -m unimem.service.server
   ```

***REMOVED******REMOVED******REMOVED*** 问题 2：模块导入错误

**错误信息**：
```
ModuleNotFoundError: No module named 'tools.base.register'
```

**解决方案**：
- 确保在 `puppeteer` 目录下运行测试
- 或者使用提供的测试脚本

***REMOVED******REMOVED******REMOVED*** 问题 3：后端服务未运行

**错误信息**：
```
✗ 存储记忆失败: Connection refused
```

**解决方案**：
1. 检查 Redis：
   ```bash
   redis-cli ping
   ```

2. 检查 Neo4j：
   ```bash
   ***REMOVED*** 查看 Neo4j 状态
   systemctl status neo4j
   ***REMOVED*** 或
   docker ps | grep neo4j
   ```

3. 检查 Qdrant：
   ```bash
   curl http://localhost:6333/health
   ```

***REMOVED******REMOVED*** 测试脚本说明

***REMOVED******REMOVED******REMOVED*** test_unimem_integration.py

完整的集成测试脚本，包含：
- 服务连接测试
- 工具注册测试
- 基本操作测试
- 工具执行测试
- 模拟任务测试

***REMOVED******REMOVED******REMOVED*** run_integration_test.sh

便捷的测试脚本，自动：
- 检查 UniMem 服务状态
- 设置正确的工作目录
- 运行测试并显示结果

***REMOVED******REMOVED*** 下一步

测试通过后，你可以：

1. **查看集成示例**
   - `novel_with_unimem.py` - 完整的创作任务集成示例
   - `unimem_integration_guide.md` - 详细的集成指南

2. **开始集成**
   - 在现有任务中添加记忆功能
   - 创建支持记忆的自定义 Agent

3. **监控和优化**
   - 查看 UniMem 服务日志
   - 优化记忆查询性能
   - 调整记忆存储策略

