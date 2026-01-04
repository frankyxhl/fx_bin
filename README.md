# fx-bin

[![PyPI version](https://badge.fury.io/py/fx-bin.svg)](https://badge.fury.io/py/fx-bin)
[![Python](https://img.shields.io/pypi/pyversions/fx-bin.svg)](https://pypi.org/project/fx-bin/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](https://github.com/frankyxhl/fx_bin)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)](https://github.com/frankyxhl/fx_bin)
[![Security](https://img.shields.io/badge/security-A+-brightgreen.svg)](https://github.com/frankyxhl/fx_bin)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**A powerful, secure, and well-tested collection of Python file operation utilities with a unified CLI.**

## 📋 Table of Contents

- [Why fx-bin?](#-why-fx-bin)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Commands](#-commands)
- [Usage Examples](#-usage-examples)
- [Development](#-development)
- [Testing](#-testing)
- [Security](#-security)
- [Contributing](#-contributing)
- [License](#-license)

## 🤔 Why fx-bin?

**fx-bin** addresses common pain points in file operations:

- **Unified Interface**: One command (`fx`) for all file operations - no need to remember multiple tools
- **Safety First**: Built-in safeguards prevent accidental data loss (especially in `fx replace`)
- **Performance**: Optimized algorithms handle large directories and files efficiently
- **Cross-Platform**: Works seamlessly on Windows, macOS, and Linux
- **Developer Friendly**: Comprehensive testing (95%+ coverage) and clean, maintainable code
- **Security Focused**: Regular security audits, safe path handling, and input validation
- **Modern Python**: Built with Python 3.11+ features and best practices

Whether you're organizing files, analyzing disk usage, performing bulk text replacements, or filtering files by type, fx-bin provides a reliable, fast, and safe solution.

## ✨ Features

### Core Capabilities

- 📁 **File Counting** - Quickly count files in directories with pattern matching
- 📊 **Size Analysis** - Analyze file and directory sizes with human-readable output
- 🔍 **File Finding** - Search for files by keywords with multiple search strategies
- 🎯 **File Filtering** - Filter files by extension with intelligent sorting (NEW in v1.2.0!)
- 🔄 **Text Replacement** - Safe, bulk text replacement across files with backup options
- 💾 **File Backup** - Create timestamped backups of files and directories (NEW in v1.4.0!)

- 📋 **Command Listing** - Built-in help and command discovery

### Technical Excellence

- 🛡️ **Security Hardened** - Protection against path traversal, command injection, and other vulnerabilities
- ✅ **Thoroughly Tested** - TDD/BDD methodology with 95%+ test coverage
- 🚀 **High Performance** - Optimized for large-scale operations
- 🔧 **Extensible** - Clean architecture for easy feature additions
- 📝 **Well Documented** - Comprehensive documentation and examples

## 🚀 Quick Start

```bash
# Install fx-bin
pip install fx-bin  # or: pipx install fx-bin

# Show help and available commands
fx help              # Same as fx -h
fx list              # Show all available commands

# Count Python files
fx files . --pattern "*.py"

# Find large files
fx size . --limit 10 --unit MB

# Filter documents by extension
fx filter ~/Documents "pdf,docx" --format detailed

# Find files containing keyword
fx ff TODO

# Safe text replacement
fx replace "old_text" "new_text" file.txt
```

## 📦 Installation

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
- No external dependencies required for core functionality

## 🛠️ Commands

### Overview

| Command | Description | Key Features |
|---------|-------------|--------------|
| `fx files` | Count files in directories | Pattern matching, recursive search, detailed stats |
| `fx size` | Analyze file/directory sizes | Human-readable units, sorting, limit results |
| `fx ff` | Find files by keyword | Multiple search modes, content search, regex support |
| `fx filter` | Filter files by extension | Time-based sorting, multiple formats, recursive search |
| `fx replace` | Replace text in files | Atomic file operations, safe text replacement |
| `fx backup` | Create timestamped backups | File/dir backup, compression |
| `fx list` | List all available commands | Help and usage information |

### Detailed Command Documentation

#### 📁 fx files - File Counter

Count files in directories with powerful filtering options.

```bash
# Basic usage
fx files /path/to/directory

# Count only Python files
fx files . --pattern "*.py"

# Exclude test files
fx files . --exclude "*test*"

# Recursive search with details
fx files . --recursive --detailed
```

**Options:**
- `--pattern`: File pattern to match (glob syntax)
- `--exclude`: Pattern to exclude files
- `--recursive`: Search subdirectories
- `--detailed`: Show detailed statistics

#### 📊 fx size - Size Analyzer

Analyze file and directory sizes with flexible output options.

```bash
# Show top 10 largest files
fx size . --limit 10

# Display sizes in MB
fx size . --unit MB

# Sort by size ascending
fx size . --sort asc

# Include hidden files
fx size . --all
```

**Options:**
- `--limit`: Number of results to show
- `--unit`: Size unit (B, KB, MB, GB)
- `--sort`: Sort order (asc/desc)
- `--all`: Include hidden files

#### 🎯 fx filter - File Filter (NEW in v1.2.0!)

Filter files by extension with intelligent sorting capabilities.

```bash
# Find Python files sorted by creation time
fx filter . py

# Multiple extensions
fx filter . "jpg,png,gif" --format detailed

# Sort by modification time, newest first
fx filter ~/Documents pdf --sort-by modified --reverse

# Non-recursive search
fx filter txt --no-recursive
```

**Options:**
- `--sort-by`: Sort by 'created' (creation time) or 'modified' (modification time)
- `--reverse`: Reverse sort order (newest first)
- `--format`: Output format (simple/detailed, default: detailed)

**Output Formats:**
- **simple**: Just file paths
- **detailed**: Includes timestamp, size, and relative time

#### 🔍 fx ff - File Finder

Find files whose names contain a keyword, with powerful filtering options and smart exclusions.

```bash
# Basic usage: Find files containing "test" in their names
fx ff test

# Find configuration files
fx ff config

# Find all Python files (using partial match)
fx ff .py

# Include normally ignored directories (.git, .venv, node_modules)
fx ff test --include-ignored

# Exclude specific directories or patterns
fx ff test --exclude build --exclude "*.log"

# Complex filtering example: find "api" files but exclude build and cache directories
fx ff api --exclude build --exclude cache --exclude "*.pyc"

# Find source files while excluding test directories
fx ff src --exclude "*test*" --exclude "*spec*"

# Case-sensitive search for specific components
fx ff Component --exclude node_modules
```

**Real-World Use Cases:**

```bash
# Development workflow: Find all TODO comments in code files
fx ff TODO --exclude node_modules --exclude .git

# Project cleanup: Find all backup files
fx ff .bak

# Debug logging: Find all log files
fx ff .log --exclude archive

# Configuration management: Find all config files across subdirectories
fx ff config --exclude backup

# Library hunting: Find specific library files
fx ff jquery --exclude node_modules --exclude dist

# Testing: Find test files but exclude coverage reports
fx ff test --exclude coverage --exclude .nyc_output
```

**Options:**
- `--include-ignored`: Include `.git`, `.venv`, `node_modules` (default skips these heavy directories)
- `--exclude NAME`: Exclude names or glob patterns; repeatable for complex filtering

#### 🔄 fx replace - Text Replacer

Replace text across multiple files with atomic write operations.

```bash
# Replace in a specific file
fx replace "old_text" "new_text" file.txt

# Replace across multiple files
fx replace "v1.0" "v2.0" *.py

# Replace in all matching files
fx replace "foo" "bar" src/*.js tests/*.js
```

**Usage:**
```
fx replace SEARCH_TEXT REPLACE_TEXT FILES...
```

**Safety Features:**
- Atomic file writes prevent corruption
- Binary files are automatically skipped
- Reports number of replacements made per file

#### 💾 fx backup - File Backup (NEW in v1.4.0!)

Create timestamped backups of files or directories with optional compression.

```bash
# Backup a single file
fx backup data.json

# Backup a directory with compression
fx backup my_project --compress

# Custom backup directory
fx backup config.yaml --backup-dir ./archive

# Custom timestamp format
fx backup important.txt --timestamp-format %Y-%m-%d_%H-%M
```

**Options:**
- `--backup-dir`: Directory to store backups (default: 'backups')
- `--compress`: Compress directory backup as .tar.xz
- `--timestamp-format`: Custom strftime format for the backup timestamp

#### 📅 fx today - Daily Workspace Manager

Create and navigate to date-organized workspace directories for daily file management.

```bash
# Navigate to today's workspace (~/Downloads/YYYYMMDD)
fx today

# Custom base directory
fx today --base ~/Projects

# Custom date format
fx today --format %Y-%m-%d  # Creates ~/Downloads/2025-09-06

# Output path for shell scripts
fx today --cd

# Dry run to see what would be created
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

**Shell Integration:**
With proper setup, `fx today` can change your shell directory:
```bash
# After running setup script
$ fx today
📅 Changed to today's workspace: /Users/you/Downloads/20250906

# Or use aliases
$ ft  # Short alias for fx today
```

See [fx-today-setup.md](docs/fx-today-setup.md) for shell integration setup.

## 📚 Usage Examples

### Real-World Scenarios

#### 1. Project Cleanup
```bash
# Find and count test files
fx files . --pattern "*test*.py"

# Identify large log files
fx size . --pattern "*.log" --limit 5 --unit MB

# Find backup files for review
fx ff .bak
```

#### 2. Codebase Analysis
```bash
# Find all source files with details
fx filter "py,js,ts,jsx,tsx"

# Find TODO markers in filenames
fx ff TODO

# Update version strings in Python files
fx replace "version='1.1.0'" "version='1.2.0'" *.py
```

#### 3. Data Processing
```bash
# Find recent data files
fx filter csv ./data --sort-by modified --reverse --limit 10

# Analyze dataset sizes
fx size ./datasets
```

#### 4. System Maintenance
```bash
# Find log files sorted by modification time
fx filter "log,txt" /var/log --sort-by modified

# Count configuration files
fx files /etc

# Find error-related files
fx ff error
```

## 🔧 Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/frankyxhl/fx_bin.git
cd fx_bin

# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -
# or: pipx install poetry

# Install dependencies
poetry install --with dev

# Activate virtual environment
poetry shell
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=fx_bin --cov-report=html

# Run specific test file
poetry run pytest tests/test_filter.py -v

# Run security tests
poetry run pytest tests/test_*security*.py -v
```

### Code Quality

```bash
# Format code
poetry run black fx_bin/ tests/

# Lint code
poetry run flake8 fx_bin/

# Type checking
poetry run mypy fx_bin/

# Security scan
poetry run bandit -r fx_bin/
```

### Building and Publishing

```bash
# Build package
poetry build

# Test installation
pip install dist/fx_bin-*.whl  # or: poetry run fx --help

# Publish to PyPI
poetry publish
```

## 🧪 Testing

fx-bin follows a comprehensive testing strategy:

### Testing Methodology
- **TDD (Test-Driven Development)**: All features developed with tests first
- **BDD (Behavior-Driven Development)**: User scenarios tested with Gherkin syntax
- **Coverage**: Maintaining 95%+ code coverage
- **CI/CD**: Automated testing on every commit

### Test Categories
- **Unit Tests**: Individual function testing
- **Integration Tests**: Component interaction testing
- **Security Tests**: Vulnerability and safety testing
- **Performance Tests**: Benchmarking and optimization
- **Edge Cases**: Boundary and error condition testing

### Running Different Test Suites

```bash
# Fast unit tests only
poetry run pytest -m "not slow"

# Security tests only
poetry run pytest -m security

# Integration tests
poetry run pytest -m integration

# Performance benchmarks
poetry run pytest -m performance
```

## 🔒 Security

### Security Features

- **Path Traversal Protection**: All file operations validate paths
- **Input Sanitization**: User inputs are cleaned and validated
- **Safe Defaults**: Conservative defaults prevent accidents
- **Command Injection Prevention**: No shell execution with user input
- **Regular Security Audits**: Automated scanning with bandit and safety

### Security Testing

```bash
# Run security test suite
poetry run pytest tests/test_*security*.py -v

# Static security analysis
poetry run bandit -r fx_bin/

# Dependency vulnerability check
poetry run safety check
```

### Reporting Security Issues

If you discover a security vulnerability, please email frank@frankxu.me directly instead of opening a public issue.

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your feature
4. Implement the feature
5. Ensure all tests pass (`poetry run pytest`)
6. Check code quality (`poetry run black . && poetry run flake8`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

### Guidelines

- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Keep commits atomic and descriptive
- Ensure CI passes before requesting review

### Areas for Contribution

- New file operation commands
- Performance improvements
- Documentation enhancements
- Bug fixes
- Test coverage improvements
- Platform-specific optimizations

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Click](https://click.palletsprojects.com/) for elegant CLI creation
- Testing powered by [pytest](https://pytest.org/)
- Code formatting by [Black](https://black.readthedocs.io/)

## 📞 Contact

- Author: Frank Xu
- Email: frank@frankxu.me
- GitHub: [@frankyxhl](https://github.com/frankyxhl)
- PyPI: [fx-bin](https://pypi.org/project/fx-bin/)

---

**Made with ❤️ by Frank Xu**

*For more information, visit the [GitHub repository](https://github.com/frankyxhl/fx_bin)*
