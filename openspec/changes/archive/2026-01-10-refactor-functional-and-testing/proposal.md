# Change: Refactor Functional Programming Patterns and Testing Standards

## Why

The fx_bin codebase has evolved with a dual-mode architecture (imperative + functional), but the functional programming patterns using the `returns` library are inconsistently applied. Additionally, the test code has accumulated duplication and could benefit from modernization. This refactoring will:

1. Establish consistent Railway-Oriented Programming patterns
2. Eliminate test code duplication and improve isolation
3. Consolidate shared logic (backup utilities)
4. Add property-based testing for stronger guarantees

## What Changes

### Functional Programming Improvements
- Replace direct `_inner_value` access with proper `returns` library APIs
- Implement Railway-Oriented composition using `flow`/`pipe`
- Separate pure functions from IO effects more clearly
- Add intermediate error type hierarchy

### Testing Standards Improvements
- Extract shared test fixtures to `conftest.py`
- Add property-based tests using `hypothesis`
- Improve test naming conventions (given_when_then)
- Simplify complex mock setups

### Code Structure Improvements
- Create shared `backup_utils.py` module
- Extract pure utilities to avoid circular imports
- Improve type annotations with `Sequence` instead of `Tuple`

## Impact

- **Affected specs**: functional-programming, testing-standards, code-structure (new)
- **Affected code**:
  - `fx_bin/replace_functional.py`
  - `fx_bin/common_functional.py`
  - `fx_bin/errors.py`
  - `fx_bin/replace.py`
  - `tests/conftest.py` (new)
  - `tests/unit/*.py`
  - `tests/security/*.py`
- **Risk**: Medium - refactoring core functional code requires careful testing
- **Breaking changes**: None - all changes are internal refactoring
