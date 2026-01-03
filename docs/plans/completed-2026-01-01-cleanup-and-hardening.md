# fx-bin 清理与强化计划

> **Status:** Completed  
> **Completed:** 2026-01-03

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 移除 pandas/json2excel 依赖，修复 Oracle 审查发现的问题，强化 CI/CD 和文档

**Architecture:** 分四阶段执行 - 依赖精简 → 代码修复 → CI 强化 → 文档同步

**Tech Stack:** Python 3.12, Poetry, GitHub Actions, pytest

---

## Agent → Model 映射

| Agent | Model |
|-------|-------|
| `oracle` | `openai/gpt-5.2-high` |
| `explore` | `google/gemini-3-flash` |
| `librarian` | `google/gemini-3-flash` |
| `coder` | `google/gemini-3-flash` |
| `document-writer` | `google/gemini-3-flash` |

---

## 工作流表格

| 阶段 | Skill | Agent | Model | Context | 说明 |
|------|-------|-------|-------|---------|------|
| 1. 移除 pandas | `superpowers:test-driven-development` | `coder` | `google/gemini-3-flash` | 独立上下文 | 删除文件、更新配置 |
| 2. 代码修复 | `superpowers:test-driven-development` | `coder` | `google/gemini-3-flash` | 独立上下文 | 修复版本号、错误处理 |
| 3. CI 强化 | `superpowers:test-driven-development` | `coder` | `google/gemini-3-flash` | 独立上下文 | 移除 `|| true`，添加验证 |
| 4. 文档同步 | - | `document-writer` | `google/gemini-3-flash` | 独立上下文 | README/CHANGELOG 更新 |
| 5a. Code Review A | `superpowers:requesting-code-review` | `oracle` | `openai/gpt-5.2-high` | 独立上下文 | **并行** GPT-5.2 审查 |
| 5b. Code Review B | `superpowers:requesting-code-review` | Task (Opus) | `anthropic/claude-opus-4` | 独立上下文 | **并行** Opus 4 审查 |
| 5c. 汇总与交付 | `superpowers:verification-before-completion` | 主会话 | 主会话模型 | 同一上下文 | 汇总 review、提交 PR |

---

## Phase 1: 移除 pandas/json2excel

### Task 1.1: 删除 pd 模块文件

**Files:**
- Delete: `fx_bin/pd.py`
- Delete: `fx_bin/pd_functional.py`

**Step 1: 删除文件**
```bash
rm fx_bin/pd.py fx_bin/pd_functional.py
```

**Step 2: 验证删除**
```bash
ls fx_bin/pd*.py  # 应该报错 "No such file"
```

---

### Task 1.2: 删除相关测试文件

**Files:**
- Delete: `tests/functional/test_pd_functional_complete.py`
- Delete: `tests/security/test_pd_safety.py`

**Step 1: 删除测试文件**
```bash
rm tests/functional/test_pd_functional_complete.py
rm tests/security/test_pd_safety.py
```

**Step 2: 验证删除**
```bash
ls tests/functional/test_pd*.py tests/security/test_pd*.py  # 应该报错
```

---

### Task 1.3: 从 CLI 移除 json2excel 命令

**Files:**
- Modify: `fx_bin/cli.py`

**Step 1: 移除 COMMANDS_INFO 中的 json2excel**

找到并删除:
```python
("json2excel", "Convert JSON to Excel"),
```

**Step 2: 移除 json2excel 命令函数**

删除整个函数 (约 L340-L350):
```python
@cli.command()
@click.argument("url")
@click.argument("output_filename")
def json2excel(url, output_filename):
    ...
```

**Step 3: 运行测试验证**
```bash
poetry run pytest tests/integration/test_cli.py -v --no-cov -k "not json2excel"
```

---

### Task 1.4: 移除 json2excel 相关测试

**Files:**
- Modify: `tests/integration/test_cli.py`

**Step 1: 删除 TestJson2ExcelCommand 类**

删除整个测试类 (搜索 `class TestJson2ExcelCommand`)

**Step 2: 运行测试验证**
```bash
poetry run pytest tests/integration/test_cli.py -v --no-cov
```

---

### Task 1.5: 清理 pyproject.toml 依赖

**Files:**
- Modify: `pyproject.toml`

**Step 1: 移除 pandas optional dependency**

