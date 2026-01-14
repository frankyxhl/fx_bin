# Use Case: Version Updates

Safely update version strings and configuration across multiple files with atomic operations.

## Overview

When releasing a new version, you need to update version numbers in multiple files (setup.py, __init__.py, README.md, etc.). This use case demonstrates safe version update workflows with fx-bin.

## Version Update Workflow

### 1. Create Backup

Always backup before version updates:

```bash
# Backup project directory
fx backup project_dir --compress

# Verify backup created
ls -la project_dir_*.tar.xz
```

### 2. Update Version Strings

Replace version strings across files:

```bash
# Update version in setup.py
fx replace "version='1.0.0'" "version='2.0.0'" setup.py

# Update version in __init__.py
fx replace "__version__ = '1.0.0'" "__version__ = '2.0.0'" */__init__.py

# Update version in README
fx replace "v1.0.0" "v2.0.0" README.md
```

### 3. Verify Changes

Check that version strings were updated correctly:

```bash
# Count occurrences of new version
grep -r "2.0.0" . --include="*.py" --include="*.md" | wc -l

# Show context of changes
grep -r "2.0.0" . --include="*.py" --include="*.md" -C 2

# Ensure no old versions remain
grep -r "1.0.0" . --include="*.py" --include="*.md"
# Should return nothing if all updated
```

## Comprehensive Version Update Script

```bash
#!/bin/bash
# update_version.sh

set -e

OLD_VERSION=$1
NEW_VERSION=$2

if [ -z "$OLD_VERSION" ] || [ -z "$NEW_VERSION" ]; then
  echo "Usage: update_version.sh OLD_VERSION NEW_VERSION"
  echo "Example: update_version.sh 1.0.0 2.0.0"
  exit 1
fi

echo "=== Version Update: $OLD_VERSION -> $NEW_VERSION ==="

# 1. Create backup
echo "1. Creating backup..."
BACKUP_NAME=$(fx backup . --compress | grep -o "backup_[^ ]*")
echo "   Backup: $BACKUP_NAME"

# 2. Update version strings
echo "2. Updating version strings..."
fx replace "$OLD_VERSION" "$NEW_VERSION" setup.py
fx replace "$OLD_VERSION" "$NEW_VERSION" */__init__.py
fx replace "$OLD_VERSION" "$NEW_VERSION" README.md
echo "   Version strings updated"

# 3. Verify updates
echo "3. Verifying updates..."
NEW_COUNT=$(grep -r "$NEW_VERSION" . --include="*.py" --include="*.md" | wc -l)
echo "   Found $NEW_COUNT occurrences of new version"

echo "=== Version Update Complete ==="
```

## Related Commands

- [`fx replace`](../commands/replace.md) - Replace text in files
- [`fx backup`](../commands/backup.md) - Create backups
- [`fx ff`](../commands/ff.md) - Find files by keyword
