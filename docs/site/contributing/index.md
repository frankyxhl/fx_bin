# Contributing Guide

We welcome contributions! This guide will help you get started with contributing to fx-bin.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Poetry for dependency management
- Git for version control
- Familiarity with Click framework

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/YOUR_USERNAME/fx_bin.git
cd fx_bin
```

3. Add upstream remote:

```bash
git remote add upstream https://github.com/frankyxhl/fx_bin.git
```

## Development Setup

### Install Dependencies

```bash
# Install using Poetry
poetry install --with dev

# Activate virtual environment
poetry shell
```

### Verify Installation

```bash
# Check fx commands work
fx --version
fx --help
fx list
```

### Run Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=fx_bin --cov-report=html
```

## Making Changes

### Project Structure

```
fx_bin/
├── fx_bin/           # Source code
│   ├── cli.py       # CLI commands (Click)
│   ├── files.py     # File counting
│   ├── size.py      # Size analysis
│   ├── find_files.py # File finding
│   ├── filter.py    # File filtering
│   ├── replace.py   # Text replacement
│   ├── backup.py    # Backup creation
│   ├── root.py      # Git root finder
│   ├── realpath.py  # Path resolution
│   ├── today.py     # Daily workspace
│   └── organize.py  # File organization
├── tests/            # Test files
├── docs/            # Documentation
└── pyproject.toml   # Project configuration
```

### Adding a New Command

1. **Create command module**:

```python
# fx_bin/mycommand.py
import click
from pathlib import Path

@click.command()
@click.argument("input", type=click.Path(exists=True))
def mycommand(input: Path) -> int:
    """Description of what the command does.

    Examples:
      fx mycommand file.txt  # Process file.txt
    """
    # Implementation here
    click.echo(f"Processing: {input}")
    return 0
```

2. **Register command in CLI**:

```python
# fx_bin/cli.py
from .mycommand import mycommand

# Register with fx group
@cli.command()
@click.argument("input", type=click.Path(exists=True))
def mycommand(input: Path) -> int:
    """Description."""
    from . import mycommand as mycommand_module
    return mycommand_module.mycommand(input)

# Add to COMMANDS_INFO
COMMANDS_INFO: List[Tuple[str, str]] = [
    # ... existing commands
    ("mycommand", "Description of mycommand"),
]
```

3. **Add tests**:

```python
# tests/test_mycommand.py
from click.testing import CliRunner
from fx_bin.cli import mycommand

def test_mycommand(tmp_path):
    """Test mycommand."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    runner = CliRunner()
    result = runner.invoke(mycommand, [str(test_file)])

    assert result.exit_code == 0
    assert "Processing:" in result.output
```

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for function signatures
- Write docstrings for all functions and commands
- Keep functions focused and small
- Use descriptive variable names

## Testing

### Test Structure

```python
# tests/test_files.py
import pytest
from pathlib import Path
from fx_bin.cli import files

def test_files_basic(tmp_path):
    """Test basic file counting."""
    # Create test files
    (tmp_path / "file1.txt").touch()
    (tmp_path / "file2.txt").touch()

    # Run command
    runner = CliRunner()
    result = runner.invoke(files, [str(tmp_path)])

    # Assertions
    assert result.exit_code == 0
    assert "2" in result.output
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_files.py

# Run specific test
pytest tests/test_files.py::test_files_basic

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=fx_bin --cov-report=html
```

### Writing Tests

1. **Test happy path**: Normal operation
2. **Test edge cases**: Empty input, special characters
3. **Test errors**: Invalid input, permissions
4. **Test performance**: Large files, many files

## Documentation

### Command Documentation

Each command needs comprehensive documentation in `docs/site/commands/`:

```markdown
# Command: fx mycommand

Brief description of what the command does.

## Overview
Detailed overview...

## Usage
```bash
fx mycommand [OPTIONS] input
```

## Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `input` | path | Yes | Input file |

## Examples
### Basic Usage
```bash
fx mycommand file.txt
```
```

### Update Docs Site

After adding a new command:

1. Create documentation file
2. Add to navigation (if needed)
3. Update Quick Start guide (if appropriate)
4. Test documentation builds

## Pull Request Process

### Before Submitting

1. **Run tests**: Ensure all tests pass
2. **Check code style**: Run linter if configured
3. **Update documentation**: Update relevant docs
4. **Add tests**: Ensure new code is tested
5. **Update CHANGELOG**: Add entry to changelog

### Submitting PR

1. Create feature branch:

```bash
git checkout -b feature/my-feature
```

2. Make changes and commit:

```bash
git add .
git commit -m "feat: add my new feature"
```

3. Push to your fork:

```bash
git push origin feature/my-feature
```

4. Create Pull Request on GitHub

### PR Description Template

```markdown
## Description
Brief description of changes...

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How did you test these changes?

## Checklist
- [ ] Tests pass
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Self-review completed
```

## Getting Help

- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and discuss ideas
- **Email**: frank@frankxu.me

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Happy contributing!** 🚀 We look forward to your contributions!
