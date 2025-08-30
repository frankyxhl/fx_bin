# language: en
@file_management @filter_command
Feature: File Filtering by Extension
  As a developer working with file collections
  I want to filter files by their extensions with flexible sorting options
  So that I can quickly locate and organize files by type and recency

  Business Rules:
  - Files are filtered by exact extension match (case-insensitive)
  - Default sorting is by creation time (newest first)
  - Recursive search is enabled by default
  - Multiple extensions can be specified in a single command
  - Output format can be simple (filename only) or detailed (with metadata)
  - Security: Path traversal attacks are blocked
  - Performance: Large directories are handled efficiently

  Background:
    Given I have a test directory structure with various file types
    And the test directory contains files with different creation and modification times

  @smoke @critical
  Scenario: Filter files by single extension with default settings
    Given I have a directory containing files with extensions "txt", "py", and "md"
    When I run "fx filter txt"
    Then I should see only files with ".txt" extension
    And the results should be sorted by creation time (newest first)
    And the search should be recursive
    And the output should be in simple format

  @smoke @critical  
  Scenario: Filter files by multiple extensions
    Given I have a directory with files having extensions "mp4", "avi", "mkv", "txt"
    When I run "fx filter mp4,avi,mkv"
    Then I should see files with extensions ".mp4", ".avi", and ".mkv"
    And I should not see files with other extensions
    And the results should be sorted by creation time (newest first)

  @sorting
  Scenario: Sort filtered files by modification time
    Given I have multiple ".txt" files with different modification times
    When I run "fx filter txt --sort-by modified"
    Then I should see files sorted by modification time (newest first)
    And the most recently modified file should appear first

  @sorting
  Scenario: Sort filtered files in reverse order
    Given I have multiple ".py" files with different creation times
    When I run "fx filter py --reverse"
    Then I should see files sorted by creation time (oldest first)
    And the oldest file should appear first

  @sorting
  Scenario: Combine sorting options
    Given I have multiple ".log" files with different modification times
    When I run "fx filter log --sort-by modified --reverse"
    Then I should see files sorted by modification time (oldest first)
    And the least recently modified file should appear first

  @recursion
  Scenario: Non-recursive search limits to current directory
    Given I have a directory structure:
      | Level    | Path              | Files         |
      | current  | ./                | file1.txt     |
      | subdir   | ./subdir/         | file2.txt     |
      | nested   | ./subdir/nested/  | file3.txt     |
    When I run "fx filter txt --no-recursive"
    Then I should see only "file1.txt"
    And I should not see files from subdirectories

  @recursion
  Scenario: Recursive search includes all subdirectories
    Given I have a directory structure:
      | Level    | Path              | Files         |
      | current  | ./                | file1.txt     |
      | subdir   | ./subdir/         | file2.txt     |
      | nested   | ./subdir/nested/  | file3.txt     |
    When I run "fx filter txt --recursive"
    Then I should see "file1.txt", "file2.txt", and "file3.txt"
    And the paths should show the relative directory structure

  @output_format
  Scenario: Simple format output shows filenames only
    Given I have files "document.pdf", "image.jpg", "video.mp4"
    When I run "fx filter pdf --format simple"
    Then I should see only the filename "document.pdf"
    And I should not see timestamps, sizes, or other metadata

  @output_format
  Scenario: Detailed format output shows file metadata
    Given I have a file "report.docx" with known metadata
    When I run "fx filter docx --format detailed"
    Then I should see the filename "report.docx"
    And I should see the creation time
    And I should see the modification time
    And I should see the file size
    And I should see the relative path

  @pagination
  Scenario: Limit number of results returned
    Given I have 50 files with ".txt" extension
    When I run "fx filter txt --limit 10"
    Then I should see exactly 10 results
    And the results should be the 10 most recently created files

  @edge_cases
  Scenario: No files found with specified extension
    Given I have a directory with only ".txt" and ".py" files
    When I run "fx filter pdf"
    Then I should see a message "No files found with extension(s): pdf"
    And the command should exit with status 0

  @edge_cases
  Scenario: Empty directory
    Given I have an empty directory
    When I run "fx filter txt"
    Then I should see a message "No files found in the specified directory"
    And the command should exit with status 0

  @edge_cases
  Scenario: Directory does not exist
    Given the directory "/nonexistent/path" does not exist
    When I run "fx filter txt /nonexistent/path"
    Then I should see an error message "Directory not found: /nonexistent/path"
    And the command should exit with status 1

  @security
  Scenario: Block path traversal attempts
    Given I am in a secure directory environment
    When I run "fx filter txt ../../../etc/passwd"
    Then I should see an error message "Invalid path: path traversal detected"
    And the command should exit with status 1
    And no files outside the allowed directory should be accessed

  @security
  Scenario: Handle permission denied gracefully
    Given I have a directory with restricted permissions
    When I run "fx filter txt /restricted/directory"
    Then I should see a warning "Permission denied for some files in: /restricted/directory"
    And accessible files should still be displayed
    And the command should exit with status 0

  @error_handling
  Scenario: Invalid sort-by option
    Given I have files with ".txt" extension
    When I run "fx filter txt --sort-by invalid"
    Then I should see an error message "Invalid sort option: invalid. Use 'created' or 'modified'"
    And the command should exit with status 1

  @error_handling
  Scenario: Invalid format option
    Given I have files with ".txt" extension
    When I run "fx filter txt --format invalid"
    Then I should see an error message "Invalid format option: invalid. Use 'simple' or 'detailed'"
    And the command should exit with status 1

  @performance
  Scenario: Handle large directories efficiently
    Given I have a directory with 10,000 files of various extensions
    When I run "fx filter txt --limit 100"
    Then the command should complete within 5 seconds
    And memory usage should remain under 100MB
    And I should see up to 100 results

  @integration
  Scenario: Integration with other fx commands
    Given I have filtered results from "fx filter py"
    When I pipe the results to "fx size"
    Then I should see size information for only the Python files
    And the pipeline should execute successfully

  @case_sensitivity
  Scenario: Extension matching is case-insensitive
    Given I have files "Document.PDF", "image.JPG", "script.PY"
    When I run "fx filter pdf,jpg,py"
    Then I should see all three files
    And case variations should be handled correctly

  @multiple_directories
  Scenario: Filter files across multiple directories
    Given I have directories "dir1" and "dir2" with ".txt" files
    When I run "fx filter txt dir1 dir2"
    Then I should see ".txt" files from both directories
    And each result should show which directory it came from

  @glob_patterns
  Scenario: Support for glob-like patterns in extensions
    Given I have files with extensions "txt", "tx1", "tx2"
    When I run "fx filter 'tx*'"
    Then I should see files matching the pattern
    And files with "txt", "tx1", and "tx2" extensions should be included

  @help_and_usage
  Scenario: Display help information
    When I run "fx filter --help"
    Then I should see usage information
    And I should see all available options explained
    And I should see example commands

  @version_compatibility
  Scenario: Version information display
    When I run "fx filter --version"
    Then I should see the current version number
    And the format should match other fx commands