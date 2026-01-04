# Changelog

All notable changes to fx-bin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.7.0] - 2026-01-04

### Added
- **`fx backup` command**: Create timestamped backups of files and directories
  - File backups with intelligent multi-extension handling (.tar.gz, .tar.bz2, .tar.xz)
  - Directory backups with optional .tar.xz compression (--compress)
  - Custom timestamp format support (--timestamp-format)
  - Microsecond precision to prevent timestamp collisions

### Fixed
- **Backup security hardening**:
  - Added symlink preservation in directory backups (symlinks=True)
  - Implemented collision detection for rapid backup creation

### Implementation
- TDD approach with 28 comprehensive tests (100% pass rate)
- Follows fx-bin patterns: lazy imports, Click CLI, returns.result error handling
- OpenSpec validated (50/50 tasks complete)

## [1.6.0] - 2026-01-01

### Removed
- **BREAKING: `fx json2excel` command removed**: Simplified project by removing pandas dependency
- **pandas and openpyxl dependencies**: Project now has no heavy optional dependencies

### Fixed
- **Documentation accuracy**: Fixed README CLI examples to match actual implementation
  - Fixed `fx replace` example (removed non-existent `--preview` flag)
  - Fixed `fx filter --sort-by` options (`created`/`modified`, not `ctime`/`mtime`)
  - Updated MIGRATION_GUIDE to mark json2excel as REMOVED
- **Benchmark suite**: Removed references to deleted pandas/pd_functional modules
- **Test runners**: Removed references to deleted test_pd_safety module

### Changed
- **CI pipeline hardened**:
  - Bandit security scans now enforced (removed `|| true`)
  - MyPy type checking now enforced
  - Added test/lint gates before PyPI deployment

### Added
- **pipx upgrade instructions**: Added `pipx upgrade fx-bin` example in README

## [1.5.0] - 2026-01-01

### Added
- **`fx fff` command**: New alias for `fx ff --first` - finds first matching file and exits immediately
- **`fx ff --first` option**: Stop after first match for faster searches
- **Binary file detection**: `fx replace` now automatically skips binary files to prevent corruption

### Fixed
- **`__version__` fallback**: Updated from "0.9.4" to "1.5.0" to match current version
- **Documentation accuracy**: README examples now match actual CLI behavior
  - Fixed `fx ff` examples (takes only KEYWORD, not PATH)
  - Fixed `fx filter` format options (only `simple`/`detailed`, no `count`)

### Changed
- **pytest configuration**: Consolidated pytest-bdd.ini into pyproject.toml

## [Unreleased]

_Nothing yet_

## [1.3.5] - 2025-09-05

### Added
- **Test Organization**: Reorganized test suite into categorized structure
  - `tests/unit/` - Unit tests for individual functions
  - `tests/integration/` - Integration and command interaction tests
  - `tests/security/` - Security and safety validation tests
  - `tests/performance/` - Performance benchmarks and profiling
  - `tests/functional/` - End-to-end functional testing
- **Test Isolation**: Added pytest-forked for proper test isolation
- **Documentation**: Created CONTRIBUTING.md from contributing.rst

### Fixed
- **Critical Bug**: Fixed replace command "str expected, not tuple" error
  - Refactored replace.py to separate CLI from core logic
  - Created new `replace_files()` function for programmatic access
- **Test Suite**: Fixed 18 failing tests with proper isolation
- **Warnings**: Resolved 26 test warnings (24 pytest-bdd, 2 dataclass naming)
- **Skipped Tests**: Fixed 2 skipped tests in replace module

### Changed
- **Documentation Format**: Consolidated to Markdown throughout project
  - Merged README.rst → README.md
  - Merged HISTORY.rst → CHANGELOG.md
  - Removed 8 obsolete Sphinx documentation files
- **Build Configuration**: Updated Makefile to use --forked for tests
- **Project Structure**: Comprehensive cleanup of cache and build artifacts

### Removed
- Sphinx documentation files (Makefile, conf.py, *.rst files in docs/)
- Duplicate test files (merged into consolidated versions)
- All __pycache__, .pytest_cache, .mypy_cache directories

## [1.3.4] - 2025-08-31

