***REMOVED*** Cursor Rules 文档

本文档说明 Creator 项目中 Cursor IDE 的规则配置和使用方法。

---

***REMOVED******REMOVED*** 📋 规则文件列表

项目中的规则文件（`.mdc` 格式）：

| 文件 | 描述 | 状态 |
|------|------|------|
| `code.mdc` | 代码规范 | ✅ 已配置 |
| `env.mdc` | 虚拟环境激活规则 | ✅ 已配置 |
| `instructions.mdc` | Instructions 目录上下文规则 | ✅ 已配置 |
| `copy.mdc` | 迁移和复制功能规则 | ✅ 已配置 |
| `import.mdc` | Python 导入优先级规则 | ✅ 已配置 |

所有规则文件格式都正确，应该能正常工作。

---

***REMOVED******REMOVED*** 📝 规则详情

***REMOVED******REMOVED******REMOVED*** 1. code.mdc - 代码规范

**配置**：
```yaml
---
description: 代码规范
globs: []
alwaysApply: true
---
```

**规则内容**：
1. 保证代码清晰可读，逻辑严谨，结构精简，性能稳定
2. 代码架构一定要可靠优雅，不要过多的嵌套和深层逻辑处理
3. 集百家之所长，超越顶级架构师
4. 每个模块目录下如果有文档，就只要 README.md

**配置检查**：
- ✅ YAML frontmatter 格式正确
- ✅ `description` 字段已设置
- ✅ `alwaysApply: true` 已设置（应该始终应用）
- ⚠️ `globs: []` 为空数组（但 `alwaysApply: true` 应该能覆盖）

**优化建议**（可选）：
如果需要更明确地指定规则应用范围，可以更新 `globs`：

```yaml
---
description: 代码规范
globs:
  - "**/*.py"
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.jsx"
alwaysApply: true
---
```

但当前配置（`globs: []` + `alwaysApply: true`）应该也能正常工作。

***REMOVED******REMOVED******REMOVED*** 2. env.mdc - 虚拟环境激活规则

**配置**：
```yaml
---
description: 项目执行代码前需要激活虚拟环境
globs: []
alwaysApply: true
---
```

**规则内容**：
当前项目执行代码前需要激活虚拟环境：`conda activate seeme`

***REMOVED******REMOVED******REMOVED*** 3. instructions.mdc - Instructions 目录上下文规则

**配置**：
```yaml
---
description: 如果项目根目录下存在Instructions目录，则浏览其中所有文件作为上下文
globs: []
alwaysApply: true
---
```

**规则内容**：
如果项目根目录下存在目录 `Instructions`，则浏览其中所有文件作为上下文。

***REMOVED******REMOVED******REMOVED*** 4. copy.mdc - 迁移和复制功能规则

**配置**：
```yaml
---
description: 迁移和复制功能时，请严格遵循原来的接口和参数定义，以及使用原来的URL请求
globs: []
alwaysApply: true
---
```

**规则内容**：
迁移和复制功能时，请严格遵循原来的接口和参数定义，以及使用原来的 URL 请求。

***REMOVED******REMOVED******REMOVED*** 5. import.mdc - Python 导入优先级规则

**配置**：
```yaml
---
description: Python代码导入库的优先级规则
globs: []
alwaysApply: true
---
```

**规则内容**：
Python 代码导入库时，优先 `import`，然后 `from xxx import xxx`。优先系统基础库，然后 AI 基础库，然后自定义库。

---

***REMOVED******REMOVED*** 🔍 验证规则是否生效

***REMOVED******REMOVED******REMOVED*** 方法1：重启 Cursor 对话窗口

1. 关闭当前 Cursor 聊天窗口
2. 重新打开新的对话窗口
3. Cursor 会在新对话开始时加载项目规则

***REMOVED******REMOVED******REMOVED*** 方法2：在对话中测试

尝试以下 prompt 测试规则是否生效：

```
请按照 code.mdc 中的代码规范生成一个函数，要求：
- 避免深层嵌套
- 结构精简
- 逻辑严谨
```

如果生成的代码符合规则（如：没有深层嵌套、结构清晰），说明规则已生效。

***REMOVED******REMOVED******REMOVED*** 方法3：检查 Active Rules

1. 在 Cursor UI 中查看是否有 "Active Rules" 或 "Project Rules" 显示
2. 确认规则文件是否在列表中

***REMOVED******REMOVED******REMOVED*** 方法4：查看规则上下文

在 Cursor 的上下文面板中查看是否有项目规则被加载。

---

***REMOVED******REMOVED*** 🛠️ 规则配置说明

***REMOVED******REMOVED******REMOVED*** YAML Frontmatter 格式

每个 `.mdc` 规则文件都需要包含 YAML frontmatter：

```yaml
---
description: 规则描述
globs: []  ***REMOVED*** 文件匹配模式（可选）
alwaysApply: true  ***REMOVED*** 是否始终应用（可选）
---
```

***REMOVED******REMOVED******REMOVED*** 字段说明

- **description**: 规则的简短描述
- **globs**: 文件匹配模式数组，指定哪些文件会触发此规则
  - 空数组 `[]` 表示不限制文件类型
  - 可以指定模式如 `["**/*.py", "**/*.ts"]`
- **alwaysApply**: 是否始终应用此规则
  - `true`: 始终应用，无论文件类型
  - `false` 或不设置：只在匹配 `globs` 的文件中应用

***REMOVED******REMOVED******REMOVED*** 规则生效机制

1. **新对话开始时加载**：Cursor 会在新对话开始时读取 `.cursor/rules/` 目录下的所有 `.mdc` 文件
2. **alwaysApply: true**：确保规则在所有情况下都被加载
3. **globs 匹配**：如果设置了 `globs`，规则会在匹配的文件被编辑时自动加载

---

***REMOVED******REMOVED*** 📚 使用建议

1. **规则命名**：使用描述性的文件名，如 `code.mdc`、`env.mdc`
2. **规则内容**：保持简洁明确，避免过于复杂的规则
3. **规则数量**：不要创建过多规则文件，保持合理数量（建议 5-10 个）
4. **定期检查**：定期验证规则是否生效，确保 Cursor 正确加载规则

---

***REMOVED******REMOVED*** 🔧 故障排查

***REMOVED******REMOVED******REMOVED*** 规则未生效？

1. **检查文件位置**：确保文件在 `.cursor/rules/` 目录下
2. **检查文件格式**：确保 YAML frontmatter 格式正确
3. **重启对话**：关闭并重新打开 Cursor 对话窗口
4. **检查文件扩展名**：确保是 `.mdc` 而不是 `.md`

***REMOVED******REMOVED******REMOVED*** 规则冲突？

如果多个规则有冲突，Cursor 会按照文件名的字母顺序加载，后加载的规则可能会覆盖前面的规则。

---

***REMOVED******REMOVED*** 📖 参考资源

- [Cursor Rules 官方文档](https://docs.cursor.com/context/rules)
- [Cursor Context 文档](https://docs.cursor.com/en/context)

---

**最后更新**：2026-01-21
