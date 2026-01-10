# Implementation Tasks (TDD Style)

**Priority**: Phase 1 → Phase 17 (sequential order)

Each task follows RED-GREEN-REFACTOR:
1. **RED**: Write failing test or capture baseline
2. **GREEN**: Apply refactoring with minimal changes
3. **REFACTOR**: Optimize while keeping tests green

---

## Phase 1: cli.py Confirmation Prompts (organize function)

**Location**: `fx_bin/cli.py` organize() function, confirmation prompts at two locations
**Current Nesting**: 4 levels
**Refactoring Technique**: Extract duplicate logic
**Code Pattern**: Two identical `if sys.stdin.isatty(): if not click.confirm("\nProceed?...` blocks

- [x] 1.1 **RED**: Write test: verify confirmation prompt behavior
- [x] 1.2 **RED**: Run test to confirm baseline
- [x] 1.3 **GREEN**: Extract `_confirm_with_user()` inner function
- [x] 1.4 **GREEN**: Replace first confirmation logic with extracted function
- [x] 1.5 **GREEN**: Replace second confirmation logic with extracted function
- [x] 1.6 **GREEN**: Run tests to confirm passing
- [x] 1.7 Commit: "Phase 1: Extract _confirm_with_user to reduce duplication"

---

## Phase 2: cli.py ASK TTY Branch (organize function)

**Location**: `fx_bin/cli.py` organize() function, ASK mode TTY conflict handling
**Current Nesting**: 4-6 levels
**Refactoring Technique**: Early returns
**Code Pattern**: `if sys.stdin.isatty(): for conflict in conflicts: if click.confirm(...)`

- [x] 2.1 **RED**: Write test: verify TTY conflict handling
- [x] 2.2 **RED**: Run test to confirm baseline
- [x] 2.3 **GREEN**: Use early return to simplify isatty() check
- [x] 2.4 **GREEN**: Use early return to simplify confirm() check
- [x] 2.5 **GREEN**: Run ASK TTY tests
- [x] 2.6 Commit: "Phase 2: Use early returns in ASK TTY handling"

---

## Phase 3: cli.py Disk Conflict Filtering (organize function)

**Location**: `fx_bin/cli.py` organize() function, disk conflict filtering
**Current Nesting**: 4 levels
**Refactoring Technique**: List comprehension
**Code Pattern**: `for item in plan: if item.action == "moved" and os.path.exists(item.target)`

- [x] 3.1 **RED**: Write test: verify conflict filtering logic
- [x] 3.2 **RED**: Run test to confirm baseline
- [x] 3.3 **GREEN**: Replace for+if with list comprehension
- [x] 3.4 **GREEN**: Run conflict filtering tests
- [x] 3.5 Commit: "Phase 3: Use list comprehension for conflict filtering"

---

## Phase 4: cli.py fail_fast Error Handling (organize function)

**Location**: `fx_bin/cli.py` organize() function, error handling with context.fail_fast
**Current Nesting**: 4-8 levels
**Refactoring Technique**: Early returns + match/case
**Code Pattern**: Nested try/except with `if context.fail_fast` inside

- [x] 4.1 **RED**: Write test: verify fail_fast behavior
- [x] 4.2 **RED**: Run test to confirm baseline
- [x] 4.3 **GREEN**: Use match/case to rewrite error handling
- [x] 4.4 **GREEN**: Use early return to simplify conditions
- [x] 4.5 **GREEN**: Run fail_fast tests
- [x] 4.6 Commit: "Phase 4-8: Simplify ask execution with match/case and early returns"

---

## Phase 5: cli.py ask_user_choices Execution-skip (organize function)

**Location**: `fx_bin/cli.py` organize() function, skip choice execution
**Current Nesting**: 5 levels
**Refactoring Technique**: Early returns + match/case
**Code Pattern**: `if item.action == "moved": if item.source in choices: if choice == "skip"`

- [x] 5.1 **RED**: Write test: verify skip choice execution
- [x] 5.2 **RED**: Run test to confirm baseline
- [x] 5.3 **GREEN**: Use early return to pre-check conditions
- [x] 5.4 **GREEN**: Use match/case to handle choice
- [x] 5.5 **GREEN**: Run skip execution tests
- [x] 5.6 Commit: "Phase 4-8: Simplify ask execution with match/case and early returns"

---

## Phase 6: cli.py ask_user_choices Execution-overwrite (organize function)

**Location**: `fx_bin/cli.py` organize() function, overwrite choice execution
**Current Nesting**: 5-8 levels
**Refactoring Technique**: Early returns + match/case
**Code Pattern**: Deep nesting in move_file_safe call with dir_created tracking

