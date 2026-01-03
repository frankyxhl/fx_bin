# Add Backup Command Implementation Plan

> **Status:** Active  
> **Created:** 2026-01-03

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

## Meta: Workflow Configuration

**Agent -> Model Mapping:**
| Agent | Model | Role |
|-------|-------|------|
| Sisyphus | zai-coding-plan/glm-4.7 | Coordination |
| `oracle` | openai/gpt-5.2-pro | Review, Architecture |
| `build` | google/gemini-3-flash | TDD Implementation |
| `coder` | zai-coding-plan/glm-4.7 | Code Refinement |

**Execution Mode:** Coordination

**Workflow:**
| Phase | Skill | Agent | Context |
|-------|-------|-------|---------|
| Requirements | brainstorming | Sisyphus | Same |
| Planning | writing-plans | oracle | Independent |
| Implementation | test-driven-development | build | Independent |
| Verification | verification-before-completion | oracle | Independent |

---

**Goal:** Add a `fx backup` command to create timestamped backups of files and directories with optional compression and automatic cleanup.

**Architecture:** Create new `backup.py` module following fx command patterns with Click CLI, supporting file and directory backup with configurable timestamp formats (default %Y%m%d%H%M%S), optional compression (--compress creates .tar.gz for directories), backup limit (--max-backups), and intelligent multi-extension handling for files like .tar.gz. Follow project conventions (lazy import in cli.py, return exit codes, proper error handling, no restore command).

**Tech Stack:** Python 3.11+, Click, pathlib, shutil, datetime

---

## Task 1: Core Backup Module Structure

**Files:**
- Create: `fx_bin/backup.py`
- Test: `tests/unit/test_backup.py`

**Step 1: Write failing test - module exists**
```python
import pytest
from pathlib import Path

def test_backup_module_exists():
    from fx_bin import backup
    assert hasattr(backup, 'KNOWN_MULTI_EXTS')
    assert hasattr(backup, 'DEFAULT_TIMESTAMP_FORMAT')
```

**Step 2: Run test (expect FAIL)**
Run: `poetry run pytest tests/unit/test_backup.py::test_backup_module_exists -v --no-cov`
Expected: FAIL with ModuleNotFoundError

**Step 3: Implement minimal code**
```python
#!/usr/bin/env python
"""Backup command for fx."""

from pathlib import Path
from typing import List

# Known multi-part extensions (e.g., .tar.gz)
KNOWN_MULTI_EXTS = {'.tar.gz', '.tar.bz2', '.tar.xz'}

# Default timestamp format
DEFAULT_TIMESTAMP_FORMAT = "%Y%m%d%H%M%S"

def get_multi_ext(path: Path) -> str:
    """Get multi-part extension if path has one."""
    name = str(path.name).lower()
    for ext in sorted(KNOWN_MULTI_EXTS, key=len, reverse=True):
        if name.endswith(ext):
            return ext
    return ""

def get_base_name(path: Path) -> str:
    """Get base name without multi-part extension."""
    multi_ext = get_multi_ext(path)
    if multi_ext:
        return path.name[:-len(multi_ext)]
    return path.stem
```

**Step 4: Run test (expect PASS)**
Run: `poetry run pytest tests/unit/test_backup.py::test_backup_module_exists -v --no-cov`
Expected: PASS

**Step 5: Commit**
```bash
git add fx_bin/backup.py tests/unit/test_backup.py
git commit -m "feat: add backup module structure with multi-extension handling"
```

---

## Task 2: File Backup Functionality

**Files:**
- Modify: `fx_bin/backup.py:20-50`
- Test: `tests/unit/test_backup.py`

