# Tasks: Add fx realpath command

## 1. Setup
- [x] 1.1 Create feature branch using git worktree

## 2. Implementation (TDD)
- [x] 2.1 Write unit tests for `resolve_path()` function
  - [x] Test current directory `.` resolution
  - [x] Test relative path `../foo` resolution
  - [x] Test absolute path returns correctly
  - [x] Test default argument `"."` handling
  - [x] Test `~` expansion to home directory
  - [x] Test symlink resolution
  - [x] Test circular symlink raises OSError
  - [x] Test FileNotFoundError for non-existent paths
  - [x] Test PermissionError handling
- [x] 2.2 Implement `fx_bin/realpath.py` with `resolve_path()` function
- [x] 2.3 Add CLI command to `fx_bin/cli.py`
  - [x] Add `realpath` to `COMMANDS_INFO`
  - [x] Create `@cli.command()` for realpath
  - [x] Handle OSError for edge cases (circular symlinks, etc.)
- [x] 2.4 Write integration tests for CLI
  - [x] Test successful path output
  - [x] Test no argument uses current directory
  - [x] Test error exit code for non-existent path
  - [x] Test `--help` output
  - [x] Test command appears in `fx list`
  - [x] Test command appears in `fx --help`
  - [x] Test invalid flag handled gracefully

## 3. Verification
- [x] 3.1 Run `make lint` - zero errors
- [x] 3.2 Run `make type-check` - zero errors
- [x] 3.3 Run `make test` - all tests pass
- [x] 3.4 Run `make security-scan` - no issues

## 4. Review & Merge
- [x] 4.1 Code review by oracle
- [x] 4.2 Address review feedback (if any)
- [x] 4.3 Merge to main branch
