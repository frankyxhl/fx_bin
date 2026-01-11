# Proposal: Add BDD Tests for Organize Command

**Change ID**: 2026-01-11-add-organize-bdd-tests
**Status**: Draft
**Created**: 2026-01-11
**Type**: Testing

---

## Why

organize 命令目前只有 71 个集成测试（pytest），缺少可读性强的 BDD 测试（Gherkin `.feature` 文件）。BDD 测试能更清晰地描述真实使用场景，便于非技术人员理解和验证功能。

## What

- 新增 `features/organize.feature` - 包含真实使用场景的 Gherkin 规范
- 新增 `tests/bdd/test_organize_steps.py` - BDD 步骤定义实现
- 新增 `tests/bdd/conftest.py` 的 organize 专用 fixtures（如需要）
- 复用现有的 BDD 基础设施（`tests/bdd/step_patterns.py`）

## Impact

- **Affected Code**: 仅新增测试文件，不修改生产代码
- **Affected Specs**: `openspec/changes/2026-01-11-add-organize-bdd-tests/specs/testing-standards/spec.md`
- **Breaking Change**: No
- **Backward Compatible**: Yes（纯测试添加）

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| BDD 测试运行时间过长 | 中 | 限制场景数量，使用 `@smoke` 和 `@integration` 标签分类 |
| 步骤定义与现有测试重复 | 低 | 复用 `step_patterns.py` 中的通用步骤 |
| Fixture 复杂度 | 低 | 参考现有 `test_file_filter_steps.py` 模式 |

## Rollback Strategy

删除新增的文件即可：
- `features/organize.feature`
- `tests/bdd/test_organize_steps.py`

无数据迁移或生产代码变更。

## Acceptance Criteria

- [ ] BDD 测试覆盖核心场景（默认组织、冲突处理、dry-run、递归扫描）
- [ ] 所有 BDD 测试可运行：`poetry run pytest tests/bdd/test_organize_steps.py -v`
- [ ] BDD 测试通过：`poetry run pytest -m bdd -v`
- [ ] 现有 71 个集成测试继续通过
- [ ] BDD 场景描述清晰，非技术人员可理解

## Scenarios Overview

| Scenario | Tags | Description |
|----------|------|-------------|
| 按日期组织文件 | @smoke @critical | 默认行为，按文件创建日期分类到 YYYY/YYYYMM/YYYYMMDD/ 目录 |
| 递归扫描嵌套目录 | @smoke @recursion | 处理多层嵌套目录结构 |
| Dry-run 预览变更 | @smoke | 显示将要进行的操作，不实际修改文件 |
| SKIP 模式跳过冲突 | @error_handling | 遇到冲突文件时跳过 |
| OVERWRITE 覆盖冲突 | @error_handling | 遇到冲突文件时覆盖 |
| RENAME 自动重命名 | @error_handling | 遇到冲突时自动添加后缀 |
| ASK 模式 TTY 交互 | @integration | 交互式询问用户如何处理 |
| ASK 模式非-TTY 回退 | @integration @error_handling | 非交互环境自动回退到 SKIP |
| 空目录处理 | @edge_cases | 处理空输入目录 |
| 无效路径错误 | @edge_cases @error_handling | 处理不存在的目录路径 |