**Step 1: Write failing test**
```python
import pytest
from pathlib import Path
from datetime import datetime

def test_backup_file_creates_timestamped_copy(tmp_path):
    from fx_bin.backup import backup_file

    # Create test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")

    # Backup
    result = backup_file(test_file, tmp_path / "backups", timestamp_format="%Y%m%d%H%M%S")

    assert result.is_success()
    assert len(list((tmp_path / "backups").glob("test_*.txt"))) >= 1

def test_backup_file_handles_multi_extensions(tmp_path):
    from fx_bin.backup import backup_file

    test_file = tmp_path / "archive.tar.gz"
    test_file.write_bytes(b"tar content")

    result = backup_file(test_file, tmp_path / "backups", timestamp_format="%Y%m%d%H%M%S")

    assert result.is_success()
    backups = list((tmp_path / "backups").glob("archive_*.tar.gz"))
    assert len(backups) >= 1
```

**Step 2: Run test (expect FAIL)**
Run: `poetry run pytest tests/unit/test_backup.py::test_backup_file_creates_timestamped_copy -v --no-cov`
Expected: FAIL with function not found

**Step 3: Implement minimal code**
```python
from datetime import datetime
from returns.result import Result, Success, Failure
from .errors import FxBinError

def backup_file(
    source: Path,
    backup_dir: Path,
    timestamp_format: str = DEFAULT_TIMESTAMP_FORMAT,
) -> Result[Path, FxBinError]:
    """Backup a single file with timestamp."""
    if not source.exists():
        return Failure(FxBinError(f"Source file not found: {source}"))

    backup_dir.mkdir(parents=True, exist_ok=True)

    # Get base name and extension
    multi_ext = get_multi_ext(source)
    if multi_ext:
        base_name = source.name[:-len(multi_ext)]
        timestamped_name = f"{base_name}_{datetime.now().strftime(timestamp_format)}{multi_ext}"
    else:
        timestamped_name = f"{source.stem}_{datetime.now().strftime(timestamp_format)}{source.suffix}"

    backup_path = backup_dir / timestamped_name

    try:
        shutil.copy2(source, backup_path)
        return Success(backup_path)
    except (PermissionError, OSError) as e:
        return Failure(FxBinError(f"Failed to backup file: {e}"))
```

**Step 4: Run test (expect PASS)**
Run: `poetry run pytest tests/unit/test_backup.py::test_backup_file_creates_timestamped_copy tests/unit/test_backup.py::test_backup_file_handles_multi_extensions -v --no-cov`
Expected: PASS

**Step 5: Commit**
```bash
git add fx_bin/backup.py tests/unit/test_backup.py
git commit -m "feat: implement file backup with timestamp and multi-extension support"
```

---

## Task 3: Directory Backup (No Compression)

**Files:**
- Modify: `fx_bin/backup.py:50-80`
- Test: `tests/unit/test_backup.py`

**Step 1: Write failing test**
```python
def test_backup_directory_no_compression(tmp_path):
    from fx_bin.backup import backup_directory

    # Create test directory
    test_dir = tmp_path / "mydir"
    test_dir.mkdir()
    (test_dir / "file.txt").write_text("content")

    result = backup_directory(test_dir, tmp_path / "backups", compress=False, timestamp_format="%Y%m%d%H%M%S")

    assert result.is_success()
    assert (tmp_path / "backups").exists()
    backups = list((tmp_path / "backups").glob("mydir_*"))
    assert len(backups) >= 1
    assert backups[0].is_dir()
```

**Step 2: Run test (expect FAIL)**
Run: `poetry run pytest tests/unit/test_backup.py::test_backup_directory_no_compression -v --no-cov`
Expected: FAIL with function not found

**Step 3: Implement minimal code**
```python
def backup_directory(
    source: Path,
    backup_dir: Path,
    compress: bool = False,
    timestamp_format: str = DEFAULT_TIMESTAMP_FORMAT,
) -> Result[Path, FxBinError]:
    """Backup a directory, optionally compress."""
    if not source.is_dir():
        return Failure(FxBinError(f"Source is not a directory: {source}"))

    backup_dir.mkdir(parents=True, exist_ok=True)

    if compress:
        return _backup_directory_compressed(source, backup_dir, timestamp_format)
    else:
        return _backup_directory_uncompressed(source, backup_dir, timestamp_format)

def _backup_directory_uncompressed(
    source: Path,
    backup_dir: Path,
    timestamp_format: str,
) -> Result[Path, FxBinError]:
    """Backup directory without compression."""
    timestamped_name = f"{source.name}_{datetime.now().strftime(timestamp_format)}"
    backup_path = backup_dir / timestamped_name

    try:
        shutil.copytree(source, backup_path)
        return Success(backup_path)
    except (PermissionError, OSError) as e:
        return Failure(FxBinError(f"Failed to backup directory: {e}"))
```

