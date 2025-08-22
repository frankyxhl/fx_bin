---
id: 20250823_015652_bug-fix_failing-tests-comprehensive-fix
type: bug-fix
title: Fix 29 Failing Tests Across Multiple Modules
slug: failing-tests-comprehensive-fix
created_at: 2025-08-23T01:56:52+09:00
owner: frank
priority: P1
estimate: 12h
issue: '-'
branch: bug-fix/failing-tests-comprehensive-fix
status: planned
---

# Rule
## When you work this plan, update the last status, e.g., ✅ COMPLETED when each task is done.

# bug-fix: Fix 29 Failing Tests Across Multiple Modules

## Description
- Background: The fx_bin project has 29 failing tests across 4 test files affecting core functionality
- Goal: Fix all failing tests to ensure code safety, security, and reliability
- Scope: upload_server.py, pd.py, replace.py, common.py, and related test files
- Non-goal: Adding new features or changing existing API behavior

## Acceptance Criteria
- [ ] All 29 failing tests pass
- [ ] No regression in existing passing tests
- [ ] Code maintains backward compatibility
- [ ] Security improvements properly implemented
- [ ] Performance not degraded for large operations
- [ ] Memory leaks resolved

---

## Phase 1 — Plan / Scope
- [ ] Associated Issue: -
- [ ] In scope: 
  - Fix simple typo: `os.exit(0)` → `sys.exit(0)` in upload_server.py
  - Resolve pandas import SystemExit(1) issue in pd.py
  - Handle macOS file path length limitations in deep directory tests
  - Implement missing safety features in replace.py (backup, readonly handling, etc.)
  - Add YB unit support to size conversion
- [ ] Out of scope: 
  - Complete rewrite of any modules
  - Adding new command-line options
  - Changing test framework from unittest
- [ ] Risks/Mitigations:
  - Risk: File operations safety changes may break existing functionality
  - Mitigation: Extensive testing and gradual rollout
  - Risk: Performance impact from safety improvements
  - Mitigation: Benchmark critical paths before/after changes
- [ ] Create branch: `bug-fix/failing-tests-comprehensive-fix`

## Phase 2 — Design
- [ ] Module-by-module fix strategy:
  - upload_server.py: Simple import fix
  - pd.py: Graceful pandas import handling
  - replace.py: Implement transaction-like operations with backup/rollback
  - common.py: Add missing size units and path length handling
- [ ] Test adaptations: Adjust path length limits for macOS filesystem constraints
- [ ] Performance targets: No more than 10% performance degradation for large operations
- [ ] Rollback strategy: Git revert for each module if issues arise

## Phase 3 — Implement

### Priority 1: Quick Fixes (1h)
- [ ] **upload_server.py typo fix** (5 min)
  - Line 439: Change `os.exit(0)` to `sys.exit(0)`
  - Verify test_server_binds_localhost_only passes
- [ ] **common.py YB unit support** (15 min)  
  - Add YB handling to convert_size function
  - Update very_large_sizes test expectation
- [ ] **pd.py graceful import handling** (40 min)
  - Wrap pandas import with try/except at module level
  - Exit gracefully without SystemExit when pandas missing
  - Update all pd tests to handle graceful degradation

### Priority 2: Path Length Issues (2h)
- [ ] **test_common_safety.py path fixes**
  - Reduce depth in test_max_recursion_depth_limit (1000 → 100 levels)
  - Add filesystem-aware path length checking
  - Implement proper cleanup for deeply nested structures
- [ ] **test_performance.py path fixes**
  - Adjust test_deep_directory_performance for macOS limitations
  - Add platform-specific path length constraints

### Priority 3: Replace Module Safety (6h)
- [ ] **Backup functionality**
  - Implement backup creation before file modification
  - Add backup cleanup after successful operations
  - Test: test_backup_before_modification
- [ ] **Transaction-like behavior**
  - Pre-validate all files before starting operations
  - Implement rollback mechanism for partial failures
  - Test: test_transaction_like_behavior, test_partial_failure_handling
- [ ] **File permission handling**
  - Add readonly file detection and graceful error handling
  - Implement proper permission preservation
  - Test: test_readonly_file_handling
- [ ] **Symlink safety**
  - Add symlink detection and safe handling
  - Prevent symlink-based attacks
  - Test: test_symlink_handling
