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

Quick Start - New Unified CLI (v0.10.0+)
=========================================

**NEW**: Starting from version 0.10.0, FX Bin provides a unified ``fx`` command with subcommands for better usability:

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
    fx replace     - Replace text in files
    fx json2excel  - Convert JSON to Excel
    fx upgrade     - Run upgrade program
    fx list        - List all available commands

Examples with New CLI
---------------------

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

Available Commands (Legacy)
============================

For backward compatibility, the original commands are still available:

fx_size - Directory Size Analyzer
----------------------------------

Analyze and display file and directory sizes in human-readable format.

**New CLI (recommended):**

.. code-block:: bash

    fx size                    # Current directory
    fx size /path/to/dir       # Specific directory

**Legacy CLI:**

.. code-block:: bash

    fx_size                    # Current directory
    fx_size /path/to/dir       # Specific directory

**Features:**

* Human-readable size formatting (B, KB, MB, GB)
* Sort by size automatically
* Handle symbolic links safely
* Recursive directory traversal with loop detection

fx_files - File Counter
------------------------

Count files in directories with detailed statistics.

**New CLI (recommended):**

.. code-block:: bash

    fx files                   # Current directory
    fx files /path/to/dir      # Specific directory

**Legacy CLI:**

.. code-block:: bash

    fx_files                   # Current directory
    fx_files /path/to/dir      # Specific directory

**Features:**

* Fast file counting
* Extension-based grouping
* Hidden files detection
* Recursive counting with depth control

fx_ff - Find Files
------------------

Advanced file search utility with pattern matching.

**New CLI (recommended):**

.. code-block:: bash

    fx ff "*.py"               # Find Python files
    fx ff config               # Find files with 'config' in name

**Legacy CLI:**

.. code-block:: bash

    fx_ff "*.py"               # Find Python files
    fx_ff config               # Find files with 'config' in name

**Features:**

* Glob pattern matching
* Content search
* Size filtering
* Date filtering
* Regular expression support

fx_replace - Text Replacement
------------------------------

Safe text replacement in files with atomic operations.

**New CLI (recommended):**

.. code-block:: bash

    fx replace "old" "new" file.txt              # Single file
    fx replace "old" "new" *.txt                 # Multiple files

**Legacy CLI:**

.. code-block:: bash

    fx_replace "old" "new" file.txt              # Single file
    fx_replace "old" "new" *.txt                 # Multiple files

**Features:**

* Atomic file operations (no data loss)
* UTF-8 encoding support
* Permission preservation
* Backup creation
* Dry-run mode for preview

fx_grab_json_api_to_excel - JSON to Excel Converter
-----------------------------------------------------

Convert JSON API responses to Excel spreadsheets.

**New CLI (recommended):**

.. code-block:: bash

    fx json2excel data.json output.xlsx          # Convert JSON file
    fx json2excel https://api.example.com/data output.xlsx  # From API

**Legacy CLI:**

.. code-block:: bash

    fx_grab_json_api_to_excel data.json output.xlsx
    fx_grab_json_api_to_excel https://api.example.com/data output.xlsx

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
    │   ├── size.py          # fx_size implementation
    │   ├── files.py         # fx_files implementation
    │   ├── find_files.py    # fx_ff implementation
    │   ├── replace.py       # fx_replace implementation
    │   └── pd.py            # fx_grab_json_api_to_excel
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

Migration Guide (v0.10.0)
==========================

Version 0.10.0 introduces a unified ``fx`` command while maintaining backward compatibility:

**Old way (still works):**

.. code-block:: bash

    fx_files
    fx_size
    fx_ff "*.py"
    fx_replace "old" "new" file.txt

**New way (recommended):**

.. code-block:: bash

    fx files
    fx size
    fx ff "*.py"
    fx replace "old" "new" file.txt

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