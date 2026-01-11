# Change: Refactor Organize Nesting Complexity

## Why

Current code has severe nesting complexity issues:
- `cli.py`: `organize()` function is 462 lines with 21 instances of 4+ level nesting, deepest at 10 levels
- `organize_functional.py`: 14 instances of 4+ level nesting, deepest at 10 levels
- Poor readability, difficult maintenance, prone to bugs

## What Changes

Perform independent TDD refactoring for **each deeply nested location**:
- Each location is a complete RED → GREEN → REFACTOR cycle
- Use early returns, Python 3.10+ match/case, list comprehensions, small helpers, etc.
- 100% preserve functional behavior

### Refactoring Technique Distribution

| Technique | Description | Locations |
|-----------|-------------|-----------|
| Early Returns | Pre-condition checks, reduce nesting | 12 |
| match/case | Pattern matching instead of if/elif | 7 |
| List Comprehension | Replace for+if filtering | 1 |
| Logical Short-circuit | Merge complex conditions | 3 |

## Impact

- **Affected Code**:
  - `fx_bin/cli.py` (organize function and execution logic)
  - `fx_bin/organize_functional.py` (scan and file move logic)
- **Affected Specs**: code-structure (adds internal nesting complexity requirements)
- **Breaking Change**: No
- **Backwards Compatible**: Yes (100% behavior preserved)

## Risks

| Risk | Mitigation |
|------|------------|
| Refactor introduces bugs | Strict TDD ensures test coverage for each step |
| Python version compatibility | match/case requires Python 3.10+ (project already requires 3.11+) |
| Performance regression | Early returns and match/case have equal or better performance |

## Rollback Strategy

- Each Phase is committed independently, can selectively revert
- Git revert of specific commit to rollback
- All tests serve as regression protection

## Acceptance Criteria

- [ ] All nesting reduced to maximum ≤4 levels (measured by AST analysis)
- [ ] All 560 tests still pass
- [ ] Behavior identical before/after each refactor
- [ ] No new flake8/mypy warnings
- [ ] No significant performance degradation