**Step 4: Run test (expect PASS)**
Run: `poetry run pytest tests/unit/test_backup.py::test_backup_directory_no_compression -v --no-cov`
Expected: PASS

**Step 5: Commit**
```bash
git add fx_bin/backup.py tests/unit/test_backup.py
git commit -m "feat: implement uncompressed directory backup"
```

---

## Task 4: Directory Backup With Compression

**Files:**
- Modify: `fx_bin/backup.py:80-100`
- Test: `tests/unit/test_backup.py`

**Step 1: Write failing test**
```python
def test_backup_directory_with_compression(tmp_path):
    from fx_bin.backup import backup_directory

    test_dir = tmp_path / "mydir"
    test_dir.mkdir()
    (test_dir / "file.txt").write_text("content")

    result = backup_directory(test_dir, tmp_path / "backups", compress=True, timestamp_format="%Y%m%d%H%M%S")

    assert result.is_success()
    backups = list((tmp_path / "backups").glob("mydir_*.tar.gz"))
    assert len(backups) >= 1
    assert backups[0].is_file()
```

**Step 2: Run test (expect FAIL)**
Run: `poetry run pytest tests/unit/test_backup.py::test_backup_directory_with_compression -v --no-cov`
Expected: FAIL with compression not implemented

**Step 3: Implement minimal code**
```python
import tarfile

def _backup_directory_compressed(
    source: Path,
    backup_dir: Path,
    timestamp_format: str,
) -> Result[Path, FxBinError]:
    """Backup directory with compression (.tar.gz)."""
    timestamped_name = f"{source.name}_{datetime.now().strftime(timestamp_format)}.tar.gz"
    backup_path = backup_dir / timestamped_name

    try:
        with tarfile.open(backup_path, "w:gz") as tar:
            tar.add(source, arcname=source.name)
        return Success(backup_path)
    except (PermissionError, OSError, tarfile.TarError) as e:
        return Failure(FxBinError(f"Failed to create compressed backup: {e}"))
```

**Step 4: Run test (expect PASS)**
Run: `poetry run pytest tests/unit/test_backup.py::test_backup_directory_with_compression -v --no-cov`
Expected: PASS

**Step 5: Commit**
```bash
git add fx_bin/backup.py tests/unit/test_backup.py
git commit -m "feat: implement compressed directory backup (.tar.gz)"
```

---

## Task 5: Backup Cleanup (Max Backups)

**Files:**
- Modify: `fx_bin/backup.py:100-120`
- Test: `tests/unit/test_backup.py`

**Step 1: Write failing test**
```python
def test_cleanup_keeps_max_backups(tmp_path):
    from fx_bin.backup import cleanup_old_backups

    # Create 5 backup files
    for i in range(5):
        (tmp_path / f"test_{i:03d}.txt").write_text(f"content{i}")

    result = cleanup_old_backups(tmp_path, pattern="test_*.txt", max_backups=3)

    assert result.is_success()
    remaining = list(tmp_path.glob("test_*.txt"))
    assert len(remaining) == 3
```

**Step 2: Run test (expect FAIL)**
Run: `poetry run pytest tests/unit/test_backup.py::test_cleanup_keeps_max_backups -v --no-cov`
Expected: FAIL with function not found