### Added
- **Default exclusions for fx ff**: Now skips `.git`, `.venv`, and `node_modules` by default to reduce unnecessary traversal
- **New fx ff options**:
  - `--include-ignored`: Include default-ignored directories
  - `--exclude NAME`: Repeatable option supporting glob patterns to prune names/paths
- **Enhanced testing**: Added `tests/test_ff_exclude.py` covering default skip, include-ignored, and exclude patterns
- **Poetry Migration**: Complete transition from pip/setuptools to Poetry
  - Removed legacy requirements files
  - Updated installation instructions
  - Added Poetry-specific .gitignore entries

### Changed
- **Documentation updates**: Updated README, docs/quick-start.md, and migration guide examples for new fx ff behavior
- **Improved file finding efficiency**: Reduces traversal time by intelligently skipping common development directories

## [1.3.3] - 2025-08-30

### Fixed
- **File Size Alignment**: Fixed misaligned file sizes in `fx filter` detailed output
  - Standardized all size units (B, KB, MB, GB) to 9-character width
  - Ensures perfect right-alignment for improved readability
  - Resolves user-reported alignment issues with mixed unit sizes
  - Updated all related tests to match new formatting

### Changed
- Improved consistency in tabular output formatting
- Enhanced visual scanning of file size columns

### Testing
- All 36 filter tests passing including 14 doctests
- Updated test expectations in test_filter_improvements_v1_3_1.py
- Fixed doctest examples with proper skip directives

## [1.3.2] - 2025-08-30

### Fixed
- Enhanced file size formatting in filter command output
- Improved CLI features and test stability

## [1.3.1] - 2025-08-30

### Security
- **CRITICAL**: Fixed Black ReDoS vulnerability (CVE affecting versions < 24.3.0)
  - Updated Black from ^24.0.0 to ^24.3.0 in pyproject.toml
  - Updated Black from >=22.0.0,<24.0.0 to >=24.3.0,<25.0.0 in requirements-bdd.txt
  - Vulnerability allowed potential denial of service through crafted regular expressions
  - Affects development environment only (Black is a dev dependency)

### Fixed
- Synchronized poetry.lock with updated Black dependency
- Updated all Black version constraints for security compliance

### Verified
- Bandit security scan: 0 issues found across 13 files
- Safety dependency scan: 55 tests passed, no vulnerabilities
- All 43 core unit tests passing
- CLI functionality fully operational

## [1.3.0] - 2025-08-30

### Added
- **Major Feature**: Comprehensive BDD testing infrastructure with pytest-bdd 7.0+ integration
- 25+ Gherkin scenarios providing business-readable specifications
- Smart step definition patterns with 70%+ reuse across scenarios
- 18+ pytest markers for comprehensive test categorization
- Advanced test fixtures and data builders for realistic scenarios
- Production-grade BDD framework with quality validation tools
- Comprehensive BDD testing guide (480+ lines of documentation)

### Enhanced
- pytest configuration with proper BDD marker definitions
- Test infrastructure with sophisticated data management
- Documentation with living specifications through Gherkin

### Technical
- `pytest-bdd` 7.3.0+ added to development dependencies
- Smart fixtures: TestFile and TestDirectory dataclasses
- Pattern library with StepPatternLibrary and SmartStepGenerator
- BDD quality validation with compliance scoring (0-100 scale)

## [1.2.0] - 2025-08-30

### Added
- **New Command**: `fx filter` - comprehensive file filtering by extension
  - Single/multiple extension filtering support
  - Sort by creation time (default) or modification time
  - Recursive (default) or non-recursive search options
  - Multiple output formats: simple, detailed, count
  - Cross-platform creation time handling
  - Human-readable file size formatting

### Testing
- 23 comprehensive unit tests following TDD methodology
- 25+ BDD scenarios with Gherkin specifications
- Complete pytest-bdd integration with reusable steps
- Performance benchmarking and security validation

### Documentation
- Complete fx filter command documentation in README
- BDD testing guide and living documentation system
- Session chronicles and decision logs

## [1.1.0] - 2025-08-25

