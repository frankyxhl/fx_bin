---
id: 20250823_011019_refactor_test-structure-reorganization
type: refactor
title: Reorganize test files and structure according to Python best practices
slug: test-structure-reorganization
created_at: 2025-08-23T01:10:19+09:00
owner: frank
priority: P2
estimate: 6h
issue: -
branch: refactor/test-structure-reorganization
status: planned
---

# Rule
## When you work this plan, update the last status, e.g., ✅ COMPLETED when each task is done.

# refactor: Reorganize test files and structure according to Python best practices

## Description
- Background: The fx_bin project has scattered test-related files with Chinese names and a non-standard virtual environment structure that needs reorganization
- Goal: Establish Python best practices for testing with proper file organization, English naming, and standard conventions
- Scope: File system reorganization, documentation updates, and virtual environment standardization
- Out of scope: Modifying test logic or functionality (tests should remain functional)

## Acceptance Criteria
- [ ] All Chinese-named files renamed to English equivalents
- [ ] All test-related files properly organized under tests/ directory
- [ ] Virtual environment renamed from "test_env" to ".venv" per Python conventions
- [ ] All file references updated in documentation and scripts
- [ ] Test suite remains fully functional after reorganization
- [ ] Documentation reflects new structure and naming conventions

---

## Phase 1 — Plan / Scope
- [ ] Associated Issue: -
- [ ] In scope: File renaming, directory reorganization, documentation updates, virtual environment restructuring
- [ ] Out of scope: Changing test logic, adding new tests, modifying core functionality
- [ ] Risks: Test scripts may break if file paths not updated properly; virtual environment recreation may require dependency reinstallation
- [ ] Create branch: `refactor/test-structure-reorganization`

## Phase 2 — Design
- [ ] File mapping strategy: Chinese → English equivalent names
- [ ] Directory structure: Consolidate all test runners under tests/runners/
- [ ] Virtual environment: Replace test_env with .venv standard
- [ ] Documentation updates: Update all references to new file paths and structure

## Phase 3 — Implement
- [ ] Rename Chinese files to English equivalents:
  - `简单测试运行.py` → `tests/runners/simple_test_runner.py`
  - `测试运行指南.md` → `docs/testing/testing_guide.md`
  - `运行测试-最终指南.md` → `docs/testing/final_testing_guide.md`
- [ ] Reorganize scattered test files:
  - `run_simple_tests.py` → `tests/runners/run_simple_tests.py`
  - `run_tdd_tests.py` → `tests/runners/run_tdd_tests.py`
  - `TDD_IMPLEMENTATION_SUMMARY.md` → `docs/testing/tdd_implementation_summary.md`
- [ ] Create proper directory structure:
  - `tests/runners/` for test execution scripts
  - `docs/testing/` for test-related documentation
- [ ] Update virtual environment:
  - Remove `test_env/` directory
  - Create `.venv/` directory with same dependencies
- [ ] Update file references in all scripts and documentation

## Phase 4 — Test
- [ ] Verify all test runners work with new file paths
- [ ] Confirm test discovery still functions correctly
- [ ] Validate all documentation links are working
- [ ] Test virtual environment activation and dependency installation
- [ ] Run full test suite to ensure functionality preserved

## Phase 5 — Docs
- [ ] Update CLAUDE.md with new test structure
- [ ] Update README/CHANGELOG if applicable
- [ ] Update testing documentation with new file paths
- [ ] Add note about virtual environment convention change

## Phase 6 — Review & Merge
- [ ] PR description contains file mapping and rationale
- [ ] All file moves properly tracked in git
- [ ] No broken references in codebase
- [ ] Test suite passes with new structure

## Phase 7 — Release
- [ ] Verify new structure in development environment
- [ ] Update any CI/CD configurations if needed
- [ ] Confirm all team members aware of new structure

## Phase 8 — Post-Release
- [ ] Monitor for any missed file references
- [ ] Update any external documentation that references old structure
- [ ] Mark status as `completed`

---

## Detailed File Mapping

### Files to Rename and Move

#### Chinese-named Files → English Equivalents
1. **`简单测试运行.py`** → **`tests/runners/simple_test_runner.py`**
   - Purpose: Simple test runner without Poetry dependencies
   - Contains manual functionality and security tests
   - Chinese comments should be translated to English

