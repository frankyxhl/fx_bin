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

# FX-Bin Agent Guidelines

Python CLI toolkit for file operations. Entry: `fx` command with subcommands.

## Commands

```bash
# Setup & Run
make install              # Install dev deps (Poetry)
poetry run fx --help      # All commands
poetry run fx filter py   # Filter by extension

# Quality
make check                # lint + format + type + security
make lint                 # Flake8
make format               # Black
make type-check           # Mypy strict
make security-scan        # Bandit
```

## Testing

```bash
# Full suite
make test                 # All tests + coverage (≥80%)
make test-all             # No coverage gate

# Single test file
poetry run pytest tests/unit/test_filter.py -v --no-cov

# Single test function
poetry run pytest tests/unit/test_filter.py::TestFilterCore::test_find_files_by_extension_single_txt -v --no-cov

# By marker
poetry run pytest -m security -v --no-cov
poetry run pytest -m integration -v --no-cov
poetry run pytest -m "not slow" --no-cov

# Parallel
make test-parallel        # pytest-xdist (-n auto)
```

## Structure

```
fx_bin/
├── cli.py               # Click CLI entry point
├── common.py            # Shared utils (SizeEntry, FileCountEntry)
├── errors.py            # Error hierarchy (FxBinError base)
├── files.py, size.py    # fx files, fx size
├── find_files.py        # fx ff, fx fff
├── filter.py            # fx filter
├── replace.py           # fx replace (atomic writes)
├── root.py, today.py    # fx root, fx today

tests/
├── unit/                # Unit tests
├── integration/         # CLI tests
├── security/            # Safety tests
└── bdd/                 # BDD tests
```

## Code Style

- **Python**: 3.11+
- **Black**: 88 char lines
- **Flake8**: Zero tolerance
- **Mypy**: Strict mode

### Imports
```python
#!/usr/bin/env python
"""Module docstring required."""

# 1. stdlib
import os
from pathlib import Path
from typing import List, Optional

# 2. third-party
import click
from returns.result import Result, Success, Failure

# 3. local
from .errors import FxBinError
```

### Naming
| Type | Convention | Example |
|------|------------|---------|
| Functions/vars | snake_case | `find_files_by_extension` |
| Classes | PascalCase | `SizeEntry` |
| Constants | UPPER_CASE | `COMMANDS_INFO` |
| Private | _prefix | `_visited_inodes` |

### Type Annotations (Required)
```python
def find_files(path: str, ext: str, recursive: bool = True) -> List[Path]:
    ...

def from_scandir(cls, obj) -> Optional["SizeEntry"]:
    ...
```

### Error Handling
```python
# Use errors.py hierarchy
from .errors import FxBinError, ValidationError

# Catch specific, handle gracefully
try:
    result = risky_op()
except (PermissionError, OSError):
    pass  # Skip inaccessible

# CLI: report via click.echo
try:
    process()
except FileNotFoundError as e:
    click.echo(f"Error: {e}", err=True)
    return 1
```

### Dataclass Pattern
```python
@dataclass
@total_ordering
class SizeEntry:
    __slots__ = ["name", "size", "tpe"]  # Memory opt
    name: str
    size: int
    tpe: EntryType
```

## Security (CRITICAL)

- Path traversal protection
- Symlink loop detection (track inodes)
- Atomic writes (replace operations)
- Max recursion depth: 100
- Input sanitization

```bash
make test-security
make security-scan
poetry run safety check
```

## Test Markers

```python
@pytest.mark.security     # Security tests
@pytest.mark.integration  # CLI tests
@pytest.mark.performance  # Benchmarks
@pytest.mark.slow         # Long-running
```

## Commits

Format: `feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`

Before commit: `make check && make test-coverage`

## CLI Template

```python
@cli.command()
@click.argument("path", type=click.Path(exists=True))
def cmd(path):
    """Docstring with examples."""
    from . import module  # Lazy import
    try:
        click.echo(module.process(path))
        return 0
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        return 1
```

## Functional Pattern

```python
from returns.result import Result, Success, Failure

def safe_op(path: str) -> Result[str, FxBinError]:
    if not valid(path):
        return Failure(ValidationError("Invalid"))
    return Success(process(path))
```
