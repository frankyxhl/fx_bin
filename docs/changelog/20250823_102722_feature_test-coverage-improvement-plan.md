---
id: 20250823_102722_feature_test-coverage-improvement-plan
type: feature
title: Comprehensive Test Coverage Improvement from 55% to 80%+
slug: test-coverage-improvement-plan
created_at: 2025-08-23T10:27:22+09:00
owner: frank
priority: P1
estimate: 3d
issue: -
branch: feature/test-coverage-improvement-plan
status: planned
---

# Rule
## When you work this plan, update the last status, e.g., ✅ COMPLETED when each task is done.

# feature: Comprehensive Test Coverage Improvement from 55% to 80%+

## Description (任务描述 / Description)
- Background / 背景：Currently at 55% test coverage (564/1030 statements), need to reach 80%+ for CI/CD requirements
- Goal / 目标：Increase test coverage from 55% to 80%+ (≥824 statements covered) by adding ~260 covered statements
- Scope / 影响范围：All fx_bin modules, focusing on untested and under-tested components
- Non-goals / 非目标：Coverage gaming without meaningful tests, breaking existing functionality

## Acceptance Criteria（验收标准）
- [ ] Total test coverage ≥ 80% (≥824 statements covered)
- [ ] All modules with 0% coverage have meaningful tests
- [ ] Upload server coverage improved from 26% to ≥70%
- [ ] All functional modules have ≥70% coverage
- [ ] New tests include both success and failure paths
- [ ] All tests pass consistently in CI/CD pipeline
- [ ] Test execution time remains under 30 seconds

---

## Phase 1 — Plan / Scope（规划）
- [ ] Associated Issue: -
- [ ] In scope: lib.py (0%), run_upgrade_program.py (0%), upload_server.py (26%), functional modules (46-51%)
- [ ] Out of scope: Modules already at 80%+ coverage, performance optimization tests
- [ ] Risks & Mitigations: Complex functional code testing → Use mocking and returns library test patterns
- [ ] Create branch: `feature/test-coverage-improvement-plan`

## Phase 2 — Design（设计）
- [ ] Test Architecture: Separate test files for each uncovered module
- [ ] Security & Privacy: Maintain security test coverage, no real file system modifications in tests
- [ ] Performance Budget: Test suite should complete in <30s, use mocks for I/O operations
- [ ] Rollback Strategy: Each test file independent, can disable problematic tests individually

## Phase 3 — Implement（实现）

### Phase 3A — Zero Coverage Modules (Priority 1, +36 statements)
- [ ] **test_lib.py** - New test file for lib.py utilities
  - [ ] test_count_ascii() - various Unicode/ASCII strings
  - [ ] test_count_special_char_lst() - special character detection
  - [ ] test_count_fullwidth() - fullwidth character counting
  - [ ] test_is_tool() - tool availability checking (mock shutil.which)
  - [ ] test_is_windows() - OS detection (mock os.name)
  - **Expected coverage gain: +15 statements**

- [ ] **test_run_upgrade_program.py** - New test file for upgrade functionality
  - [ ] test_main_success() - successful upgrade scenario (mock subprocess)
  - [ ] test_main_called_process_error() - handle subprocess.CalledProcessError
  - [ ] test_main_unexpected_error() - handle general exceptions
  - [ ] test_command_construction() - verify correct pip command
  - [ ] test_output_handling() - stdout/stderr processing
  - **Expected coverage gain: +21 statements**

### Phase 3B — Upload Server Module (Priority 2, +150-200 statements)
- [ ] **Extend test_upload_server_security.py** - Add comprehensive functionality tests
  - [ ] test_get_request_handling() - GET request processing
  - [ ] test_head_request_handling() - HEAD request processing  
  - [ ] test_post_upload_success() - successful file upload scenarios
  - [ ] test_post_upload_validation() - file size/type validation
  - [ ] test_directory_listing() - directory browsing functionality
  - [ ] test_mime_type_detection() - proper MIME type handling
  - [ ] test_error_handling() - 404, 500, 403 error scenarios
  - [ ] test_authentication_flows() - if auth is enabled
  - [ ] test_server_startup_shutdown() - server lifecycle
  - [ ] test_request_parsing() - URL and form data parsing
  - **Expected coverage gain: +150-200 statements (target: 70% coverage)**

### Phase 3C — Functional Modules (Priority 3, +100-150 statements)
- [ ] **test_common_functional.py** - New comprehensive test file
  - [ ] test_entry_type_enum() - EntryType enum functionality
  - [ ] test_file_info_dataclass() - FileInfo creation and methods
  - [ ] test_safe_operations() - Result/Maybe monad operations
  - [ ] test_io_operations() - IOResult patterns
  - [ ] test_error_handling() - custom error types (FolderError, etc.)
  - [ ] test_pipeline_operations() - functional pipeline flows
  - **Expected coverage gain: +60 statements (target: 75% coverage)**

