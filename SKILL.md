# FX-BIN Command Reference

A comprehensive guide to all fx-bin commands, installation, and usage patterns.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Installation](#installation)
3. [Available Commands](#available-commands)
4. [Command Details](#command-details)
5. [Common Use Cases](#common-use-cases)
6. [Development Commands](#development-commands)
7. [Architecture Notes](#architecture-notes)
8. [Key Files](#key-files)
9. [Getting Help](#getting-help)
10. [Documentation](#documentation)

## Project Overview

**fx-bin** is a Python utility collection providing command-line tools for file operations, including file counting, size analysis, finding files, text replacement, and a simple upload server. The project is packaged using Poetry and distributed via PyPI.

- **Package Name**: `fx-bin`
- **Repository**: https://github.com/frankyxhl/fx_bin
- **PyPI**: https://pypi.org/project/fx-bin/
- **Python Version**: 3.11+ required
- **Unified CLI**: All utilities accessible through a single `fx` command
- **Key Technologies**: Click (CLI framework), Loguru (logging), Returns (functional programming)

### Key Features

- **Security Hardened**: Protection against path traversal, command injection, and other vulnerabilities
- **Thoroughly Tested**: TDD/BDD methodology with 95%+ test coverage
- **High Performance**: Optimized for large-scale operations
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Modern Python**: Built with Python 3.11+ features and functional programming patterns

## Installation

### Via pip (Recommended)

```bash
pip install fx-bin
```

### Via pipx (For Isolated Installation)

```bash
pipx install fx-bin

# Upgrade to latest version
pipx upgrade fx-bin
```

### From Source

```bash
git clone https://github.com/frankyxhl/fx_bin.git
cd fx_bin
poetry install
poetry run fx --help
```

### Requirements

- Python 3.11 or higher
- Dependencies: click, loguru, returns (automatically installed)

## Available Commands

| Command | Description | Primary Use Case |
|---------|-------------|------------------|
| `fx files` | Count files in directories | Project statistics and file inventory |
| `fx size` | Analyze file/directory sizes | Disk usage analysis and cleanup |
| `fx ff` | Find files by keyword | Quick file location by name |
| `fx fff` | Find first file matching keyword | Fast single file lookup |
| `fx filter` | Filter files by extension | File organization and analysis |
| `fx replace` | Replace text in files | Bulk text replacement with safety |
| `fx backup` | Create timestamped backups | File/directory backup with compression |
| `fx root` | Find Git project root directory | Navigate to project root |
| `fx realpath` | Get absolute path | Resolve paths and symlinks |
| `fx today` | Create/navigate to today's workspace | Daily file organization |
| `fx organize` | Organize files by date | Photo/file organization by date |
| `fx list` | List all available commands | Command discovery |
| `fx help` | Show help information | Quick reference |
| `fx version` | Show version and system info | Version checking |

## Command Details

### 1. fx files - File Counter

Count files in directories with detailed statistics.

```bash
# Basic usage - count files in current directory
fx files

# Count files in specific path
fx files /path/to/directory

# Count files in multiple directories
fx files /path/one /path/two /path/three
```

**Use Cases:**
- Quick project statistics
- Directory content inventory
- File count comparison across directories

**Example Output:**
```
/path/to/directory: 42 files
/another/path: 128 files
```

---

### 2. fx size - Size Analyzer

Analyze file and directory sizes with human-readable output.

```bash
# Basic usage - show sizes in current directory
fx size

# Analyze specific directory
fx size /path/to/directory

# Analyze multiple directories
fx size ~/Downloads ~/Documents ~/Projects
```

**Use Cases:**
- Disk usage analysis
- Finding large directories
- Storage optimization
- Directory size comparison

**Example Output:**
```
/Users/frank/Projects/large_project: 2.4 GB
/Users/frank/Downloads: 1.8 GB
/Users/frank/Documents: 456 MB
```

---

### 3. fx ff - File Finder

Find files whose names contain a keyword, with smart filtering.

```bash
# Basic usage - find files with "test" in name
fx ff test

# Find configuration files
fx ff config

# Find Python files
fx ff .py

# Include normally ignored directories (.git, .venv, node_modules)
fx ff test --include-ignored

# Exclude specific patterns
fx ff test --exclude build --exclude "*.log"

# Complex filtering
fx ff api --exclude build --exclude cache --exclude "*.pyc"

# Find source files excluding tests
fx ff src --exclude "*test*" --exclude "*spec*"
```

**Options:**
- `--include-ignored`: Include `.git`, `.venv`, `node_modules` (default: skip)
- `--exclude PATTERN`: Exclude names or glob patterns (repeatable)

**Smart Defaults:**
- Automatically excludes: `.git`, `.venv`, `node_modules`, `__pycache__`, `.pytest_cache`
- Case-insensitive matching by default
- Recursive search from current directory

**Use Cases:**
- Quick file location in projects
- Finding specific file types
- Locating configuration files
- Code navigation

**Example Output:**
```
./src/config/app.config.json
./tests/fixtures/test.config.yaml
./docs/configuration.md
```

---

### 4. fx fff - Find First File

Alias for `fx ff --first` - returns only the first match and exits immediately.

```bash
# Find first file with 'test' in name
fx fff test

# Find first config file
fx fff config

# Find first Python file
fx fff .py
```

**Use Cases:**
- Quick lookups when you only need one result
- Shell scripts that need a single file path
- Fast navigation to known file types

**Example Output:**
```
./src/test_main.py
```

---

### 5. fx filter - File Filter

Filter files by extension with intelligent sorting capabilities.

```bash
# Find Python files sorted by creation time
fx filter py .

# Multiple extensions with detailed output
fx filter "jpg,png,gif" . --format detailed

# Sort by modification time, newest first
fx filter pdf ~/Documents --sort-by modified --reverse

# Non-recursive search
fx filter txt . --no-recursive

# Simple output format (just paths)
fx filter py . --format simple
```

**Options:**
- `--sort-by TYPE`: Sort by 'created' or 'modified' (default: created)
- `--reverse`: Reverse sort order (newest first)
- `--format FORMAT`: Output format (simple/detailed, default: detailed)
- `--no-recursive`: Don't search subdirectories

**Output Formats:**
- **simple**: Just file paths
- **detailed**: Includes timestamp, size, and relative time

**Use Cases:**
- Finding recent files by type
- Media file organization
- Document management
- Log file analysis

**Example Output (detailed):**
```
2025-09-06 14:23:15  (2 hours ago)  1.2 MB  ./document.pdf
2025-09-06 10:15:42  (6 hours ago)  856 KB  ./report.pdf
2025-09-05 18:30:21  (yesterday)    2.4 MB  ./archive.pdf
```

---

### 6. fx replace - Text Replacer

Replace text across files with atomic operations and safety features.

```bash
# Replace in a specific file
fx replace "old_text" "new_text" file.txt

# Replace across multiple files
fx replace "v1.0" "v2.0" *.py

# Replace in multiple file patterns
fx replace "foo" "bar" src/*.js tests/*.js

# Common use case: version updates
fx replace "version='1.1.0'" "version='1.2.0'" setup.py
```

**Usage:**
```
fx replace SEARCH_TEXT REPLACE_TEXT FILES...
```

**Safety Features:**
- Atomic file writes (write to temp, then rename)
- Binary files automatically skipped
- Reports number of replacements per file
- Automatic backup/restore on failure
- Preserves file permissions

**Use Cases:**
- Bulk text replacement
- Version string updates
- Configuration changes
- Refactoring assistance

**Example Output:**
```
file1.txt: 3 replacements
file2.txt: 1 replacement
file3.txt: 0 replacements (skipped)
```

---

### 7. fx backup - File Backup

Create timestamped backups of files or directories with optional compression.

Backups are created in the same directory as the source file by default.

```bash
# Backup a single file (creates data_20250906_142315.json in same directory)
fx backup data.json

# Backup a directory
fx backup my_project

# Backup with compression (creates .tar.xz archive)
fx backup my_project --compress

# Custom timestamp format
fx backup important.txt --timestamp-format %Y-%m-%d_%H-%M
```

**Options:**
- `--compress`: Compress directory backup as .tar.xz
- `--timestamp-format FORMAT`: Custom strftime format (default: %Y%m%d_%H%M%S)

**Use Cases:**
- Pre-deployment backups
- Configuration file versioning
- Data snapshots
- Project archiving

**Example Output:**
```
Created backup: ./data_20250906_142315.json
Created backup: ./my_project_20250906_142315.tar.xz
```

---

### 8. fx root - Find Git Root

Find the Git project root directory from the current location.

```bash
# Show root directory with description
fx root

# Output just the path (for scripts)
fx root --cd

# Change to root directory (shell usage)
cd "$(fx root --cd)"
```

**Options:**
- `-c, --cd`: Output path only, suitable for cd command

**Use Cases:**
- Navigate to project root
- Shell scripts that need project root
- Build scripts and automation
- Path resolution in tools

**Example Output:**
```
# Without --cd
Git root: /Users/frank/Projects/my_project

# With --cd
/Users/frank/Projects/my_project
```

---

### 9. fx realpath - Absolute Path

Get the absolute, canonical path of a file or directory, resolving symlinks and relative paths.

```bash
# Get absolute path of current directory
fx realpath .

# Resolve relative path
fx realpath ../foo

# Expand home directory
fx realpath ~/Downloads

# Resolve symlink
fx realpath /usr/local/bin/python
```

**Use Cases:**
- Resolve relative paths to absolute
- Follow symlinks to real files
- Path normalization in scripts
- Configuration file generation

**Example Output:**
```
/Users/frank/Projects/fx_bin
/Users/frank/foo
/Users/frank/Downloads
/usr/local/Cellar/python@3.11/3.11.5/bin/python3.11
```

---

### 10. fx today - Daily Workspace

Create and navigate to date-organized workspace directories for daily file management.

```bash
# Navigate to today's workspace (~/Downloads/YYYYMMDD)
fx today

# Custom base directory
fx today --base ~/Projects

# Custom date format
fx today --format %Y-%m-%d

# Output path only (for shell integration)
fx today --cd

# Preview without creating
fx today --dry-run

# Verbose output
fx today --verbose
```

**Options:**
- `--cd, -c`: Output path only (for shell integration)
- `--base, -b`: Base directory (default: ~/Downloads)
- `--format, -f`: Date format string (default: %Y%m%d)
- `--verbose, -v`: Show detailed output
- `--dry-run`: Preview without creating directory

**Use Cases:**
- Daily download organization
- Project work segregation by date
- Screenshot management
- Temporary workspace creation

**Example Output:**
```
Created today's workspace: /Users/frank/Downloads/20250906
```

**Shell Integration:**
After proper setup (see `docs/fx-today-setup.md`), you can use `fx today` to change your shell directory.

---

### 11. fx organize - File Organization

Organize files into date-based directory structures based on creation or modification time.

```bash
# Organize photos by creation date
fx organize ~/Photos

# Custom output directory
fx organize ~/Downloads -o ~/Sorted

# Use year/day structure (depth 2)
fx organize . --depth 2

# Preview without making changes
fx organize . --dry-run

# Include only images
fx organize . -i "*.jpg" -i "*.png"

# Exclude hidden files
fx organize . -e ".*"

# Use modification time instead of creation time
fx organize . --date-source modified

# Auto-rename conflicts
fx organize . --on-conflict rename

# Include hidden files and subdirectories
fx organize ~/Downloads -H -r

# Clean up empty directories after organizing
fx organize . --clean-empty
```

**Options:**
- `-o, --output DIR`: Output directory (default: ./organized)
- `--date-source TYPE`: Use 'created' or 'modified' time (default: created)
- `--depth LEVEL`: Directory depth 1-3 (default: 3)
  - 1: `output/20260110/`
  - 2: `output/2026/20260110/`
  - 3: `output/2026/202601/20260110/`
- `--on-conflict MODE`: Handle conflicts (rename/skip/overwrite/ask, default: rename)
- `-i, --include PATTERN`: Include only matching patterns (repeatable)
- `-e, --exclude PATTERN`: Exclude matching patterns (repeatable)
- `-H, --hidden`: Include hidden files
- `-r, --recursive`: Process subdirectories recursively
- `--clean-empty`: Remove empty directories after organization
- `--fail-fast`: Stop on first error
- `-n, --dry-run`: Preview changes without executing
- `-y, --yes`: Skip confirmation prompt
- `-v, --verbose`: Show detailed progress
- `-q, --quiet`: Suppress progress output

**Use Cases:**
- Photo library organization
- Download folder cleanup
- Document archiving by date
- Media file management
- Time-based file segregation

**Example Output:**
```
Scanning files...
Found 156 files to organize

Preview:
  Downloads/IMG_1234.jpg -> organized/2025/202509/20250906/IMG_1234.jpg
  Downloads/IMG_1235.jpg -> organized/2025/202509/20250906/IMG_1235.jpg
  ...

Proceed with organization? [y/N]: y

Organizing files...
✓ Moved 156 files
✓ Created 3 directories
✓ Removed 2 empty directories

Summary:
  Total files: 156
  Moved: 156
  Skipped: 0
  Errors: 0
```

---

### 12. fx list - Command List

List all available fx commands with brief descriptions.

```bash
fx list
```

**Use Cases:**
- Command discovery
- Quick reference
- New user onboarding

**Example Output:**
```
Available fx commands:

  fx files     - Count files in directories
  fx size      - Analyze file/directory sizes
  fx ff        - Find files by keyword
  fx fff       - Find first file matching keyword
  fx filter    - Filter files by extension
  fx replace   - Replace text in files
  fx backup    - Create timestamped backups
  fx root      - Find Git project root
  fx realpath  - Get absolute path
  fx today     - Daily workspace manager
  fx organize  - Organize files by date
  fx list      - List all commands
  fx help      - Show help information
  fx version   - Show version info
```

---

### 13. fx help - Help Information

Show help information (same as `fx -h` or `fx --help`).

```bash
fx help

# Or use standard help flags
fx -h
fx --help
```

**Use Cases:**
- Quick reference
- Option discovery
- Usage examples

---

### 14. fx version - Version Information

Show version number and repository information.

```bash
fx version
```

**Example Output:**
```
FX-Bin v2.5.6
Repository: https://github.com/frankyxhl/fx_bin
```

**Use Cases:**
- Version verification
- Bug reporting
- Compatibility checking

---

## Common Use Cases

### 1. Project Analysis and Cleanup

```bash
# Count all files in project
fx files .

# Find large directories taking up space
fx size .

# Find old log files
fx filter log . --sort-by modified --reverse

# Find backup files for deletion
fx ff .bak

# Clean up test files
fx files . | grep test
```

### 2. Code Repository Management

```bash
# Navigate to project root
cd "$(fx root --cd)"

# Find all Python source files
fx filter py .

# Find TODO markers
fx ff TODO

# Update version strings
fx replace "version='1.1.0'" "version='1.2.0'" setup.py pyproject.toml

# Backup before major changes
fx backup src --compress
```

### 3. Media and Document Organization

```bash
# Organize photos by date
fx organize ~/Photos -i "*.jpg" -i "*.png" -i "*.heic"

# Find recent PDFs
fx filter pdf ~/Documents --sort-by modified --reverse --limit 10

# Backup important documents (creates backup in same directory)
fx backup ~/Documents/important.xlsx

# Create today's workspace for downloads
fx today --base ~/Downloads
```

### 4. Daily Workflow

```bash
# Start of day: create today's workspace
fx today

# Find configuration files quickly
fx fff config

# Get absolute path for scripts
fx realpath ./relative/path/to/script.sh

# End of day: backup work (creates compressed archive in same directory)
fx backup ~/today_work --compress
```

### 5. Bulk Operations

```bash
# Replace across multiple file types
fx replace "old_api_url" "new_api_url" *.py *.js *.yaml

# Organize downloads by date
fx organize ~/Downloads -o ~/Organized --depth 3 --clean-empty

# Find and count all source files
fx filter "py,js,ts,jsx,tsx" . --format simple | wc -l

# Batch backup multiple directories
for dir in src tests docs; do
    fx backup "$dir" --compress
done
```

### 6. System Maintenance

```bash
# Find large log files
fx filter log /var/log --sort-by modified

# Count configuration files
fx files /etc

# Find error logs
fx ff error /var/log

# Get absolute paths for system files
fx realpath /usr/local/bin/python
```

## Development Commands

### Testing

```bash
# Run all tests
poetry run pytest

# Run without coverage requirement
poetry run pytest --no-cov

# Run with coverage report
poetry run pytest --cov=fx_bin --cov-report=html --cov-report=term-missing

# Run specific test file
poetry run pytest tests/test_filter.py -v

# Run security tests only
poetry run pytest tests/test_*security*.py -v --no-cov

# Run BDD tests
poetry run pytest tests/bdd/ -v

# Run property-based tests (Hypothesis)
poetry run pytest -m hypothesis -v --no-cov

# Run tests in parallel
poetry run pytest -n auto --no-cov

# Run smoke tests (critical paths)
poetry run pytest -m smoke -v
```

### Code Quality

```bash
# Format code with Black
poetry run black fx_bin/ tests/

# Check formatting (dry run)
poetry run black --check fx_bin/ tests/

# Lint with flake8
poetry run flake8 fx_bin/

# Type checking with mypy
poetry run mypy fx_bin/

# Security scan with bandit
poetry run bandit -r fx_bin/

# Check dependency vulnerabilities
poetry run safety check
```

### Build and Package

```bash
# Install dependencies
poetry install --with dev

# Build package
poetry build

# Install locally for testing
pip install -e .

# Test installation
fx --help

# Publish to PyPI (maintainers only)
poetry publish
```

### Development Workflow

```bash
# Clone and setup
git clone https://github.com/frankyxhl/fx_bin.git
cd fx_bin
poetry install --with dev

# Create feature branch
git checkout -b feature/new-command

# Run tests frequently
poetry run pytest --no-cov

# Format and lint before commit
poetry run black fx_bin/ tests/
poetry run flake8 fx_bin/
poetry run mypy fx_bin/

# Commit and push
git add .
git commit -m "feat: add new command"
git push origin feature/new-command
```

## Architecture Notes

### Package Structure

```
fx_bin/
├── __init__.py          # Package initialization
├── cli.py              # Main CLI entry point (fx command)
├── files.py            # File counting utility
├── size.py             # Size analysis utility
├── find_files.py       # File finder (ff/fff)
├── filter.py           # File filter by extension
├── replace.py          # Text replacement utility
├── backup.py           # Backup utility
├── root.py             # Git root finder
├── realpath.py         # Path resolution
├── today.py            # Daily workspace manager
├── organize.py         # File organization by date
├── shared_types.py     # Shared type definitions
└── errors.py           # Custom error classes
```

### Module Pattern

Each utility module follows this pattern:

1. **Core Functionality**: Implements business logic in pure/IO-separated functions
2. **CLI Entry Point**: Provides a `main()` function decorated with Click
3. **Error Handling**: Uses custom exception hierarchy for clean error reporting
4. **Type Safety**: Full type annotations with mypy checking
5. **Testing**: Comprehensive unit, integration, and BDD tests

### Unified CLI

All commands are accessible through the `fx` CLI, registered in `pyproject.toml`:

```toml
[tool.poetry.scripts]
fx = "fx_bin.cli:main"
```

The CLI uses Click's command group pattern for subcommand routing.

### Functional Programming Patterns

The project uses functional programming principles:

- **Railway-Oriented Programming**: `Result[T, E]` and `IOResult[T, E]` for explicit error handling
- **Pure vs IO Separation**: Pure functions for logic, IO functions for side effects
- **Immutable Data**: `@dataclass(frozen=True)` for all data structures
- **Type Safety**: Precise type annotations with `Sequence[T]` for parameters
- **Error Hierarchy**: Polymorphic exception handling with custom error classes

### Testing Strategy

- **TDD/BDD**: Test-driven development with pytest-bdd for behavior scenarios
- **Coverage**: 95%+ code coverage requirement
- **Security**: Dedicated security test suite with bandit integration
- **Property-Based**: Hypothesis for automatic edge case discovery
- **Integration**: Full command-line interface testing with Click's CliRunner

## Key Files

### Configuration Files

- `pyproject.toml`: Project metadata, dependencies, and build configuration
- `poetry.lock`: Locked dependency versions
- `pytest.ini`: (embedded in pyproject.toml) Test configuration
- `.python-version`: Python version specification

### Documentation

- `README.md`: User-facing documentation and quick start
- `CLAUDE.md`: Development guidelines and architecture notes
- `SKILL.md`: This comprehensive command reference (you are here)
- `docs/`: Additional documentation (testing, setup guides)
- `CHANGELOG.md`: Version history and release notes

### Source Code

- `fx_bin/`: Main package directory
- `tests/`: Test suite (unit, integration, BDD)
- `features/`: BDD feature files (Gherkin scenarios)

### Build Artifacts

- `dist/`: Built packages (.whl, .tar.gz)
- `.venv/`: Virtual environment (created by Poetry)
- `htmlcov/`: Coverage reports (generated by pytest-cov)

## Getting Help

### Command-Specific Help

Every command has built-in help:

```bash
fx COMMAND --help

# Examples:
fx files --help
fx filter --help
fx organize --help
```

### General Help

```bash
# Show main help
fx help
fx -h
fx --help

# List all commands
fx list

# Show version
fx version
```

### Online Resources

- **GitHub**: https://github.com/frankyxhl/fx_bin
  - Issues: Report bugs and request features
  - Discussions: Ask questions and share ideas
  - Pull Requests: Contribute improvements

- **PyPI**: https://pypi.org/project/fx-bin/
  - Package metadata and version history

- **Documentation**: See `docs/` directory in repository
  - Testing guides
  - Setup instructions
  - Development workflows

### Contact

- **Author**: Frank Xu
- **Email**: frank@frankxu.me
- **GitHub**: [@frankyxhl](https://github.com/frankyxhl)

## Documentation

### Internal Documentation

- **CLAUDE.md**: Comprehensive development guidelines
  - Git workflow rules
  - Development commands
  - Testing methodology
  - Architecture patterns
  - Functional programming patterns
  - BDD/TDD approach

- **README.md**: User guide and quick reference
  - Installation instructions
  - Quick start examples
  - Security features
  - Contributing guidelines

- **SKILL.md** (this file): Complete command reference
  - All 14 commands documented
  - Use cases and examples
  - Development workflows
  - Architecture overview

### External Documentation

- **Click Documentation**: https://click.palletsprojects.com/
  - CLI framework used by fx-bin
  - Option parsing and command groups

- **Returns Documentation**: https://returns.readthedocs.io/
  - Functional programming library
  - Railway-oriented programming patterns

- **pytest-bdd**: https://pytest-bdd.readthedocs.io/
  - BDD testing with Gherkin syntax

- **Hypothesis**: https://hypothesis.readthedocs.io/
  - Property-based testing framework

### Version History

See `CHANGELOG.md` for detailed version history and release notes.

Current version: **2.5.6**

### Contributing

See the Contributing section in `README.md` for:
- Development process
- Code style guidelines
- Pull request workflow
- Testing requirements

---

**Document Version**: 1.0.0
**Last Updated**: 2025-09-06
**fx-bin Version**: 2.5.6

For the most up-to-date information, visit the [GitHub repository](https://github.com/frankyxhl/fx_bin).
