# Functional Programming Patterns

## ADDED Requirements

### Requirement: Railway-Oriented Composition

The system SHALL use Railway-Oriented Programming patterns for chaining operations that may fail, using the `returns` library's `flow`, `bind`, and `map` functions instead of explicit type checking.

#### Scenario: Successful operation chain
- **GIVEN** a valid file path
- **WHEN** `work_functional` is called with valid parameters
- **THEN** operations are composed using `bind` without accessing private attributes

#### Scenario: Error propagation in pipeline
- **GIVEN** an operation that fails midway in the pipeline
- **WHEN** the error occurs
- **THEN** subsequent operations are skipped and error is propagated via Railway pattern

### Requirement: Pure Function Separation

The system SHALL separate pure computational functions from IO-performing functions, with pure functions being testable without mocking IO.

#### Scenario: Testing pure entry processing
- **GIVEN** an `os.DirEntry` object
- **WHEN** `process_entry` pure function is called
- **THEN** it returns computed values without performing any IO operations

#### Scenario: IO function composition
- **GIVEN** a directory path
- **WHEN** `scan_directory` IO function is called
- **THEN** it wraps IO in `IOResult` and composes with pure functions

### Requirement: Result Type API Usage

The system SHALL NOT access private attributes of `returns` library types (such as `_inner_value`). Instead, it SHALL use public API methods like `map`, `bind`, `alt`, `lash`, `value_or`, and pattern matching.

#### Scenario: Error handling without private access
- **GIVEN** an `IOResult` that may contain a failure
- **WHEN** checking for failure
- **THEN** use `lash` for error recovery or `alt` for alternative values, not `isinstance(_inner_value, Failure)`

## ADDED Requirements

### Requirement: Shared Backup Utilities

The system SHALL provide a `backup_utils` module with reusable backup operations (`create_backup`, `restore_backup`, `cleanup_backup`) to eliminate duplication between `replace.py` and `replace_functional.py`.

#### Scenario: Creating a backup before modification
- **GIVEN** a file path to modify
- **WHEN** `create_backup` is called
- **THEN** a `BackupHandle` is returned containing original path, backup path, and original permissions

#### Scenario: Restoring from backup on failure
- **GIVEN** a `BackupHandle` from a previous backup
- **WHEN** `restore_backup` is called
- **THEN** the original file is restored with original permissions

#### Scenario: Cleaning up backup on success
- **GIVEN** a `BackupHandle` from a successful operation
- **WHEN** `cleanup_backup` is called
- **THEN** the backup file is removed
