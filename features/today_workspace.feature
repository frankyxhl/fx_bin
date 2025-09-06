# language: en
@workspace @today_command
Feature: Daily Workspace Management
  As a developer who downloads and works with files daily
  I want to quickly navigate to a date-organized workspace
  So that I can keep my Downloads folder organized by date

  Business Rules:
  - Default directory is ~/Downloads/YYYYMMDD (e.g., ~/Downloads/20250906)
  - Directory is created if it doesn't exist
  - Command is idempotent (safe to run multiple times)
  - Supports custom base directories
  - Supports custom date formats
  - Security: Path traversal attacks are blocked
  - Shell integration enables actual directory navigation

  Background:
    Given I have a home directory with a Downloads folder
    And the current date is "2025-09-06"

  @smoke @critical
  Scenario: Create today's workspace directory with default settings
    When I run "fx today --cd"
    Then the exit code should be 0
    And the output should contain "/Downloads/20250906"
    And the directory "~/Downloads/20250906" should exist
    And the directory permissions should be readable and writable by the user

  @smoke @critical
  Scenario: Navigate to existing today directory
    Given the directory "~/Downloads/20250906" already exists
    When I run "fx today --cd"
    Then the exit code should be 0
    And the output should contain "/Downloads/20250906"
    And no duplicate directory should be created
    And the existing directory should remain unchanged

  @output_format
  Scenario: Display friendly message without --cd flag
    When I run "fx today"
    Then the exit code should be 0
    And the output should contain "Today's workspace: "
    And the output should contain "/Downloads/20250906"
    And the directory "~/Downloads/20250906" should exist

  @custom_path
  Scenario: Use custom base directory
    When I run "fx today --base ~/Projects --cd"
    Then the exit code should be 0
    And the output should contain "/Projects/20250906"
    And the directory "~/Projects/20250906" should exist
    And the directory "~/Downloads/20250906" should not be created

  @custom_path
  Scenario: Handle relative base directory
    When I run "fx today --base ./temp --cd"
    Then the exit code should be 0
    And the output should contain "/temp/20250906"
    And the directory "./temp/20250906" should exist

  @date_format
  Scenario: Support custom date format with dashes
    When I run "fx today --format %Y-%m-%d --cd"
    Then the exit code should be 0
    And the output should contain "/Downloads/2025-09-06"
    And the directory "~/Downloads/2025-09-06" should exist

  @date_format
  Scenario: Support custom date format with underscores
    When I run "fx today --format %Y_%m_%d --cd"
    Then the exit code should be 0
    And the output should contain "/Downloads/2025_09_06"
    And the directory "~/Downloads/2025_09_06" should exist

  @error_handling
  Scenario: Handle permission denied error gracefully
    Given the directory "~/Downloads" has no write permissions
    When I run "fx today --cd"
    Then the exit code should be 1
    And the error output should contain "Permission denied"
    And the error output should contain "Cannot create directory"

  @error_handling
  Scenario: Handle invalid date format
    When I run "fx today --format invalid_format --cd"
    Then the exit code should be 1
    And the error output should contain "Invalid date format"

  @security
  Scenario: Block path traversal attempts in base directory
    When I run "fx today --base ~/Downloads/../../../etc --cd"
    Then the exit code should be 1
    And the error output should contain "Invalid base directory"
    And no directory should be created in "/etc"

  @integration
  Scenario: Show help information for today command
    When I run "fx today --help"
    Then the exit code should be 0
    And the output should contain "Create and navigate to today's workspace directory"
    And the output should contain "--cd"
    And the output should contain "--base"
    And the output should contain "--format"

  @integration
  Scenario: Appear in command list
    When I run "fx list"
    Then the output should contain "today"
    And the output should contain "workspace directory"

  @dry_run
  Scenario: Support dry run mode
    When I run "fx today --dry-run --cd"
    Then the exit code should be 0
    And the output should contain "Would create: "
    And the output should contain "/Downloads/20250906"
    And the directory "~/Downloads/20250906" should not exist

  @verbose
  Scenario: Show verbose output when requested
    When I run "fx today --verbose --cd"
    Then the exit code should be 0
    And the output should contain "Creating directory"
    And the output should contain "/Downloads/20250906"
    And the output should contain "Directory created successfully"

  @exec_shell @shell_integration
  Scenario: Default behavior starts new shell in today's directory
    When I run "fx today" with shell mocking
    Then the exit code should be 0
    And a new shell should be spawned
    And the shell should be started in "~/Downloads/20250906"
    And the output should contain "Starting new shell in:"
    And the output should contain "/Downloads/20250906"

  @exec_shell @shell_detection
  Scenario: Detect user's preferred shell from environment
    Given the SHELL environment variable is set to "/bin/zsh"
    When I run "fx today" with shell mocking
    Then a new shell should be spawned with "/bin/zsh"
    And the output should contain "Shell: /bin/zsh"

  @exec_shell @shell_detection
  Scenario: Fallback to system shell when SHELL not set
    Given the SHELL environment variable is not set
    When I run "fx today" with shell mocking
    Then a new shell should be spawned with a system default shell
    And the shell executable should be one of ["/bin/zsh", "/bin/bash", "/bin/sh"]

  @exec_shell @no_exec
  Scenario: Disable shell execution with --no-exec flag
    When I run "fx today --no-exec"
    Then the exit code should be 0
    And no shell should be spawned
    And the output should contain "Today's workspace: "
    And the output should contain "/Downloads/20250906"
    And the directory "~/Downloads/20250906" should exist

  @exec_shell @output_modes
  Scenario: Shell execution disabled in --cd mode
    When I run "fx today --cd"
    Then the exit code should be 0
    And no shell should be spawned
    And the output should only contain "/Downloads/20250906"

  @exec_shell @output_modes
  Scenario: Shell execution disabled in --dry-run mode
    When I run "fx today --dry-run"
    Then the exit code should be 0
    And no shell should be spawned
    And the output should contain "Would create: "
    And the directory "~/Downloads/20250906" should not exist

  @exec_shell @verbose
  Scenario: Verbose output shows shell information
    When I run "fx today --verbose" with shell mocking
    Then the exit code should be 0
    And the output should contain "Starting new shell in:"
    And the output should contain "Shell:"
    And the output should contain "Type 'exit' to return"

  @exec_shell @error_handling
  Scenario: Handle shell execution errors gracefully
    When I run "fx today" with shell execution failing
    Then the exit code should be 1
    And the error output should contain "Error starting shell"
    And the directory "~/Downloads/20250906" should still exist

  @exec_shell @cross_platform
  Scenario: Windows PowerShell detection and execution
    Given the platform is Windows
    And PowerShell is available
    When I run "fx today" with shell mocking
    Then a new shell should be spawned with "powershell"
    And the shell should be started with "-NoLogo" parameter

  @exec_shell @cross_platform
  Scenario: Windows cmd fallback when PowerShell unavailable
    Given the platform is Windows
    And PowerShell is not available
    When I run "fx today" with shell mocking
    Then a new shell should be spawned with "cmd"