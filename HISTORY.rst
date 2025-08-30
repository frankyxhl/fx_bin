=======
History
=======

1.3.0 (2025-08-30)
------------------

**MAJOR ENHANCEMENT - BDD Testing Infrastructure & Enhanced Test Coverage**

This release introduces comprehensive Behavior-Driven Development (BDD) testing capabilities with pytest-bdd integration, significantly expanding the test coverage and providing stakeholder-readable specifications.

**New BDD Testing Infrastructure:**

* **pytest-bdd Integration:** Complete BDD test suite with pytest-bdd 7.0+ support
  - Added pytest-bdd dependency to development requirements
  - Comprehensive Gherkin feature specifications with 25+ scenarios
  - Smart step definitions with 70%+ pattern reuse across scenarios
  - Living documentation that serves as both tests and specifications

* **Comprehensive Feature Coverage:** Complete fx filter command validation
  - Core functionality: Single/multiple extension filtering, sorting options
  - Output formats: Simple, detailed, and count modes with metadata validation
  - Edge cases: Empty directories, non-existent paths, permission restrictions
  - Security: Path traversal protection and permission handling validation
  - Performance: Large directory handling and memory usage limits
  - Integration: Case sensitivity, multiple directories, pipeline compatibility

* **Advanced BDD Framework:** Production-ready testing infrastructure
  - Smart step pattern library with intelligent parameterization
  - Sophisticated test data builders for realistic scenarios
  - Quality validation with BDD best practice compliance scoring
  - Performance benchmarking integration with memory profiling
  - Comprehensive fixture management with proper cleanup strategies

**Enhanced Testing Capabilities:**

* **Extended pytest Markers:** Comprehensive test categorization system
  - Priority markers: `smoke`, `critical`, `regression` for test execution control
  - Functional markers: `filter_command`, `file_management`, `sorting`, `recursion`
  - Quality markers: `edge_cases`, `error_handling`, `case_sensitivity`
  - Performance markers: `performance`, `pagination`, `multiple_directories`
  - Documentation markers: `help_and_usage`, `version_compatibility`
  - Integration markers: `glob_patterns`, `output_format`

* **BDD Test Organization:** Structured test suite with maximum reuse
  - `features/file_filter.feature`: 25+ Gherkin scenarios with business-readable specifications
  - `tests/bdd/conftest.py`: Comprehensive test fixtures and data builders (400+ lines)
  - `tests/bdd/test_file_filter_steps.py`: Smart step definitions with pattern reuse
  - `tests/bdd/step_patterns.py`: Reusable step pattern library and utilities (590+ lines)

**Configuration & Compatibility Updates:**

* **pytest Configuration:** Enhanced pytest.ini with proper marker definitions
  - All 18+ BDD markers properly defined for strict marker validation
  - Extended timeout configuration for performance tests (300 seconds)
  - Comprehensive coverage configuration with proper exclusions
  - BDD-specific test path and pattern configuration

* **Dependency Management:** Updated Poetry configuration
  - pytest-bdd 7.3.0+ added to development dependencies
  - Compatible with existing pytest 8.0+ and pytest-cov 4.1+ infrastructure
  - Mako, parse, and parse-type dependencies automatically managed
  - Maintained compatibility with Python 3.11+ requirements

**Documentation & Quality Improvements:**

* **Comprehensive BDD Guide:** Complete documentation in `docs/bdd-testing-guide.md`
  - 480+ lines of detailed BDD testing documentation
  - Step-by-step setup and execution instructions
  - Advanced features: Smart step generation, test data builders, quality validation
  - Best practices: Scenario writing guidelines, step definition patterns
  - Troubleshooting: Common issues, debug tips, performance considerations
  - Integration examples: CI/CD workflows, custom fixtures, performance benchmarking

* **Enhanced Test Infrastructure:** Professional-grade testing capabilities
  - Intelligent test data generation with realistic file structures
  - Cross-platform compatibility testing (Windows/macOS/Linux)
  - Permission testing with proper cleanup and error handling
  - Memory usage validation and performance profiling
  - Security validation with path traversal and permission tests

**Technical Implementation:**

* **Smart Fixtures:** Sophisticated test data management
  - `TestFile` and `TestDirectory` dataclasses for structured test data
  - File builder with timestamp manipulation and size control
  - Directory builder for complex nested structures
  - Permission testing with proper platform compatibility
  - Large file collection generators for performance testing

* **Pattern Library:** Reusable step definition patterns
  - `StepPatternLibrary` with Given/When/Then pattern templates
  - `SmartStepGenerator` for optimized step definition creation
  - `BDDQualityValidator` for best practice compliance scoring
  - `StepReuseAnalyzer` for optimization opportunity identification

**Quality Assurance:**

* **BDD Best Practices:** Built-in quality validation
  - Scenario independence validation
  - Business language usage validation
  - Step clarity and specificity checking
  - Given-When-Then structure validation
  - Comprehensive quality scoring (0-100 scale)

* **Performance Testing:** Production-ready performance validation
  - Large directory handling (100+ files per test)
  - Memory usage limits and profiling
  - Execution time benchmarking
  - Parallel test execution support
  - CI/CD integration examples

**Migration Notes:**

* No breaking changes - all existing functionality preserved
* BDD tests complement existing unit tests (both test suites can run independently)
* New pytest markers are optional - existing test execution patterns continue to work
* BDD dependencies are in development group only - production installations unaffected

This release establishes fx-bin as a mature testing exemplar with enterprise-grade BDD capabilities, providing both comprehensive validation and stakeholder-readable documentation.

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
