# Testing Standards

## ADDED Requirements

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
