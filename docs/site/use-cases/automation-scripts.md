# Use Case: Automation Scripts

Integrate fx-bin commands into automation scripts for deployment, CI/CD, and batch operations.

## Overview

Automation scripts need reliable file operations for deployment, testing, and maintenance. This use case demonstrates how to integrate fx-bin commands into shell scripts and CI/CD pipelines.

## Deployment Automation

### 1. Deployment Script

```bash
#!/bin/bash
# deploy.sh

set -e

echo "=== Deployment Script ==="
echo ""

# 1. Navigate to project root
echo "1. Navigating to project root..."
PROJECT_ROOT=$(fx root --cd)
if [ $? -ne 0 ]; then
  echo "Error: Not in a Git repository"
  exit 1
fi
cd "$PROJECT_ROOT"
echo "   Project root: $PROJECT_ROOT"
echo ""

# 2. Backup current deployment
echo "2. Backing up current deployment..."
BACKUP_NAME=$(fx backup ~/deploy/current --compress | grep -o "backup_[^ ]*")
echo "   Backup: $BACKUP_NAME"
echo ""

# 3. Build project
echo "3. Building project..."
make build
echo "   Build complete"
echo ""

# 4. Deploy files
echo "4. Deploying files..."
cp -r dist/* ~/deploy/current/
echo "   Deployment complete"
echo ""

# 5. Verify deployment
echo "5. Verifying deployment..."
if [ -f ~/deploy/current/version.txt ]; then
  echo "   Version: $(cat ~/deploy/current/version.txt)"
fi
echo ""

# 6. Summary
echo "=== Deployment Complete ==="
echo "   Backup: $BACKUP_NAME"
echo "   Deployed to: ~/deploy/current"
```

### 2. Rollback Script

```bash
#!/bin/bash
# rollback.sh

set -e

echo "=== Rollback Script ==="
echo ""

BACKUP_NAME=$1

if [ -z "$BACKUP_NAME" ]; then
  echo "Usage: rollback.sh BACKUP_NAME"
  echo "Example: rollback.sh backup_20260110_143022.tar.xz"
  exit 1
fi

echo "Rollback: $BACKUP_NAME"
echo ""

# 1. Extract backup
echo "1. Extracting backup..."
tar -xf "$BACKUP_NAME"
BACKUP_DIR=$(echo "$BACKUP_NAME" | sed 's/\.tar\.xz//')
echo "   Extracted: $BACKUP_DIR"
echo ""

# 2. Stop current deployment
echo "2. Stopping current deployment..."
sudo systemctl stop myapp
echo "   Service stopped"
echo ""

# 3. Restore from backup
echo "3. Restoring from backup..."
rm -rf ~/deploy/current/*
cp -r "$BACKUP_DIR"/* ~/deploy/current/
echo "   Restoration complete"
echo ""

# 4. Start service
echo "4. Starting service..."
sudo systemctl start myapp
echo "   Service started"
echo ""

# 5. Cleanup
echo "5. Cleanup..."
rm -rf "$BACKUP_DIR"
echo "   Cleanup complete"
echo ""

# 6. Summary
echo "=== Rollback Complete ==="
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install fx-bin
        run: pip install fx-bin

      - name: Navigate to project root
        run: |
          PROJECT_ROOT=$(fx root --cd)
          echo "PROJECT_ROOT=$PROJECT_ROOT" >> $GITHUB_ENV

      - name: Create backup
        run: |
          BACKUP_NAME=$(fx backup . --compress)
          echo "BACKUP_NAME=$BACKUP_NAME" >> $GITHUB_ENV

      - name: Build project
        run: |
          cd $PROJECT_ROOT
          make build

      - name: Deploy
        run: |
          cd $PROJECT_ROOT
          make deploy
```

### GitLab CI Example

```yaml
stages:
  - deploy

deploy_production:
  stage: deploy
  script:
    - pip install fx-bin
    - PROJECT_ROOT=$(fx root --cd)
    - cd $PROJECT_ROOT
    - BACKUP_NAME=$(fx backup . --compress)
    - make build
    - make deploy
  only:
    - main
```

## Batch Operations

### 1. File Processing Script

