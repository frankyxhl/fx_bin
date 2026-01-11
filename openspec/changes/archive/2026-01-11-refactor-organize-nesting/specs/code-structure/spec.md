# Code Structure Specification - Delta: Refactor Organize Nesting

## Purpose

Reduce nesting complexity in `fx organize` command implementation to improve code readability and maintainability.

## ADDED Requirements

### Requirement: Nesting Complexity Limits
The code SHALL maintain maximum nesting depth of 4 levels in organize-related implementation files (`fx_bin/cli.py` and `fx_bin/organize_functional.py`).

#### Scenario: CLI file maintains nesting limit (ADDED)
- **WHEN** analyzing `fx_bin/cli.py` with `scripts/check_nesting.py`
- **THEN** maximum nesting depth is ≤4 levels (file-level measurement)
- **AND** all functionality is preserved

#### Scenario: Functional module maintains nesting limit (ADDED)
- **WHEN** analyzing `fx_bin/organize_functional.py` with `scripts/check_nesting.py`
- **THEN** maximum nesting depth is ≤4 levels (file-level measurement)
- **AND** all functionality is preserved

#### Note on elif nesting measurement (ADDED)
- **WHEN** counting nesting depth with `scripts/check_nesting.py`
- **THEN** elif chains are counted as AST represents them (nested if inside orelse)
- **This means** `if A: ... elif B: ... elif C:` is counted as depth 3 (not depth 1)
- **Rationale**: AST structure accurately represents control flow complexity (each elif nests 1 level deeper)

### Requirement: Early Return Pattern
The code SHALL use early return pattern to reduce nesting where applicable.

#### Scenario: Early return replaces deep nesting (ADDED)
- **WHEN** a function has multiple nested conditions
- **THEN** early return statements are used to check conditions upfront
- **AND** nesting depth is reduced by at least 1 level
- **AND** functional behavior is unchanged

### Requirement: Match/Case for Branching
The code SHALL use Python 3.10+ match/case statements for multi-way branching where applicable.

#### Scenario: Match/case replaces if/elif chains (ADDED)
- **WHEN** a function has 3 or more sequential if/elif branches
- **THEN** match/case statement is used where appropriate
- **AND** nesting depth is reduced by at least 1 level
- **AND** functional behavior is unchanged

## MODIFIED Requirements

### Requirement: Code Quality Standards
Existing code SHALL maintain high quality while reducing complexity.

#### Scenario: All tests pass after refactoring (MODIFIED)
- **WHEN** running complete test suite
- **THEN** all 560 tests pass
- **AND** no tests are modified unless adding new coverage
- **AND** functional behavior is preserved

#### Scenario: Cyclomatic complexity reduced (ADDED)
- **WHEN** measuring complexity with `scripts/check_complexity.py`
- **THEN** `cli.py:organize()` function complexity is ≤50 (special threshold for large orchestrator)
- **AND** all other functions maintain complexity ≤15
- **AND** complexity is calculated as: 1 + count of decision points (if/elif/for/while/try/except/with/match/boolop) with function boundary isolation

#### Scenario: No new linting warnings (MODIFIED)
- **WHEN** running flake8 on refactored code
- **THEN** no new warnings are introduced
- **AND** existing warnings are not increased

#### Scenario: Type safety maintained (MODIFIED)
- **WHEN** running mypy on refactored code
- **THEN** no new type errors are introduced
- **AND** type coverage is maintained or improved