- [ ] **Resource management**
  - Ensure proper file descriptor cleanup
  - Add interrupt signal handling
  - Test: test_interrupt_handling, test_disk_space_handling

### Priority 4: Advanced Error Handling (3h)
- [ ] **Timeout and hanging operations**
  - Add timeout mechanisms for long-running operations
  - Test: test_timeout_on_hanging_operations
- [ ] **Permission error handling**
  - Improve error handling in from_scandir methods
  - Test: test_permission_error_handling_in_from_scandir
- [ ] **Memory management**
  - Optimize large file processing to prevent memory issues
  - Add memory usage monitoring and limits

## Phase 4 — Test
- [ ] **Unit tests verification**
  - Run all failing tests to confirm fixes
  - Verify no regressions in passing tests
  - Execute: `poetry run pytest tests/test_*security*.py -v`
- [ ] **Integration testing**
  - Test multi-file operations end-to-end
  - Verify upload server security with real HTTP requests
  - Test concurrent operations safety
- [ ] **Performance benchmarking**
  - Compare before/after performance for large operations
  - Memory usage profiling for deep directory traversals
  - Ensure no significant performance degradation
- [ ] **Security verification**
  - Path traversal attack prevention
  - File upload security (size limits, type validation)
  - Authentication and authorization checks

## Phase 5 — Docs
- [ ] Update CHANGELOG.md with security improvements
- [ ] Document new safety features in replace module
- [ ] Add troubleshooting section for common issues
- [ ] Update security considerations in README

## Phase 6 — Review & Merge
- [ ] PR description includes:
  - Security improvements summary
  - Performance impact analysis
  - Test coverage metrics
- [ ] ≥2 code reviewers approval
- [ ] All CI checks passing
- [ ] squash merge to maintain clean history

## Phase 7 — Release
- [ ] Pre-release verification in test environment
- [ ] Gradual rollout strategy: dev → staging → production
- [ ] Monitor error rates and performance metrics

## Phase 8 — Post-Release
- [ ] Monitor system stability for 48 hours
- [ ] Remove temporary debug logging
- [ ] Security audit follow-up
- [ ] Update status to `released`

---

## Rollback Plan
- **Trigger conditions**: Test failure rate > 5% or performance degradation > 20%
- **Operation**: 
  - Git revert specific commits by module
  - Emergency hotfix deployment if needed
- **Data**: No data migrations involved
- **Verification**: All tests passing + performance benchmarks within normal range

## Metrics & Alerts
- **KPIs**: 
  - Test pass rate: 100%
  - Memory usage: < 50MB increase for large operations
  - File operation latency: < 10% increase
- **Dashboard**: Test results dashboard + performance monitoring
- **Alerts**: Test failure alerts + memory usage threshold alerts

## References
- Security test requirements in test_*security*.py files
- Performance benchmarks in test_performance.py
- Error handling patterns in existing modules

## Detailed Fix Breakdown

### Module: upload_server.py
**Issue**: `os.exit(0)` should be `sys.exit(0)` (line 439)
**Fix**: Simple import correction
**Test**: test_server_binds_localhost_only
**Effort**: 5 minutes

### Module: pd.py  
**Issue**: SystemExit(1) on pandas import failure breaks all tests
**Fix**: 
- Wrap pandas import in function-level try/except
- Return error codes instead of sys.exit() in module loading
- Allow tests to mock pandas availability
**Tests**: All 16 pandas-related tests
**Effort**: 1 hour

### Module: replace.py
**Issues**: Missing safety features for file operations
**Fixes**:
- Pre-operation backup creation
- Transaction-like multi-file operations
- Readonly file detection and handling
- Proper symlink handling
- Resource cleanup and interrupt handling
- Disk space error handling
**Tests**: 7 failing safety tests
**Effort**: 6 hours

### Module: common.py
**Issues**: Path length limitations and missing YB unit
**Fixes**:
- Add YB support to convert_size()
- Implement max recursion depth limits
- Handle very long file paths gracefully
- Add proper timeout handling
**Tests**: 4 failing tests
**Effort**: 2 hours

### Test Adjustments
**Issues**: Platform-specific limitations on macOS
**Fixes**:
- Reduce path depth in deep directory tests
- Add platform-aware path length checking
- Improve timeout handling in hanging operation tests
**Tests**: Platform-specific test adaptations
**Effort**: 1 hour