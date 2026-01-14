# Command: fx backup

Create timestamped backups of files and directories with optional compression.

## Overview

`fx backup` creates timestamped backups of files or directories. Backups are created in the same directory as the source with a timestamp appended to the filename/directory name. Supports compression for directory backups.

**Key Features:**
- 📅 Automatic timestamp generation
- 🗜️ Optional compression for directories
- 📁 File and directory backup support
- 🔄 Consistent naming convention
- 💾 Same-directory backup creation

## Usage

```bash
fx backup [OPTIONS] path
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | path | Yes | File or directory to backup |
| `--compress` | flag | No | Compress directory backup as .tar.xz |
| `--timestamp-format` | string | No | Custom timestamp format (strftime) |

## Examples

### Basic Usage

Backup a file:

```bash
fx backup file.txt
```

**Output:**
```
Backup created: file_20260110_143022.txt
```

Backup a directory:

```bash
fx backup mydir/
```

**Output:**
```
Backup created: mydir_20260110_143022/
```

### Compressed Backups

Compress directory backup:

```bash
fx backup mydir/ --compress
```

**Output:**
```
Backup created: mydir_20260110_143022.tar.xz
```

### Custom Timestamp Format

Use custom timestamp format:

```bash
# Default format (YYYYMMDD_HHMMSS)
fx backup file.txt

# Custom format (YYYY-MM-DD)
fx backup file.txt --timestamp-format "%Y-%m-%d"

# Custom format (YYYYMMDD)
fx backup file.txt --timestamp-format "%Y%m%d"
```

### Real-World Scenarios

#### Scenario 1: Pre-Update Backup

Backup before making changes:

```bash
# Backup project directory
fx backup project_dir/

# Make changes...
# If needed, restore from backup
cp project_dir_20260110_143022/ project_dir/
```

#### Scenario 2: Code Refactoring

Backup before refactoring:

```bash
# Backup current version
fx backup src/

# Refactor code...
# Test refactored code
pytest

# If tests fail, restore
cp src_20260110_143022/ src/
```

#### Scenario 3: Configuration Backup

Backup configuration files:

```bash
# Backup config directory
fx backup ~/.config/myapp/

# Make configuration changes...
# If issues occur, restore
cp ~/.config/myapp_20260110_143022/ ~/.config/myapp/
```

#### Scenario 4: Data Migration

Backup before data migration:

```bash
# Backup data directory with compression
fx backup ~/data/ --compress

# Perform data migration
python migrate_data.py

# Verify migration
# If needed, restore from backup
tar -xf data_20260110_143022.tar.xz
```

#### Scenario 5: Daily Backup Routine

Create daily backups:

```bash
# Backup today's work
fx backup ~/workspace/

# Compress to save space
fx backup ~/workspace/ --compress
```

## Tips and Tricks

### Combining with Other Commands

```bash
# Find and backup files
fx ff important.txt | xargs fx backup

# Backup multiple directories
for dir in src/ tests/ docs/; do
  fx backup "$dir"
done
```

### Automated Backup Script

```bash
#!/bin/bash
# Daily backup script

# Create compressed backup
timestamp=$(date +%Y%m%d_%H%M%S)
backup_file="project_${timestamp}.tar.xz"

# Backup project
fx backup . --compress

# Copy to remote storage (optional)
# cp project_${timestamp}.tar.xz /backup/remote/
```

### Backup with Verification

```bash
#!/bin/bash
# Backup and verify

# Create backup
backup_name=$(fx backup mydir/ | grep -o "mydir_[^ ]*")

# Verify backup exists
if [ -e "$backup_name" ]; then
  echo "Backup verified: $backup_name"
else
  echo "Backup failed!"
  exit 1
fi
```

### Selective Backup

```bash
# Backup specific file types
fx backup $(fx ff .py) --timestamp-format "%Y%m%d"

