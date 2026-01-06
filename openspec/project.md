# Project Context

## Purpose
FX bin is a Python utility collection providing command-line tools for file operations, including file counting, size analysis, finding files, text replacement, and backup utilities. The project is packaged using Poetry and distributed via PyPI as `fx-bin`.

## Tech Stack
- **Language**: Python 3.11+
- **CLI Framework**: Click
- **Logging**: Loguru
- **Functional Programming**: returns library (Result, Maybe, IOResult types)
- **Package Management**: Poetry
- **Testing**: pytest, pytest-bdd, pytest-cov

## Project Conventions

### Code Style
- **Formatter**: Black (88 char line length)
- **Linter**: Flake8
- **Type Checking**: MyPy (strict mode enabled)
- **Docstrings**: Google style

### Architecture Patterns
- **Dual-Mode**: Traditional imperative + functional patterns coexist
- **Dataclasses**: Immutable with `frozen=True`
- **Error Handling**: Custom error hierarchy + Result types from `returns` library
- **CLI Pattern**: Each utility module has `main()` entry point with Click decorators

### Testing Strategy
- **Framework**: pytest with unittest.TestCase support
- **Coverage**: Minimum 80% required
- **Categories**: unit, integration, security, performance, bdd
- **Safety Tests**: File descriptor leak detection, atomic operation verification

### Git Workflow
- Main branch: `main`
- Commit message: Conventional commits style
- PR required for feature changes

## Domain Context
- File operations must be atomic with backup/restore on failure
- Binary file detection required before text operations
- Symlink handling with cycle detection
- Cross-filesystem move handling (EXDEV errors)

## Important Constraints
- Must support Python 3.11+
- All file operations must be safe (no data loss)
- Backward compatibility with existing CLI interface

## External Dependencies
- PyPI distribution as `fx-bin`
- No runtime external services required
