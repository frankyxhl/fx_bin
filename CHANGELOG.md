# Changelog

All notable changes to fx-bin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[1.3.1]: https://github.com/frankyxhl/fx_bin/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/frankyxhl/fx_bin/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/frankyxhl/fx_bin/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/frankyxhl/fx_bin/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/frankyxhl/fx_bin/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/frankyxhl/fx_bin/releases/tag/v1.0.0