## ADDED Requirements

### Requirement: Documentation Site Structure
The project SHALL provide a static documentation site deployed to GitHub Pages using MkDocs with Material Theme.

#### Scenario: User accesses documentation homepage
- **GIVEN** the documentation site is deployed
- **WHEN** a user accesses https://frankyxhl.github.io/fx_bin/
- **THEN** the site SHALL display a professional homepage with:
  - Project title and tagline
  - Key features (unified CLI, safety first, performance, cross-platform, high coverage, security)
  - Installation instructions (pip and pipx)
  - Quick preview commands
  - Badges showing version, tests, coverage, security, and code style

#### Scenario: User navigates documentation
- **GIVEN** the documentation site is loaded
- **WHEN** a user clicks navigation links
- **THEN** the site SHALL provide clear navigation to:
  - Quick Start guide
  - Command reference (all 10 commands)
  - Use Cases
  - Advanced topics
  - Contributing guide

#### Scenario: Documentation is mobile-responsive
- **GIVEN** a user visits the documentation site on a mobile device
- **WHEN** the site loads on a viewport < 768px
- **THEN** the site SHALL display correctly with:
  - Readable font sizes (≥ 16px)
  - Touch-friendly navigation
  - Properly stacked content
  - Accessible code blocks with horizontal scrolling

---

### Requirement: Command Reference Documentation
The documentation SHALL include comprehensive reference pages for all 10 fx commands with examples and use cases.

#### Scenario: User views fx ff command reference
- **GIVEN** a user navigates to the fx ff command page
- **WHEN** the page loads
- **THEN** the page SHALL display:
  - Command overview and core features
  - Complete parameter reference with defaults
  - At least 10 practical examples including:
    - Basic keyword search
    - Pattern matching (e.g., `.py`, `.log`)
    - Excluding directories with `--include-ignored`
    - Multiple `--exclude` patterns
    - First match only with `--first` flag
    - Development workflow examples
    - Project cleanup examples
    - Debugging workflow examples
    - Dependency management examples
    - Configuration file discovery examples

#### Scenario: User views fx replace command reference
- **GIVEN** a user navigates to the fx replace command page
- **WHEN** the page loads
- **THEN** the page SHALL display:
  - Command overview emphasizing atomic write safety
  - Complete parameter reference
  - At least 5 practical examples including:
    - Single file replacement
    - Batch replacement across multiple files
    - Binary file handling explanation
    - Backup and restore behavior
    - Safety best practices

#### Scenario: User views fx organize command reference
- **GIVEN** a user navigates to the fx organize command page
- **WHEN** the page loads
- **THEN** the page SHALL display:
  - Command overview explaining date-based organization
  - Complete parameter reference (date-source, depth, on-conflict, include, exclude, etc.)
  - At least 5 practical examples including:
    - Basic organization with default depth (3)
    - Custom depth (1 or 2) directory structures
    - Dry-run preview before execution
    - Using creation vs modification time
    - Conflict resolution strategies (rename, skip, overwrite)
    - Pattern filtering (include/exclude)
    - Recursive vs non-recursive modes
    - Empty directory cleanup
    - Hidden file handling

#### Scenario: All 10 commands have reference pages
- **GIVEN** the command reference section
- **WHEN** a user browses the navigation
- **THEN** reference pages SHALL exist for:
  - fx files (file counting)
  - fx size (size analysis)
  - fx ff (file finding)
  - fx fff (first file finding)
  - fx filter (file filtering by extension)
  - fx replace (text replacement)
  - fx backup (file/directory backup)
  - fx organize (date-based organization)
  - fx root (Git project root)
  - fx today (daily workspace management)
- **AND** each page SHALL include:
  - Command overview
  - Complete parameter reference
  - At least 5 practical examples
  - Cross-references to related commands

---

### Requirement: Real-World Use Case Documentation
The documentation SHALL include detailed real-world use case scenarios demonstrating practical workflows.