2. **`测试运行指南.md`** → **`docs/testing/testing_guide.md`**
   - Purpose: Comprehensive testing guide with multiple approaches
   - Contains setup instructions and troubleshooting
   - All Chinese content should be translated to English

3. **`运行测试-最终指南.md`** → **`docs/testing/final_testing_guide.md`**
   - Purpose: Final testing guide with success metrics
   - Contains validated testing approaches and TDD results
   - All Chinese content should be translated to English

#### Root-level Test Files → Organized Structure
4. **`run_simple_tests.py`** → **`tests/runners/run_simple_tests.py`**
   - Purpose: Simplified test runner without Poetry
   - Currently in root, should be in tests/runners/

5. **`run_tdd_tests.py`** → **`tests/runners/run_tdd_tests.py`**
   - Purpose: TDD-focused test runner with priority ordering
   - Currently in root, should be in tests/runners/

6. **`TDD_IMPLEMENTATION_SUMMARY.md`** → **`docs/testing/tdd_implementation_summary.md`**
   - Purpose: Comprehensive TDD implementation documentation
   - Currently in root, should be in docs/testing/

### Virtual Environment Restructuring
7. **`test_env/`** → **`.venv/`**
   - Current non-standard name should follow Python convention
   - Contains project dependencies for testing
   - Should be recreated rather than renamed to ensure clean state

### Directory Structure After Reorganization

```
fx_bin/
├── .venv/                          # Standard Python virtual environment
├── docs/
│   ├── changelog/
│   └── testing/                    # NEW: Testing documentation
│       ├── testing_guide.md        # Translated from 测试运行指南.md
│       ├── final_testing_guide.md  # Translated from 运行测试-最终指南.md
│       └── tdd_implementation_summary.md # Moved from root
├── fx_bin/                         # Main package (unchanged)
├── tests/
│   ├── runners/                    # NEW: Test execution scripts
│   │   ├── __init__.py             # NEW: Make it a package
│   │   ├── simple_test_runner.py   # Translated from 简单测试运行.py
│   │   ├── run_simple_tests.py     # Moved from root
│   │   └── run_tdd_tests.py        # Moved from root
│   ├── __init__.py                 # Existing
│   ├── test_*.py                   # Existing test files (unchanged)
│   └── ...
└── pyproject.toml                  # Existing (unchanged)
```

### Files to Update with New References

#### Documentation Files
- **`CLAUDE.md`**: Update testing commands to use new paths
- **`docs/testing/testing_guide.md`**: Update internal references and translate content
- **`docs/testing/final_testing_guide.md`**: Update internal references and translate content

#### Test Runner Scripts
- **`tests/runners/simple_test_runner.py`**: Update any hardcoded paths, translate comments
- **`tests/runners/run_simple_tests.py`**: Update any hardcoded paths
- **`tests/runners/run_tdd_tests.py`**: Update any hardcoded paths

#### Configuration Files
- **`pyproject.toml`**: Update any references to old virtual environment name
- **`tox.ini`**: Update any references to old paths or virtual environment

---

## Translation Requirements

### Chinese → English Content Translation

#### File Content Translation Priorities
1. **High Priority**: Function/variable names, comments in code files
2. **Medium Priority**: Documentation headers and section titles
3. **Low Priority**: Example output text (can remain Chinese if it's just examples)

#### Key Translation Mappings
- `简单测试运行` → `Simple Test Runner`
- `测试运行指南` → `Testing Guide`
- `运行测试-最终指南` → `Final Testing Guide`
- `基本功能测试` → `Basic Functionality Tests`
- `安全功能测试` → `Security Functionality Tests`
- `文件替换` → `File Replacement`
- `目录扫描` → `Directory Scanning`

---

## Rollback Plan
- Trigger condition: Test suite fails after reorganization or critical file references break
- Operation: Restore files to original locations using git, recreate test_env if needed
- Data: No data migration needed, only file location changes
- Validation: Test suite passes and all documentation references work

## Metrics & Alerts
- Metrics: Test suite pass rate, file reference validation, documentation link checks
- Dashboard: Local testing results, file organization compliance
- Alerts: Any broken imports or file not found errors during testing

## References
- Python Testing Best Practices: https://docs.python-guide.org/writing/tests/
- Virtual Environment Conventions: https://docs.python.org/3/tutorial/venv.html
- Project file organization: PEP 518, PEP 621