# Use Case: Project Cleanup

Clean up project directories by identifying and managing temporary, backup, and old files.

## Overview

Over time, project directories accumulate temporary files, backup files, and outdated content. This use case demonstrates how to use fx-bin to identify, analyze, and clean up these files systematically.

## Cleanup Tasks

### 1. Find Backup Files

Identify all backup files in project:

```bash
# Find .bak files
fx ff .bak --exclude node_modules --exclude .git --exclude __pycache__

# Find .backup files
fx ff .backup --exclude node_modules --exclude .git

# Find all backup patterns
for pattern in .bak .backup _backup old_*; do
  echo "=== $pattern ==="
  fx ff "$pattern" --exclude node_modules --exclude .git --exclude __pycache__
done
```

### 2. Find Temporary Files

Identify temporary files:

```bash
# Find .tmp files
fx ff .tmp --exclude node_modules --exclude .git

# Find .swp files (vim)
fx ff .swp --exclude node_modules --exclude .git

# Find .DS_Store files (macOS)
fx ff .DS_Store --exclude node_modules --exclude .git
```

### 3. Analyze Large Files

Find and analyze large files that might need cleanup:

```bash
# Find top 20 largest files
fx size . --recursive --limit 20

# Find large log files
fx ff .log --exclude archive | xargs fx size | sort -rn | head -10

# Find large temporary files
for pattern in .tmp .bak .swp; do
  fx ff "$pattern" | xargs fx size | sort -rn | head -5
done
```

## Cleanup Script

Create a comprehensive cleanup script:

```bash
#!/bin/bash
# cleanup_project.sh

set -e

PROJECT_ROOT=$(fx root --cd 2>/dev/null)
if [ -z "$PROJECT_ROOT" ]; then
  echo "Error: Not in a Git repository"
  exit 1
fi

cd "$PROJECT_ROOT"

echo "=== Project Cleanup: $PROJECT_ROOT ==="
echo ""

# 1. Find backup files
echo "1. Backup files found:"
backup_count=$(fx ff .bak --exclude node_modules --exclude .git --exclude __pycache__ | wc -l)
echo "   .bak files: $backup_count"

if [ "$backup_count" -gt 0 ]; then
  echo "   Files:"
  fx ff .bak --exclude node_modules --exclude .git --exclude __pycache__ | head -10
fi
echo ""

# 2. Find temporary files
echo "2. Temporary files found:"
tmp_count=$(fx ff .tmp --exclude node_modules --exclude .git | wc -l)
echo "   .tmp files: $tmp_count"

if [ "$tmp_count" -gt 0 ]; then
  echo "   Files:"
  fx ff .tmp --exclude node_modules --exclude .git | head -10
fi
echo ""

# 3. Summary
echo "=== Cleanup Complete ==="
echo "Review files and delete as needed"
```

## Related Commands

- [`fx ff`](../commands/ff.md) - Find files by keyword
- [`fx size`](../commands/size.md) - Analyze file sizes
- [`fx files`](../commands/files.md) - Count files
