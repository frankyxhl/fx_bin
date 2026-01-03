# Backup Capability Specification

## ADDED Requirements

### Requirement: File Backup with Timestamps
The system SHALL create timestamped copies of files with configurable timestamp formats.

#### Scenario: Backup single file
- **WHEN** user runs `fx backup myfile.txt`
- **THEN** a copy is created as `backups/myfile_YYYYMMDDHHMMSS.txt`

#### Scenario: Custom timestamp format
- **WHEN** user runs `fx backup myfile.txt --timestamp-format "%Y-%m-%d"`
- **THEN** a copy is created as `backups/myfile_YYYY-MM-DD.txt`

#### Scenario: Custom backup directory
- **WHEN** user runs `fx backup myfile.txt -d /custom/path`
- **THEN** a copy is created in `/custom/path/myfile_YYYYMMDDHHMMSS.txt`

### Requirement: Multi-Part Extension Handling
The system SHALL correctly handle multi-part file extensions when creating backups.

#### Scenario: Backup .tar.gz file
- **WHEN** user runs `fx backup archive.tar.gz`
- **THEN** a copy is created as `backups/archive_YYYYMMDDHHMMSS.tar.gz`
- **AND** the extension `.tar.gz` is preserved as a unit

#### Scenario: Backup .tar.bz2 file
- **WHEN** user runs `fx backup data.tar.bz2`
- **THEN** a copy is created as `backups/data_YYYYMMDDHHMMSS.tar.bz2`

### Requirement: Directory Backup (Uncompressed)
The system SHALL create timestamped copies of directories without compression by default.

#### Scenario: Backup directory uncompressed
- **WHEN** user runs `fx backup mydir/`
- **THEN** a copy is created as `backups/mydir_YYYYMMDDHHMMSS/`
- **AND** all contents are preserved

### Requirement: Directory Backup (Compressed)
The system SHALL create compressed .tar.gz archives when the --compress flag is used.

#### Scenario: Backup directory with compression
- **WHEN** user runs `fx backup mydir/ --compress`
- **THEN** a compressed archive is created as `backups/mydir_YYYYMMDDHHMMSS.tar.gz`

#### Scenario: Verify compressed archive contents
- **WHEN** a compressed backup is created
- **THEN** the archive SHALL contain all directory contents
- **AND** the archive SHALL be readable with standard tar tools

### Requirement: Automatic Backup Cleanup
The system SHALL automatically remove old backups when --max-backups is specified.

#### Scenario: Cleanup old backups
- **WHEN** user runs `fx backup myfile.txt --max-backups 3`
- **AND** there are already 5 backups
- **THEN** only the 3 most recent backups remain
- **AND** the 2 oldest backups are deleted

#### Scenario: No cleanup when under limit
- **WHEN** user runs `fx backup myfile.txt --max-backups 5`
- **AND** there are only 3 backups
- **THEN** no backups are deleted

### Requirement: Error Handling
The system SHALL handle backup errors gracefully with clear error messages.

#### Scenario: Backup nonexistent file
- **WHEN** user attempts to backup `/nonexistent/file.txt`
- **THEN** an error message is displayed
- **AND** the command returns non-zero exit code

#### Scenario: Permission denied
- **WHEN** user attempts to backup a file without read permissions
- **THEN** an error message indicates permission issue
- **AND** the command returns non-zero exit code

#### Scenario: Backup directory creation failure
- **WHEN** backup directory cannot be created
- **THEN** an error message explains the failure
- **AND** no partial backups are created

### Requirement: Cross-Platform Compatibility
The system SHALL work consistently across Windows, macOS, and Linux.

#### Scenario: Backup on different platforms
- **WHEN** user runs `fx backup` on any supported platform
- **THEN** backups are created with correct path separators
- **AND** timestamps use platform-independent formats
