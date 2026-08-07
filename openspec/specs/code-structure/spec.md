# code-structure Specification

## Purpose
TBD - created by archiving change refactor-functional-and-testing. Update Purpose after archive.
## Requirements
### Requirement: Error Type Hierarchy

The system SHALL organize error types with intermediate base classes to enable granular error handling. `FileOperationError` SHALL be the base for all file-related errors.

#### Scenario: Catching all file operation errors
- **GIVEN** code that may raise `ReplaceError`, `IOError`, or `PermissionError`
- **WHEN** catching file operation errors
- **THEN** `except FileOperationError` catches all three

#### Scenario: Specific error handling
- **GIVEN** code that may raise `ReplaceError`
- **WHEN** catching only replace errors
- **THEN** `except ReplaceError` catches only replace-specific errors

### Requirement: Type Annotation Precision

The system SHALL use `Sequence[str]` instead of `Tuple[str, ...]` for function parameters that accept any iterable of strings, following Python typing best practices.

#### Scenario: Accepting list or tuple of filenames
- **GIVEN** a function that processes multiple filenames
- **WHEN** defining the parameter type
- **THEN** use `filenames: Sequence[str]` to accept both lists and tuples

### Requirement: Module Organization for Imports

The system SHALL organize modules to avoid circular imports by extracting shared pure utilities to dedicated modules.

#### Scenario: Pure utilities in separate module
- **GIVEN** a pure function like `convert_size` used by multiple modules
- **WHEN** organizing imports
- **THEN** the function resides in a utilities module importable by all dependent modules

### Requirement: Path Boundary Validation (Retired 2026-08-08)

Retired with FXB-2112: the only implementation (`validate_file_access` in `replace_functional.py`) was unreachable from the CLI and removed. fx-bin is a local CLI operating on paths the user names explicitly; there is no server-style trust boundary requiring `allowed_base` confinement. If a network-facing or sandboxed mode is ever added, reintroduce boundary validation with it.

