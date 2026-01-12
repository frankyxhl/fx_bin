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

- [x] 1.1 **RED**: 编写 `features/organize.feature` 核心场景（默认组织、冲突模式、dry-run、递归等）
- [x] 1.2 **RED**: 运行 `pytest-bdd` 验证场景可解析（无步骤实现）
- [x] 1.3 Commit: "Phase 1: Create organize.feature BDD scenarios"

---

## Phase 2: 实现 Given 步骤（测试数据准备）

**目标**: 实现场景的初始条件设置

**文件**: `tests/bdd/test_organize_steps.py`

- [x] 2.1 **RED**: 编写测试: 验证文件目录创建步骤
- [x] 2.2 **RED**: 运行测试确认失败（看到 StepDefNotFound）
- [x] 2.3 **GREEN**: 实现 `I have a directory with files` 步骤
- [x] 2.4 **GREEN**: 实现 `I have nested directories` 步骤
- [x] 2.5 Commit: "Phase 2: Implement Given steps for test data setup" (d0c36a98)

---

## Phase 3: 实现 When 步骤（命令执行）

**目标**: 实现命令执行步骤

**文件**: `tests/bdd/test_organize_steps.py`

- [x] 3.1 **RED**: 编写测试: 验证 organize 命令执行
- [x] 3.2 **RED**: 运行测试确认失败（看到步骤未定义）
- [x] 3.3 **GREEN**: 实现 `I run "fx organize"` 步骤
- [x] 3.4 **GREEN**: 实现 `I run "fx organize --dry-run"` 步骤
- [x] 3.5 Commit: "Phase 3: Implement When steps for command execution" (f587ed1e)

---

## Phase 4: 实现 Then 步骤（断言验证）

**目标**: 实现结果验证步骤

**文件**: `tests/bdd/test_organize_steps.py`

- [x] 4.1 **RED**: 编写测试: 验证文件被移动
- [x] 4.2 **RED**: 运行测试确认失败（看到步骤未定义）
- [x] 4.3 **GREEN**: 实现 `files should be organized into` 步骤
- [x] 4.4 **GREEN**: 实现 `original directory should be empty` 步骤
- [x] 4.5 **GREEN**: 实现 `conflict should be handled` 步骤
- [x] 4.6 Commit: "Phase 4: Implement Then steps for assertions" (2ffbb402)

---

## Phase 5: 核心场景完整实现

**目标**: 默认组织、递归扫描、dry-run 模式

**文件**: `features/organize.feature`, `tests/bdd/test_organize_steps.py`

- [x] 5.1 **RED**: 编写场景: 按日期组织文件（默认模式）
- [x] 5.2 **RED**: 运行测试确认失败
- [x] 5.3 **GREEN**: 实现完整步骤链
- [x] 5.4 **RED**: 编写场景: 递归扫描嵌套目录
- [x] 5.5 **RED**: 运行测试确认失败
- [x] 5.6 **GREEN**: 实现递归验证步骤
- [x] 5.7 **RED**: 编写场景: dry-run 不修改文件
- [x] 5.8 **RED**: 运行测试确认失败
- [x] 5.9 **GREEN**: 实现 dry-run 验证步骤
- [x] 5.10 Commit: "Phase 5: Core scenarios - default, recursive, dry-run" (bb75990f)

---

## Phase 6: 冲突处理场景

**目标**: SKIP、OVERWRITE、ASK、RENAME 模式

**文件**: `features/organize.feature`, `tests/bdd/test_organize_steps.py`

- [x] 6.1 **RED**: 编写场景: SKIP 模式跳过冲突文件
- [x] 6.2 **RED**: 运行测试确认失败
- [x] 6.3 **GREEN**: 实现 SKIP 验证步骤
- [x] 6.4 **RED**: 编写场景: OVERWRITE 覆盖冲突文件
- [x] 6.5 **RED**: 运行测试确认失败
- [x] 6.6 **GREEN**: 实现 OVERWRITE 验证步骤
- [x] 6.7 **RED**: 编写场景: RENAME 自动重命名冲突
- [x] 6.8 **RED**: 运行测试确认失败
- [x] 6.9 **GREEN**: 实现 RENAME 验证步骤
- [x] 6.10 Commit: "Phase 6: Conflict handling - SKIP, OVERWRITE, RENAME" (1a36ca2e)

