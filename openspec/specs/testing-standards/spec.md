# testing-standards Specification

## Purpose
TBD - created by archiving change refactor-functional-and-testing. Update Purpose after archive.
## Requirements
### Requirement: Shared Test Fixtures

The system SHALL provide shared pytest fixtures in `tests/conftest.py` for common test setup operations, including temporary directory creation and cleanup.

#### Scenario: Using temp_test_dir fixture
- **GIVEN** a test function with `temp_test_dir` parameter
- **WHEN** the test runs
- **THEN** a temporary directory is created before the test and cleaned up after

#### Scenario: Using temp_file fixture
- **GIVEN** a test function with `temp_file` parameter
- **WHEN** the test runs
- **THEN** a temporary file with default content is available

### Requirement: Property-Based Testing

The system SHALL include property-based tests using `hypothesis` library for core operations that process arbitrary input, ensuring invariants hold across generated test cases.

#### Scenario: Text replacement invariant
- **GIVEN** arbitrary search text, replace text, and file content
- **WHEN** replacement is performed
- **THEN** the search text does not appear in result unless replace text contains it

#### Scenario: Size calculation non-negative
- **GIVEN** any valid directory path
- **WHEN** size is calculated
- **THEN** the result is always non-negative

### Requirement: Test Naming Convention

Test functions SHALL follow the `test_given_X_when_Y_then_Z` naming pattern for clarity about preconditions, actions, and expected outcomes.

#### Scenario: Descriptive test name
- **GIVEN** a test for file replacement
- **WHEN** naming the test function
- **THEN** use `test_given_file_with_content_when_replace_called_then_content_updated`

### Requirement: Logger Isolation

Tests SHALL isolate logger configuration using pytest fixtures rather than module-level `logger.remove()` calls, to prevent test pollution.

#### Scenario: Logger silenced per test
- **GIVEN** a test that generates log output
- **WHEN** the test runs
- **THEN** logger is silenced only for that test, not affecting other tests

### Requirement: Mock Simplification

Complex mock setups SHALL be extracted into helper functions with descriptive names, improving test readability and maintainability.

#### Scenario: Reusable mock for rename failure
- **GIVEN** multiple tests need to simulate rename failures
- **WHEN** setting up the mock
- **THEN** use `create_failing_rename_mock()` helper instead of inline mock setup

### Requirement: BDD Feature File Coverage
The organize command SHALL have Behavior-Driven Development (BDD) tests using pytest-bdd with Gherkin `.feature` files.

#### Scenario: BDD tests are executable
- **WHEN** developer runs `poetry run pytest tests/bdd/test_organize_steps.py -v`
- **THEN** all BDD scenarios execute successfully
- **AND** step definitions are properly implemented

#### Scenario: BDD tests use correct markers
- **WHEN** developer runs `poetry run pytest -m "bdd and smoke" -v`
- **THEN** only smoke-tagged BDD tests execute
- **AND** markers align with pyproject.toml definitions

### Requirement: BDD Scenario Coverage
The organize command BDD tests SHALL cover core functionality scenarios.

#### Scenario: Core functionality coverage
- **WHEN** BDD test suite is executed
- **THEN** scenarios cover: date-based organization, dry-run mode, recursive scanning
- **AND** scenarios cover: conflict resolution modes (SKIP, OVERWRITE, RENAME, ASK)
- **AND** scenarios cover: edge cases (empty directories, invalid paths, symlinks)

#### Scenario: Path structure matches specification
- **WHEN** BDD scenarios describe date-based organization
- **THEN** default path structure is documented as `YYYY/YYYYMM/YYYYMMDD/` (depth 3)
- **AND** aligns with `openspec/specs/organize/spec.md`

