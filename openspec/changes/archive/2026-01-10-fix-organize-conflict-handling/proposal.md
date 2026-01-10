# Change: Fix Organize Conflict Handling

## Why

Code review 发现 `fx organize` 命令的冲突处理存在关键语义问题和潜在的覆盖风险：

1. **RENAME 模式不会对磁盘冲突进行重命名**，会导致意外覆盖
2. **ASK 模式未实现**，直接等同于 SKIP
3. **OVERWRITE 模式缺少 atomic replace 和 EXDEV 跨盘处理**
4. **--quiet 模式行为与 help 文案不一致**
5. **_should_skip_entry 未捕获 ValueError**，跨盘场景会崩溃

## What Changes

- **RENAME 模式修复**：磁盘冲突时自动添加 _1, _2 后缀（当前会覆盖）
- **ASK 模式实现**：添加交互式 prompt（或从 CLI 中移除此选项）
- **OVERWRITE 模式增强**：使用 `os.replace()` 实现 atomic overwrite，处理 EXDEV 跨盘错误
- **--quiet 行为修正**：确保始终输出 summary（与 help 文案 "errors and summary only" 一致）
- **跨盘健壮性**：`_should_skip_entry` 捕获 `ValueError`

## Impact

- **Affected specs**: organize
- **Affected code**:
  - Modified: `fx_bin/organize_functional.py` (move_file_safe, _should_skip_entry)
  - Modified: `fx_bin/cli.py` (help 文案、quiet 输出、ask 交互)
  - Modified: `tests/integration/test_organize_io.py` (冲突处理测试)
  - Modified: `openspec/specs/organize/spec.md` (文档同步)

## Breaking Change

No - 修复 buggy 行为，不破坏正确用法
