***REMOVED*** 修改记录：使用本地实例

***REMOVED******REMOVED*** 修改时间
2026-01-08

***REMOVED******REMOVED*** 修改内容
将测试脚本默认使用本地 UniMem 实例，而不是 HTTP 服务。

***REMOVED******REMOVED*** 修改的文件
1. `run_multi_test_workflow.py`
   - 将 `USE_UNIMEM_SERVICE` 默认值从 `"true"` 改为 `"false"`
   - 现在默认使用本地实例，确保记忆正确存储到 Neo4j

2. `test_optimization_with_feedback.py`
   - 将 `USE_UNIMEM_SERVICE` 默认值从 `"true"` 改为 `"false"`
   - 现在默认使用本地实例

***REMOVED******REMOVED*** 原因
HTTP 服务存储的记忆没有出现在 Neo4j 中，而本地实例可以正确存储。使用本地实例可以：
- 确保记忆正确存储到 Neo4j LTM 层
- 避免 HTTP 服务的配置和初始化问题
- 更直接地使用修复后的存储后端代码

***REMOVED******REMOVED*** 如何切换回 HTTP 服务
如果需要使用 HTTP 服务，可以设置环境变量：
```bash
export USE_UNIMEM_SERVICE=true
python run_multi_test_workflow.py
```

***REMOVED******REMOVED*** 验证
- ✅ 本地实例初始化成功
- ✅ LTM 后端配置为 neo4j
- ✅ 记忆可以正确存储到 Neo4j
