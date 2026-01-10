# Implementation Tasks (TDD Style)

**Priority**: Phase 1 > Phase 2 > Phase 4 > Phase 3 > Phase 5

Each task follows RED-GREEN-REFACTOR:
1. **RED**: Write failing test first
2. **GREEN**: Write minimal code to pass
3. **REFACTOR**: Clean up while keeping tests green

---

## Phase 1: Fix File Descriptor Leak

**目标**: 修复 tempfile.mkstemp() 的 FD 泄漏

**问题**: tempfile.mkstemp() 返回的 fd 没有关闭，可能导致：
- 文件描述符耗尽（长期运行）
- 临时文件无法被覆盖/删除（某些平台）

**位置**: fx_bin/organize_functional.py:423 和 475

### 1.1 Fix FD Leak in EXDEV Handling

- [x] 1.1.1 **RED**: Write test that fd is closed after EXDEV handling
- [x] 1.1.2 **RED**: Run test to confirm fd is leaked (current state)
- [x] 1.1.3 **GREEN**: Add os.close(fd) after tempfile.mkstemp() in first EXDEV block
- [x] 1.1.4 **GREEN**: Add os.close(fd) after tempfile.mkstemp() in second EXDEV block
- [x] 1.1.5 **GREEN**: Verify tests pass
- [x] 1.1.6 Commit: "Phase 1: Fix file descriptor leak in EXDEV handling"

---

## Phase 2: Fix --yes with --quiet

**目标**: --yes 分支尊重 --quiet 标志

**问题**: fx_bin/cli.py:784 --yes 分支输出 "Organizing files..."，违反 --quiet 的 "errors and summary only" 语义

### 2.1 Add Quiet Check to --yes Branch

- [x] 2.1.1 **RED**: Write test that --yes + --quiet doesn't output extra info
- [x] 2.1.2 **RED**: Run test to confirm "Organizing files..." is printed
- [x] 2.1.3 **GREEN**: Add quiet check to --yes branch (only print if not quiet)
- [x] 2.1.4 **GREEN**: Verify test passes
- [x] 2.1.5 Commit: "Phase 2: Fix --yes to respect --quiet flag"

---

## Phase 3: Configure loguru and Document ASK Runtime Conflicts

**目标**: 配置 loguru 遵守 --quiet/--verbose，并文档 ASK 运行时冲突行为

**问题**:
- loguru 默认不遵守 --quiet（需要显式配置）
- fx_bin/cli.py:895 ASK 模式只在扫描阶段检测磁盘冲突。运行时新出现的冲突（TOCTOU）会被 move_file_safe() 视为 skip

**决策**:
1. 在 organize() 入口根据 quiet/verbose 配置 loguru level
2. 固定选 B - 文档 ASK 只处理扫描时冲突，运行时冲突 skip 并记录警告日志

**实现说明**:
- quiet=ERROR: 只显示 ERROR 及以上（WARNING 不输出）
- verbose=DEBUG: 显示 DEBUG 及以上（WARNING 会输出）
- 使用 loguru.logger.warning() 记录警告（level 由入口配置控制）

### 3.1 Configure loguru in organize() Entry Point

- [x] 3.1.1 **RED**: Write test that --quiet suppresses WARNING output
- [x] 3.1.2 **RED**: Write test that --verbose shows WARNING output
- [x] 3.1.3 **GREEN**: In organize() entry, configure loguru level based on quiet/verbose
- [x] 3.1.4 **GREEN**: Use logger.remove() and logger.add() with level filter
- [x] 3.1.5 **GREEN**: Verify tests pass with CliRunner(mix_stderr=False)

### 3.2 Document ASK Runtime Behavior with Warning Log

- [x] 3.2.1 **RED**: Write test that runtime conflict skips with loguru warning
- [x] 3.2.2 **RED**: Write test that warning respects loguru configuration
- [x] 3.2.3 **GREEN**: Add logger.warning() for runtime conflicts in move_file_safe()
- [x] 3.2.4 **GREEN**: Update CLI help text to clarify scan-time vs runtime behavior
- [x] 3.2.5 **GREEN**: Verify tests pass
- [x] 3.2.6 Commit: "Phase 3: Configure loguru and document ASK runtime conflicts"

---

## Phase 4: Fix Directory Creation Path

**目标**: 使用 real_target 而非 target 创建目录

**问题**: fx_bin/organize_functional.py:453 使用 `os.path.dirname(target)` 而不是 `os.path.dirname(real_target)`

**影响**: 存在符号链接或相对路径时，"实际写入路径"和"创建目录路径"的语义可能不一致

**测试用例**: target 包含 `..` 时会暴露问题
- **用例**: `output/subdir/../file.txt`（安全，在 output_root 内）
- 旧代码断言: 创建了 `output/subdir/` 目录
- 新代码断言: 只创建 `output/` 目录（正确位置）
- 旧代码: `os.path.dirname(target)` = `"output/subdir/.."` （多创建 output/subdir）
- 新代码: `os.path.dirname(real_target)` = `"output"` （正确的 output 目录）

### 4.1 Use real_target for Directory Creation

- [x] 4.1.1 **RED**: Write test that target with .. creates directory at real_target location
- [x] 4.1.2 **RED**: Run test to confirm current uses target (wrong directory created)
- [x] 4.1.3 **GREEN**: Change to os.path.dirname(real_target)
- [x] 4.1.4 **GREEN**: Verify test passes
- [x] 4.1.5 Commit: "Phase 4: Fix directory creation to use real_target"

---

## Phase 5: Verification

**目标**: 验证所有修复

### 5.1 Automated Testing

- [x] 5.1.1 Run all tests: `poetry run pytest tests/ -v`
- [x] 5.1.2 Verify all tests pass
- [x] 5.1.3 Run flake8: `poetry run flake8 fx_bin/`
- [x] 5.1.4 Run black: `poetry run black fx_bin/ tests/`
- [x] 5.1.5 Run mypy: `poetry run mypy fx_bin/`
- [x] 5.1.6 Run bandit: `poetry run bandit -r fx_bin/`

### 5.2 Coverage Check

- [x] 5.2.1 Run coverage: `poetry run pytest --cov=fx_bin --cov-report=term-missing`
- [x] 5.2.2 Verify coverage ≥ 80% (organize_functional.py: 80%)

### 5.3 Manual Testing

- [x] 5.3.1 Test --yes + --quiet output
- [x] 5.3.2 Test ASK mode with runtime conflicts
- [x] 5.3.3 Test directory creation with symlinks

### 5.4 Documentation Update

- [x] 5.4.1 Update help text in cli.py (if ASK behavior changed)
- [x] 5.4.2 Update openspec/specs/organize/spec.md (if needed)

### 5.5 Final Commit

- [x] 5.5.1 Commit: "Phase 5: Verification and documentation"
