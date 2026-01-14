# Command: fx organize

Organize files into date-based directories with comprehensive options for filtering, conflict handling, and depth control.

## Overview

`fx organize` organizes files from a source directory into an output directory using a date-based folder structure. Perfect for photo sorting, dataset management, and organizing downloads by date.

**Key Features:**
- 📅 Date-based directory organization
- 🎚️ Configurable directory depth (1-3 levels)
- 🔄 Multiple conflict handling modes
- 🎯 Include/exclude pattern filtering
- 🗑️ Empty directory cleanup
- 🔍 Dry-run preview mode
- ⚡ Smart file processing

## Usage

```bash
fx organize [OPTIONS] source
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|----------|-------------|
| `source` | path | Required | Source directory to organize |
| `--output` / `-o` | path | `./organized` | Output directory for organized files |
| `--date-source` | choice | `created` | Which file date to use (`created`, `modified`) |
| `--depth` | integer | `3` | Directory depth: 1=day, 2=year/day, 3=year/month/day |
| `--on-conflict` | choice | `rename` | How to handle filename conflicts (`rename`, `skip`, `overwrite`, `ask`) |
| `--include` / `-i` | string | - | Include only files matching glob patterns (repeatable) |
| `--exclude` / `-e` | string | - | Exclude files matching glob patterns (repeatable) |
| `--hidden` / `-H` | flag | False | Include hidden files (files starting with `.`) |
| `--recursive` / `-r` | flag | False | Process files in subdirectories recursively |
| `--clean-empty` | flag | False | Remove empty directories after organization |
| `--fail-fast` | flag | False | Stop on first error instead of continuing |
| `--dry-run` / `-n` | flag | False | Preview changes without actually moving files |
| `--yes` / `-y` | flag | False | Skip confirmation prompt |
| `--verbose` / `-v` | flag | False | Show detailed progress information |
| `--quiet` / `-q` | flag | False | Suppress progress output (errors and summary only) |

## Directory Depth

| Depth | Example Structure | Description |
|-------|------------------|-------------|
| `1` | `output/20260110/` | All files in single day folder |
| `2` | `output/2026/20260110/` | Year and day folders |
| `3` | `output/2026/202601/20260110/` | Year, month, and day folders (default) |

## Conflict Modes

| Mode | Behavior | Use Case |
|-------|-----------|-----------|
| `rename` | Auto-rename with `_1`, `_2` suffix | Safe default, keeps all files |
| `skip` | Skip conflicting files | Preserve existing files |
| `overwrite` | Overwrite existing files | Latest version wins |
| `ask` | Prompt for each conflict (scan-time) | Interactive control |

## Examples

### Basic Usage

Organize photos by date:

```bash
fx organize ~/Photos
```

Organize with custom output directory:

```bash
fx organize ~/Downloads -o ~/Sorted
```

### Dry-Run Preview

Preview changes without executing:

```bash
fx organize ~/Downloads --dry-run
```

### Custom Depth

Use 2-level depth (year/day):

```bash
fx organize ~/Photos --depth 2
```

Use 1-level depth (day only):

```bash
fx organize ~/Downloads --depth 1
```

### Filtering

Organize only images:

```bash
fx organize ~/Downloads -i "*.jpg" -i "*.png" -i "*.gif"
```

Organize excluding hidden files:

```bash
fx organize ~/Downloads -e ".*"
```

Organize only PDF and Word documents:

```bash
fx organize ~/Documents -i "*.pdf" -i "*.docx"
```

### Conflict Handling

Skip conflicting files:

```bash
fx organize ~/Downloads --on-conflict skip
```

Overwrite existing files:

```bash
fx organize ~/Downloads --on-conflict overwrite
```

### Date Source

Use modification time instead of creation:

```bash
fx organize ~/Downloads --date-source modified
```

### Real-World Scenarios

#### Scenario 1: Photo Organization

Organize photos by creation date:

```bash
# Organize all photos
fx organize ~/Photos -i "*.jpg" -i "*.jpeg" -i "*.png" -i "*.gif"

# With dry-run preview
fx organize ~/Photos -i "*.jpg" --dry-run

