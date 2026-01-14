# Command: fx today

Create and navigate to today's workspace directory for daily work organization.

## Overview

`fx today` creates a date-organized directory (default: `~/Downloads/YYYYMMDD`) and optionally starts a new shell there. Perfect for daily work organization, time-tracking, and keeping work separate by day.

**Key Features:**
- 📅 Automatic date-based directory creation
- 🏠 Customizable base directory
- 📝 Customizable date format
- 💻 Optional shell integration
- 🎯 Perfect for daily workflows
- 🔄 Consistent daily structure

## Usage

```bash
fx today [OPTIONS]
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|----------|-------------|
| `--cd` / `-c` | flag | False | Output path suitable for cd command (no extra text) |
| `--base` / `-b` | string | `~/Downloads` | Base directory for daily workspaces |
| `--format` / `-f` | string | `%Y%m%d` | Date format (strftime) for directory names |
| `--verbose` / `-v` | flag | False | Show verbose output |
| `--dry-run` | flag | False | Show what would be created without creating it |
| `--no-exec` | flag | False | Don't start new shell, just create directory |

## Examples

### Basic Usage

Create today's workspace and start new shell:

```bash
fx today
```

**Output:**
```
Created workspace: ~/Downloads/20260110
Starting new shell...
```

Create workspace without starting shell:

```bash
fx today --no-exec
```

### Path-Only Output

Output path for shell integration:

```bash
fx today --cd
```

**Output:**
```
/home/user/Downloads/20260110
```

### Custom Base Directory

Use custom base directory:

```bash
fx today --base ~/Projects
fx today --base ~/Documents
fx today --base /tmp/workspaces
```

### Custom Date Format

Use custom date format:

```bash
# Format: YYYY-MM-DD
fx today --format "%Y-%m-%d"
# Creates: ~/Downloads/2026-01-10

# Format: YYYYMMDD
fx today --format "%Y%m%d"
# Creates: ~/Downloads/20260110

# Format: YYYYMM
fx today --format "%Y%m"
# Creates: ~/Downloads/202601
```

### Real-World Scenarios

#### Scenario 1: Daily Development Workflow

```bash
# Start daily development session
fx today

# In the new shell, work on today's tasks
# Create files, write code, etc.
# All work is automatically organized by date

# When done, exit shell
exit

# Return to previous directory
```

#### Scenario 2: Shell Integration

Add to `.bashrc` or `.zshrc`:

```bash
# Create alias for quick access
alias ft='fx today'
alias ftcd='cd "$(fx today --cd)"'

# Usage
ft          # Create workspace and start shell
ftcd        # Just change to today's workspace
```

#### Scenario 3: Daily Documentation

Organize daily documentation:

```bash
# Create workspace for today's docs
fx today --base ~/Documents

# Write documentation in workspace
# Automatically organized by date
```

#### Scenario 4: Research Notes

Organize daily research:

```bash
# Create workspace for research
fx today --base ~/Research

# All notes for today go here
# Easy to find later by date
```

#### Scenario 5: Meeting Notes

Organize daily meeting notes:

```bash
# Create workspace for meetings
fx today --base ~/Meetings

# All meeting notes organized by date
# Easy to review chronologically
```

#### Scenario 6: Testing Workspace

Create daily testing workspace:

```bash
# Create workspace for testing
fx today --base ~/Testing

# All test results organized by date
# Easy to compare results across days
```

#### Scenario 7: Backup Workspace

Create daily backup workspace:

```bash
# Create workspace for backups
fx today --base ~/Backups

# All backups organized by date
# Easy to rotate and clean up
```

#### Scenario 8: Logging Workspace

Organize daily logs:

```bash
# Create workspace for logs
fx today --base ~/Logs

# All logs organized by date
# Easy to search and analyze
```

## Tips and Tricks

### Shell Aliases

Create aliases in `.bashrc` or `.zshrc`:

```bash
# Quick workspace creation
alias ft='fx today'

# Change to workspace
alias ftcd='cd "$(fx today --cd)"'

# Workspace with custom base
alias ftp='fx today --base ~/Projects'

# Workspace for documents
alias ftd='fx today --base ~/Documents'
```

### Daily Workflows

```bash
#!/bin/bash
# Daily workflow script

# Create workspace
WORKSPACE=$(fx today --cd)
cd "$WORKSPACE"

# Create daily TODO list
cat > TODO.md << EOF
# TODO - $(date +%Y-%m-%d)

## Tasks
- [ ] Task 1
- [ ] Task 2

## Notes
EOF

# Open TODO in editor
vim TODO.md
```

### Script Integration

```bash
#!/bin/bash
# Script that uses daily workspace

# Get workspace path
WORKSPACE=$(fx today --cd)

# Create subdirectories
mkdir -p "$WORKSPACE"/{src,test,docs}

