<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FX bin is a Python utility collection providing command-line tools for file operations, including file counting, size analysis, finding files, text replacement, and a simple upload server. The project is packaged using Poetry and distributed via PyPI as `fx-bin`.

## Development Commands

### Build and Package
```bash
# Build the package
poetry build

# Install dependencies
poetry install

# Install package locally for development
pip install -e .
```

### Testing
```bash
# Install all dependencies first
poetry install --with dev

# Run all tests with pytest (recommended)
poetry run pytest

# Run tests without coverage requirement
poetry run pytest --no-cov

# Run with coverage report
poetry run pytest --cov=fx_bin --cov-report=html --cov-report=term-missing

# Run only passing core tests
poetry run pytest tests/test_size.py tests/test_files.py tests/test_find_files.py tests/test_replace.py -v

# Run security tests only (CRITICAL - must pass)
poetry run pytest tests/test_*security*.py -v --no-cov

# Run specific test file
poetry run pytest tests/test_replace_safety.py -v --no-cov
poetry run pytest tests/test_filter.py -v --no-cov

# Run specific test
poetry run pytest tests/test_upload_server_security.py::TestUploadServerSecurity::test_path_traversal_attack_blocked -v

# Run tests in parallel
poetry run pytest -n auto --no-cov

# Run tests with timeout protection
poetry run pytest --timeout=30 --no-cov

# Run only fast tests (exclude slow/integration tests)
poetry run pytest -m "not slow" --no-cov

# Run integration tests only
poetry run pytest -m integration --no-cov

# Run performance tests only
poetry run pytest -m performance --no-cov

# Run property-based tests (hypothesis)
poetry run pytest -m hypothesis -v --no-cov

# Alternative test runners (no Poetry required)
python tests/runners/simple_test_runner.py
python tests/runners/run_simple_tests.py
python tests/runners/run_tdd_tests.py

# Using unittest via Poetry
poetry run python -m unittest discover tests
poetry run python -m unittest tests.test_size

# Quick test for basic functionality
poetry run python -m unittest tests.test_size tests.test_files tests.test_replace tests.test_find_files -v
```

### Code Quality
```bash
# Run flake8 linting
poetry run flake8 fx_bin

# Run flake8 on specific file
poetry run flake8 fx_bin/files.py

# Run type checking with mypy
poetry run mypy fx_bin/

# Run code formatting with black
poetry run black fx_bin/ tests/

# Check code formatting (dry run)
poetry run black --check fx_bin/ tests/
```

### Security Testing
```bash
# Run security analysis with bandit
poetry run bandit -r fx_bin/

# Check dependencies for known vulnerabilities
poetry run safety check

# Run comprehensive security test suite
poetry run tox -e security

# Run all security-related checks
poetry run pytest tests/test_*security*.py -v && poetry run bandit -r fx_bin/ && poetry run safety check
```

### Property-Based Testing with Hypothesis

The project uses [Hypothesis](https://hypothesis.readthedocs.io/) for property-based testing to automatically discover edge cases.

**When to use property-based tests:**
- Testing invariants that should hold for all inputs
- Discovering edge cases automatically
- Verifying mathematical properties (idempotency, commutativity, etc.)
- Boundary condition testing

**Example usage:**
```python
from hypothesis import given, strategies as st, settings, HealthCheck

@pytest.mark.hypothesis
@given(
    search=st.text(min_size=1, max_size=50),
    replace=st.text(max_size=50),
    content=st.text(max_size=500)
)
@settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_property_invariant(temp_test_dir, search, replace, content):
    """Test that invariant holds for all generated inputs."""
    # INVARIANT: After replacement, search shouldn't appear
    # unless replace contains it
    test_file = temp_test_dir / "test.txt"
    test_file.write_text(content)
    work(search, replace, str(test_file))
    result = test_file.read_text()

    if search not in replace:
        assert result.count(search) <= content.count(search)
```

**Important notes:**
- Mark tests with `@pytest.mark.hypothesis`
- Use `suppress_health_check=[HealthCheck.function_scoped_fixture]` when using pytest fixtures with `@given`
- Hypothesis generates many test cases (controlled by `max_examples`)
- Failed tests are automatically shrunk to minimal failing example
- Use `assume()` to filter out invalid inputs

**Running hypothesis tests:**
```bash
# Run all hypothesis tests
poetry run pytest -m hypothesis -v

# Run with more examples for thorough testing
poetry run pytest -m hypothesis --hypothesis-seed=random -v
```

## Architecture

### Package Structure
- **fx_bin/**: Main package directory containing all utility modules
  - Each utility is a standalone module with a `main()` function entry point
  - Scripts are registered in `pyproject.toml` under `[tool.poetry.scripts]`

### Available Commands (via unified `fx` CLI)
- `fx files`: Count files in directories (files.py)
- `fx size`: Analyze file/directory sizes (size.py)
- `fx ff`: Find files utility (find_files.py)
- `fx fff`: Find first file (alias for ff --first)
- `fx filter`: Filter files by extension and sort by time (filter.py)
- `fx replace`: Text replacement utility (replace.py)
- `fx root`: Find Git project root (root.py)
- `fx today`: Daily workspace manager (today.py)
- `fx list`: List all available commands

### Key Dependencies
- **click**: Command-line interface creation
- **loguru**: Logging functionality
- Python 3.11+ required

### Module Pattern
Each utility module follows this pattern:
1. Implements core functionality in functions/classes
2. Provides a `main()` function as the CLI entry point
3. Uses Click decorators for command-line argument parsing
4. Registered as a console script in pyproject.toml

### Testing Approach
- Uses unittest framework with pytest enhancements
- Tests located in `tests/` directory
- Test runners available in `tests/runners/` directory
- Testing documentation in `docs/testing/` directory
- Click's CliRunner used for testing CLI interfaces
- Test files follow `test_*.py` naming convention
- Virtual environment: `.venv/` (Python standard)
- Comprehensive security and safety tests implemented