# With custom depth (year/day)
fx organize ~/Photos -i "*.jpg" --depth 2
```

#### Scenario 2: Download Sorting

Organize downloads by type:

```bash
# Organize images
fx organize ~/Downloads -i "*.jpg" -i "*.png" -o ~/Downloads/Images

# Organize documents
fx organize ~/Downloads -i "*.pdf" -i "*.docx" -o ~/Downloads/Documents

# Organize code
fx organize ~/Downloads -i "*.py" -i "*.js" -o ~/Downloads/Code
```

#### Scenario 3: Dataset Management

Organize datasets with filtering:

```bash
# Organize CSV files
fx organize ~/Data -i "*.csv" --recursive --depth 2

# Organize all data files
fx organize ~/Data -i "*.csv" -i "*.json" -i "*.xml" --recursive
```

#### Scenario 4: Cleanup Organization

Organize with conflict handling:

```bash
# Preview organization
fx organize ~/Downloads --dry-run

# Skip existing files
fx organize ~/Downloads --on-conflict skip

# Overwrite with confirmation
fx organize ~/Downloads --on-conflict ask
```

#### Scenario 5: Archive Organization

Organize archives by date:

```bash
# Organize all archives
fx organize ~/Archives -i "*.zip" -i "*.tar" -i "*.gz" -i "*.rar"

# Use modification time for archives
fx organize ~/Archives -i "*.zip" --date-source modified
```

#### Scenario 6: Backup Before Organization

Create backup before organizing:

```bash
# Backup source directory
fx backup ~/Downloads --compress

# Organize with dry-run
fx organize ~/Downloads --dry-run

# If preview looks good, organize
fx organize ~/Downloads
```

#### Scenario 7: Multiple Source Organization

Organize multiple sources:

```bash
# Organize each source
fx organize ~/Photos1 -o ~/Photos
fx organize ~/Photos2 -o ~/Photos
fx organize ~/Photos3 -o ~/Photos
```

#### Scenario 8: Large Directory Organization

Optimize for large directories:

```bash
# Use verbose to track progress
fx organize ~/LargeDir --verbose

# Use fail-fast to stop on first error
fx organize ~/LargeDir --fail-fast

# Use quiet to suppress output
fx organize ~/LargeDir --quiet
```

## Tips and Tricks

### Pattern Matching

```bash
# Include patterns (repeatable)
fx organize src/ -i "*.py" -i "*.js" -i "*.ts"

# Exclude patterns (repeatable)
fx organize src/ -e "*.pyc" -e "__pycache__" -e ".*"

# Combine include and exclude
fx organize src/ -i "*.py" -e "*test*" -e "*spec*"
```

### Recursive Processing

```bash
# Process all subdirectories
fx organize ~/Downloads --recursive

# With filtering
fx organize ~/Downloads --recursive -i "*.jpg"

# Clean up empty directories
fx organize ~/Downloads --recursive --clean-empty
```

### Automation

```bash
#!/bin/bash
# Automated organization script

# Backup source
fx backup ~/Downloads --compress

# Preview changes
fx organize ~/Downloads --dry-run

# If preview looks good, organize
if [ $? -eq 0 ]; then
  fx organize ~/Downloads --yes
fi
```

### Scheduled Organization

```bash
# Add to cron for automatic organization
# Example: Organize downloads daily at 3 AM
# 0 3 * * * fx organize ~/Downloads --yes --quiet
```

### Batch Processing

```bash
# Organize multiple directories
for dir in Downloads1 Downloads2 Downloads3; do
  fx organize ~/"$dir" --yes --quiet
done
```

## Advanced Usage

### Conflict Resolution Strategies

```bash
# Rename conflicting files (default)
fx organize src/ --on-conflict rename

# Skip conflicting files
fx organize src/ --on-conflict skip

# Overwrite existing files (use with caution)
fx organize src/ --on-conflict overwrite

# Interactive conflict resolution
fx organize src/ --on-conflict ask
```

### Date Source Selection

```bash
# Use creation time (default)
fx organize src/ --date-source created

# Use modification time
fx organize src/ --date-source modified

# Comparison: Different date sources
fx organize src/ --date-source created --dry-run
fx organize src/ --date-source modified --dry-run
```

### Depth Configuration

```bash
# Depth 1: output/20260110/
fx organize src/ --depth 1

# Depth 2: output/2026/20260110/
fx organize src/ --depth 2

