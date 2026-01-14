# fx-bin

**A powerful, secure, and well-tested collection of Python file operation utilities with a unified CLI.**

!!! abstract
    Why fx-bin?
    **One command** for all file operations | **Safety-first** with atomic operations | **95%+ test coverage** | **Cross-platform** support

---

## Features

### 🎯 Unified Interface
One `fx` command provides access to all file operations - no need to remember multiple tools.

### 🛡️ Safety First
Built-in safeguards prevent accidental data loss, especially in `fx replace` with automatic backup and restore on failure.

### ⚡ High Performance
Optimized algorithms handle large directories and files efficiently with smart caching and indexing.

### 🌍 Cross-Platform
Works seamlessly on Windows, macOS, and Linux with consistent behavior across all platforms.

### ✅ Thoroughly Tested
TDD/BDD methodology with 95%+ code coverage ensures reliability and correctness.

### 🔒 Security Focused
Regular security audits, safe path handling, and input validation protect against common vulnerabilities.

---

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

---

## Quick Preview

```bash
# Show help and available commands
fx --help              # Same as fx -h
fx list                 # Show all commands

# Count Python files
fx files . --pattern "*.py"

# Find large files
fx size . --limit 10 --unit MB

# Find files containing keyword
fx ff TODO

# Filter documents by extension
fx filter ~/Documents "pdf,docx" --format detailed

# Safe text replacement
fx replace "old_text" "new_text" file.txt
```

---

## Commands

| Command | Description | Use Case |
|----------|-------------|-----------|
| `fx files` | Count files in directories | Project statistics, file auditing |
| `fx size` | Analyze file/directory sizes | Disk usage analysis, cleanup planning |
| `fx ff` | Find files by keyword | Debugging, file discovery |
| `fx fff` | Find first matching file | Quick file lookup |
| `fx filter` | Filter files by extension | Content analysis, organization |
| `fx replace` | Replace text in files | Batch updates, refactoring |
| `fx backup` | Create timestamped backups | Safe file operations |
| `fx organize` | Organize files by date | Photo sorting, dataset management |
| `fx root` | Find Git project root | Navigation, script integration |
| `fx today` | Daily workspace manager | Daily work organization |

---

## Getting Started

1. **Install** fx-bin using pip or pipx
2. **Explore** available commands with `fx list`
3. **Learn** command details with `fx <command> --help`
4. **Integrate** into your workflow with shell aliases and scripts

For detailed documentation, see the [Full documentation](docs/index.md).

---

## Project Status

[![PyPI version](https://badge.fury.io/py/fx-bin.svg)](https://badge.fury.io/py/fx-bin)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://github.com/frankyxhl/fx_bin)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](https://github.com/frankyxhl/fx_bin)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)](https://github.com/frankyxhl/fx_bin)
[![Security](https://img.shields.io/badge/security-A+-brightgreen.svg)](https://github.com/frankyxhl/fx_bin)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## Real-World Use Cases

### Development Workflow
```bash
# Start your daily workspace
fx today

# Count Python files
fx files . --pattern "*.py" --recursive

# Find recently modified files
fx filter "py,js,ts" --sort-by modified --reverse --limit 10

# Locate TODO markers
fx ff TODO --exclude node_modules --exclude .git
```

### Project Cleanup
```bash
# Find and analyze large log files
fx ff .log --exclude archive | xargs fx size

# Identify backup files
fx ff .bak --exclude node_modules

# Count configuration files
fx files /etc
```

### Version Updates
```bash
# Backup before changes
fx backup project_dir --compress

# Update version strings
fx replace "version='1.0.0'" "version='2.0.0'" *.py

# Verify changes
grep -r "version='2.0.0'" . | wc -l
```

---

## Contributing

We welcome contributions! See the [Contributing Guide](contributing/index.md) for details.

---

## Links

- **Documentation**: [Full documentation](quick-start.md)
- **GitHub**: [Repository](https://github.com/frankyxhl/fx_bin)
- **PyPI**: [Package page](https://pypi.org/project/fx-bin/)
- **Issues**: [Report bugs](https://github.com/frankyxhl/fx_bin/issues)

---

**Made with ❤️ by Frank Xu**

*For more information, visit the [GitHub repository](https://github.com/frankyxhl/fx_bin)*