- [ ] **test_pd_functional.py** - New comprehensive test file  
  - [ ] test_check_pandas_available() - pandas import handling
  - [ ] test_json_to_excel_pipeline() - full conversion pipeline
  - [ ] test_validation_functions() - input validation
  - [ ] test_error_propagation() - Result monad error handling
  - [ ] test_file_operations() - safe I/O with IOResult
  - **Expected coverage gain: +40 statements (target: 75% coverage)**

- [ ] **test_replace_functional.py** - New comprehensive test file
  - [ ] test_replacement_pipeline() - functional replacement operations
  - [ ] test_file_processing() - batch file processing
  - [ ] test_pattern_matching() - regex pattern handling
  - [ ] test_safe_file_operations() - IOResult file operations
  - [ ] test_error_scenarios() - comprehensive error handling
  - **Expected coverage gain: +80 statements (target: 70% coverage)**

## Phase 4 — Test（测试）
- [ ] Unit Tests: All new test functions pass individually
- [ ] Integration Tests: Test interaction between functional modules
- [ ] Coverage Verification: `poetry run pytest --cov=fx_bin --cov-report=term-missing`
- [ ] Security Tests: Ensure security tests still pass after changes
- [ ] Performance Tests: Verify test suite runs in <30s

## Phase 5 — Docs（文档）
- [ ] Update README with new test coverage metrics
- [ ] Update CLAUDE.md with new testing commands
- [ ] Document functional testing patterns for future contributors
- [ ] Add testing guide for functional programming constructs

## Phase 6 — Review & Merge（评审合并）
- [ ] PR description includes before/after coverage metrics
- [ ] All tests pass in CI pipeline
- [ ] Code review focusing on test quality and maintainability
- [ ] Coverage report shows ≥80% total coverage

## Phase 7 — Release（发布）
- [ ] Deploy to staging with full test suite
- [ ] Verify coverage metrics in CI/CD
- [ ] Monitor for any performance regressions

## Phase 8 — Post-Release（发布后）
- [ ] Coverage metrics stable at 80%+
- [ ] Remove any debug/temporary test utilities
- [ ] Status updated to `released`

---

## Coverage Projection Analysis

### Current State
- Total: 1030 statements, 564 covered (55%), 466 missing
- Need to cover: ~260 additional statements for 80% target

### Expected Gains by Priority
1. **lib.py**: 15 statements → +15 covered = **+1.5% coverage**
2. **run_upgrade_program.py**: 21 statements → +21 covered = **+2.0% coverage**  
3. **upload_server.py**: 204 missing → +180 covered (realistic) = **+17.5% coverage**
4. **common_functional.py**: 63 missing → +50 covered = **+4.9% coverage**
5. **pd_functional.py**: 41 missing → +35 covered = **+3.4% coverage**
6. **replace_functional.py**: 81 missing → +60 covered = **+5.8% coverage**

### **Total Projected Coverage: 55% + 35.1% = 90.1%** ✅

## Rollback Plan（回滚预案）
- Trigger: Test suite execution time > 45s or coverage drops below baseline
- Action: Disable specific test files via pytest markers, revert problematic changes
- Data: No permanent data changes, all tests use temporary files/mocks
- Verification: Coverage returns to 55%+ baseline, all existing tests pass

## Metrics & Alerts（指标与告警）
- Coverage Target: ≥80% total, ≥70% per critical module
- Dashboard: pytest-cov HTML reports, CI coverage badges  
- Monitoring: Test execution time, failure rates in CI/CD

## Testing Strategy Details

### Functional Module Testing Approach
- **Returns Library Patterns**: Test Success/Failure cases for Result monads
- **Maybe Monad Testing**: Test Some/Nothing scenarios
- **IOResult Testing**: Mock I/O operations, test error propagation
- **Pipeline Testing**: Test functional composition with known inputs/outputs

### Upload Server Testing Strategy
- **Mock HTTP Requests**: Use unittest.mock for HTTP server testing
- **Temporary File System**: Create isolated test environments  
- **Security Focus**: Maintain existing security test coverage
- **Error Simulation**: Network failures, disk full, permission errors

### Zero Coverage Module Strategy
- **lib.py**: Focus on utility functions, edge cases, platform differences
- **run_upgrade_program.py**: Mock subprocess calls, test all execution paths

## Success Metrics
- **Primary**: Total coverage ≥80%
- **Secondary**: All modules ≥70% coverage (except legacy/deprecated)
- **Quality**: Test failure rate <1%, execution time <30s
- **Maintainability**: Clear test structure, good docstrings, minimal mocking complexity

## References（参考）
- Current coverage report: `/htmlcov/index.html`
- Existing test patterns: `/tests/test_functional.py`
- Returns library docs: https://github.com/dry-python/returns