#### Scenario: User learns daily development workflow
- **GIVEN** a user navigates to the Use Cases section
- **WHEN** they read the "Daily Development Workflow" use case
- **THEN** the documentation SHALL provide a complete workflow including:
  - Using `fx today` to enter daily workspace
  - Using `fx files` to count project files by pattern
  - Using `fx filter` to find recently modified files
  - Using `fx ff` to locate TODO markers
  - Shell script example combining commands
  - Expected output for each command

#### Scenario: User learns project cleanup workflow
- **GIVEN** a user navigates to the "Project Cleanup" use case
- **WHEN** they read the documentation
- **THEN** the documentation SHALL provide:
  - Finding backup files with `fx ff .bak`
  - Finding temporary files with `fx ff .tmp`
  - Analyzing temporary file sizes
  - Safe cleanup workflow with confirmation prompts
  - Example shell script for automated cleanup

#### Scenario: User learns version update workflow
- **GIVEN** a user navigates to the "Version Updates" use case
- **WHEN** they read the documentation
- **THEN** the documentation SHALL provide:
  - Creating project backup with `fx backup --compress`
  - Finding version-related files with `fx ff`
  - Batch version string replacement with `fx replace`
  - Verification steps with grep
  - Rollback procedure if needed

#### Scenario: User learns dataset management workflow
- **GIVEN** a user navigates to the "Dataset Management" use case
- **WHEN** they read the documentation
- **THEN** the documentation SHALL provide:
  - Previewing organization plan with `fx organize --dry-run`
  - Organizing data by creation date with depth 3
  - Filtering by file types (csv, json, etc.)
  - Cleaning up empty directories
  - Example output showing directory structure

#### Scenario: User learns automation script integration
- **GIVEN** a user navigates to the "Automation Scripts" use case
- **WHEN** they read the documentation
- **THEN** the documentation SHALL provide:
  - Using `fx root` for Git project detection
  - Using `fx ff` for file discovery
  - Using `fx filter` for file filtering
  - Complete shell script example for deployment
  - Error handling patterns
  - Integration with CI/CD pipelines

---

### Requirement: Shell Integration Documentation
The documentation SHALL include a comprehensive guide for integrating fx commands into shell scripts and workflows.

#### Scenario: User integrates fx root into shell
- **GIVEN** a user reads the Shell Integration guide
- **WHEN** they implement fx root integration
- **THEN** the documentation SHALL provide:
  - Git project navigation patterns
  - Shell function examples (.bashrc/.zshrc)
  - Usage of `--cd` flag for path-only output
  - Error handling for non-Git directories
  - Example: `cd $(fx root --cd)` pattern

#### Scenario: User integrates fx today into shell
- **GIVEN** a user reads the Shell Integration guide
- **WHEN** they implement fx today integration
- **THEN** the documentation SHALL provide:
  - Daily workspace setup patterns
  - Shell alias examples (e.g., `ft` for fx today)
  - Configuration options (base directory, date format)
  - Integration with shell startup scripts
  - Example: Function to change to today's workspace

#### Scenario: User creates custom shell functions
- **GIVEN** a user reads the Shell Integration guide
- **WHEN** they implement custom functions
- **THEN** the documentation SHALL provide:
  - Combining multiple fx commands
  - Pipeline examples (fx ff | xargs ...)
  - Error handling patterns
  - Interactive prompts with user confirmation
  - Example: Project stats function combining files, size, and filter

---

### Requirement: Performance Optimization Documentation
The documentation SHALL include tips and best practices for optimizing fx command performance on large projects.

#### Scenario: User learns to optimize file finding
- **GIVEN** a user reads the Performance Optimization guide
- **WHEN** they implement optimization strategies
- **THEN** the documentation SHALL provide:
  - Using `--first` flag for quick first-match returns
  - Excluding heavy directories (.git, .venv, node_modules)
  - Using multiple `--exclude` patterns to filter results
  - Benchmark data showing performance improvements
  - Example: Before/after timing comparisons

