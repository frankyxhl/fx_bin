# Implementation Tasks (TDD Style)

**Priority**: Phase 1 > Phase 2 > Phase 5 > Phase 3 > Phase 4 > Phase 6

Each task follows RED-GREEN-REFACTOR:
1. **RED**: Write failing test first
2. **GREEN**: Write minimal code to pass
3. **REFACTOR**: Clean up while keeping tests green

---

## Phase 1: Fix RENAME Mode (Critical - 防止数据覆盖)

**目标**: 修复 RENAME 模式对磁盘冲突不重命名的问题

**问题**: 当前 RENAME 模式遇到磁盘已存在的目标文件时，不会重命名而是直接覆盖（通过 shutil.move），与 CLI help 文案 "Auto-rename with _1, _2 suffix" 不符

**注意**: 现有 `resolve_conflict_rename(target_path, allocated_paths)` 用于 intra-run 冲突（纯函数，检查 allocated_paths 集合）。磁盘冲突需要新的 helper 函数来检查文件系统。

**期望行为**:
- 创建新的 `resolve_disk_conflict_rename(target_path)` helper 函数
- RENAME 模式遇到磁盘冲突时，调用新 helper 生成唯一路径
- 不会覆盖现有文件

### 1.1 Create resolve_disk_conflict_rename Helper
- [x] 1.1.1 **RED**: Write test for new helper that adds _1 suffix when file exists on disk
- [x] 1.1.2 **RED**: Write test that helper increments suffix (_2, _3) for multiple existing files
- [x] 1.1.3 **RED**: Write test that helper correctly handles multi-part extensions (.tar.gz → .tar_1.gz)
- [x] 1.1.4 **GREEN**: Implement `resolve_disk_conflict_rename(target_path)` in organize_functional.py
- [x] 1.1.5 **GREEN**: Reuse `get_base_name()` and `get_multi_ext()` from common.py (same as intra-run rename)
- [x] 1.1.6 **GREEN**: Verify tests pass

### 1.2 Integrate Helper into move_file_safe
- [x] 1.2.1 **RED**: Write integration test that RENAME mode uses helper for disk conflicts
- [x] 1.2.2 **RED**: Run test to confirm it fails (currently overwrites)
- [x] 1.2.3 **GREEN**: Update RENAME branch in move_file_safe() to call `resolve_disk_conflict_rename()`
- [x] 1.2.4 **REFACTOR**: Ensure no accidental overwrites
- [x] 1.2.5 **GREEN**: Verify test passes
- [x] 1.2.6 Commit: "Phase 1: Fix RENAME mode to rename on disk conflict"

---

## Phase 2: Implement ASK Mode in CLI Layer

**目标**: 在 CLI 层实现 ASK 模式的交互式 prompt

**问题**: 当前 ASK 模式在 move_file_safe() 中直接等同于 SKIP，但 CLI help 文案说 "Prompt for conflicts"

**决策**: 在 CLI 层实现 click.prompt()（design.md Decision 2）
- move_file_safe() 保持无 UI（低层 IO 函数）
- CLI 层在 execute_organize() 之前处理 ASK 交互
- 非 TTY 场景 fallback 到 SKIP

### 2.1 Implement ASK in CLI Layer
- [x] 2.1.1 **RED**: Write test that ASK mode prompts in CLI layer for disk conflicts
- [x] 2.1.2 **RED**: Write test that ASK falls back to SKIP when stdin is not TTY
- [x] 2.1.3 **GREEN**: Implement prompt logic in CLI layer (before execute_organize)
- [x] 2.1.4 **GREEN**: Remove ASK handling from move_file_safe() (keep as SKIP pass-through)
- [x] 2.1.5 **GREEN**: Verify tests pass
- [x] 2.1.6 Commit: "Phase 2: Implement ASK mode in CLI layer"

---

## Phase 3: Implement OVERWRITE Atomic & EXDEV

**目标**: 使用 os.replace() 实现 atomic overwrite，处理跨盘

**问题**:
- 当前 OVERWRITE 模式使用 shutil.move()，不是 atomic 的
- 没有处理 EXDEV (跨设备) 错误
- 测试中仍有 "atomic overwrite with os.replace" 的 docstring，但实际用的是 RENAME 模式