删除:
```toml
pandas = {version = "^2.0.0", optional = true}
```

**Step 2: 移除 excel extras**

删除:
```toml
excel = ["pandas"]
```

**Step 3: 从 dev dependencies 移除 pandas 和 openpyxl**

删除:
```toml
pandas = "^2.2.0"
openpyxl = "^3.1.2"
```

**Step 4: 更新 lock 文件**
```bash
poetry lock --no-update
poetry install
```

**Step 5: 验证安装**
```bash
poetry run fx list  # 不应显示 json2excel
poetry run fx --help
```

---

### Task 1.6: 清理 errors.py

**Files:**
- Modify: `fx_bin/errors.py`

**Step 1: 移除 PdError 类**

删除:
```python
class PdError(FxBinError):
    """Errors in pandas/Excel operations."""
    pass
```

**Step 2: 运行测试**
```bash
poetry run pytest tests/ -v --no-cov -q
```

---

### Task 1.7: 提交 Phase 1

```bash
git add -A
git commit -m "refactor: remove pandas/json2excel command

- Remove pd.py and pd_functional.py modules
- Remove json2excel CLI command
- Remove related tests
- Remove pandas/openpyxl from dependencies
- Simplify project by ~500 lines of code"
```

---

## Phase 2: 代码修复

### Task 2.1: 修复 __version__ fallback

**Files:**
- Modify: `fx_bin/__init__.py`

**Step 1: 更新 fallback 版本**

将:
```python
__version__ = "0.9.4"
```

改为:
```python
__version__ = "1.5.0"
```

**Step 2: 验证**
```bash
poetry run python -c "import fx_bin; print(fx_bin.__version__)"
```

---

### Task 2.2: 改进 replace.py 二进制文件检测

**Files:**
- Modify: `fx_bin/replace.py`
- Create: `tests/unit/test_replace_binary.py`

**Step 1: 添加二进制文件检测函数**

在 `replace.py` 顶部添加:
```python
def _is_binary_file(file_path: Path, sample_size: int = 8192) -> bool:
    """Check if a file appears to be binary by looking for null bytes."""
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(sample_size)
            return b"\x00" in chunk
    except (OSError, IOError):
        return True  # Treat unreadable files as binary (skip them)
```

**Step 2: 在替换逻辑中使用**

在 `replace_in_file` 函数开头添加检查:
```python
if _is_binary_file(file_path):
    return 0  # Skip binary files
```

**Step 3: 添加测试**
```python
# tests/unit/test_replace_binary.py
def test_skip_binary_files(tmp_path):
    """Test that binary files are skipped."""
    binary_file = tmp_path / "test.bin"
    binary_file.write_bytes(b"\x00\x01\x02\x03")
    
    from fx_bin.replace import replace_in_file
    result = replace_in_file(binary_file, "test", "replaced")
    assert result == 0  # No replacements in binary
```

**Step 4: 运行测试**
```bash
poetry run pytest tests/unit/test_replace.py tests/unit/test_replace_binary.py -v --no-cov
```

---

### Task 2.3: 提交 Phase 2

```bash
git add -A
git commit -m "fix: improve code quality

- Update __version__ fallback to match current version
- Add binary file detection to replace command
- Skip binary files to prevent corruption"
```

---

## Phase 3: CI 强化

### Task 3.1: 移除安全扫描的 || true

**Files:**
- Modify: `.github/workflows/tdd-test.yml`

**Step 1: 修改 Bandit 步骤**

将:
```yaml
poetry run bandit -r fx_bin/ -f json -o bandit-report.json || true
poetry run bandit -r fx_bin/ || true
```

改为:
```yaml
poetry run bandit -r fx_bin/ -f json -o bandit-report.json
poetry run bandit -r fx_bin/
```

**Step 2: 修改 Safety 步骤**

将:
```yaml
poetry run safety check --json --output safety-report.json || true
poetry run safety check || true
```

改为:
```yaml
poetry run safety check --json --output safety-report.json || echo "::warning::Safety check found issues"
poetry run safety check || echo "::warning::Safety check found issues"
```

(Safety 可能因网络问题失败，保留 warning 但不 fail)

---

### Task 3.2: 强制 MyPy 检查

**Files:**
- Modify: `.github/workflows/tdd-test.yml`