# Depth 3: output/2026/202601/20260110/ (default)
fx organize src/ --depth 3
```

### Clean Empty Directories

```bash
# Clean up empty source directories
fx organize src/ --recursive --clean-empty

# Combine with other options
fx organize src/ --recursive --clean-empty --yes --quiet
```

## Performance Optimization

### For Large Directories

```bash
# Use quiet mode to reduce output
fx organize ~/LargeDir --quiet

# Use fail-fast to stop on errors
fx organize ~/LargeDir --fail-fast

# Use specific patterns to limit scope
fx organize ~/LargeDir -i "*.jpg" -i "*.png"
```

### For Many Files

```bash
# Use verbose to monitor progress
fx organize ~/ManyFiles --verbose

# Process in batches
fx organize ~/Batch1 --yes
fx organize ~/Batch2 --yes
fx organize ~/Batch3 --yes
```

### Preview Before Execution

```bash
# Always use dry-run first
fx organize src/ --dry-run

# Review preview
# Then execute
fx organize src/ --yes
```

## Best Practices

### Always Use Dry-Run First

```bash
# Preview changes
fx organize src/ --dry-run

# Review output
# Then execute
fx organize src/ --yes
```

### Backup Before Organization

```bash
# Create backup
fx backup src/ --compress

# Organize
fx organize src/

# If issues, restore from backup
tar -xf src_*.tar.xz
```

### Use Appropriate Conflict Mode

```bash
# Safe default: rename
fx organize src/ --on-conflict rename

# Preserve existing: skip
fx organize src/ --on-conflict skip

# Latest version: overwrite (use carefully)
fx organize src/ --on-conflict overwrite
```

### Choose Right Depth

```bash
# Many files, short period: depth 1
fx organize ~/Downloads --depth 1

# Moderate files, long period: depth 2
fx organize ~/Photos --depth 2

# Few files, very long period: depth 3
fx organize ~/Archive --depth 3
```

### Filter Appropriately

```bash
# Include specific types
fx organize src/ -i "*.jpg" -i "*.png"

# Exclude unwanted files
fx organize src/ -e "*.pyc" -e "__pycache__"

# Combine for precise control
fx organize src/ -i "*.py" -e "*test*"
```

## Common Issues

### Permission Denied

```bash
# Error: Permission denied
fx organize /protected/path

# Solution: Use sudo (not recommended)
sudo fx organize /protected/path

# Or fix permissions
chmod +r /path/to/directory
```

### Disk Space Issues

```bash
# Error: No space left on device
fx organize src/

# Solution: Check disk space
df -h

# Clean up or use different output
fx organize src/ -o /external/drive/organized
```

### Conflicts Not Resolved

```bash
# Files with conflicts may be skipped
fx organize src/ --on-conflict skip

# Solution: Check output
fx size src/organized/

# Or use rename mode
fx organize src/ --on-conflict rename
```

### Date Issues

```bash
# Files with no creation date may use modification
fx organize src/ --date-source created

# Or explicitly use modification time
fx organize src/ --date-source modified
```

### Pattern Matching Issues

```bash
# Patterns not matching as expected
fx organize src/ -i "*.py"

# Solution: Test pattern first
ls *.py

# Use correct glob syntax
fx organize src/ -i "*.py"
```

## Troubleshooting

### No Files Organized

```bash
# Check if files match patterns
fx organize src/ -i "*.py" --dry-run

# Check source directory
ls src/

# Check permissions
ls -la src/
```

### Wrong Dates

```bash
# Check file dates
stat filename

# Use modification time instead
fx organize src/ --date-source modified
```

### Duplicate Files

```bash
# Use rename mode to keep all
fx organize src/ --on-conflict rename

# Or skip mode to preserve existing
fx organize src/ --on-conflict skip
```

### Organization Too Slow

```bash
# Use quiet mode
fx organize src/ --quiet

# Limit file types
fx organize src/ -i "*.jpg"

# Process in batches
fx organize src/ --fail-fast
```

## See Also

- [`fx backup`](backup.md) - Create timestamped backups
- [`fx filter`](filter.md) - Filter files by extension
- [`fx size`](size.md) - Analyze file/directory sizes

---

**Organize with confidence!** Use `fx organize` for structured, date-based file management. 📅
