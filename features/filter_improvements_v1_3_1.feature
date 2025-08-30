# language: en
@file_management @filter_command @v1_3_1
Feature: Enhanced File Filter Display (v1.3.1)
  As a user of fx filter command
  I want improved output formatting and better parameter handling
  So that I can view filtered files with better alignment and readability

  Business Rules:
  - Remove 'count' format option to simplify interface
  - Default format is 'detailed' instead of 'simple'
  - Detailed format shows: Date | Size | Filename in aligned columns
  - Date format is standard YYYY-MM-DD HH:MM:SS
  - File sizes are right-aligned with units (B/KB/MB/GB) left-aligned
  - File names show basename by default, full path with --show-path flag
  - No redundant words like "modified" in output

  Background:
    Given I have a test directory with files of various sizes and dates
    And the files have different creation and modification times

  @smoke @critical @format_improvements
  Scenario: Default format is now detailed with improved layout
    Given I have files "small.txt" (100 bytes), "medium.py" (5 KB), "large.json" (2 MB)
    When I run "fx filter txt,py,json"
    Then the output should use detailed format by default
    And I should see aligned columns with format:
      """
      2024-08-30 14:22:15    100  B    small.txt
      2024-08-30 14:20:33    5.0 KB    medium.py
      2024-08-30 14:18:45    2.0 MB    large.json
      """
    And the date should be in YYYY-MM-DD HH:MM:SS format
    And the file sizes should be right-aligned
    And the units (B, KB, MB) should be left-aligned
    And only filenames should be shown (not full paths)

  @format_improvements
  Scenario: Count format option has been removed
    Given I have files with ".txt" extension
    When I run "fx filter txt --format count"
    Then I should see an error message "Invalid format option: count. Use 'simple' or 'detailed'"
    And the command should exit with status 1

  @format_improvements
  Scenario: Simple format still available for backward compatibility
    Given I have files "doc1.txt", "doc2.txt", "doc3.txt"
    When I run "fx filter txt --format simple"
    Then I should see only file paths:
      """
      doc1.txt
      doc2.txt
      doc3.txt
      """
    And I should not see dates or file sizes

  @format_improvements @show_path
  Scenario: Show-path flag displays relative paths
    Given I have a directory structure:
      | Path                | File        | Size |
      | ./                  | root.txt    | 1 KB |
      | ./docs/             | guide.txt   | 2 KB |
      | ./src/utils/        | helper.txt  | 3 KB |
    When I run "fx filter txt --show-path"
    Then I should see aligned output with relative paths:
      """
      2024-08-30 14:22:15    1.0 KB    root.txt
      2024-08-30 14:21:30    2.0 KB    docs/guide.txt
      2024-08-30 14:20:45    3.0 KB    src/utils/helper.txt
      """

  @format_improvements @show_path
  Scenario: Default behavior shows only filenames (no path)
    Given I have a directory structure:
      | Path                | File        | Size |
      | ./                  | root.txt    | 1 KB |
      | ./docs/             | guide.txt   | 2 KB |
      | ./src/utils/        | helper.txt  | 3 KB |
    When I run "fx filter txt"
    Then I should see aligned output with filenames only:
      """
      2024-08-30 14:22:15    1.0 KB    root.txt
      2024-08-30 14:21:30    2.0 KB    guide.txt
      2024-08-30 14:20:45    3.0 KB    helper.txt
      """
    And I should not see directory paths

  @format_improvements
  Scenario: File size alignment with different units
    Given I have files with various sizes:
      | File      | Size    |
      | tiny.txt  | 42 B    |
      | small.py  | 1.5 KB  |
      | medium.js | 256 KB  |
      | large.sql | 15.7 MB |
      | huge.log  | 2.3 GB  |
    When I run "fx filter txt,py,js,sql,log"
    Then the file sizes should be aligned:
      """
      2024-08-30 14:25:00     42  B    tiny.txt
      2024-08-30 14:24:30    1.5 KB    small.py
      2024-08-30 14:24:15    256 KB    medium.js
      2024-08-30 14:24:00   15.7 MB    large.sql
      2024-08-30 14:23:45    2.3 GB    huge.log
      """
    And the numbers should be right-aligned
    And the units (B, KB, MB, GB) should be left-aligned in the same column

  @format_improvements
  Scenario: No redundant words in detailed output
    Given I have a file "document.pdf" modified yesterday
    When I run "fx filter pdf"
    Then I should see clean output without redundant words:
      """
      2024-08-29 16:30:45    1.2 MB    document.pdf
      """
    And I should not see words like "modified:" or "size:" in the output

  @error_handling
  Scenario: Invalid format options updated
    Given I have files with ".txt" extension
    When I run "fx filter txt --format invalid"
    Then I should see an error message "Invalid format option: invalid. Use 'simple' or 'detailed'"
    And the command should exit with status 1

  @help_and_usage
  Scenario: Help shows updated format options
    When I run "fx filter --help"
    Then I should see format options listed as:
      """
      --format [simple|detailed]  Output format (default: detailed)
      """
    And I should see the --show-path option documented:
      """
      --show-path                  Show relative file paths instead of just filenames
      """
    And I should not see 'count' as a format option

  @backwards_compatibility
  Scenario: Existing scripts using simple format continue to work
    Given I have existing scripts that call "fx filter txt --format simple"
    When I run "fx filter txt --format simple"
    Then the output should still be in simple format
    And the behavior should be unchanged from previous versions

  @integration
  Scenario: Enhanced format works with sorting options
    Given I have files with different modification times and sizes
    When I run "fx filter txt --sort-by modified --reverse --show-path"
    Then I should see the enhanced detailed format
    And files should be sorted by modification time (oldest first)
    And relative paths should be displayed
    And the alignment should be maintained

  @edge_cases
  Scenario: Very long filenames don't break alignment
    Given I have files with very long names:
      | File                                          | Size |
      | very_long_filename_that_exceeds_normal_length.txt | 1 KB |
      | short.txt                                     | 2 KB |
    When I run "fx filter txt"
    Then the date and size columns should remain aligned
    And the output should handle long filenames gracefully

  @edge_cases
  Scenario: Empty results with enhanced format
    Given I have a directory with no matching files
    When I run "fx filter nonexistent"
    Then I should see a user-friendly message
    And the command should exit with status 0