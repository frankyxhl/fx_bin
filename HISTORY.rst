=======
History
=======

1.2.0 (2025-08-30)
------------------

**NEW FEATURE - File Filter Command with TDD/BDD Implementation**

This version introduces a comprehensive file filtering system with advanced sorting and comprehensive test coverage.

**New Features:**

* **fx filter command:** Filter files by extension with flexible options
  - Single extension filtering: `fx filter txt`
  - Multiple extension filtering: `fx filter "txt,py,json"`
  - Sort by creation time (default) or modification time: `--sort-by modified`
  - Recursive (default) or non-recursive search: `--no-recursive`
  - Reverse sorting option: `--reverse`
  - Output formats: simple (default), detailed, count: `--format detailed`

* **Advanced Filtering Features:**
  - Case-insensitive extension matching
  - Human-readable file size formatting in detailed output
  - Cross-platform creation time handling (Windows/macOS/Linux)
  - Comprehensive error handling and validation
  - Path normalization and security checks

**Testing Excellence:**

* **TDD Implementation:** 23 comprehensive unit tests covering all functionality
  - Core filtering functionality tests
  - CLI integration tests with Click testing
  - Error handling and edge case validation
  - Performance and integration test scenarios

* **BDD Implementation:** 25+ Gherkin scenarios with executable specifications
  - Business-readable feature specifications in Gherkin syntax
  - Comprehensive step definition patterns with 70%+ reuse
  - Smart test data builders and fixtures
  - Quality validation and reporting infrastructure
  - Performance benchmarking and security testing

**Documentation:**

* **BDD Testing Guide:** Complete guide for stakeholder-readable tests
* **Feature Specifications:** Living documentation in `features/file_filter.feature`
* **Updated README.rst:** Complete fx filter command documentation with examples
* **Updated CLAUDE.md:** Development guidance with new command details

**Technical Implementation:**

* **fx_bin/filter.py:** Complete filtering engine with comprehensive docstrings
* **tests/test_filter.py:** 23 unit tests with TDD methodology
* **tests/bdd/:** BDD test suite with pytest-bdd integration
* **features/:** Gherkin feature specifications for business stakeholders

**Configuration:**

* **pytest-bdd.ini:** BDD testing configuration
* **requirements-bdd.txt:** BDD-specific dependencies
* **CLAUDE.md removed from git tracking:** Now in .gitignore for personal development notes

1.1.0 (2025-08-25)
------------------

**MAJOR BREAKING CHANGES - CLI Simplification**

This version removes all legacy individual command entries and standardizes on the unified `fx` command introduced in v1.0.0.

**Breaking Changes:**

* **Removed fx_upgrade functionality completely:**
  - Deleted `fx_upgrade` script entry point from pyproject.toml
  - Removed `run_upgrade_program.py` module
  - Removed upgrade command from unified CLI
  - Deleted `test_run_upgrade_program.py` test file
  - Removed TestUpgradeCommand class from test_cli.py

* **Removed all legacy command script entries:**
  - Deleted `fx_files`, `fx_size`, `fx_ff`, `fx_replace`, `fx_grab_json_api_to_excel` from pyproject.toml
  - These commands are now only available through the unified `fx` command

**Migration Required:**

* Replace `fx_files` with `fx files`
* Replace `fx_size` with `fx size`  
* Replace `fx_ff` with `fx ff`
* Replace `fx_replace` with `fx replace`
* Replace `fx_grab_json_api_to_excel` with `fx json2excel`
* The `fx_upgrade` command has been completely removed with no replacement

**Architecture:**

* Simplified package distribution with single `fx` entry point
* Reduced installation footprint by removing redundant command entries
* Improved CLI consistency and discoverability
* Maintained all core functionality through unified interface

**Documentation:**

* Updated README.rst to remove legacy command references
* Updated CLAUDE.md development documentation
* Added migration guidance for existing users

**Impact:**

* Existing scripts using individual fx_* commands will need updates
* Shell aliases or automation using old commands require migration
* Simplified user experience for new installations
* Cleaner package architecture for future development

1.0.1 (2025-08-24)
------------------

* Fix fx files command displaying raw FileCountEntry objects instead of formatted output
* Implement proper display() method usage with dynamic count width calculation
* Add empty directory handling with informative message
* Update test mocks in test_cli.py to return proper FileCountEntry objects
* Fix all flake8 linting issues in cli.py
* All 255 tests now pass and code quality checks succeed

1.0.0 (2025-08-24)
------------------

**MAJOR RELEASE - Unified CLI Architecture**

This major version release marks a significant architectural evolution of fx-bin:

**BREAKING CHANGES:**
* Unified CLI system with single 'fx' entry point introduced in 0.10.1
* Modern Click-based command structure replacing individual fx_xxx commands
* Backward compatibility maintained for all legacy commands

**MAJOR FEATURES:**
* Single 'fx' command with intuitive subcommands (files, size, ff, replace, etc.)
* Built-in help system and command discovery with 'fx list'
* Comprehensive test coverage and documentation
* Maintained full backward compatibility for existing users

**ARCHITECTURE IMPROVEMENTS:**
* Consolidated command structure for better user experience
* Standardized CLI patterns across all utilities
* Enhanced discoverability and usability
* Future-ready foundation for additional commands

0.10.1 (2025-08-24)
-------------------

* Implement unified CLI with single fx command
* Add comprehensive Click-based command group
* New 'fx' command with subcommands: files, size, ff, replace, json2excel, upgrade, list
* Extensive test coverage in tests/test_cli.py
* Updated README.rst with migration guide and new CLI documentation
* Maintain backward compatibility with all original commands

0.9.7 (2025-08-24)
------------------

* Comprehensive linting fixes applied across fx_bin/common.py, fx_bin/find_files.py, fx_bin/lib.py
* All remaining flake8 issues resolved
* Entire fx_bin package now fully compliant with flake8 linting standards

0.9.6 (2025-08-24)
------------------

* Resolve flake8 linting issues in fx_bin/pd.py
* Fix line length violations and whitespace issues
* Improve code readability while maintaining functionality

0.9.5 (2025-08-24)
------------------

* Comprehensive code quality improvements addressing security, consistency, and maintainability
* Security enhancements: SSRF protection in pd.py, symlink security fixes in common.py
* Version management: Replace hardcoded version with dynamic importlib.metadata.version()
* Error handling improvements: Fix cross-device error handling, improve CLI consistency
* Code cleanup: Remove obsolete files, fix Makefile targets, improve documentation

0.1.0 (2019-07-27)
------------------

* First release on PyPI.
