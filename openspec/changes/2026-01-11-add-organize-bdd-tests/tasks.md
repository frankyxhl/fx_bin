# Implementation Tasks (TDD Style)

**Priority**: Phase 1 → Phase 9 (sequential order)

Each task follows RED-GREEN-REFACTOR:
1. **RED**: Write failing test or capture baseline
2. **GREEN**: Apply implementation with minimal changes
3. **REFACTOR**: Optimize while keeping tests green

---

## Phase 1: 创建 BDD Feature 文件

**目标**: 编写 organize 命令的真实使用场景（Gherkin 规范）

**文件**: `features/organize.feature`

- [ ] 1.1 **RED**: 编写 `features/organize.feature` 核心场景（默认组织、冲突模式、dry-run、递归等）
- [ ] 1.2 **RED**: 运行 `pytest-bdd` 验证场景可解析（无步骤实现）
- [ ] 1.3 Commit: "Phase 1: Create organize.feature BDD scenarios"

---

## Phase 2: 实现 Given 步骤（测试数据准备）

**目标**: 实现场景的初始条件设置

**文件**: `tests/bdd/test_organize_steps.py`

- [ ] 2.1 **RED**: 编写测试: 验证文件目录创建步骤
- [ ] 2.2 **RED**: 运行测试确认失败（看到 StepDefNotFound）
- [ ] 2.3 **GREEN**: 实现 `I have a directory with files` 步骤
- [ ] 2.4 **GREEN**: 实现 `I have nested directories` 步骤
- [ ] 2.5 Commit: "Phase 2: Implement Given steps for test data setup"

---

## Phase 3: 实现 When 步骤（命令执行）

**目标**: 实现命令执行步骤

**文件**: `tests/bdd/test_organize_steps.py`

- [ ] 3.1 **RED**: 编写测试: 验证 organize 命令执行
- [ ] 3.2 **RED**: 运行测试确认失败（看到步骤未定义）
- [ ] 3.3 **GREEN**: 实现 `I run "fx organize"` 步骤
- [ ] 3.4 **GREEN**: 实现 `I run "fx organize --dry-run"` 步骤
- [ ] 3.5 Commit: "Phase 3: Implement When steps for command execution"

---

## Phase 4: 实现 Then 步骤（断言验证）

**目标**: 实现结果验证步骤

**文件**: `tests/bdd/test_organize_steps.py`

- [ ] 4.1 **RED**: 编写测试: 验证文件被移动
- [ ] 4.2 **RED**: 运行测试确认失败（看到步骤未定义）
- [ ] 4.3 **GREEN**: 实现 `files should be organized into` 步骤
- [ ] 4.4 **GREEN**: 实现 `original directory should be empty` 步骤
- [ ] 4.5 **GREEN**: 实现 `conflict should be handled` 步骤
- [ ] 4.6 Commit: "Phase 4: Implement Then steps for assertions"

---

## Phase 5: 核心场景完整实现

**目标**: 默认组织、递归扫描、dry-run 模式

**文件**: `features/organize.feature`, `tests/bdd/test_organize_steps.py`

- [ ] 5.1 **RED**: 编写场景: 按日期组织文件（默认模式）
- [ ] 5.2 **RED**: 运行测试确认失败
- [ ] 5.3 **GREEN**: 实现完整步骤链
- [ ] 5.4 **RED**: 编写场景: 递归扫描嵌套目录
- [ ] 5.5 **RED**: 运行测试确认失败
- [ ] 5.6 **GREEN**: 实现递归验证步骤
- [ ] 5.7 **RED**: 编写场景: dry-run 不修改文件
- [ ] 5.8 **RED**: 运行测试确认失败
- [ ] 5.9 **GREEN**: 实现 dry-run 验证步骤
- [ ] 5.10 Commit: "Phase 5: Core scenarios - default, recursive, dry-run"

---

## Phase 6: 冲突处理场景

**目标**: SKIP、OVERWRITE、ASK、RENAME 模式

**文件**: `features/organize.feature`, `tests/bdd/test_organize_steps.py`

- [ ] 6.1 **RED**: 编写场景: SKIP 模式跳过冲突文件
- [ ] 6.2 **RED**: 运行测试确认失败
- [ ] 6.3 **GREEN**: 实现 SKIP 验证步骤
- [ ] 6.4 **RED**: 编写场景: OVERWRITE 覆盖冲突文件
- [ ] 6.5 **RED**: 运行测试确认失败
- [ ] 6.6 **GREEN**: 实现 OVERWRITE 验证步骤
- [ ] 6.7 **RED**: 编写场景: RENAME 自动重命名冲突
- [ ] 6.8 **RED**: 运行测试确认失败
- [ ] 6.9 **GREEN**: 实现 RENAME 验证步骤
- [ ] 6.10 Commit: "Phase 6: Conflict handling - SKIP, OVERWRITE, RENAME"

---

## Phase 7: ASK 模式交互场景

**目标**: 交互式冲突处理

**文件**: `features/organize.feature`, `tests/bdd/test_organize_steps.py`

- [ ] 7.1 **RED**: 编写场景: ASK 模式 TTY 交互
- [ ] 7.2 **RED**: 运行测试确认失败
- [ ] 7.3 **GREEN**: 实现 ASK 交互模拟（mock click.confirm）
- [ ] 7.4 **RED**: 编写场景: ASK 模式非-TTY 回退 SKIP
- [ ] 7.5 **RED**: 运行测试确认失败
- [ ] 7.6 **GREEN**: 实现非-TTY 验证步骤
- [ ] 7.7 Commit: "Phase 7: ASK mode interactive scenarios"

---

## Phase 8: 边界条件和错误处理

**目标**: 空目录、权限错误、无效路径

**文件**: `features/organize.feature`, `tests/bdd/test_organize_steps.py`

- [ ] 8.1 **RED**: 编写场景: 空目录处理
- [ ] 8.2 **RED**: 运行测试确认失败
- [ ] 8.3 **GREEN**: 实现空目录验证步骤
- [ ] 8.4 **RED**: 编写场景: 无效路径错误处理
- [ ] 8.5 **RED**: 运行测试确认失败
- [ ] 8.6 **GREEN**: 实现错误消息验证步骤
- [ ] 8.7 Commit: "Phase 8: Edge cases and error handling"

---

## Phase 9: 验证和文档

**目标**: 确保所有测试通过，文档完整

- [ ] 9.1 **GREEN**: 运行所有 BDD 测试: `poetry run pytest tests/bdd/test_organize_steps.py -v`
- [ ] 9.2 **GREEN**: 运行标签过滤（smoke 测试）: `poetry run pytest -m "bdd and smoke" -v`
- [ ] 9.3 **GREEN**: 运行现有集成测试确保无回归: `poetry run pytest tests/integration/test_organize*.py -v`
- [ ] 9.4 **REFACTOR**: 添加 BDD 测试运行说明到 CLAUDE.md
- [ ] 9.5 Commit: "Phase 9: Final verification and documentation"

---

## Summary

**Total**: 9 Phases, 43 Tasks

### Scenario Coverage

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