- [x] 6.1 **RED**: Write test: verify overwrite choice execution
- [x] 6.2 **RED**: Run test to confirm baseline
- [x] 6.3 **GREEN**: Use match/case for branching
- [x] 6.4 **GREEN**: Use early return to reduce nesting from 8 to 4 levels
- [x] 6.5 **GREEN**: Run overwrite execution tests
- [x] 6.6 Commit: "Phase 4-8: Simplify ask execution with match/case and early returns"

---

## Phase 7: cli.py ask_user_choices Execution-else Branch (organize function)

**Location**: `fx_bin/cli.py` organize() function, other action types execution
**Current Nesting**: 5-7 levels
**Refactoring Technique**: Early returns
**Code Pattern**: elif branch with nested error handling

- [x] 7.1 **RED**: Write test: verify other action type execution
- [x] 7.2 **RED**: Run test to confirm baseline
- [x] 7.3 **GREEN**: Use early return to simplify condition chain
- [x] 7.4 **GREEN**: Run execution tests
- [x] 7.5 Commit: "Phase 4-8: Simplify ask execution with match/case and early returns"

---

## Phase 8: cli.py ask_user_choices Second Location (organize function)

**Location**: `fx_bin/cli.py` organize() function, second ask execution loop
**Current Nesting**: 4-5 levels
**Refactoring Technique**: Early returns + match/case
**Code Pattern**: Similar to Phase 5-7 but in different execution branch

- [x] 8.1 **RED**: Write test: verify second ask execution
- [x] 8.2 **RED**: Run test to confirm baseline
- [x] 8.3 **GREEN**: Use match/case to unify handling logic
- [x] 8.4 **GREEN**: Use early return to reduce nesting
- [x] 8.5 **GREEN**: Run complete ask execution tests
- [x] 8.6 Commit: "Phase 4-8: Simplify ask execution with match/case and early returns"

---

## Phase 9: organize_functional.py Symbolic Link Handling (_scan_recursive)

**Location**: `fx_bin/organize_functional.py` _scan_recursive() function, symlink handling
**Current Nesting**: 5-7 levels
**Refactoring Technique**: Early returns + match/case
**Code Pattern**: `if entry.is_symlink(): if follow_symlinks: if os.path.isdir(target):`

- [ ] 9.1 **RED**: Write test: verify symlink recursive handling
- [ ] 9.2 **RED**: Run test to confirm baseline
- [ ] 9.3 **GREEN**: Use match/case for symlink type handling
- [ ] 9.4 **GREEN**: Use early return to reduce nesting from 7 to 4 levels
- [ ] 9.5 **GREEN**: Run symlink integration tests
- [ ] 9.6 Commit: "Phase 9: Simplify symlink handling with match/case"

---

## Phase 10: organize_functional.py File Type Judgment (_scan_recursive)

**Location**: `fx_bin/organize_functional.py` _scan_recursive() function, file/dir classification
**Current Nesting**: 5 levels
**Refactoring Technique**: Early returns + match/case
**Code Pattern**: `if entry.is_file(): ... elif entry.is_dir() and not entry.is_symlink():`

- [ ] 10.1 **RED**: Write test: verify file/directory classification
- [ ] 10.2 **RED**: Run test to confirm baseline
- [ ] 10.3 **GREEN**: Use match/case for file type handling
- [ ] 10.4 **GREEN**: Use early return to simplify conditions
- [ ] 10.5 **GREEN**: Run file classification tests
- [ ] 10.6 Commit: "Phase 10: Simplify file type handling with match/case"

---

## Phase 11: organize_functional.py Skip Entry Judgment (_scan_recursive)

**Location**: `fx_bin/organize_functional.py` _scan_recursive() function, output dir skip
**Current Nesting**: 5 levels
**Refactoring Technique**: Logical short-circuit
**Code Pattern**: `if _should_skip_entry(...): L.debug(...); continue`

- [ ] 11.1 **RED**: Write test: verify entry skip logic
- [ ] 11.2 **RED**: Run test to confirm baseline
- [ ] 11.3 **GREEN**: Merge condition checks to reduce nesting
- [ ] 11.4 **GREEN**: Run skip logic tests
- [ ] 11.5 Commit: "Phase 11: Simplify skip entry with logical short-circuit"

---

## Phase 12: organize_functional.py EXDEV Handling (move_file_safe, first location)

**Location**: `fx_bin/organize_functional.py` move_file_safe() function, EXDEV in conflict check
**Current Nesting**: 5 levels
**Refactoring Technique**: Early return
**Code Pattern**: `elif conflict_mode == ConflictMode.OVERWRITE: try: ... except OSError as e: if e.errno == errno.EXDEV:`

- [ ] 12.1 **RED**: Write test: verify EXDEV handling
- [ ] 12.2 **RED**: Run test to confirm baseline
- [ ] 12.3 **GREEN**: Use early return to simplify exception handling
- [ ] 12.4 **GREEN**: Run EXDEV tests
- [ ] 12.5 Commit: "Phase 12: Simplify EXDEV handling with early return"

