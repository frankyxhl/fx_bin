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

Available Commands
==================

After installation, the following commands will be available in your terminal:

fx_size - Directory Size Analyzer
----------------------------------

Analyze and display file and directory sizes in human-readable format.

.. code-block:: bash

    # Show sizes of all items in current directory
    fx_size
    
    # Show sizes in a specific directory
    fx_size /path/to/directory
    
    # Show only directories
    fx_size --only-dirs
    
    # Show only files
    fx_size --only-files

**Features:**

* Human-readable size formatting (B, KB, MB, GB)
* Sort by size automatically
* Handle symbolic links safely
* Recursive directory traversal with loop detection

fx_files - File Counter
------------------------

Count files in directories with detailed statistics.

.. code-block:: bash

    # Count files in current directory
    fx_files
    
    # Count files in specific directory
    fx_files /path/to/directory
    
    # Count files recursively
    fx_files --recursive

**Features:**

* Fast file counting
* Extension-based grouping
* Hidden files detection
* Recursive counting with depth control

fx_ff - Find Files
------------------

Advanced file search utility with pattern matching.

.. code-block:: bash

    # Find files by name pattern
    fx_ff "*.py"
    
    # Find files containing text
    fx_ff --contains "TODO"
    
    # Find files modified in last 7 days
    fx_ff --modified-days 7
    
    # Find files larger than 10MB
    fx_ff --size-min 10485760

**Features:**

* Glob pattern matching
* Content search
* Size filtering
* Date filtering
* Regular expression support

fx_replace - Text Replacement
------------------------------

Safe text replacement in files with atomic operations.

.. code-block:: bash

    # Replace text in a single file
    fx_replace "old_text" "new_text" file.txt
    
    # Replace in multiple files
    fx_replace "old_text" "new_text" *.txt
    
    # Preview changes without modifying
    fx_replace "old_text" "new_text" file.txt --dry-run
    
    # Create backup before replacing
    fx_replace "old_text" "new_text" file.txt --backup

**Features:**

* Atomic file operations (no data loss)
* UTF-8 encoding support
* Permission preservation
* Backup creation
* Dry-run mode for preview

fx_grab_json_api_to_excel - JSON to Excel Converter
-----------------------------------------------------

Convert JSON API responses to Excel spreadsheets.

.. code-block:: bash

    # Convert JSON file to Excel
    fx_grab_json_api_to_excel data.json output.xlsx
    
    # Fetch from API and convert
    fx_grab_json_api_to_excel https://api.example.com/data output.xlsx
    
    # Specify custom headers
    fx_grab_json_api_to_excel api_url output.xlsx --header "Authorization: Bearer TOKEN"

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
    
    # Create virtual environment
    python3 -m venv .venv
    source .venv/bin/activate
    
    # Install development dependencies
    pip install -e .
    pip install click loguru pytest psutil

Running tests
-------------

.. code-block:: bash

    # Run all tests
    python tests/runners/simple_test_runner.py
    
    # Run specific test modules
    python -m unittest tests.test_size
    python -m unittest tests.test_files
    
    # Run with pytest (if installed)
    pytest tests/ -v
    
    # Run security tests only
    pytest tests/test_*security*.py -v

Test Coverage
-------------

The project maintains comprehensive test coverage:

* Security vulnerability tests
* File operation safety tests
* Performance benchmarks
* Integration tests
* Unit tests for all modules

Code Quality
------------

.. code-block:: bash

    # Run linting
    flake8 fx_bin/
    
    # Run type checking
    mypy fx_bin/
    
    # Format code
    black fx_bin/ tests/

Architecture
============

Project Structure
-----------------

.. code-block:: text

    fx_bin/
    ├── fx_bin/              # Main package
    │   ├── common.py        # Shared utilities
    │   ├── size.py          # fx_size implementation
    │   ├── files.py         # fx_files implementation
    │   ├── find_files.py    # fx_ff implementation
    │   ├── replace.py       # fx_replace implementation
    │   └── pd.py            # fx_grab_json_api_to_excel
    ├── tests/               # Test suite
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

Requirements
============

* Python 3.11 or higher
* click (CLI framework)
* loguru (logging)
* psutil (system operations)
* pandas (optional, for Excel features)

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