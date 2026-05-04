# Alfred / AF Workflow Instructions

This project uses Alfred (`af`) runbook documents for planning, proposals,
change requests, and workflow routing. Do not use OpenSpec for new project work
unless the user explicitly asks for OpenSpec.

## AF Session Routing

At the start of a substantial task, run:

```bash
af guide --root .
```

Use the routing output to choose the applicable SOPs. Before executing a routed
task, run `af plan <SOP_IDS>` to generate the checklist and follow it. Declare
the active SOP in progress updates when the work depends on an AF SOP.

Core routing rules:

- New feature, tool, command, or capability: create a PRP via `COR-1102`.
- Change to existing system/config/architecture: create a CHG via `COR-1101`.
- Execution coordination for approved/in-progress work: create a PLN.
- Durable decision already made: create an ADR.
- Code changes: apply the TDD overlay from `COR-1500`.
- Existing document updates: follow `COR-1300`.

## AF Commands

```bash
af guide --root .                         # Show routing for this project/session
af plan COR-1102 COR-1500 --todo          # Generate SOP checklist
af create prp --prefix FXB --area 21 --title "Feature Name"
af create chg --prefix FXB --area 21 --title "Change Name"
af list                                   # List available documents
af read COR-1102                          # Read an SOP/document
af validate                               # Validate Alfred documents
```

Project-layer AF documents should live under `./rules/` when created. If the
project prefix is unclear, ask the user before creating a PRP/CHG/ADR/PLN.

For a new command like `fx open`, prefer a PRP first because it is a new
capability. Use a CHG only when modifying an existing approved design or when the
user explicitly requests a change record for implementation.

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