**Step 3: Implement minimal code**
```python
def cleanup_old_backups(
    backup_dir: Path,
    pattern: str,
    max_backups: int,
) -> Result[List[Path], FxBinError]:
    """Remove old backups, keeping only max_backups most recent."""
    backups = sorted(backup_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)

    if len(backups) <= max_backups:
        return Success([])

    to_remove = backups[max_backups:]
    removed = []

    for backup in to_remove:
        try:
            if backup.is_dir():
                shutil.rmtree(backup)
            else:
                backup.unlink()
            removed.append(backup)
        except (PermissionError, OSError) as e:
            return Failure(FxBinError(f"Failed to remove backup {backup}: {e}"))

    return Success(removed)
```

**Step 4: Run test (expect PASS)**
Run: `poetry run pytest tests/unit/test_backup.py::test_cleanup_keeps_max_backups -v --no-cov`
Expected: PASS

**Step 5: Commit**
```bash
git add fx_bin/backup.py tests/unit/test_backup.py
git commit -m "feat: implement backup cleanup with max-backups limit"
```

---

## Task 6: Click CLI Command

**Files:**
- Modify: `fx_bin/cli.py:1-10` (import section)
- Modify: `fx_bin/cli.py` (add command)
- Test: `tests/integration/test_backup_cli.py`

**Step 1: Write failing test**
```python
import pytest
from click.testing import CliRunner
from fx_bin.cli import cli

def test_backup_command_requires_path():
    runner = CliRunner()
    result = runner.invoke(cli, ['backup'])
    assert result.exit_code != 0
    assert 'Missing argument' in result.output

def test_backup_file_creates_backup(tmp_path):
    runner = CliRunner()

    test_file = tmp_path / "test.txt"
    test_file.write_text("content")

    result = runner.invoke(cli, ['backup', str(test_file), '-d', str(tmp_path / 'backups')])

    assert result.exit_code == 0
    assert (tmp_path / 'backups').exists()
```

**Step 2: Run test (expect FAIL)**
Run: `poetry run pytest tests/integration/test_backup_cli.py::test_backup_command_requires_path -v --no-cov`
Expected: FAIL with command not found

**Step 3: Implement minimal code**

First, add lazy import to `cli.py`:
```python
# At end of cli.py, add:
@cli.command()
@click.argument('path', type=click.Path(exists=True, path_type=Path))
@click.option('-d', '--backup-dir', type=click.Path(path_type=Path), default=None,
              help='Backup directory (default: ./backups)')
@click.option('--compress', is_flag=True, help='Compress directory backups')
@click.option('--max-backups', type=int, default=None,
              help='Maximum number of backups to keep')
@click.option('--timestamp-format', default=DEFAULT_TIMESTAMP_FORMAT,
              help='Timestamp format (default: %%Y%%m%%d%%H%%M%%S)')
def backup(path: Path, backup_dir: Path, compress: bool, max_backups: int, timestamp_format: str):
    """Create timestamped backup of file or directory."""
    from . import backup as backup_module

    if backup_dir is None:
        backup_dir = path.parent / 'backups'

    if path.is_file():
        result = backup_module.backup_file(path, backup_dir, timestamp_format)
    else:
        result = backup_module.backup_directory(path, backup_dir, compress, timestamp_format)

    if result.is_success():
        click.echo(f"Backup created: {result.value()}")

        if max_backups:
            pattern = f"{backup_module.get_base_name(path)}_*"
            if path.is_dir() and compress:
                pattern += ".tar.gz"
            elif path.is_file():
                multi_ext = backup_module.get_multi_ext(path)
                pattern += multi_ext if multi_ext else path.suffix

            cleanup_result = backup_module.cleanup_old_backups(backup_dir, pattern, max_backups)
            if cleanup_result.is_success() and cleanup_result.value():
                click.echo(f"Removed {len(cleanup_result.value())} old backup(s)")

        return 0
    else:
        click.echo(f"Error: {result.error()}", err=True)
        return 1
```

**Step 4: Run test (expect PASS)**
Run: `poetry run pytest tests/integration/test_backup_cli.py::test_backup_command_requires_path tests/integration/test_backup_cli.py::test_backup_file_creates_backup -v --no-cov`
Expected: PASS