```bash
#!/bin/bash
# process_files.sh

set -e

PATTERN=$1
OPERATION=$2

if [ -z "$PATTERN" ] || [ -z "$OPERATION" ]; then
  echo "Usage: process_files.sh PATTERN OPERATION"
  echo "Example: process_files.sh '*.py' 'python -m py_compile'"
  exit 1
fi

echo "=== Batch File Processing ==="
echo "Pattern: $PATTERN"
echo "Operation: $OPERATION"
echo ""

# 1. Find files
echo "1. Finding files..."
FILES=$(fx ff . --pattern "$PATTERN" --exclude node_modules --exclude .git --exclude __pycache__)
FILE_COUNT=$(echo "$FILES" | wc -l)
echo "   Found $FILE_COUNT files"
echo ""

# 2. Process files
echo "2. Processing files..."
for file in $FILES; do
  echo "   Processing: $file"
  $OPERATION "$file"
done
echo ""

# 3. Summary
echo "=== Processing Complete ==="
echo "   Processed $FILE_COUNT files"
```

### 2. Log Analysis Script

```bash
#!/bin/bash
# analyze_logs.sh

set -e

echo "=== Log Analysis ==="
echo ""

# 1. Find log files
echo "1. Finding log files..."
LOG_FILES=$(fx ff .log --exclude archive)
LOG_COUNT=$(echo "$LOG_FILES" | wc -l)
echo "   Found $LOG_COUNT log files"
echo ""

# 2. Analyze log sizes
echo "2. Analyzing log sizes..."
for log_file in $LOG_FILES; do
  echo "   $log_file: $(fx size "$log_file" | head -1)"
done
echo ""

# 3. Find large logs
echo "3. Finding large logs..."
LARGE_LOGS=$(fx ff .log --exclude archive | xargs fx size | sort -rn | head -10)
echo "$LARGE_LOGS"
echo ""

# 4. Summary
echo "=== Analysis Complete ==="
echo "   Total logs: $LOG_COUNT"
```

## Maintenance Automation

### 1. Daily Maintenance Script

```bash
#!/bin/bash
# daily_maintenance.sh

set -e

echo "=== Daily Maintenance ==="
echo ""

# 1. Navigate to project root
echo "1. Navigating to project root..."
PROJECT_ROOT=$(fx root --cd 2>/dev/null || echo ".")
cd "$PROJECT_ROOT"
echo "   Project root: $PROJECT_ROOT"
echo ""

# 2. Find backup files
echo "2. Finding backup files..."
BACKUP_FILES=$(fx ff .bak --exclude node_modules --exclude .git --exclude __pycache__)
BACKUP_COUNT=$(echo "$BACKUP_FILES" | wc -l)
echo "   Found $BACKUP_COUNT backup files"
echo ""

# 3. Find temporary files
echo "3. Finding temporary files..."
TEMP_FILES=$(fx ff .tmp --exclude node_modules --exclude .git)
TEMP_COUNT=$(echo "$TEMP_FILES" | wc -l)
echo "   Found $TEMP_COUNT temporary files"
echo ""

# 4. Analyze large files
echo "4. Analyzing large files..."
LARGE_FILES=$(fx size . --recursive --limit 10)
echo "$LARGE_FILES"
echo ""

# 5. Summary
echo "=== Maintenance Complete ==="
echo "   Backup files: $BACKUP_COUNT"
echo "   Temporary files: $TEMP_COUNT"
```

### 2. Cleanup Script

```bash
#!/bin/bash
# cleanup.sh

set -e

echo "=== Cleanup Script ==="
echo ""

# 1. Create backup
echo "1. Creating backup..."
BACKUP_NAME=$(fx backup . --compress)
echo "   Backup: $BACKUP_NAME"
echo ""

# 2. Find files to clean
echo "2. Finding files to clean..."
BACKUP_FILES=$(fx ff .bak --exclude node_modules --exclude .git --exclude __pycache__)
TEMP_FILES=$(fx ff .tmp --exclude node_modules --exclude .git)

BACKUP_COUNT=$(echo "$BACKUP_FILES" | wc -l)
TEMP_COUNT=$(echo "$TEMP_FILES" | wc -l)

echo "   Backup files: $BACKUP_COUNT"
echo "   Temporary files: $TEMP_COUNT"
echo ""

# 3. Clean files
echo "3. Cleaning files..."
if [ -n "$BACKUP_FILES" ]; then
  echo "$BACKUP_FILES" | xargs rm -f
  echo "   Cleaned $BACKUP_COUNT backup files"
fi

if [ -n "$TEMP_FILES" ]; then
  echo "$TEMP_FILES" | xargs rm -f
  echo "   Cleaned $TEMP_COUNT temporary files"
fi
echo ""

# 4. Summary
echo "=== Cleanup Complete ==="
echo "   Backup: $BACKUP_NAME"
```

## Related Commands

- [`fx root`](../commands/root.md) - Find Git project root
- [`fx backup`](../commands/backup.md) - Create backups
- [`fx ff`](../commands/ff.md) - Find files by keyword
- [`fx size`](../commands/size.md) - Analyze file sizes