**Step 1: 移除 continue-on-error**

将:
```yaml
- name: Run MyPy
  continue-on-error: true
  run: |
    echo "🔍 Running MyPy type checking..."
    poetry run mypy fx_bin/ || true
```

改为:
```yaml
- name: Run MyPy
  run: |
    echo "🔍 Running MyPy type checking..."
    poetry run mypy fx_bin/ --ignore-missing-imports
```

---

### Task 3.3: 在 Deploy 前添加质量门

**Files:**
- Modify: `.github/workflows/main.yml`

**Step 1: 添加测试步骤 (在 build 之前)**

在 `Install dependencies and build` 步骤之前添加:
```yaml
    - name: Run tests before deploy
      if: steps.pypi_check.outputs.version_exists == 'false'
      run: |
        echo "🧪 Running tests before deployment..."
        poetry run pytest tests/ -v --no-cov -q
        echo "✅ All tests passed"
    
    - name: Run lint checks
      if: steps.pypi_check.outputs.version_exists == 'false'
      run: |
        echo "🔍 Running lint checks..."
        poetry run flake8 fx_bin/
        echo "✅ Lint passed"
```

---

### Task 3.4: 合并 pytest 配置

**Files:**
- Modify: `pyproject.toml`
- Delete: `pytest-bdd.ini`

**Step 1: 合并 pytest-bdd.ini 内容到 pyproject.toml**

在 `[tool.pytest.ini_options]` 中确保包含:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
markers = [
    "security: Security-related tests",
    "integration: Integration tests",
    "performance: Performance tests",
    "slow: Slow tests",
    "bdd: BDD tests"
]
bdd_features_base_dir = "features"
```

**Step 2: 删除 pytest-bdd.ini**
```bash
rm pytest-bdd.ini
```

**Step 3: 验证**
```bash
poetry run pytest tests/ -v --no-cov -q
```

---

### Task 3.5: 提交 Phase 3

```bash
git add -A
git commit -m "ci: strengthen CI/CD pipeline

- Remove || true from security scans (Bandit)
- Enforce MyPy type checking
- Add test/lint gates before PyPI deployment
- Consolidate pytest configuration"
```

---

## Phase 4: 文档同步

### Task 4.1: 更新 README.md

**Files:**
- Modify: `README.md`

**Changes needed:**

1. **移除 json2excel 相关内容**
   - 从命令表格移除
   - 删除 json2excel 使用示例
   - 删除 Data Processing 相关段落

2. **修复 fx ff 文档**
   - 移除 PATH 参数 (实际只接受 keyword)
   - 示例改为: `fx ff TODO` (不是 `fx ff . TODO`)

3. **修复 fx filter 文档**
   - 移除 `--format count` (不存在)
   - 只保留 `simple` 和 `detailed`

4. **修复 fx replace 文档**
   - 移除 `--preview`, `--backup`, `--interactive` (不存在)
   - 更新为实际支持的选项

5. **添加 fx fff 命令** (v1.5.0 新增)
   - 添加到命令表格
   - 添加使用示例

6. **修正覆盖率数字**
   - 改为实际数字 (~83%)

---

### Task 4.2: 更新 CHANGELOG.md

**Files:**
- Modify: `CHANGELOG.md`

**Step 1: 添加 v1.5.0 条目**

```markdown
## [1.5.0] - 2026-01-01

### Added
- `fx ff --first` option to return only the first match
- `fx fff` command as alias for `fx ff --first`

### Removed
- `fx json2excel` command (simplification - pandas dependency removed)
- pandas and openpyxl dependencies

### Fixed
- Binary file detection in `fx replace` command
- `__version__` fallback now matches current version

### Changed
- CI pipeline now enforces security scans and type checking
- Consolidated pytest configuration
```

---

### Task 4.3: 提交 Phase 4

```bash
git add -A
git commit -m "docs: sync documentation with implementation