**Step 5: Commit**
```bash
git add fx_bin/cli.py tests/integration/test_backup_cli.py
git commit -m "feat: add backup CLI command with options"
```

---

## Task 7: Integration Tests - Compression and Cleanup

**Files:**
- Modify: `tests/integration/test_backup_cli.py`

**Step 1: Write failing test**
```python
def test_backup_directory_with_compress_flag(tmp_path):
    runner = CliRunner()

    test_dir = tmp_path / "mydir"
    test_dir.mkdir()
    (test_dir / "file.txt").write_text("content")

    result = runner.invoke(cli, ['backup', str(test_dir), '-d', str(tmp_path / 'backups'), '--compress'])

    assert result.exit_code == 0
    assert (tmp_path / 'backups').exists()
    backups = list((tmp_path / 'backups').glob("mydir_*.tar.gz"))
    assert len(backups) == 1

def test_backup_with_max_backups_cleanup(tmp_path):
    runner = CliRunner()

    test_file = tmp_path / "test.txt"
    test_file.write_text("content")

    # Create 5 backups
    for _ in range(5):
        runner.invoke(cli, ['backup', str(test_file), '-d', str(tmp_path / 'backups')])

    initial_backups = len(list((tmp_path / 'backups').glob("test_*.txt")))
    assert initial_backups == 5

    # Create one more with max-backups=3
    result = runner.invoke(cli, ['backup', str(test_file), '-d', str(tmp_path / 'backups'), '--max-backups', '3'])

    assert result.exit_code == 0
    remaining_backups = len(list((tmp_path / 'backups').glob("test_*.txt")))
    assert remaining_backups == 3
```

**Step 2: Run test (expect FAIL)**
Run: `poetry run pytest tests/integration/test_backup_cli.py::test_backup_directory_with_compress_flag tests/integration/test_backup_cli.py::test_backup_with_max_backups_cleanup -v --no-cov`
Expected: FAIL (may need fixes to CLI integration)

**Step 3: Fix implementation issues** (if any)
- Check import of DEFAULT_TIMESTAMP_FORMAT
- Verify pattern generation for cleanup
- Ensure proper file handling

**Step 4: Run test (expect PASS)**
Run: `poetry run pytest tests/integration/test_backup_cli.py::test_backup_directory_with_compress_flag tests/integration/test_backup_cli.py::test_backup_with_max_backups_cleanup -v --no-cov`
Expected: PASS

**Step 5: Commit**
```bash
git add tests/integration/test_backup_cli.py
git commit -m "feat: add integration tests for compression and cleanup"
```

---

## Task 8: Error Handling Tests

**Files:**
- Modify: `tests/unit/test_backup.py`

**Step 1: Write failing test**
```python
def test_backup_nonexistent_file():
    from fx_bin.backup import backup_file
    from pathlib import Path

    result = backup_file(Path("/nonexistent/file.txt"), Path("/tmp/backups"))
    assert result.is_failure()
    assert "not found" in str(result.error())

def test_backup_file_permission_error(tmp_path):
    from fx_bin.backup import backup_file

    # Create read-only file
    test_file = tmp_path / "readonly.txt"
    test_file.write_text("content")
    test_file.chmod(0o000)

    backup_dir = tmp_path / "backups"
    backup_dir.chmod(0o000)

    result = backup_file(test_file, backup_dir)
    assert result.is_failure()
```

**Step 2: Run test (expect FAIL)**
Run: `poetry run pytest tests/unit/test_backup.py::test_backup_nonexistent_file tests/unit/test_backup.py::test_backup_file_permission_error -v --no-cov`
Expected: FAIL (error handling may need refinement)

**Step 3: Implement/refine error handling**
- Ensure proper FxBinError messages
- Handle edge cases gracefully

**Step 4: Run test (expect PASS)**
Run: `poetry run pytest tests/unit/test_backup.py::test_backup_nonexistent_file tests/unit/test_backup.py::test_backup_file_permission_error -v --no-cov`
Expected: PASS

