# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FX bin is a Python utility collection providing command-line tools for file operations, including file counting, size analysis, finding files, text replacement, and a simple upload server. The project is packaged using Poetry and distributed via PyPI as `fx-bin`.

## Development Commands

### Build and Package
```bash
# Build the package
poetry build

# Install dependencies
poetry install

# Install package locally for development
pip install -e .
```

### Testing
```bash
# Run tests using unittest
python -m unittest tests/test_py_fx_bin.py

# Run tests with tox (if tox is installed)
tox

# Run specific test
python -m unittest tests.test_py_fx_bin.TestPy_fx_bin.test_command_line_interface
```

### Code Quality
```bash
# Run flake8 linting (configured in tox.ini)
flake8 fx_bin

# Run flake8 on specific file
flake8 fx_bin/files.py
```

## Architecture

### Package Structure
- **fx_bin/**: Main package directory containing all utility modules
  - Each utility is a standalone module with a `main()` function entry point
  - Scripts are registered in `pyproject.toml` under `[tool.poetry.scripts]`

### Available Commands
- `fx_upgrade`: Run upgrade program (run_upgrade_program.py)
- `fx_files`: Count files in directories (files.py)
- `fx_size`: Analyze file/directory sizes (size.py)
- `fx_ff`: Find files utility (find_files.py)
- `fx_replace`: Text replacement utility (replace.py)
- `fx_grab_json_api_to_excel`: JSON to Excel converter (pd.py)
- `fx_server`: Simple upload server (upload_server.py)

### Key Dependencies
- **click**: Command-line interface creation
- **loguru**: Logging functionality
- Python 3.11+ required

### Module Pattern
Each utility module follows this pattern:
1. Implements core functionality in functions/classes
2. Provides a `main()` function as the CLI entry point
3. Uses Click decorators for command-line argument parsing
4. Registered as a console script in pyproject.toml

### Testing Approach
- Uses unittest framework
- Tests located in `tests/` directory
- Click's CliRunner used for testing CLI interfaces
- Test files follow `test_*.py` naming convention