- Remove json2excel from README
- Fix fx ff examples (no PATH argument)
- Fix fx filter format options
- Fix fx replace options
- Add fx fff command documentation
- Update CHANGELOG for v1.5.0"
```

---

## Phase 5: 最终验证与双模型 Code Review

### Task 5.1: 运行全量测试

```bash
make check  # lint + format + type + security
make test   # 全量测试
```

### Task 5.2: 验证 CLI

```bash
poetry run fx list
poetry run fx --help
poetry run fx ff --help
poetry run fx fff --help
poetry run fx filter --help
poetry run fx replace --help
```

### Task 5.3: 验证版本

```bash
poetry version  # 应显示 1.5.0
poetry run python -c "import fx_bin; print(fx_bin.__version__)"
```

---

### Task 5.4: 并行双模型 Code Review

**策略**: 同时派发两个独立的 code review 任务，汇总结果

| Reviewer | Agent | Model | Context |
|----------|-------|-------|---------|
| Reviewer A | `oracle` | `openai/gpt-5.2-high` | 独立上下文 |
| Reviewer B | 主会话 Task | `anthropic/claude-sonnet-4` 或 `opus-4` | 独立上下文 |

**Step 1: 并行派发 Code Review**

使用 `background_task` 同时启动两个 review:

```
# Reviewer A: Oracle (GPT-5.2)
background_task(
  agent="oracle",
  prompt="Review all changes in this PR for fx-bin cleanup:
    1. Code quality issues
    2. Security concerns  
    3. Missing edge cases
    4. Documentation accuracy
    Files changed: fx_bin/*.py, tests/, .github/workflows/, README.md, CHANGELOG.md
    Return structured findings: Critical/Warning/Suggestion"
)

# Reviewer B: Claude Opus 4.5 (通过 Task tool)
task(
  subagent_type="coder",  # 或配置专门的 review agent
  prompt="Review all changes in this PR for fx-bin cleanup:
    1. Code quality issues
    2. Security concerns
    3. Missing edge cases
    4. Documentation accuracy
    Files changed: fx_bin/*.py, tests/, .github/workflows/, README.md, CHANGELOG.md
    Return structured findings: Critical/Warning/Suggestion"
)
```

**Step 2: 收集并汇总结果**

等待两个 review 完成后，汇总成统一报告:

```markdown
## Code Review Summary

### 🔴 Critical (两者都发现)
- [issue]

### 🟡 Warning
- [Oracle 发现]: ...
- [Opus 发现]: ...

### 🟢 Suggestions
- [Oracle 建议]: ...
- [Opus 建议]: ...

### ✅ Consensus (两者一致认可)
- [good practice]
```

**Step 3: 处理 Review 结果**

- Critical issues: 必须修复后再提交
- Warnings: 评估后决定是否修复
- Suggestions: 记录到后续改进计划

---

### Task 5.5: 创建 PR

```bash
git push -u origin cleanup/remove-pandas-and-harden
gh pr create --title "refactor: remove pandas, strengthen CI, sync docs" --body "$(cat <<'EOF'
## Summary
- Remove pandas/json2excel command (~500 lines removed)
- Strengthen CI pipeline (enforce security scans, type checking)
- Sync documentation with actual implementation
- Add binary file detection to replace command

## Changes
- **Removed**: `fx json2excel`, pandas, openpyxl dependencies
- **Fixed**: README examples, CHANGELOG, __version__ fallback
- **Improved**: CI gates, pytest config consolidation
- **Added**: Binary file skip in replace command

## Testing
- All tests pass
- `make check` passes
- CLI commands verified

## Code Review
- ✅ Reviewed by Oracle (GPT-5.2-high)
- ✅ Reviewed by Claude Opus 4.5
- See review summary in PR comments
EOF
)"
```

---

## 预估时间

| Phase | 预估时间 |
|-------|----------|
| Phase 1: 移除 pandas | 30 min |
| Phase 2: 代码修复 | 20 min |
| Phase 3: CI 强化 | 30 min |
| Phase 4: 文档同步 | 40 min |
| Phase 5: 验证与双模型 Review | 30 min |
| **Total** | **~2.5 hours** |

---

## Agent → Model 映射 (完整版)

| Agent | Model | 用途 |
|-------|-------|------|
| `oracle` | `openai/gpt-5.2-high` | 架构决策、Code Review A |
| `explore` | `google/gemini-3-flash` | 代码搜索 |
| `librarian` | `google/gemini-3-flash` | 文档查找 |
| `coder` | `google/gemini-3-flash` | TDD 实现 |
| `document-writer` | `google/gemini-3-flash` | 文档更新 |
| 主会话 Task (Opus) | `anthropic/claude-opus-4` | Code Review B |
