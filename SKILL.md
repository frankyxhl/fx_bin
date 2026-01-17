# SKILL.md - fx-bin AI Assistant Guide

This document helps AI assistants understand and work with the fx-bin project effectively.

## Project Overview

**fx-bin** is a Python CLI tool collection for file operations. It provides a unified `fx` command with subcommands for common file tasks.

- **Package**: `fx-bin` (PyPI)
- **Repository**: https://github.com/frankyxhl/fx_bin
- **Python**: 3.11+
- **License**: MIT

## Installation

```bash
# Via pip
pip install fx-bin

# Via pipx (recommended for CLI tools)
pipx install fx-bin

# From source
git clone https://github.com/frankyxhl/fx_bin.git
cd fx_bin
poetry install
```

## Available Commands

### File Discovery & Analysis

| Command | Description | Example |
|---------|-------------|---------|
| `fx files` | Count files in directories | `fx files . --pattern "*.py"` |
| `fx size` | Analyze file/directory sizes | `fx size . --top 10` |
| `fx ff` | Find files by keyword | `fx ff config` |
| `fx fff` | Find first matching file | `fx fff main.py` |
| `fx filter` | Filter files by extension | `fx filter . --ext py --sort time` |

### File Operations

| Command | Description | Example |
|---------|-------------|---------|
| `fx replace` | Replace text in files | `fx replace "old" "new" file.txt` |
| `fx backup` | Create timestamped backups | `fx backup important.txt` |
| `fx organize` | Organize files by date | `fx organize ./downloads --format %Y/%m` |

### Navigation & Utilities

| Command | Description | Example |
|---------|-------------|---------|
| `fx root` | Find Git project root | `fx root` |
| `fx realpath` | Get absolute path | `fx realpath ./relative/path` |
| `fx today` | Create/navigate to today's workspace | `fx today` |

### Help

| Command | Description |
|---------|-------------|
| `fx list` | List all available commands |
| `fx help` | Show help information |
| `fx version` | Show version and system info |

## Command Details

### fx files
Count files in directories with optional pattern matching.

```bash
fx files .                      # Count all files
fx files . --pattern "*.py"     # Count Python files only
fx files ./src ./tests          # Count in multiple directories
```

### fx size
Analyze and display file/directory sizes.

```bash
fx size .                       # Show size of current directory
fx size . --top 10              # Show top 10 largest items
fx size ~/Downloads --human     # Human-readable sizes
```

### fx ff (find files)
Find files matching a keyword in their name.

```bash
fx ff config                    # Find files containing "config"
fx ff test --ext py             # Find Python test files
fx ff README --case-sensitive   # Case-sensitive search
```

### fx fff (find first file)
Find the first file matching a keyword (useful for scripts).

```bash
fx fff main.py                  # Find first main.py
fx fff config --ext yaml        # Find first YAML config file
```

### fx filter
Filter and list files by extension, sorted by various criteria.

```bash
fx filter . --ext py            # List all Python files
fx filter . --ext py --sort time  # Sort by modification time
fx filter . --ext log --sort size # Sort by size
```

### fx replace
Replace text in files with automatic backup.

```bash
fx replace "old_text" "new_text" file.txt
fx replace "localhost" "production.server.com" config.yaml
fx replace "v1.0" "v2.0" *.md   # Multiple files
```

**Safety features:**
- Automatic backup before modification
- Atomic write operations
- Backup restoration on failure

### fx backup
Create timestamped backups of files or directories.

```bash
fx backup important.txt         # Creates important.txt.20260117_120000.bak
fx backup ./project             # Backup entire directory
fx backup file.txt --dest ~/backups  # Custom destination
```

### fx organize
Organize files into date-based directory structures.

```bash
fx organize ./downloads                    # Organize by file date
fx organize ./photos --format %Y/%m        # Year/Month folders
fx organize ./docs --format %Y-%m-%d       # Date folders
fx organize ./files --dry-run              # Preview changes
```

### fx root
Find the root directory of the current Git repository.

```bash
fx root                         # Print Git root path
cd $(fx root)                   # Navigate to Git root
```

### fx realpath
Get the absolute path of a file or directory.

```bash
fx realpath ./relative/path     # Get absolute path
fx realpath ~/Documents         # Expand home directory
```

### fx today
Create and navigate to today's workspace directory.

```bash
fx today                        # Create/show today's directory
fx today --base ~/workspaces    # Custom base directory
```

## Common Use Cases

### 1. Project Cleanup
```bash
# Find large files
fx size . --top 20

# Count files by type
fx files . --pattern "*.log"
fx files . --pattern "*.tmp"

# Organize old downloads
fx organize ~/Downloads --format %Y/%m
```

### 2. Code Refactoring
```bash
# Find all config files
fx ff config --ext yaml

# Replace deprecated API calls
fx replace "old_api_call" "new_api_call" $(fx ff api --ext py)

# Find the main entry point
fx fff main.py
```

### 3. Backup Workflow
```bash
# Backup before major changes
fx backup ./src
fx backup config.yaml

# Make changes safely with replace
fx replace "debug=true" "debug=false" config.yaml
```

### 4. Daily Development
```bash
# Start daily workspace
fx today

# Navigate to project root
cd $(fx root)

# Find recent Python files
fx filter . --ext py --sort time
```

## Development Commands

When working on the fx-bin codebase:

```bash
# Install development dependencies
poetry install --with dev

# Run tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_replace.py -v

# Run with coverage
poetry run pytest --cov=fx_bin --cov-report=term-missing

# Code quality
poetry run flake8 fx_bin
poetry run mypy fx_bin/
poetry run black fx_bin/ tests/
```

## Architecture Notes

- Each command is a standalone module in `fx_bin/`
- Entry points defined in `pyproject.toml`
- Uses Click for CLI interface
- Uses `returns` library for functional error handling
- Immutable data classes with `@dataclass(frozen=True)`
- Railway-Oriented Programming for error handling

## Key Files

| File | Purpose |
|------|---------|
| `fx_bin/cli.py` | Main CLI entry point |
| `fx_bin/files.py` | File counting |
| `fx_bin/size.py` | Size analysis |
| `fx_bin/find_files.py` | File search |
| `fx_bin/filter.py` | File filtering |
| `fx_bin/replace.py` | Text replacement |
| `fx_bin/backup.py` | Backup creation |
| `fx_bin/organize.py` | File organization |
| `pyproject.toml` | Project configuration |
| `CLAUDE.md` | Detailed development guide |

## Getting Help

```bash
# General help
fx --help

# Command-specific help
fx replace --help
fx organize --help

# List all commands
fx list
```

## Documentation

- **GitHub Pages**: https://frankyxhl.github.io/fx_bin/
- **PyPI**: https://pypi.org/project/fx-bin/
- **CLAUDE.md**: Detailed development instructions in repository root
