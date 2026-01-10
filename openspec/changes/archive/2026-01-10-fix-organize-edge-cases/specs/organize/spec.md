# organize Specification - Delta: Fix Edge Cases

## Purpose
Fix 5 edge cases and resource leaks: FD leak, --yes+--quiet consistency, loguru configuration, ASK runtime behavior clarification, and directory creation path semantics.

## MODIFIED Requirements

### Requirement: Resource Management - File Descriptors
The system SHALL properly close file descriptors to prevent leaks.

#### Scenario: Close fd after mkstemp (FIXED)
- **WHEN** system creates temporary file with tempfile.mkstemp()
- **THEN** file descriptor is closed with os.close(fd) before copying
- **AND** file descriptor does not leak

### Requirement: Loguru Configuration for Quiet/Verbose Modes
The system SHALL configure loguru logger level based on --quiet/--verbose flags.

#### Scenario: Quiet mode suppresses WARNING output (FIXED)
- **WHEN** user runs `fx organize --quiet`
- **THEN** loguru is configured to ERROR level
- **AND** WARNING messages are not displayed
- **AND** ERROR messages are still shown

#### Scenario: Verbose mode shows all output (FIXED)
- **WHEN** user runs `fx organize --verbose`
- **THEN** loguru is configured to DEBUG level
- **AND** all log messages including WARNING are displayed

#### Scenario: Close fd after mkstemp (FIXED)
- **WHEN** system creates temporary file with tempfile.mkstemp()
- **THEN** file descriptor is closed with os.close(fd) before copying
- **AND** file descriptor does not leak

### Requirement: Quiet Mode Consistency
The system SHALL respect --quiet flag in all code paths, including --yes branch.

#### Scenario: --yes with --quiet suppresses extra output (FIXED)
- **WHEN** user runs `fx organize --yes --quiet`
- **THEN** "Organizing files..." message is suppressed
- **AND** only summary is displayed

### Requirement: ASK Mode Runtime Conflict Behavior
The system SHALL clearly document ASK mode behavior for runtime conflicts and log warnings that respect --quiet mode.

#### Scenario: ASK mode runtime conflict skips (DOCUMENTED)
- **WHEN** user runs `fx organize --on-conflict ask`
- **AND** new disk conflict appears during execution (TOCTOU)
- **THEN** file is skipped with loguru warning
- **AND** warning is logged but not displayed in --quiet mode
- **AND** behavior is documented in help text

**Note:** ASK mode only prompts for conflicts detected during scan phase. Runtime conflicts (files modified between scan and execution) are skipped for safety. Warnings use loguru.logger.warning() to respect --quiet flag.

### Requirement: Directory Creation Path Semantics
The system SHALL create parent directories using the resolved target path.

#### Scenario: Directory created at real target location (FIXED)
- **WHEN** file target contains symbolic links or relative paths
- **THEN** parent directory is created using resolved path (real_target)
- **AND** directory creation matches actual file write location
