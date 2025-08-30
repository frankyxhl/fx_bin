=======
FX Bin
=======

.. image:: https://img.shields.io/pypi/v/fx-bin.svg
   :target: https://pypi.org/project/fx-bin/
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/fx-bin.svg
   :target: https://pypi.org/project/fx-bin/
   :alt: Python Versions

.. image:: https://img.shields.io/github/license/fx/fx_bin.svg
   :target: https://github.com/fx/fx_bin/blob/main/LICENSE
   :alt: License

A comprehensive Python utility collection providing command-line tools for file operations, directory analysis, text manipulation, and more. Built with security and safety as top priorities.

**Key Features:**

* 🔒 Security-first design with extensive safety checks
* ⚡ Fast and efficient file operations
* 🛡️ Atomic file operations to prevent data loss
* 📊 Comprehensive file and directory analysis
* 🔍 Advanced file search capabilities
* 🎯 **NEW**: Unified CLI with single ``fx`` command
* 🚀 Production-ready with extensive test coverage

Installation
============

Using pip (recommended)
------------------------

.. code-block:: bash

    pip install --upgrade fx-bin

Using Poetry
------------

.. code-block:: bash

    poetry add fx-bin

From source
-----------

.. code-block:: bash

    git clone https://github.com/fx/fx_bin.git
    cd fx_bin
    pip install -e .

Quick Start
===========

FX Bin provides a unified ``fx`` command with subcommands for all utilities:

.. code-block:: bash

    # List all available commands
    fx list
    
    # Get help for any command
    fx --help
    fx COMMAND --help

Available fx Commands
---------------------

.. code-block:: text

    fx files       - Count files in directories
    fx size        - Analyze file/directory sizes
    fx ff          - Find files by keyword
    fx filter      - Filter files by extension and sort by time
    fx replace     - Replace text in files
    fx json2excel  - Convert JSON to Excel
    fx list        - List all available commands

Examples
--------

.. code-block:: bash

    # Count files in current directory
    fx files
    
    # Analyze directory sizes
    fx size /path/to/directory
    
    # Find Python files
    fx ff "*.py"
    
    # Replace text in files
    fx replace "old_text" "new_text" file.txt
    
    # Convert JSON to Excel
    fx json2excel data.json output.xlsx

Available Commands
==================

fx size - Directory Size Analyzer
----------------------------------

Analyze and display file and directory sizes in human-readable format.

.. code-block:: bash

    fx size                    # Current directory
    fx size /path/to/dir       # Specific directory

**Features:**

* Human-readable size formatting (B, KB, MB, GB)
* Sort by size automatically
* Handle symbolic links safely
* Recursive directory traversal with loop detection

fx files - File Counter
------------------------

Count files in directories with detailed statistics.

.. code-block:: bash

    fx files                   # Current directory
    fx files /path/to/dir      # Specific directory

**Features:**

* Fast file counting
* Extension-based grouping
* Hidden files detection
* Recursive counting with depth control

fx ff - Find Files
------------------

Advanced file search utility with pattern matching.

.. code-block:: bash

    fx ff "*.py"               # Find Python files
    fx ff config               # Find files with 'config' in name

**Features:**

* Glob pattern matching
* Content search
* Size filtering
* Date filtering
* Regular expression support

fx filter - File Filter by Extension
-------------------------------------

Filter files by extension and sort by creation or modification time.

.. code-block:: bash

    fx filter mp4                           # Find all .mp4 files
    fx filter "mp4,avi,mkv"                  # Multiple extensions
    fx filter mp4 --sort-by modified        # Sort by modification time
    fx filter mp4 --no-recursive            # Current directory only
    fx filter mp4 --reverse                 # Oldest first
    fx filter mp4 --format detailed         # Show size and timestamps

**Features:**

* Filter by single or multiple extensions
* Sort by creation time (default) or modification time
* Recursive or non-recursive search
* Simple, detailed, or count-only output formats
* Reverse sorting option

fx replace - Text Replacement
------------------------------

Safe text replacement in files with atomic operations.

.. code-block:: bash

    fx replace "old" "new" file.txt              # Single file
    fx replace "old" "new" *.txt                 # Multiple files

**Features:**

* Atomic file operations (no data loss)
* UTF-8 encoding support
* Permission preservation
* Backup creation
* Dry-run mode for preview

fx json2excel - JSON to Excel Converter
-----------------------------------------

Convert JSON API responses to Excel spreadsheets.

.. code-block:: bash

    fx json2excel data.json output.xlsx          # Convert JSON file
    fx json2excel https://api.example.com/data output.xlsx  # From API

**Note:** Requires pandas installation: ``pip install fx-bin[excel]``

Security & Safety
=================

FX Bin prioritizes security and safety in all operations:

**Security Features:**