**期望行为**:
- OVERWRITE 模式使用 os.replace() 实现 atomic 操作
- EXDEV 错误时：copy 到临时文件 → os.replace() → 删除源文件

### 3.1 Implement Atomic Overwrite
- [x] 3.1.1 **RED**: Write test that OVERWRITE uses os.replace() for atomic operation
- [x] 3.1.2 **RED**: Write test that OVERWRITE handles EXDEV (cross-device) error
- [x] 3.1.3 **GREEN**: Implement OVERWRITE branch with os.replace()
- [x] 3.1.4 **GREEN**: Handle EXDEV with copy-to-temp then replace pattern
- [x] 3.1.5 **GREEN**: Update existing test docstrings and assertions to use correct modes
- [x] 3.1.6 **REFACTOR**: Ensure atomic semantics are preserved
- [x] 3.1.7 Commit: "Phase 3: Implement atomic OVERWRITE with EXDEV handling"

---

## Phase 4: Fix --quiet Behavior

**目标**: 确保 --quiet 始终输出 summary

**问题**: CLI help 说 "errors and summary only"，但当前 --quiet 无错误时不输出 summary

**期望行为**:
- --quiet 模式始终输出 summary（无论是否有错误）

### 4.1 Fix Quiet Summary Output
- [x] 4.1.1 **RED**: Write test that --quiet outputs summary even with no errors
- [x] 4.1.2 **GREEN**: Fix CLI output logic (remove `or summary.errors > 0` condition)
- [x] 4.1.3 **GREEN**: Verify test passes
- [ ] 4.1.4 Commit: "Phase 4: Fix --quiet to always show summary"

---

## Phase 5: Fix Cross-Device ValueError

**目标**: _should_skip_entry 捕获 ValueError

**问题**: _should_skip_entry() 直接调用 os.path.commonpath()，未捕获 ValueError。当 output_dir 在不同盘符时会崩溃。

**期望行为**:
- 捕获 ValueError，返回 False（不跳过）

### 5.1 Handle ValueError in _should_skip_entry
- [x] 5.1.1 **RED**: Write test that cross-device output_dir doesn't crash
- [x] 5.1.2 **GREEN**: Wrap os.path.commonpath() in try-except ValueError
- [x] 5.1.3 **GREEN**: Return False on ValueError (don't skip)
- [x] 5.1.4 **GREEN**: Verify test passes
- [x] 5.1.5 Commit: "Phase 5: Handle ValueError for cross-device paths"

---

## Phase 6: Verification & Documentation

**目标**: 验证所有修复并更新文档

### 6.1 Automated Testing
- [x] 6.1.1 Run all tests: `poetry run pytest tests/ -v`
- [x] 6.1.2 Verify all tests pass (551 tests passed)
- [x] 6.1.3 Run flake8: `poetry run flake8 fx_bin/`
- [x] 6.1.4 Run black: `poetry run black fx_bin/ tests/`
- [x] 6.1.5 Run mypy: `poetry run mypy fx_bin/`
- [x] 6.1.6 Run bandit: `poetry run bandit -r fx_bin/`

### 6.2 Coverage Check
- [x] 6.2.1 Run coverage: `poetry run pytest --cov=fx_bin --cov-report=term-missing`
- [x] 6.2.2 Verify coverage ≥ 80% (Coverage meets 80% threshold)

### 6.3 Documentation Update
- [x] 6.3.1 Update help text in cli.py to match implementation (already accurate)
- [x] 6.3.2 Update openspec/specs/organize/spec.md with corrected behavior (already accurate)

### 6.4 Manual Testing
- [x] 6.4.1 Test RENAME mode with actual disk conflicts (verified: test1_1.txt created)
- [x] 6.4.2 Test OVERWRITE mode with atomic replace (verified: file overwritten atomically)
- [x] 6.4.3 Test --quiet output behavior (verified: summary always shown)
- [x] 6.4.4 Test cross-device output directory (verified: no crash on unrelated paths)

### 6.5 Final Commit
- [x] 6.5.1 Commit: "Phase 6: Verification and documentation updates"