**Step 5: Commit**
```bash
git add fx_bin/backup.py tests/unit/test_backup.py
git commit -m "feat: add comprehensive error handling tests"
```

---

## Task 9: Documentation and Help Text

**Files:**
- Modify: `fx_bin/backup.py:1-10` (docstrings)
- Modify: `fx_bin/cli.py` (command docstring)

**Step 1: Add comprehensive docstrings**
```python
#!/usr/bin/env python
"""Backup command for fx.

Provides functionality to create timestamped backups of files and directories
with optional compression and automatic cleanup of old backups.

Features:
- File backup with timestamp
- Directory backup (uncompressed or .tar.gz)
- Multi-extension handling (e.g., .tar.gz)
- Configurable timestamp formats
- Automatic cleanup with --max-backups

Usage:
    fx backup <path> [options]
    fx backup myfile.txt
    fx backup mydir --compress
    fx backup myfile.txt --max-backups 5
"""
```

**Step 2: Add CLI examples in docstring**
```python
@cli.command()
@click.argument('path', type=click.Path(exists=True, path_type=Path))
@click.option('-d', '--backup-dir', type=click.Path(path_type=Path), default=None,
              help='Backup directory (default: ./backups)')
@click.option('--compress', is_flag=True, help='Compress directory backups (.tar.gz)')
@click.option('--max-backups', type=int, default=None,
              help='Maximum number of backups to keep (oldest are removed)')
@click.option('--timestamp-format', default=DEFAULT_TIMESTAMP_FORMAT,
              help='Timestamp format (default: %%Y%%m%%d%%H%%M%%S)')
def backup(path: Path, backup_dir: Path, compress: bool, max_backups: int, timestamp_format: str):
    """Create timestamped backup of file or directory.

    \b
    Examples:
        fx backup document.txt
        fx backup project/ --compress
        fx backup data.json --max-backups 3
        fx backup report.pdf -d /backup/dir

    By default, backups are saved to a 'backups' subdirectory.
    Use --compress to create .tar.gz archives for directories.
    Use --max-backups to automatically remove old backups.
    """
    # ... implementation
```

**Step 3: Verify help text**
Run: `poetry run fx backup --help`
Expected: Clear, readable help text with examples

**Step 4: Commit**
```bash
git add fx_bin/backup.py fx_bin/cli.py
git commit -m "docs: add comprehensive documentation and help text for backup command"
```

---

## Task 10: Final Verification

**Files:**
- All project files

**Step 1: Run linter**
Run: `make lint`
Expected: Zero errors

**Step 2: Run type checker**
Run: `make type-check`
Expected: Zero errors

**Step 3: Run full test suite**
Run: `make test-coverage`
Expected: All tests pass, coverage ≥80%

**Step 4: Run security scan**
Run: `make security-scan`
Expected: No high/critical issues

**Step 5: Manual smoke test**
Run: `poetry run fx backup README.md`
Expected: Backup created in ./backups/

**Step 6: Commit verification**
```bash
git add .
git commit -m "feat: complete fx backup command implementation

- Add backup.py module with file/directory backup support
- Implement timestamped backups with configurable format
- Support compression for directories (--compress flag)
- Add backup limit option (--max-backups)
- Handle multi-part extensions (.tar.gz, .tar.bz2)
- Comprehensive error handling and validation
- Full test coverage (unit + integration)
- Documentation and help text with examples"
```

---

## Summary

This plan follows TDD principles, implementing the `fx backup` command in 10 logical tasks:

1. Module structure with multi-extension handling
2. File backup with timestamps
3. Uncompressed directory backup
4. Compressed directory backup (.tar.gz)
5. Backup cleanup with --max-backups
6. Click CLI command implementation
7. Integration tests for compression and cleanup
8. Error handling and edge cases
9. Documentation and help text
10. Final verification

Each task follows the TDD cycle: write failing test → implement → verify → commit.
