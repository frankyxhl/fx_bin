# fx-bin

[![PyPI version](https://badge.fury.io/py/fx-bin.svg)](https://badge.fury.io/py/fx-bin)
[![Python](https://img.shields.io/pypi/pyversions/fx-bin.svg)](https://pypi.org/project/fx-bin/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](https://github.com/frankyxhl/fx_bin)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)](https://github.com/frankyxhl/fx_bin)
[![Security](https://img.shields.io/badge/security-A+-brightgreen.svg)](https://github.com/frankyxhl/fx_bin)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**A powerful, secure, and well-tested collection of Python file operation utilities with a unified CLI.**

## 🎉 New in v1.2.0

Introducing **`fx filter`** - A powerful file filtering utility that helps you find and organize files by extension with intelligent sorting options!

```bash
# Find all Python files sorted by creation time
fx filter . py

# Find multiple file types with detailed output
fx filter . "py,txt,json" --format detailed

# Sort by modification time, newest first
fx filter ~/Documents pdf --sort-by mtime --reverse
```

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
- 📈 **JSON to Excel** - Convert JSON data to Excel spreadsheets
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

# Count Python files
fx files . --pattern "*.py"

# Find large files
fx size . --limit 10 --unit MB

# Filter documents by extension
fx filter ~/Documents "pdf,docx" --format detailed

# Find files containing keyword
fx ff . "TODO"

# Safe text replacement
fx replace . "old_text" "new_text" --preview
```

## 📦 Installation

### Via pip (Recommended)

```bash
pip install fx-bin
```

### Via pipx (For Isolated Installation)

```bash
pipx install fx-bin
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
- Optional: pandas for Excel operations (`pip install fx-bin[excel]`)

## 🛠️ Commands

### Overview

| Command | Description | Key Features |
|---------|-------------|--------------|
| `fx files` | Count files in directories | Pattern matching, recursive search, detailed stats |
| `fx size` | Analyze file/directory sizes | Human-readable units, sorting, limit results |
| `fx ff` | Find files by keyword | Multiple search modes, content search, regex support |
| `fx filter` | Filter files by extension | Time-based sorting, multiple formats, recursive search |
| `fx replace` | Replace text in files | Preview mode, backup creation, pattern exclusion |
| `fx json2excel` | Convert JSON to Excel | Automatic formatting, multiple sheets |
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
fx filter ~/Documents pdf --sort-by mtime --reverse

# Non-recursive search with count
fx filter . txt --no-recursive --format count
```

**Options:**
- `--sort-by`: Sort by 'ctime' (creation) or 'mtime' (modification)
- `--reverse`: Reverse sort order (newest first)
- `--format`: Output format (simple/detailed/count)
- `--no-recursive`: Don't search subdirectories

**Output Formats:**
- **simple**: Just file paths
- **detailed**: Includes timestamp and relative time
- **count**: Summary statistics

#### 🔍 fx ff - File Finder

Find files containing specific keywords or patterns.

```bash
# Find files containing "TODO"
fx ff . "TODO"

# Case-insensitive search
fx ff . "config" --ignore-case

# Search only in Python files
fx ff . "import" --extension py

# Use regex pattern
fx ff . "^class.*Model" --regex
```

**Options:**
- `--extension`: Limit to specific file extensions
- `--ignore-case`: Case-insensitive search
- `--regex`: Use regular expressions
- `--content`: Search file contents

#### 🔄 fx replace - Text Replacer

Safely replace text across multiple files with preview and backup options.

```bash
# Preview changes without applying
fx replace . "old_text" "new_text" --preview

# Create backups before replacing
fx replace . "v1.0" "v2.0" --backup

# Exclude certain patterns
fx replace . "foo" "bar" --exclude "*.min.js"

# Interactive mode
fx replace . "test" "production" --interactive
```

**Options:**
- `--preview`: Show changes without applying
- `--backup`: Create .bak files
- `--exclude`: Exclude file patterns
- `--interactive`: Confirm each replacement

**Safety Features:**
- Always preview changes first
- Automatic backup creation available
- Pattern exclusion for sensitive files
- Dry-run mode for testing

#### 📈 fx json2excel - JSON to Excel Converter

Convert JSON files to Excel spreadsheets.

```bash
# Basic conversion
fx json2excel data.json output.xlsx

# With custom sheet name
fx json2excel data.json report.xlsx --sheet "Results"

# Pretty formatting
fx json2excel data.json output.xlsx --pretty
```

**Options:**
- `--sheet`: Excel sheet name
- `--pretty`: Apply formatting

## 📚 Usage Examples

### Real-World Scenarios

#### 1. Project Cleanup
```bash
# Find and count test files
fx files . --pattern "*test*.py"

# Identify large log files
fx size . --pattern "*.log" --limit 5 --unit MB

# Remove old backup files
fx ff . ".bak" | xargs rm -f
```

#### 2. Codebase Analysis
```bash
# Count source files by type
fx filter . "py,js,ts,jsx,tsx" --format count

# Find TODO comments
fx ff . "TODO" --extension "py,js"

# Update version strings
fx replace . "version='1.1.0'" "version='1.2.0'" --preview
```

#### 3. Data Processing
```bash
# Find recent data files
fx filter ./data csv --sort-by mtime --reverse --limit 10

# Convert JSON reports to Excel
fx json2excel report.json summary.xlsx

# Analyze dataset sizes
fx size ./datasets --unit GB
```

#### 4. System Maintenance
```bash
# Find old log files
fx filter /var/log "log,txt" --sort-by mtime --format detailed

# Count configuration files
fx files /etc --pattern "*.conf"

# Search for error patterns
fx ff /var/log "ERROR" --ignore-case
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