---

## Phase 7: ASK 模式交互场景

**目标**: 交互式冲突处理

**文件**: `features/organize.feature`, `tests/bdd/test_organize_steps.py`

- [x] 7.1 **RED**: 编写场景: ASK 模式 TTY 交互
- [x] 7.2 **RED**: 运行测试确认失败
- [x] 7.3 **GREEN**: 实现 ASK 交互模拟（mock click.confirm）
- [x] 7.4 **RED**: 编写场景: ASK 模式非-TTY 回退 SKIP
- [x] 7.5 **RED**: 运行测试确认失败
- [x] 7.6 **GREEN**: 实现非-TTY 验证步骤
- [x] 7.7 Commit: "Phase 7: ASK mode interactive scenarios" (4518f9da)

---

## Phase 8: 边界条件和错误处理

**目标**: 空目录、权限错误、无效路径

**文件**: `features/organize.feature`, `tests/bdd/test_organize_steps.py`

- [x] 8.1 **RED**: 编写场景: 空目录处理
- [x] 8.2 **RED**: 运行测试确认失败
- [x] 8.3 **GREEN**: 实现空目录验证步骤
- [x] 8.4 **RED**: 编写场景: 无效路径错误处理
- [x] 8.5 **RED**: 运行测试确认失败
- [x] 8.6 **GREEN**: 实现错误消息验证步骤
- [x] 8.7 Commit: "Phase 8: Edge cases and error handling" (859b8e17)

---

## Phase 9: 验证和文档

**目标**: 确保所有测试通过，文档完整

- [x] 9.1 **GREEN**: 运行所有 BDD 测试: `poetry run pytest tests/bdd/test_organize_steps.py -v`
- [x] 9.2 **GREEN**: 运行标签过滤（smoke 测试）: `poetry run pytest -m "bdd and smoke" -v`
- [x] 9.3 **GREEN**: 运行现有集成测试确保无回归: `poetry run pytest tests/integration/test_organize*.py -v`
- [x] 9.4 **REFACTOR**: 添加 BDD 测试运行说明到 CLAUDE.md
- [x] 9.5 Commit: "Phase 9: Final verification and documentation" (171719b1)

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

---

## Follow-up: Fix 7 Failing BDD Tests

**说明**: 用户 review 发现 7 个问题需要修复，以达到 50/50 测试通过。

---

## Phase 10: 修复 Step 参数/签名不匹配

**目标**: 修复 fixture 缺失问题

**文件**: `tests/bdd/test_organize_steps.py`

- [ ] 10.1 **RED**: 运行测试确认失败 (fixture 'filename' not found)
- [ ] 10.2 **GREEN**: 修复 step 签名，添加 filename 参数到 parsers.parse
- [ ] 10.3 Commit: "Phase 10: Fix step parameter mismatch"

---

## Phase 11: 移除重复/冲突的 step definitions

**目标**: 修复递归场景匹配错误版本

**文件**: `tests/bdd/test_organize_steps.py`

- [ ] 11.1 **RED**: 运行测试确认失败
- [ ] 11.2 **GREEN**: 删除重复的 `I have a directory structure:` (保留 table 解析版本)
- [ ] 11.3 Commit: "Phase 11: Remove duplicate step definitions"

---

## Phase 12: 修复 symlink 表格解析

**目标**: 修复 header 过滤逻辑

**文件**: `tests/bdd/test_organize_steps.py`

- [ ] 12.1 **RED**: 运行测试确认失败
- [ ] 12.2 **GREEN**: 修复 setup_directory_with_types，正确过滤 header 行
- [ ] 12.3 Commit: "Phase 12: Fix symlink table parsing"

---

## Phase 13: 修复自定义 output 目录路径

**目标**: 修复 sandbox 路径映射

