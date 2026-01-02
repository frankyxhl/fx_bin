# Tasks: Add fx realpath command

## 1. Setup
- [ ] 1.1 Create feature branch using git worktree

## 2. Implementation (TDD)
- [ ] 2.1 Write unit tests for `resolve_path()` function
  - [ ] Test current directory `.` resolution
  - [ ] Test relative path `../foo` resolution
  - [ ] Test absolute path returns correctly
  - [ ] Test default argument `"."` handling
  - [ ] Test `~` expansion to home directory
  - [ ] Test symlink resolution
  - [ ] Test circular symlink raises OSError
  - [ ] Test FileNotFoundError for non-existent paths
  - [ ] Test PermissionError handling
- [ ] 2.2 Implement `fx_bin/realpath.py` with `resolve_path()` function
- [ ] 2.3 Add CLI command to `fx_bin/cli.py`
  - [ ] Add `realpath` to `COMMANDS_INFO`
  - [ ] Create `@cli.command()` for realpath
  - [ ] Handle OSError for edge cases (circular symlinks, etc.)
- [ ] 2.4 Write integration tests for CLI
  - [ ] Test successful path output
  - [ ] Test no argument uses current directory
  - [ ] Test error exit code for non-existent path
  - [ ] Test `--help` output
  - [ ] Test command appears in `fx list`
  - [ ] Test command appears in `fx --help`
  - [ ] Test invalid flag handled gracefully

## 3. Verification
- [ ] 3.1 Run `make lint` - zero errors
- [ ] 3.2 Run `make type-check` - zero errors  
- [ ] 3.3 Run `make test` - all tests pass
- [ ] 3.4 Run `make security-scan` - no issues

## 4. Review & Merge
- [ ] 4.1 Code review by oracle
- [ ] 4.2 Address review feedback (if any)
- [ ] 4.3 Merge to main branch