# Copy templates
cp ~/templates/*.py "$WORKSPACE/src/"

# Start working
cd "$WORKSPACE"
vim "$WORKSPACE/src/main.py"
```

### Dry-Run Preview

```bash
# Preview workspace creation without creating
fx today --dry-run

# Output:
# Would create: ~/Downloads/20260110
# (No directory actually created)
```

### Multiple Workspaces

```bash
# Create different workspaces for different purposes
fx today --base ~/Work           # Work workspace
fx today --base ~/Personal       # Personal workspace
fx today --base ~/Projects      # Project workspace
```

### Date Formats Reference

Common date formats (strftime):

```bash
# Daily: 20260110
fx today --format "%Y%m%d"

# Standard: 2026-01-10
fx today --format "%Y-%m-%d"

# Short: 202601
fx today --format "%Y%m"

# Long: Saturday, January 10, 2026
fx today --format "%A, %B %d, %Y"

# ISO Week: 2026-W02
fx today --format "%Y-W%V"

# Day of Week: 2026-Saturday
fx today --format "%Y-%A"
```

### Combining with Other Commands

```bash
# Create workspace and copy files
WORKSPACE=$(fx today --cd)
mkdir -p "$WORKSPACE"
cp ~/template/* "$WORKSPACE/"

# Create workspace and initialize project
fx today --base ~/Projects
cd "$(fx today --cd)"
git init
touch README.md
```

## Advanced Usage

### Custom Shell

```bash
#!/bin/bash
# Create workspace with custom shell

WORKSPACE=$(fx today --cd)

# Start zsh instead of default shell
cd "$WORKSPACE" && exec zsh
```

### Workspace Templates

```bash
#!/bin/bash
# Create workspace from template

WORKSPACE=$(fx today --cd)

# Copy template files
if [ -d ~/templates/default ]; then
  cp -r ~/templates/default/* "$WORKSPACE/"
fi

# Customize workspace
cd "$WORKSPACE"
sed -i "s/DATE/$(date +%Y-%m-%d)/g" README.md
```

### Workspace Organization

```bash
#!/bin/bash
# Create organized workspace structure

WORKSPACE=$(fx today --cd)

# Create standard directories
mkdir -p "$WORKSPACE"/{src,test,docs,build}

# Create standard files
touch "$WORKSPACE"/{README.md,TODO.md,CHANGELOG.md}

# Initialize git if desired
cd "$WORKSPACE" && git init
```

### Daily Backup

```bash
#!/bin/bash
# Daily backup routine

# Create workspace for backup
WORKSPACE=$(fx today --base ~/Backups)
cd "$WORKSPACE"

# Create backup
fx backup ~/project_dir --compress

# Link backup
ln -s ~/project_dir_*.tar.xz project_backup.tar.xz
```

## Performance Notes

- **Speed**: Instant directory creation
- **Shell**: Starts new shell (may have slight delay)
- **Path resolution**: Resolves `~` to absolute path
- **Date**: Uses current system date/time

## Common Issues

### Permission Denied

```bash
# If base directory is not writable
fx today --base /protected/path

# Error: Permission denied

# Solution: Use writable directory
fx today --base ~/Downloads
fx today --base /tmp
```

### Shell Not Found

```bash
# If default shell is not found
fx today

# Error: Shell not found

# Solution: Specify shell explicitly
cd "$(fx today --cd)" && exec /bin/bash
```

### Directory Already Exists

```bash
# If workspace already exists
fx today

# Output: Workspace already exists: ~/Downloads/20260110
# (No error, just notification)
```

### Invalid Date Format

```bash
# If date format is invalid
fx today --format "invalid"

# Error: Invalid date format

# Solution: Use valid strftime format
fx today --format "%Y-%m-%d"
```

### Base Directory Not Found

```bash
# If base directory doesn't exist
fx today --base ~/NonExistent

# Error: Base directory not found

# Solution: Create base directory first
mkdir -p ~/NonExistent
fx today --base ~/NonExistent
```

## Best Practices

### Consistent Workflow

```bash
# Always use same base directory
alias ft='fx today --base ~/Work'

# All workspaces in ~/Work/
# Easy to find and backup
```

### Organize by Project

```bash
# Different base for different projects
alias ftwork='fx today --base ~/Work'
alias ftpersonal='fx today --base ~/Personal'
alias ftprojects='fx today --base ~/Projects'

# Clear separation of concerns
```

### Use Daily TODO

```bash
# Create TODO in workspace
cd "$(fx today --cd)"
cat > TODO.md << EOF
# TODO - $(date +%Y-%m-%d)

- [ ] Task 1
- [ ] Task 2
EOF

# Update throughout day
```

### Clean Up Old Workspaces

```bash
# Remove workspaces older than N days
find ~/Work -maxdepth 1 -type d -mtime +30 -exec rm -rf {} \;
```

### Backup Workspaces

```bash
# Backup all workspaces
tar -czf workspaces_backup_$(date +%Y%m%d).tar.gz ~/Work/

# Store in backup location
mv workspaces_backup_*.tar.gz ~/Backup/
```

## See Also

- [`fx root`](root.md) - Find Git project root
- [`fx organize`](organize.md) - Organize files by date
- [`fx backup`](backup.md) - Create timestamped backups

---

**Stay organized!** Use `fx today` to keep your daily work structured and accessible. 📅
