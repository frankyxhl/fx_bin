# Quick Start

Get up and running with fx-bin in 5 minutes.

---

## Installation

### Method 1: pip (Recommended)

The easiest way to install fx-bin:

```bash
pip install fx-bin
```

Upgrade to the latest version:

```bash
pip install --upgrade fx-bin
```

### Method 2: pipx (Isolated Installation)

For a clean, isolated environment:

```bash
pipx install fx-bin
```

Upgrade to the latest version:

```bash
pipx upgrade fx-bin
```

### Method 3: From Source

For development or testing:

```bash
# Clone the repository
git clone https://github.com/frankyxhl/fx_bin.git

# Navigate to the directory
cd fx_bin

# Install using Poetry
poetry install --with dev

# Run fx commands
poetry run fx --help
```

### Verify Installation

Check that fx-bin is installed correctly:

```bash
fx --version
```

You should see output like:

```
FX-Bin v2.4.0
Repository: https://github.com/frankyxhl/fx_bin
```

---

## Your First Commands

### Explore Available Commands

List all available fx commands:

```bash
fx list
```

Get help for the fx CLI:

```bash
fx --help
```

### Count Files

Count files in the current directory:

```bash
fx files .
```

Count only Python files:

```bash
fx files . --pattern "*.py"
```

### Analyze Sizes

Show file sizes in the current directory:

```bash
fx size .
```

Show the 10 largest files:

```bash
fx size . --limit 10 --unit MB
```

### Find Files

Find files containing "config" in their name:

```bash
fx ff config
```

Find Python files:

```bash
fx ff .py
```

### Filter by Extension

Find all Python files, sorted by modification time:

```bash
fx filter py --sort-by modified --reverse
```

Find multiple file types:

```bash
fx filter "jpg,png,gif" --format detailed
```

### Replace Text

Replace "old" with "new" in a file:

```bash
fx replace "old" "new" file.txt
```

Replace text in multiple files:

```bash
fx replace "v1.0" "v2.0" *.py
```

!!! tip
    **Safety First**: `fx replace` uses atomic writes with automatic backup. If the replacement fails, the original file is automatically restored.

---

## Common Workflows

### Daily Development Setup

```bash
# Navigate to today's workspace
fx today

# Count project files
fx files . --pattern "*.py" --recursive

# Find recently modified files
fx filter "py,js,ts" --sort-by modified --reverse --limit 10

# Locate TODO markers
fx ff TODO --exclude node_modules --exclude .git
```

### Project Analysis

```bash
# Analyze file sizes
fx size . --limit 20

# Count files by type
fx files . --pattern "*.py"
fx files . --pattern "*.js"
fx files . --pattern "*.md"

# Find configuration files
fx ff config --exclude backup

# Identify largest directories
fx size . --recursive --sort desc
```

### File Organization

```bash
# Create a backup before organizing
fx backup my_project --compress

# Organize files by date (preview)
fx organize my_project --date-source created --depth 3 --dry-run

# Execute organization
fx organize my_project --date-source created --depth 3
```

---

## Command Reference

For detailed information about each command, see:

- [`fx files`](commands/files.md) - Count files in directories
- [`fx size`](commands/size.md) - Analyze file/directory sizes
- [`fx ff`](commands/ff.md) - Find files by keyword
- [`fx fff`](commands/fff.md) - Find first file matching keyword
- [`fx filter`](commands/filter.md) - Filter files by extension
- [`fx replace`](commands/replace.md) - Replace text in files
- [`fx backup`](commands/backup.md) - Create timestamped backups
- [`fx organize`](commands/organize.md) - Organize files by date
- [`fx root`](commands/root.md) - Find Git project root
- [`fx today`](commands/today.md) - Create daily workspace

---

## Troubleshooting

### Command Not Found

If you see "command not found: fx":

```bash
# Check Python installation
python --version

# Reinstall with pip
pip uninstall fx-bin
pip install fx-bin

# Or with pipx
pipx uninstall fx-bin
pipx install fx-bin
```

### Permission Denied

If you see "Permission denied" errors:

```bash
# macOS/Linux: Use sudo
sudo pip install fx-bin

# Or use a virtual environment
python -m venv .venv
source .venv/bin/activate
pip install fx-bin
```

### Module Not Found

If you see "ModuleNotFoundError":

```bash
# Reinstall with all dependencies
pip install --force-reinstall fx-bin

# Or upgrade pip first
pip install --upgrade pip
pip install --upgrade fx-bin
```

### Version Conflicts

If you have multiple Python versions:

```bash
# Specify Python version
python3.11 -m pip install fx-bin

# Or use pyenv/pyenv-win to manage Python versions
pyenv install 3.11.0
pyenv global 3.11.0
pip install fx-bin
```

---

## Next Steps

1. **Explore** the [Command Reference](commands/files.md) for detailed usage
2. **Try** the [Use Cases](use-cases/daily-workflow.md) for real-world examples
3. **Integrate** fx-bin into your workflow with [Shell Integration](advanced/shell-integration.md)

---

## Getting Help

- **Documentation**: [Full documentation](https://frankyxhl.github.io/fx_bin/)
- **GitHub Issues**: [Report bugs](https://github.com/frankyxhl/fx_bin/issues)
- **GitHub Discussions**: [Ask questions](https://github.com/frankyxhl/fx_bin/discussions)
- **Email**: frank@frankxu.me

---

**Ready to go?** Start using fx-bin today and make your file operations faster, safer, and more efficient! 🚀