# Backup multiple specific files
fx backup file1.txt file2.txt file3.txt
```

### Backup Rotation

```bash
# Keep last N backups
# Find and remove old backups (keep last 5)
find . -maxdepth 1 -name "project_*" -type d | \
  sort -r | \
  tail -n +6 | \
  xargs rm -rf
```

## Default Timestamp Format

The default timestamp format is: `%Y%m%d_%H%MSS`

Example output: `file_20260110_143022.txt`

Breakdown:
- `%Y` - Year (2026)
- `%m` - Month (01)
- `%d` - Day (10)
- `%H` - Hour (14)
- `%M` - Minute (30)
- `%S` - Second (22)

## Compression Details

- **Format**: `.tar.xz` (tar archive with xz compression)
- **Supported**: Only for directories (not single files)
- **Speed**: Slower than uncompressed but saves significant space
- **Restoration**: Use `tar -xf filename.tar.xz`

Example:

```bash
# Create compressed backup
fx backup mydir/ --compress

# Restore compressed backup
tar -xf mydir_20260110_143022.tar.xz
```

## Backup Location

Backups are created in the **same directory as the source**:

```bash
# Source: /home/user/project/file.txt
# Backup: /home/user/project/file_20260110_143022.txt

# Source: /home/user/project/mydir/
# Backup: /home/user/project/mydir_20260110_143022/
```

## Performance Notes

- **Large files**: Fast for single files, depends on size for directories
- **Compression**: Adds time overhead but saves space
- **Disk I/O**: Requires read and write operations
- **Network storage**: Not supported directly (use copy/backup tools)

## Common Issues

### Permission Denied

```bash
# Check permissions
ls -la file.txt

# Make file readable/writable (if allowed)
chmod +r file.txt
chmod +w file.txt

# Use sudo if necessary (not recommended)
sudo fx backup /protected/path
```

### Disk Space Issues

```bash
# Check available space
df -h

# Use compression to save space
fx backup large_dir/ --compress

# Check backup size
du -sh backup_20260110_143022/
```

### Backup Already Exists

```bash
# If backup name conflicts, new timestamp is generated
fx backup file.txt
# Creates: file_20260110_143022.txt

fx backup file.txt
# Creates: file_20260110_143023.txt (different timestamp)
```

### Compression Failures

```bash
# If compression fails, try without compression
fx backup mydir/  # Without --compress

# Check for sufficient disk space
df -h

# Check for xz compression support
which xz
```

### Timestamp Format Errors

```bash
# Valid formats
fx backup file.txt --timestamp-format "%Y-%m-%d"
fx backup file.txt --timestamp-format "%Y%m%d"

# Invalid formats (may cause errors)
fx backup file.txt --timestamp-format "invalid"  # ❌
```

## Best Practices

### Always Backup Before Changes

```bash
# Before any destructive operation
fx backup important_file_or_directory/

# Then perform operation
fx replace "old" "new" *.py
fx organize ~/Downloads/
```

### Use Compression for Large Directories

```bash
# Large directories - use compression
fx backup large_project/ --compress

# Small files - no compression needed
fx backup file.txt
```

### Regular Backup Schedule

```bash
# Add to cron for automated backups
# Example: Daily backup at 2 AM
# 0 2 * * * fx backup ~/workspace/ --compress
```

### Verify Backups

```bash
# Test restore on a copy
cp backup_20260110_143022.tar.xz backup_test.tar.xz
tar -xf backup_test.tar.xz

# Verify contents
ls -la backup_test/
```

### Organize Backups

```bash
# Create separate backup directory
mkdir -p ~/backups

# Copy backups to centralized location
cp project_* ~/backups/

# Clean up old backups (keep last 10)
ls -t ~/backups/project_* | tail -n +11 | xargs rm -rf
```

## See Also

- [`fx replace`](replace.md) - Replace text in files
- [`fx organize`](organize.md) - Organize files by date
- [`fx size`](size.md) - Analyze file/directory sizes

---

**Always backup before making changes!** 💾