### Changed
- **BREAKING**: Removed all legacy individual command entries
  - Removed `fx_files`, `fx_size`, `fx_ff`, `fx_replace`, `fx_grab_json_api_to_excel`
  - Commands now only available through unified `fx` command
  
### Removed
- **fx_upgrade** functionality completely removed
  - Deleted run_upgrade_program.py module
  - Removed upgrade command from CLI
  - Deleted associated test files

### Migration Required
- Replace `fx_files` with `fx files`
- Replace `fx_size` with `fx size`
- Replace `fx_ff` with `fx ff`
- Replace `fx_replace` with `fx replace`
- Replace `fx_grab_json_api_to_excel` with `fx json2excel`

## [1.0.1] - 2025-08-24

### Fixed
- fx files command displaying raw FileCountEntry objects instead of formatted output
- Implemented proper display() method usage with dynamic count width
- Added empty directory handling with informative message
- Fixed all flake8 linting issues in cli.py

## [1.0.0] - 2025-08-24

### Added
- **Major Release**: Unified CLI architecture with single 'fx' entry point
- Modern Click-based command structure
- Built-in help system and command discovery with 'fx list'
- Comprehensive test coverage and documentation
- Backward compatibility maintained for all legacy commands

### Changed
- Consolidated command structure for better user experience
- Standardized CLI patterns across all utilities
- Enhanced discoverability and usability

## [0.10.1] - 2025-08-24

### Added
- **Unified CLI**: Implemented unified CLI with single fx command
- **Comprehensive Click-based command group**: New 'fx' command with subcommands: files, size, ff, replace, json2excel, upgrade, list
- **Extensive test coverage**: Added comprehensive tests in tests/test_cli.py
- **Migration guide**: Updated README.rst with migration guide and new CLI documentation
- **Backward compatibility**: Maintained backward compatibility with all original commands

## [0.9.7] - 2025-08-24

### Fixed
- **Comprehensive linting fixes**: Applied across fx_bin/common.py, fx_bin/find_files.py, fx_bin/lib.py
- **flake8 compliance**: All remaining flake8 issues resolved
- **Code quality**: Entire fx_bin package now fully compliant with flake8 linting standards

## [0.9.6] - 2025-08-24

### Fixed
- **flake8 issues**: Resolved flake8 linting issues in fx_bin/pd.py
- **Code formatting**: Fixed line length violations and whitespace issues
- **Readability**: Improved code readability while maintaining functionality

## [0.9.5] - 2025-08-24

### Security
- **SSRF protection**: Enhanced SSRF protection in pd.py
- **Symlink security**: Fixed symlink security issues in common.py

### Changed
- **Version management**: Replace hardcoded version with dynamic importlib.metadata.version()
- **Error handling**: Fixed cross-device error handling, improved CLI consistency
- **Code cleanup**: Removed obsolete files, fixed Makefile targets, improved documentation

### Fixed
- **Comprehensive improvements**: Addressed security, consistency, and maintainability issues

## [0.1.0] - 2019-07-27

### Added
- **First release**: Initial release on PyPI

[1.3.4]: https://github.com/frankyxhl/fx_bin/compare/v1.3.3...v1.3.4
[1.3.3]: https://github.com/frankyxhl/fx_bin/compare/v1.3.2...v1.3.3
[1.3.2]: https://github.com/frankyxhl/fx_bin/compare/v1.3.1...v1.3.2
[1.3.1]: https://github.com/frankyxhl/fx_bin/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/frankyxhl/fx_bin/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/frankyxhl/fx_bin/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/frankyxhl/fx_bin/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/frankyxhl/fx_bin/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/frankyxhl/fx_bin/releases/tag/v1.0.0
[0.10.1]: https://github.com/frankyxhl/fx_bin/compare/v0.9.7...v0.10.1
[0.9.7]: https://github.com/frankyxhl/fx_bin/compare/v0.9.6...v0.9.7
[0.9.6]: https://github.com/frankyxhl/fx_bin/compare/v0.9.5...v0.9.6
[0.9.5]: https://github.com/frankyxhl/fx_bin/compare/v0.1.0...v0.9.5
[0.1.0]: https://github.com/frankyxhl/fx_bin/releases/tag/v0.1.0