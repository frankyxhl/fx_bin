# organize Specification - Delta: Fix Conflict Handling

## Purpose
Fix critical bugs in conflict handling where RENAME mode overwrites files, ASK mode is unimplemented, OVERWRITE lacks atomic semantics, --quiet doesn't show summary, and cross-device paths crash.

## MODIFIED Requirements

### Requirement: File Conflict Resolution with Correct Disk Semantics
The system SHALL handle filename conflicts with configurable strategies. Intra-run conflicts are resolved at plan time. Disk conflicts (target exists on disk) use the configured --on-conflict mode.

#### Scenario: RENAME adds suffix on disk conflict (FIXED - was overwriting)
- **WHEN** user runs `fx organize --on-conflict rename`
- **AND** target file already exists on disk
- **THEN** system calls `resolve_conflict_rename()` to generate unique path
- **AND** target path is modified with numeric suffix (e.g., `photo_1.jpg`, `photo_2.jpg`)
- **AND** file is moved to the renamed path WITHOUT overwriting existing file

#### Scenario: OVERWRITE uses atomic replace (FIXED - was non-atomic)
- **WHEN** user runs `fx organize --on-conflict overwrite`
- **AND** target file already exists on disk
- **THEN** target file is atomically replaced using `os.replace()`
- **AND** operation is guaranteed to either succeed completely or fail without corruption
- **AND** on EXDEV (cross-filesystem) error: copy to temp, then atomic replace

#### Scenario: ASK prompts user or falls back to skip (FIXED - was silent skip)
- **WHEN** user runs `fx organize --on-conflict ask`
- **AND** target file already exists on disk
- **AND** stdin is a TTY
- **THEN** user is prompted with click.confirm() for each conflict
- **WHEN** user declines the prompt
- **THEN** file is skipped
- **WHEN** stdin is not a TTY (non-interactive)
- **THEN** ASK mode falls back to SKIP behavior (no prompt)

### Requirement: Quiet Mode Always Shows Summary (FIXED)
The system SHALL display errors and summary in quiet mode, regardless of whether errors occurred.

#### Scenario: Quiet mode shows summary even with no errors (FIXED - was not showing)
- **WHEN** user runs `fx organize --quiet`
- **AND** organization completes successfully with no errors
- **THEN** summary is still displayed showing files moved, skipped, directories created
- **AND** per-file progress details are suppressed

### Requirement: Cross-Device Path Robustness (FIXED)
The system SHALL handle ValueError when comparing paths on different devices (e.g., different drives on Windows).

#### Scenario: Cross-device output directory doesn't crash (FIXED - was ValueError)
- **WHEN** user runs `fx organize --output D:\output` (while source is on C:\)
- **THEN** `_should_skip_entry()` catches ValueError from `os.path.commonpath()`
- **AND** returns False (don't skip the entry)
- **AND** processing continues without crash
