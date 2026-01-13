## ADDED Requirements

### Requirement: Realpath Command

The system SHALL provide a `realpath` command that resolves file paths to their absolute canonical form.

The command SHALL:
- Accept a single path argument (defaulting to `.` if not provided)
- Expand `~` to user's home directory
- Resolve relative path components (`.`, `..`)
- Follow and resolve symbolic links
- Output only the resolved absolute path (no prefix text)
- Exit with code 0 on success, 1 on error

#### Scenario: Resolve current directory

- **WHEN** user runs `fx realpath .`
- **THEN** output's absolute path of current working directory
- **AND** exit with code 0

#### Scenario: Resolve relative path

- **WHEN** user runs `fx realpath ../foo/bar.txt`
- **AND** path exists
- **THEN** output's absolute path `/path/to/foo/bar.txt`
- **AND** exit with code 0

#### Scenario: Expand home directory

- **WHEN** user runs `fx realpath ~/Downloads`
- **AND** path exists
- **THEN** output's expanded absolute path `/Users/username/Downloads`
- **AND** exit with code 0

#### Scenario: Path does not exist

- **WHEN** user runs `fx realpath nonexistent.txt`
- **AND** path does not exist
- **THEN** outputs error message to stderr: `Error: Path does not exist: nonexistent.txt`
- **AND** exits with code 1

#### Scenario: Permission denied

- **WHEN** user runs `fx realpath /protected/path`
- **AND** user lacks permission to access the path
- **THEN** outputs error message to stderr: `Error: Permission denied: /protected/path`
- **AND** exits with code 1