* ✅ **Path Traversal Protection**: Prevents directory traversal attacks
* ✅ **Input Sanitization**: All user inputs are validated and sanitized
* ✅ **Safe File Operations**: Atomic operations prevent data corruption
* ✅ **Resource Limits**: Memory and CPU usage constraints
* ✅ **Symlink Loop Detection**: Prevents infinite loops in directory traversal

**Safety Guarantees:**

* No file descriptor leaks
* Graceful error handling
* Original file permissions preserved
* Automatic backup options
* Dry-run mode for preview

Development
===========

Setting up development environment
-----------------------------------

.. code-block:: bash

    # Clone the repository
    git clone https://github.com/fx/fx_bin.git
    cd fx_bin
    
    # Install with Poetry (recommended)
    poetry install --with dev
    
    # Or using pip
    pip install -e .
    pip install -r requirements_dev.txt

Running tests
-------------

.. code-block:: bash

    # Run all tests with pytest
    poetry run pytest
    
    # Run specific test modules
    poetry run pytest tests/test_cli.py -v
    poetry run pytest tests/test_size.py -v
    
    # Run with coverage
    poetry run pytest --cov=fx_bin --cov-report=html
    
    # Run security tests only
    poetry run pytest tests/test_*security*.py -v --no-cov

Test Coverage
-------------

The project maintains comprehensive test coverage:

* Security vulnerability tests
* File operation safety tests
* Performance benchmarks
* Integration tests
* Unit tests for all modules
* CLI command tests (new in v0.10.0)

Code Quality
------------

.. code-block:: bash

    # Run linting
    poetry run flake8 fx_bin/
    
    # Run type checking
    poetry run mypy fx_bin/
    
    # Format code
    poetry run black fx_bin/ tests/

Architecture
============

Project Structure
-----------------

.. code-block:: text

    fx_bin/
    ├── fx_bin/              # Main package
    │   ├── cli.py           # NEW: Unified CLI entry point
    │   ├── common.py        # Shared utilities
    │   ├── size.py          # Size analyzer implementation
    │   ├── files.py         # File counter implementation
    │   ├── find_files.py    # File finder implementation
    │   ├── replace.py       # Text replacement implementation
    │   └── pd.py            # JSON to Excel converter
    ├── tests/               # Test suite
    │   ├── test_cli.py      # NEW: CLI tests
    │   ├── runners/         # Test execution scripts
    │   └── test_*.py        # Test modules
    └── docs/                # Documentation
        └── testing/         # Testing guides

Design Principles
-----------------

1. **Security First**: All operations validated for security
2. **Fail Safe**: Graceful error handling and recovery
3. **Atomic Operations**: Prevent partial updates
4. **Resource Efficient**: Memory and CPU constraints
5. **Cross-Platform**: Works on Linux, macOS, Windows
6. **User-Friendly**: Unified CLI for better usability (new in v0.10.0)

Requirements
============

* Python 3.11 or higher
* click (CLI framework)
* loguru (logging)
* psutil (system operations)
* pandas (optional, for Excel features)

Command Reference
=================

All commands are accessed through the unified ``fx`` CLI:

.. code-block:: bash

    fx files                      # Count files
    fx size                       # Analyze sizes
    fx ff "*.py"                  # Find files
    fx replace "old" "new" file   # Replace text
    fx json2excel data.json out   # Convert JSON to Excel
    fx list                       # List all commands

The new CLI provides:

* Single entry point (``fx``)
* Consistent command structure
* Built-in command listing (``fx list``)
* Better help system (``fx --help``, ``fx COMMAND --help``)

Contributing
============

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (``git checkout -b feature/amazing-feature``)
3. Make your changes
4. Run tests to ensure everything works
5. Commit your changes (``git commit -m 'Add amazing feature'``)
6. Push to your branch (``git push origin feature/amazing-feature``)
7. Open a Pull Request

Please ensure:

* All tests pass
* Code follows project style (use ``black`` for formatting)
* Security tests pass for any file operation changes
* Documentation is updated for new features

License
=======

This project is licensed under the MIT License - see the LICENSE file for details.

Support
=======

* **Issues**: https://github.com/fx/fx_bin/issues
* **Discussions**: https://github.com/fx/fx_bin/discussions
* **PyPI**: https://pypi.org/project/fx-bin/

Acknowledgments
===============

Built with:

* `Click <https://click.palletsprojects.com/>`_ for CLI interfaces
* `Loguru <https://github.com/Delgan/loguru>`_ for logging
* `psutil <https://github.com/giampaolo/psutil>`_ for system operations

Security testing powered by:

* `Bandit <https://github.com/PyCQA/bandit>`_ for security analysis
* `Safety <https://github.com/pyupio/safety>`_ for dependency scanning

---

**Made with ❤️ for the Python community**