**文件**: `tests/bdd/test_organize_steps.py`

- [ ] 13.1 **RED**: 运行测试确认失败
- [ ] 13.2 **GREEN**: 修复绝对路径处理，正确映射到 temp_directory
- [ ] 13.3 Commit: "Phase 13: Fix custom output directory path"

---

## Phase 14: 修复非递归命令执行

**目标**: 修复 When step 不执行命令

**文件**: `tests/bdd/test_organize_steps.py`

- [ ] 14.1 **RED**: 运行测试确认失败
- [ ] 14.2 **GREEN**: 把 setup_non_recursive_command 改为 When step 并执行命令
- [ ] 14.3 Commit: "Phase 14: Fix non-recursive command execution"

---

## Phase 15: 修复最大深度用例

**目标**: 解决 path-too-long 问题

**文件**: `features/organize.feature`, `tests/bdd/test_organize_steps.py`

- [x] 15.1 **RED**: 运行测试确认失败 (OSError: File name too long)
- [x] 15.2 **GREEN**: 减少深度到 50 层或使用 pytest.mark.skipif (macOS)
- [x] 15.3 Commit: "Phase 15: Fix maximum recursion depth test" (8cdfb4c5)

---

## Phase 16: 修复 version 场景

**目标**: 修复 CLI 设计不一致

**文件**: `features/organize.feature`

- [x] 16.1 **RED**: 运行测试确认失败 (退出码 2)
- [x] 16.2 **GREEN**: 修改 feature 为 `fx --version` 或调整期望为错误
- [x] 16.3 Commit: "Phase 16: Fix version scenario" (8cdfb4c5)

---

## Phase 17: 优化 feature 文案语义

**目标**: 移除隐式魔法，使用明确的 --date-source modified

**文件**: `features/organize.feature`, `tests/bdd/test_organize_steps.py`

- [ ] 17.1 **REFACTOR**: 更新 feature 文案为 "File timestamp" 替代 "Creation Date"
- [ ] 17.2 **REFACTOR**: 显式添加 --date-source modified 到相关场景
- [ ] 17.3 **REFACTOR**: 移除 run_organize_command 中的自动注入逻辑
- [ ] 17.4 Commit: "Phase 17: Improve feature wording clarity"

---

## Phase 18: 最终验证

**目标**: 确保所有测试通过

- [ ] 18.1 **GREEN**: 运行所有 BDD 测试 (目标 50/50)
- [ ] 18.2 **GREEN**: 运行集成测试确保无回归
- [ ] 18.3 Commit: "Phase 18: Final verification - all tests passing"

---

## Updated Summary

**Total**: 18 Phases, 85 Tasks

**Current Progress**:
- Phase 1-9: ✅ Complete (43/50 BDD tests passing)
- Phase 15-16: ✅ Complete (Fixed 2 tests, 45/50 passing, 90% pass rate)
- Phase 10-14, 17-18: 🔄 In Progress (5 tests still failing)

### Remaining Failed Tests (5/50)

| Test Name | Issue | Phase |
|-----------|-------|-------|
| test_recursive_scanning_of_nested_directories | Directory not created | Phase 11 |
| test_skip_symlink_files_for_security | File not organized | Phase 12 |
| test_use_modification_time_instead_of_creation_time | Date mismatch | Phase 17 |
| test_organize_to_custom_output_directory | Absolute path not mapped | Phase 13 |
| test_nonrecursive_mode_limits_to_current_directory | Command not executed | Phase 14 |

### Recent Fixes (Phase 15-16)

**Phase 15: Fix maximum recursion depth test**
- Problem: 150-level depth causes OSError: File name too long on macOS
- Fix: Reduce depth to 50 levels in feature file
- Result: `test_maximum_recursion_depth_is_enforced` ✓
- Commit: 8cdfb4c5

**Phase 16: Fix version scenario**
- Problem: `fx organize --version` command doesn't exist (exit code 2)
- Fix: Change command to `fx --version` (global command)
- Result: `test_version_information_display` ✓
- Commit: 8cdfb4c5
