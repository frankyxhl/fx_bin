# Implementation Tasks

## 1. Core Module Structure
- [x] 1.1 Create backup.py with constants (KNOWN_MULTI_EXTS, DEFAULT_TIMESTAMP_FORMAT)
- [x] 1.2 Implement get_multi_ext() helper function
- [x] 1.3 Implement get_base_name() helper function
- [x] 1.4 Write unit tests for helper functions

## 2. File Backup Functionality
- [x] 2.1 Implement backup_file() with timestamp generation
- [x] 2.2 Handle multi-part extensions (.tar.gz, .tar.bz2)
- [x] 2.3 Write unit tests for file backup success cases
- [x] 2.4 Write unit tests for file backup error cases

## 3. Directory Backup (Uncompressed)
- [x] 3.1 Implement backup_directory() dispatcher
- [x] 3.2 Implement _backup_directory_uncompressed()
- [x] 3.3 Write unit tests for uncompressed directory backup

## 4. Directory Backup (Compressed)
- [x] 4.1 Implement _backup_directory_compressed() with tarfile
- [x] 4.2 Write unit tests for compressed directory backup
- [x] 4.3 Verify .tar.gz file creation

## 5. Backup Cleanup
- [x] 5.1 Implement cleanup_old_backups() with max_backups limit
- [x] 5.2 Handle both file and directory cleanup
- [x] 5.3 Write unit tests for cleanup scenarios

## 6. CLI Integration
- [x] 6.1 Add backup command to cli.py with Click decorators
- [x] 6.2 Implement --backup-dir, --compress, --max-backups options
- [x] 6.3 Add --timestamp-format option
- [x] 6.4 Integrate with backup module functions

## 7. CLI Integration Tests
- [x] 7.1 Test CLI with file backup
- [x] 7.2 Test CLI with directory backup (compressed and uncompressed)
- [x] 7.3 Test CLI with max-backups cleanup
- [x] 7.4 Test error handling in CLI

## 8. Error Handling
- [x] 8.1 Test backup of nonexistent files
- [x] 8.2 Test permission errors
- [x] 8.3 Test invalid paths
- [x] 8.4 Verify proper error messages

## 9. Documentation
- [x] 9.1 Add comprehensive docstrings to backup.py
- [x] 9.2 Add CLI help text with examples
- [x] 9.3 Update README if needed

## 10. Final Verification
- [x] 10.1 Run linter (make lint)
- [x] 10.2 Run type checker (make type-check)
- [x] 10.3 Run full test suite (make test-coverage)
- [x] 10.4 Run security scan (make security-scan)
- [x] 10.5 Manual smoke test
