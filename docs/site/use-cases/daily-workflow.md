# Use Case: Daily Development Workflow

Streamline your daily development work with fx-bin commands for efficient project management.

## Overview

A typical development day involves navigating projects, finding files, counting code, managing workspaces, and tracking changes. This use case demonstrates how fx-bin commands can streamline these tasks into a cohesive workflow.

## Workflow

### 1. Start Daily Workspace

Begin your day by creating a dedicated workspace:

```bash
# Create today's workspace and start new shell
fx today --base ~/Projects

# All daily work is now isolated in ~/Projects/YYYYMMDD/
```

**Benefits:**
- Clean separation of work by day
- Easy to review and archive
- Prevents mixing of unrelated work

### 2. Navigate to Project Root

Quickly navigate to your Git project root:

```bash
# Create shell alias (add to .bashrc or .zshrc)
alias gr='cd "$(fx root --cd)"'

# Navigate to project root
gr

# Or use full command
cd "$(fx root --cd)"
```

**Benefits:**
- Always at the correct directory for Git operations
- No manual traversal up/down directory tree
- Consistent starting point for all operations

### 3. Project Statistics

Understand your project structure and composition:

```bash
# Count all Python files
fx files . --pattern "*.py" --recursive

# Count by file type
echo "Python: $(fx files . --pattern '*.py' --recursive | tail -1 | awk '{print $1}')"
echo "JavaScript: $(fx files . --pattern '*.{js,jsx,ts,tsx}' --recursive | tail -1 | awk '{print $1}')"
echo "Markdown: $(fx files . --pattern '*.md' --recursive | tail -1 | awk '{print $1}')"

# Analyze directory sizes
fx size . --recursive --limit 10
```

**Benefits:**
- Quick overview of project structure
- Identify large directories for cleanup
- Track codebase growth over time

### 4. Find Recent Changes

Locate recently modified files:

```bash
# Find recently modified Python files
fx filter py --sort-by modified --reverse --limit 20

# Find recently modified files of multiple types
fx filter "py,js,md" --sort-by modified --reverse --limit 30

# Show file paths
fx filter py --sort-by modified --reverse --show-path --limit 10
```

**Benefits:**
- Focus on files changed since last session
- Quick code review starting points
- Track daily progress

### 5. Locate TODO Markers

Find TODO comments and markers in code:

```bash
# Find TODO markers
fx ff TODO --exclude node_modules --exclude .git --exclude __pycache__

# Find FIXME markers
fx ff FIXME --exclude node_modules --exclude .git

# Find all types of markers
for marker in TODO FIXME XXX HACK NOTE; do
  echo "=== $marker ==="
  fx ff "$marker" --exclude node_modules --exclude .git --exclude __pycache__
done
```

**Benefits:**
- Track outstanding work items
- Clean up code debt systematically
- Prepare for code reviews

### 6. Find Configuration Files

Locate configuration files for review or updates:

```bash
# Find all config files
fx ff config --exclude backup --exclude node_modules --exclude .git

# Find environment files
fx ff .env --exclude node_modules --exclude .git

# Find settings files
fx ff settings --exclude backup --exclude node_modules
```

**Benefits:**
- Quick access to configuration
- Ensure all configs are reviewed
- Find deprecated config files

## Daily Workflow Script

Create a reusable daily workflow script:

```bash
#!/bin/bash
# daily_workflow.sh
# Automated daily development workflow

set -e  # Exit on error

echo "=== Daily Development Workflow ==="
echo ""

# 1. Create daily workspace
echo "1. Creating daily workspace..."
WORKSPACE=$(fx today --base ~/Projects)
echo "   Workspace: $WORKSPACE"
echo ""

# 2. Navigate to project root
echo "2. Navigating to project root..."
PROJECT_ROOT=$(fx root --cd)
echo "   Project root: $PROJECT_ROOT"
cd "$PROJECT_ROOT"
echo ""

# 3. Project statistics
echo "3. Project statistics..."
echo "   Python files: $(fx files . --pattern '*.py' --recursive | tail -1 | awk '{print $1}')"
echo "   JS files: $(fx files . --pattern '*.{js,jsx,ts,tsx}' --recursive | tail -1 | awk '{print $1}')"
echo "   Total files: $(fx files . --recursive | tail -1 | awk '{print $1}')"
echo ""

# 4. Recent changes
echo "4. Recently modified files (last 10)..."
fx filter py --sort-by modified --reverse --limit 10 --show-path
echo ""

# 5. TODO markers
echo "5. TODO markers..."
TODO_COUNT=$(fx ff TODO --exclude node_modules --exclude .git --exclude __pycache__ | wc -l)
echo "   Found $TODO_COUNT TODO items"
if [ "$TODO_COUNT" -gt 0 ]; then
  fx ff TODO --exclude node_modules --exclude .git --exclude __pycache__
fi
echo ""

# 6. Summary
echo "=== Daily Workflow Complete ==="
echo "Ready to start work!"
```

