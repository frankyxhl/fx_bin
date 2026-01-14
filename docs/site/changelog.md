# Changelog

All notable changes to fx-bin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation site with GitHub Pages deployment
- 10 command reference documents with detailed examples
- Use case guides for common workflows
- Advanced topics on shell integration and performance
- Contributing guide for developers

### Changed
- Improved help text for all commands
- Better error messages for edge cases
- Enhanced output formatting for readability

### Fixed
- Fixed file counting in directories with many files
- Fixed size analysis for very large directories
- Fixed text replacement with special characters

## [2.4.0] - 2026-01-10

### Added
- `fx organize` command with date-based file organization
- `fx today` command for daily workspace management
- `fx root` command for Git project root navigation
- `fx realpath` command for absolute path resolution
- Support for custom date formats in backups
- Support for directory depth configuration in organize

### Changed
- Improved `fx ff` performance with better exclusion handling
- Enhanced `fx filter` with additional sorting options
- Better integration tests coverage

### Fixed
- Fixed symlink handling in `fx size`
- Fixed date source selection in `fx filter`
- Fixed conflict handling in `fx organize`

## [2.3.0] - 2025-12-15

### Added
- `fx filter` command for extension-based file filtering
- Time-based sorting (creation/modification) in `fx filter`
- Multiple extension support in `fx filter`
- Detailed and simple output formats

### Changed
- Improved output formatting for better readability
- Enhanced performance for large directory traversal

### Fixed
- Fixed file extension matching edge cases
- Fixed date parsing for various file systems

## [2.2.0] - 2025-11-20

### Added
- `fx replace` command with atomic write operations
- Automatic backup before text replacement
- Automatic restore on replacement failure
- Multi-file replacement support

### Changed
- Improved error handling and recovery
- Better progress feedback

### Fixed
- Fixed file locking issues during replacement
- Fixed encoding handling for various file types

## [2.1.0] - 2025-10-25

### Added
- `fx backup` command with timestamp generation
- Compression support for directory backups
- Custom timestamp format support
- Backup verification and validation

### Changed
- Improved backup naming consistency
- Enhanced error messages for backup operations

### Fixed
- Fixed backup of directories with special characters
- Fixed timestamp format validation

## [2.0.0] - 2025-09-30

### Added
- Complete CLI rewrite using Click framework
- `fx files` command for file counting
- `fx size` command for size analysis
- `fx ff` command for file finding
- `fx fff` command for first-match lookup
- Command metadata and `fx list` command
- Comprehensive help documentation
- Version and system information command

### Changed
- Improved performance across all operations
- Better error handling and user feedback
- Enhanced command-line interface

### Breaking
- Python version requirement increased to 3.11+
- Removed legacy commands incompatible with new CLI
- Changed some default behaviors for consistency

### Fixed
- Fixed various memory leaks in long-running operations
- Fixed edge cases in file system operations

## [1.0.0] - 2025-08-15

### Added
- Initial release
- Basic file operations
- Text replacement functionality
- Simple backup operations

---

**Note:** This changelog format will be maintained going forward. All changes will be documented here.
