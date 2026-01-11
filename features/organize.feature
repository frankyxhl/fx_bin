# language: en
@file_management @organize_command
Feature: File Organization by Date
  As a developer managing file collections
  I want to organize files into date-based directory structures
  So that I can maintain a clean and logically organized file system

  Business Rules:
  - Files are organized by creation date into hierarchical date directories
  - Default directory structure is YYYY/YYYYMM/YYYYMMDD/ (depth 3)
  - Original files are removed from source location after successful organization
  - Date calculations use local timezone
  - Symlinks are skipped with warnings for security
  - Empty directories are preserved by default
  - Conflicts can be resolved with SKIP, OVERWRITE, RENAME, or ASK strategies

  Background:
    Given I have a test directory structure with various files
    And the test directory contains files with different creation dates

  @smoke @critical
  Scenario: Organize files by date with default settings (depth 3)
    Given I have a directory containing files from different dates:
      | Filename      | Creation Date |
      | photo1.jpg    | 2026-01-10    |
      | photo2.jpg    | 2026-01-15    |
      | document.pdf  | 2025-12-05    |
    When I run "fx organize"
    Then files should be organized into directory structure "2026/202601/20260110/"
    And "photo1.jpg" should be located at "2026/202601/20260110/photo1.jpg"
    And "photo2.jpg" should be located at "2026/202601/20260115/photo2.jpg"
    And "document.pdf" should be located at "2025/202512/20251205/document.pdf"
    And original directory should be empty

  @smoke @critical
  Scenario: Organize with depth 2
    Given I have a directory containing files from different dates:
      | Filename    | Creation Date |
      | image.png   | 2026-01-20    |
      | notes.txt   | 2026-01-20    |
    When I run "fx organize --depth 2"
    Then files should be organized into directory structure "2026/20260120/"
    And "image.png" should be located at "2026/20260120/image.png"
    And "notes.txt" should be located at "2026/20260120/notes.txt"

  @smoke @critical
  Scenario: Organize with depth 1
    Given I have a directory containing files from different dates:
      | Filename    | Creation Date |
      | data.csv    | 2026-01-25    |
    When I run "fx organize --depth 1"
    Then files should be organized into directory structure "20260125/"
    And "data.csv" should be located at "20260125/data.csv"

  @smoke @recursion
  Scenario: Recursive scanning of nested directories
    Given I have a directory structure:
      | Level    | Path                | Files            | Dates      |
      | current  | ./                  | file1.txt        | 2026-01-10 |
      | subdir   | ./photos/           | image.jpg        | 2026-01-10 |
      | nested   | ./photos/vacation/  | beach.jpg        | 2026-01-10 |
    When I run "fx organize --recursive"
    Then files should be organized into "2026/202601/20260110/" directory
    And "file1.txt" should be moved from current directory
    And "image.jpg" should be moved from photos subdirectory
    And "beach.jpg" should be moved from photos/vacation nested directory

  @smoke
  Scenario: Dry-run preview changes without modifying files
    Given I have a directory containing files from different dates:
      | Filename    | Creation Date |
      | report.pdf  | 2026-01-12    |
      | data.xlsx   | 2026-01-12    |
    When I run "fx organize --dry-run"
    Then I should see a preview of planned file movements
    And "report.pdf" should remain in original location
    And "data.xlsx" should remain in original location
    And no date directories should be created
    And filesystem should be completely unchanged

  @smoke
  Scenario: Dry-run with verbose output shows source and target paths
    Given I have a file "document.txt" created on 2026-01-18
    When I run "fx organize --dry-run --verbose"
    Then I should see source path and target path for each file
    And filesystem should be completely unchanged

  @error_handling
  Scenario: SKIP mode skips conflicting files
    Given I have a directory "organized/2026/202601/20260110/" with existing file "photo.jpg"
    And I have a source file "photo.jpg" created on 2026-01-10 in current directory
    When I run "fx organize --on-conflict skip"
    Then the conflicting "photo.jpg" should be skipped
    And the existing file in "organized/2026/202601/20260110/photo.jpg" should remain unchanged
    And the source "photo.jpg" should remain in current directory
    And skip should be recorded in statistics

  @error_handling
  Scenario: OVERWRITE mode replaces existing files
    Given I have a directory "organized/2026/202601/20260110/" with existing file "photo.jpg"
    And I have a source file "photo.jpg" created on 2026-01-10 in current directory
    When I run "fx organize --on-conflict overwrite"
    Then the existing file should be atomically replaced
    And the new "photo.jpg" should be located at "organized/2026/202601/20260110/photo.jpg"
    And the source "photo.jpg" should be removed from current directory

  @error_handling
  Scenario: RENAME mode adds suffix to conflicting files
    Given I have a directory "organized/2026/202601/20260110/" with existing file "photo.jpg"
    And I have a source file "photo.jpg" created on 2026-01-10 in current directory
    When I run "fx organize --on-conflict rename"
    Then the source file should be renamed to "photo_1.jpg"
    And "photo_1.jpg" should be located at "organized/2026/202601/20260110/photo_1.jpg"
    And the existing "photo.jpg" should remain unchanged

  @error_handling
  Scenario: RENAME mode handles multiple conflicts with incremental suffixes
    Given I have existing files "photo.jpg", "photo_1.jpg", "photo_2.jpg" in target directory
    And I have a source file "photo.jpg" created on 2026-01-10
    When I run "fx organize --on-conflict rename"
    Then the source file should be renamed to "photo_3.jpg"
    And "photo_3.jpg" should be located at the target path

  @integration
  Scenario: ASK mode prompts user in TTY environment
    Given I have a directory "organized/2026/202601/20260110/" with existing file "document.pdf"
    And I have a source file "document.pdf" created on 2026-01-10 in current directory
    And stdin is a TTY (interactive terminal)
    When I run "fx organize --on-conflict ask"
    And I confirm the prompt to overwrite
    Then the existing file should be replaced
    And the new "document.pdf" should be located at "organized/2026/202601/20260110/document.pdf"

  @integration
  Scenario: ASK mode skips when user declines prompt
    Given I have a directory "organized/2026/202601/20260110/" with existing file "data.csv"
    And I have a source file "data.csv" created on 2026-01-10 in current directory
    And stdin is a TTY (interactive terminal)
    When I run "fx organize --on-conflict ask"
    And I decline the prompt to overwrite
    Then the conflicting "data.csv" should be skipped
    And the existing file should remain unchanged
    And the source "data.csv" should remain in current directory

  @integration @error_handling
  Scenario: ASK mode falls back to SKIP in non-TTY environment
    Given I have a directory "organized/2026/202601/20260110/" with existing file "file.txt"
    And I have a source file "file.txt" created on 2026-01-10 in current directory
    And stdin is not a TTY (piped input or non-interactive)
    When I run "fx organize --on-conflict ask"
    Then the conflicting file should be skipped automatically
    And no prompt should be displayed
    And the behavior should match SKIP mode

  @edge_cases
  Scenario: Handle empty directory gracefully
    Given I have an empty directory
    When I run "fx organize"
    Then I should see a message "Summary: 0 files, 0 processed, 0 skipped"
    And the command should exit with status 0
    And no date directories should be created

  @edge_cases @error_handling
  Scenario: Handle non-existent directory path
    Given the directory "/nonexistent/path" does not exist
    When I run "fx organize /nonexistent/path"
    Then I should see an error message "Directory '/nonexistent/path' does not exist"
    And the command should exit with status 2

  @edge_cases
  Scenario: Skip symlink files for security
    Given I have a directory containing:
      | Type    | Name        | Target           |
      | file    | normal.txt  | N/A              |
      | symlink | link.txt    | normal.txt       |
    When I run "fx organize"
    Then "normal.txt" should be organized into date directory
    And "link.txt" should be skipped
    And a warning should be logged for symlink

  @edge_cases @recursion
  Scenario: Skip symlink directories in recursive mode
    Given I have a directory structure:
      | Type    | Path              | Target           |
      | dir     | ./photos/         | N/A              |
      | symlink | ./external_link/  | /other/path/     |
    When I run "fx organize --recursive"
    Then files in "./photos/" should be processed
    And "./external_link/" should not be followed
    And processing should continue without error

  @edge_cases
  Scenario: Prevent path traversal through symlinks
    Given I have a symlink pointing outside the source directory
    And the symlink target contains files
    When I run "fx organize --recursive"
    Then the symlink should be skipped
    And files outside source directory should not be accessed
    And a security warning should be logged

  @edge_cases
  Scenario: Idempotent operation on already organized files
    Given I have files already organized in "2026/202601/20260110/" directory structure
    When I run "fx organize" on the organized directory
    Then files should remain in their current locations
    And no files should be moved
    And the command should report no files to organize

  @sorting
  Scenario: Use modification time instead of creation time
    Given I have a file "old_file.txt" created on 2026-01-01
    And the file was modified on 2026-01-20
    When I run "fx organize --date-source modified"
    Then "old_file.txt" should be organized into "2026/202601/20260120/" directory
    And the modification date should determine the target directory

  @output_options
  Scenario: Organize to custom output directory
    Given I have a directory with files created on 2026-01-15
    And I have an output directory "/custom/organized"
    When I run "fx organize --output /custom/organized"
    Then date directories should be created in "/custom/organized/"
    And files should be moved to "/custom/organized/2026/202601/20260115/"

  @recursion
  Scenario: Non-recursive mode limits to current directory
    Given I have a directory structure:
      | Level    | Path              | Files         |
      | current  | ./                | file1.txt     |
      | subdir   | ./subdir/         | file2.txt     |
      | nested   | ./subdir/nested/  | file3.txt     |
    When I run "fx organize" without --recursive flag
    Then only "file1.txt" should be organized
    And files in subdirectories should not be processed

  @recursion
  Scenario: Maximum recursion depth is enforced
    Given I have a directory nested 150 levels deep with a file "deep.txt"
    When I run "fx organize --recursive"
    Then directories beyond depth 100 should be skipped
    And "deep.txt" should not be organized
    And a warning should be logged for exceeding max depth

  @recursion
  Scenario: Cycle detection prevents infinite loops
    Given I have a directory cycle created via symlinks or hardlinks
    When I run "fx organize --recursive"
    Then already visited directories should be skipped
    And processing should complete without infinite loop
    And inode-based detection should prevent reprocessing

  @output_options
  Scenario: Output directory inside source tree is excluded
    Given I run "fx organize --output ./organized" in current directory
    And "./organized/" contains files from previous run
    When I run "fx organize --recursive --output ./organized" again
    Then files in "./organized/" should not be re-scanned
    And only new files in current directory should be processed

  @output_options
  Scenario: Similar prefix paths are not confused
    Given source directory is "/a/b"
    And output directory is "/a/b2"
    When I run "fx organize --output /a/b2"
    Then "/a/b2" should not be treated as inside "/a/b"
    And output directory exclusion should not be triggered

  @output_options
  Scenario: Cross-device output directory does not crash
    Given source directory is on drive C:\
    And output directory is on drive D:\
    When I run "fx organize --output D:\output"
    Then processing should continue without crash
    And files should be successfully organized to D:\output

  @confirmation
  Scenario: Require confirmation before execution
    Given I have files ready to organize
    And stdin is a TTY (interactive terminal)
    When I run "fx organize" without --yes flag
    Then a summary should be displayed with file count
    And user should be prompted to confirm before proceeding
    And execution should wait for user confirmation

  @confirmation
  Scenario: Skip confirmation with --yes flag
    Given I have files ready to organize
    When I run "fx organize --yes"
    Then execution should proceed without confirmation prompt
    And files should be organized immediately

  @confirmation
  Scenario: Non-interactive stdin auto-confirms
    Given I have files ready to organize
    And stdin is not a TTY (piped input)
    When I run "fx organize" without --yes flag
    Then command should proceed as if --yes was specified
    And no confirmation prompt should be displayed

  @cleanup
  Scenario: Keep empty directories by default
    Given I have a directory with files that will be organized
    And the directory contains only those files
    When I run "fx organize" without --clean-empty flag
    Then source directories should remain even if empty
    And no directory cleanup should occur

  @cleanup
  Scenario: Remove empty directories under source root
    Given I have a directory structure with files that will be organized
    And moving files creates empty directories under source root
    When I run "fx organize --clean-empty"
    Then empty directories under source root should be removed
    And directories outside source root should not be removed

  @cleanup
  Scenario: Nested empty directory cleanup happens bottom-up
    Given I have nested directories "a/b/c/" with files
    And organizing all files leaves all directories empty
    When I run "fx organize --clean-empty"
    Then directory "c" should be removed first
    Then directory "b" should be removed second
    Then directory "a" should be removed last

  @error_handling
  Scenario: Continue on error by default
    Given I have multiple files to organize
    And one file will fail with a permission error
    When I run "fx organize"
    Then the error should be logged
    And processing should continue with remaining files
    And successfully organized files should remain organized
    And error count should be included in summary

  @error_handling
  Scenario: Fail fast stops processing on first error
    Given I have multiple files to organize
    And one file will fail with a permission error
    When I run "fx organize --fail-fast"
    Then processing should stop immediately on first error
    And completed moves should be preserved
    And error should be reported in summary

  @error_handling
  Scenario: Cross-filesystem move uses copy+replace pattern
    Given I have a file on one filesystem
    And target directory is on a different filesystem
    When I run "fx organize --output /different/filesystem"
    Then file should be copied to target location
    And source file should be deleted only after successful copy
    And operation should complete without EXDEV error

  @filtering
  Scenario: Include specific file extensions with repeatable option
    Given I have a directory with files "photo.jpg", "photo.png", "document.pdf", "data.txt"
    When I run "fx organize --include '*.jpg' --include '*.png'"
    Then only files matching "*.jpg" and "*.png" should be organized
    And "document.pdf" should not be organized
    And "data.txt" should not be organized

  @filtering
  Scenario: Exclude specific patterns with repeatable option
    Given I have a directory with files including "*.tmp" and ".DS_Store"
    When I run "fx organize --exclude '*.tmp' --exclude '.DS_Store'"
    Then files matching "*.tmp" should not be organized
    And files matching ".DS_Store" should not be organized
    And other files should be organized normally

  @filtering
  Scenario: Combine include and exclude filters
    Given I have a directory with various file types
    When I run "fx organize --include '*.jpg' --include '*.png' --exclude '*.tmp'"
    Then only "*.jpg" and "*.png" files should be considered
    And "*.tmp" files should be excluded even if they match include

  @filtering
  Scenario: Pattern matches basename only with case sensitivity
    Given I have a file at "photos/vacation/beach.jpg"
    When I run "fx organize --include '*.JPG'"
    Then the file should not match the pattern
    And pattern matching should be case-sensitive

  @hidden_files
  Scenario: Ignore hidden files by default
    Given I have a directory with files ".hidden.txt" and "visible.txt"
    When I run "fx organize"
    Then ".hidden.txt" should not be organized
    And "visible.txt" should be organized

  @hidden_files
  Scenario: Include hidden files with --hidden flag
    Given I have a directory with files ".hidden.txt" and "visible.txt"
    When I run "fx organize --hidden"
    Then ".hidden.txt" should be organized
    And "visible.txt" should be organized

  @progress
  Scenario: Simple progress shows current file
    Given I have multiple files to organize
    When I run "fx organize" without --quiet flag
    Then current file being processed should be shown
    And progress should update for each file

  @progress
  Scenario: Verbose output shows source, target, and status
    Given I have multiple files to organize
    When I run "fx organize --verbose"
    Then source path should be shown for each file
    And target path should be shown for each file
    And status should be shown for each file

  @progress
  Scenario: Quiet mode suppresses per-file progress
    Given I have multiple files to organize
    When I run "fx organize --quiet"
    Then per-file progress details should be suppressed
    And only errors and final summary should be displayed

  @progress
  Scenario: Quiet mode shows summary even with no errors
    Given I have files that organize successfully
    When I run "fx organize --quiet"
    Then summary should be displayed showing files moved, skipped, directories created
    And summary should appear regardless of error occurrence

  @statistics
  Scenario: Completion statistics show all metrics
    Given I have multiple files to organize with various outcomes
    When I run "fx organize"
    Then summary should show files moved count
    And summary should show files skipped count
    And summary should show errors count
    And summary should show directories created count

  @statistics
  Scenario: Output order is deterministic
    Given I have multiple files to organize
    When I run "fx organize"
    Then output should be sorted by source path
    And results should be reproducible across runs

  @help_and_usage
  Scenario: Display help information
    When I run "fx organize --help"
    Then I should see usage information
    And I should see all available options explained
    And I should see example commands

  @version_compatibility
  Scenario: Version information display
    When I run "fx organize --version"
    Then I should see the current version number
    And the format should match other fx commands