## Productivity Tips

### Shell Aliases

Add these to `.bashrc` or `.zshrc`:

```bash
# Daily workspace
alias ft='fx today --base ~/Projects'

# Project root navigation
alias gr='cd "$(fx root --cd)"'

# Show project stats
alias pstats='echo "Python: $(fx files . --pattern "*.py" --recursive | tail -1 | awk "{print \$1}")"'

# Recent files
alias precent='fx filter py --sort-by modified --reverse --limit 10 --show-path'

# Find TODOs
alias ptodo='fx ff TODO --exclude node_modules --exclude .git --exclude __pycache__'
```

### Morning Routine

```bash
# 1. Start daily workspace
ft

# 2. Navigate to project
gr

# 3. Check project status
pstats
precent
ptodo

# 4. Start working
```

### End-of-Day Routine

```bash
# 1. Review changes
git status
git diff

# 2. Commit if ready
git add .
git commit -m "Daily progress"

# 3. Backup before leaving
fx backup . --compress

# 4. Exit workspace
exit
```

## Advanced Workflows

### Multi-Project Management

```bash
#!/bin/bash
# Manage multiple projects

for project in project1 project2 project3; do
  echo "=== $project ==="

  cd ~/projects/$project

  # Show stats
  fx files . --pattern "*.py" --recursive | tail -1

  # Show recent files
  fx filter py --sort-by modified --reverse --limit 5

  # Find TODOs
  fx ff TODO --exclude node_modules --exclude .git

  echo ""
done
```

### Code Review Preparation

```bash
#!/bin/bash
# Prepare for code review

# 1. Find modified files
echo "=== Modified files ==="
fx filter py --sort-by modified --reverse --limit 20

# 2. Find TODOs in modified files
echo ""
echo "=== TODOs ==="
fx ff TODO --exclude node_modules --exclude .git --exclude __pycache__

# 3. Check for large files
echo ""
echo "=== Large files ==="
fx size . --recursive --limit 10
```

### Daily Backup

```bash
#!/bin/bash
# Daily backup routine

# Backup current directory
BACKUP_NAME=$(fx backup . --compress | grep -o "backup_[^ ]*")
echo "Backup created: $BACKUP_NAME"

# Copy to remote storage (optional)
# scp "$BACKUP_NAME" user@remote:/backup/location/

# Clean up old backups (keep last 7 days)
find . -maxdepth 1 -name "backup_*.tar.xz" -mtime +7 -exec rm -f {} \;
```

## Troubleshooting

### Workspace Already Exists

```bash
# If workspace already exists, fx today will still work
fx today --base ~/Projects

# But you may want to navigate to existing workspace
WORKSPACE=~/Projects/$(date +%Y%m%d)
cd "$WORKSPACE"
```

### Not in Git Repository

```bash
# If not in a Git repository, fx root will fail
fx root

# Solution: Initialize git or navigate to Git repository
git init
# Or
cd /path/to/git/repository
```

### No Recent Files

```bash
# If no recent files found
fx filter py --sort-by modified --reverse --limit 10

# Try without limit
fx filter py --sort-by modified --reverse

# Or check all files
fx filter py
```

## Related Commands

- [`fx today`](../commands/today.md) - Create daily workspace
- [`fx root`](../commands/root.md) - Find Git project root
- [`fx files`](../commands/files.md) - Count files
- [`fx filter`](../commands/filter.md) - Filter files by extension
- [`fx ff`](../commands/ff.md) - Find files by keyword

---

**Streamline your day!** Use fx-bin for efficient daily development workflows. 🚀
