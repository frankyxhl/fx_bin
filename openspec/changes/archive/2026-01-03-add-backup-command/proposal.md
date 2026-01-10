# Change: Add Backup Command

## Why
Users need a reliable way to create timestamped backups of files and directories with optional compression and automatic cleanup. This fills a gap in fx-bin's file operation capabilities.

## What Changes
- Add `fx backup` command to create timestamped backups
- Support file backups with intelligent extension handling (including multi-part extensions like .tar.gz)
- Support directory backups with optional .tar.gz compression
- Implement automatic cleanup with --max-backups option
- Follow existing fx-bin patterns: lazy import in CLI, Click framework, returns.result for error handling
- Full TDD implementation with comprehensive test coverage

## Impact
- Affected specs: backup (new capability)
- Affected code:
  - New: `fx_bin/backup.py` (core backup logic)
  - New: `tests/unit/test_backup.py` (unit tests)
  - New: `tests/integration/test_backup_cli.py` (CLI integration tests)
  - Modified: `fx_bin/cli.py` (add backup command)