#### Scenario: User learns to optimize recursive operations
- **GIVEN** a user reads the Performance Optimization guide
- **WHEN** they optimize recursive searches
- **THEN** the documentation SHALL provide:
  - Trade-offs between recursive and non-recursive modes
  - Using depth limits to reduce traversal
  - Skipping symlinks to prevent infinite loops
  - Pattern matching to reduce file system calls
  - Example: Optimized commands for large codebases

#### Scenario: User learns batch processing optimization
- **GIVEN** a user reads the Performance Optimization guide
- **WHEN** they process multiple files
- **THEN** the documentation SHALL provide:
  - Using glob patterns instead of individual files
  - Combining operations to reduce passes
  - Parallel processing considerations
  - Memory usage tips for large datasets
  - Example: Efficient batch replacement workflow

---

### Requirement: Automated Deployment
The documentation site SHALL be deployed automatically to GitHub Pages via GitHub Actions workflow.

#### Scenario: Developer pushes to main branch
- **GIVEN** the GitHub Actions workflow is configured
- **WHEN** a developer pushes changes to the main branch
- **THEN** the workflow SHALL:
  - Trigger automatically on push
  - Install MkDocs and Material Theme
  - Build the documentation site
  - Deploy to gh-pages branch
  - Complete deployment within 2 minutes

#### Scenario: Deployment workflow handles errors
- **GIVEN** the GitHub Actions workflow runs
- **WHEN** the build or deployment fails
- **THEN** the workflow SHALL:
  - Log detailed error messages
  - Mark workflow as failed
  - Send notifications if configured
  - Not deploy broken content to production

---

### Requirement: Documentation Quality
All documentation SHALL meet quality standards for accuracy, accessibility, and maintainability.

#### Scenario: Code examples are accurate
- **GIVEN** documentation includes code examples
- **WHEN** users copy and execute examples
- **THEN** the examples SHALL:
  - Work as documented without errors
  - Match the current version of fx-bin
  - Include expected output or results
  - Be tested against the actual codebase

#### Scenario: Documentation is accessible
- **GIVEN** a user with disabilities accesses the site
- **WHEN** they use assistive technologies
- **THEN** the documentation SHALL:
  - Meet WCAG AA color contrast ratios
  - Support keyboard navigation
  - Be compatible with screen readers
  - Use semantic HTML structure

#### Scenario: Documentation is maintainable
- **GIVEN** the documentation site structure
- **WHEN** a new feature is added to fx-bin
- **THEN** the documentation structure SHALL:
  - Provide clear location for new command pages
  - Include templates for consistent formatting
  - Support easy addition of new use cases
  - Enable link validation in CI/CD

---

### Requirement: Code Copy Functionality
The documentation site SHALL provide code copy buttons for all code blocks to improve user experience.

#### Scenario: User copies command example
- **GIVEN** a documentation page contains code examples
- **WHEN** a user clicks the copy button on a code block
- **THEN** the site SHALL:
  - Copy the code content to clipboard
  - Display visual feedback (e.g., "Copied!" message)
  - Preserve code formatting and indentation
  - Work on all modern browsers

---

### Requirement: Search Functionality
The documentation site SHALL provide full-text search for easy content discovery.

#### Scenario: User searches for command documentation
- **GIVEN** a user wants to find information about a specific command
- **WHEN** they type a search query (e.g., "replace")
- **THEN** the search SHALL:
  - Return relevant results from command pages
  - Show page titles and matching snippets
  - Highlight matching terms in results
  - Support fuzzy matching for typos

#### Scenario: User searches for use cases
- **GIVEN** a user wants to find a solution to a specific problem
- **WHEN** they search for a scenario (e.g., "cleanup")
- **THEN** the search SHALL:
  - Return use case pages matching the query
  - Display relevant context from the use case
  - Link directly to the matching section