---

## Phase 13: organize_functional.py Second EXDEV (move_file_safe)

**Location**: `fx_bin/organize_functional.py` move_file_safe() function, second EXDEV location
**Current Nesting**: 4 levels
**Refactoring Technique**: Early return
**Code Pattern**: Similar to Phase 12 but in different code path

- [ ] 13.1 **RED**: Write test: verify second EXDEV
- [ ] 13.2 **RED**: Run test to confirm baseline
- [ ] 13.3 **GREEN**: Use early return to unify handling
- [ ] 13.4 **GREEN**: Run complete EXDEV tests
- [ ] 13.5 Commit: "Phase 13: Simplify second EXDEV with early return"

---

## Phase 14: organize_functional.py Directory Creation Condition (move_file_safe)

**Location**: `fx_bin/organize_functional.py` move_file_safe() function, directory creation
**Current Nesting**: 5 levels
**Refactoring Technique**: Logical short-circuit
**Code Pattern**: Complex conditional with `and` operators in if statement

- [ ] 14.1 **RED**: Write test: verify directory creation condition
- [ ] 14.2 **RED**: Run test to confirm baseline
- [ ] 14.3 **GREEN**: Merge complex conditions into single expression
- [ ] 14.4 **GREEN**: Run directory creation tests
- [ ] 14.5 Commit: "Phase 14: Simplify directory creation condition"

---

## Phase 15: organize_functional.py Empty Directory Check (remove_empty_dirs)

**Location**: `fx_bin/organize_functional.py` remove_empty_dirs() function
**Current Nesting**: 4 levels
**Refactoring Technique**: Early return
**Code Pattern**: `if is_empty: os.rmdir(...)`

- [ ] 15.1 **RED**: Write test: verify empty directory detection
- [ ] 15.2 **RED**: Run test to confirm baseline
- [ ] 15.3 **GREEN**: Use early return to simplify judgment
- [ ] 15.4 **GREEN**: Run empty directory cleanup tests
- [ ] 15.5 Commit: "Phase 15: Use early return for empty directory check"

---

## Phase 16: organize_functional.py Execution Directory Tracking (execute_organize)

**Location**: `fx_bin/organize_functional.py` execute_organize() function
**Current Nesting**: 5 levels
**Refactoring Technique**: Early return
**Code Pattern**: Tracking dir_created with nested conditions

- [ ] 16.1 **RED**: Write test: verify directory creation tracking
- [ ] 16.2 **RED**: Run test to confirm baseline
- [ ] 16.3 **GREEN**: Use early return to simplify conditions
- [ ] 16.4 **GREEN**: Run execution tracking tests
- [ ] 16.5 Commit: "Phase 16: Simplify execution directory tracking"

---

## Phase 17: Verification and Metrics

**Goal**: Confirm all refactoring complete, metrics met

- [ ] 17.1 **GREEN**: Run complete test suite (560 tests): `poetry run pytest --no-cov`
- [ ] 17.2 **GREEN**: flake8 code quality check: `poetry run flake8 fx_bin/`
- [ ] 17.3 **GREEN**: mypy type check: `poetry run mypy fx_bin/`
- [ ] 17.4 **GREEN**: Measure final nesting complexity: `python3 scripts/check_nesting.py fx_bin/cli.py fx_bin/organize_functional.py` (confirm ≤4 levels)
- [ ] 17.5 **GREEN**: Compare cyclomatic complexity before/after: `python3 scripts/check_complexity.py fx_bin/cli.py fx_bin/organize_functional.py` (confirm: organize() ≤50, all other functions ≤15; exit code 0 required)
- [ ] 17.6 **GREEN**: Manual test all organize functionality
- [ ] 17.7 Commit: "Phase 17: Final verification and metrics"

---

## Summary

**Total**: 17 Phases, 96 Tasks

### Refactoring Technique Distribution

| Technique | Phases | Expected Impact |
|-----------|--------|-----------------|
| Early Returns | 12 | Significantly reduce nesting levels |
| match/case | 7 | Replace deep if/elif chains |
| List Comprehension | 1 | Simplify filtering logic |
| Logical Short-circuit | 3 | Merge complex conditions |

### Expected Results

**Before Refactoring**:
```
cli.py: 21 instances of 4+ level nesting (deepest: 10 levels)
organize_functional.py: 14 instances of 4+ level nesting (deepest: 10 levels)
```

**After Refactoring**:
```
cli.py: 0 instances of 5+ level nesting (deepest: 4 levels) ✓
organize_functional.py: 0 instances of 5+ level nesting (deepest: 4 levels) ✓
Overall cyclomatic complexity: 30-40% reduction expected
```
