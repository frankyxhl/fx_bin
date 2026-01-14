# Command: fx replace

Replace text in files with automatic backup and restore on failure.

## Overview

`fx replace` performs text replacement in files with built-in safety features. It uses atomic writes with automatic backup and restore on failure, ensuring data safety during text replacement operations.

**Key Features:**
- 🛡️ Atomic write operations
- 💾 Automatic backup before replacement
- 🔄 Automatic restore on failure
- 📝 Support for multiple files
- ⚡ Fast processing for large files

## Usage

```bash
fx replace search_text replace_text [filenames...]
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `search_text` | string | Yes | Text to search for |
| `replace_text` | string | Yes | Text to replace with |
| `filenames` | string | Yes | One or more files to process (repeatable) |

## Examples

### Basic Usage

Replace text in a single file:

```bash
fx replace "old" "new" file.txt
```

Replace text in multiple files:

```bash
fx replace "old" "new" *.txt
```

### Real-World Scenarios

#### Scenario 1: Version Updates

Update version strings across multiple files:

```bash
# Update version from 1.0.0 to 2.0.0
fx replace "version='1.0.0'" "version='2.0.0'" *.py

# Update __version__ variables
fx replace "__version__ = '1.0.0'" "__version__ = '2.0.0'" *.py
```

#### Scenario 2: Refactoring

Update function names across codebase:

```bash
# Rename function
fx replace "old_function_name" "new_function_name" *.py

# Update class names
fx replace "OldClassName" "NewClassName" *.py
```

#### Scenario 3: Configuration Updates

Update configuration settings:

```bash
# Update database URL
fx replace "old_database_url" "new_database_url" config.yaml

# Update API endpoints
fx replace "api.example.com" "api.newdomain.com" config.json
```

#### Scenario 4: Text Processing

Standardize text formatting:

```bash
# Replace tabs with spaces
fx replace "\t" "    " file.txt

# Remove trailing spaces
fx replace "  " "" file.txt
```

#### Scenario 5: Path Updates

Update file paths in code:

```bash
# Update import paths
fx replace "from old.module" "from new.module" *.py

# Update include paths
fx replace "#include <old.h>" "#include <new.h>" *.c
```

## Tips and Tricks

### Combining with Other Commands

```bash
# Find files and replace text
fx ff config | xargs fx replace "old" "new"

# Count files before replacement
echo "Files to update: $(fx ff __version__ | wc -l)"

# Replace and verify
fx replace "old" "new" *.py && grep -r "new" . --include="*.py"
```

### Batch Replacement with Multiple Patterns

```bash
# Multiple replacements (run sequentially)
fx replace "pattern1" "replacement1" *.py
fx replace "pattern2" "replacement2" *.py
fx replace "pattern3" "replacement3" *.py
```

### Safe Replacement Workflow

```bash
#!/bin/bash
# Safe replacement workflow

# 1. Create backup
fx backup project_dir --compress

# 2. Perform replacements
fx replace "old" "new" *.py

# 3. Verify changes
grep -c "new" *.py

# 4. Test the code
pytest
```

### Handling Special Characters

```bash
# Quote strings with special characters
fx replace "old@domain.com" "new@domain.com" file.txt

# Replace with newline (advanced)
# Note: This may require escape sequences depending on shell
fx replace "pattern" "replacement\nnewline" file.txt
```

## Safety Features

### Atomic Writes

`fx replace` uses atomic write operations:
1. Creates a temporary file
2. Writes content to temporary file
3. Renames temporary file to original (atomic on POSIX)
4. Only if all steps succeed, the original is modified

### Automatic Backup

Before any replacement:
- Original file is backed up
- Backup location is determined by the backup module
- On failure, original is automatically restored

### Failure Recovery

If replacement fails:
- Original file is automatically restored from backup
- No partial changes are left behind
- Error message indicates the failure reason

## Performance Notes

- **Large files**: Efficiently handles large files with streaming operations
- **Multiple files**: Processes files sequentially for safety
- **Encoding**: Assumes UTF-8 encoding; other encodings may cause issues
- **Binary files**: Binary files are not supported (data corruption risk)

## Common Issues

### No Changes Made

If replacement seems to have no effect:

```bash
# Check if text exists
grep "old_text" file.txt

# Check for exact match (case-sensitive)
grep -i "old_text" file.txt

# Try with different quoting
fx replace 'old' 'new' file.txt
```

### Permission Denied

```bash
# Check file permissions
ls -la file.txt

# Make file writable (if allowed)
chmod +w file.txt

# Or run with sudo (not recommended)
sudo fx replace "old" "new" file.txt
```

### Binary File Corruption

`fx replace` is not designed for binary files:

```bash
# Do not use on binary files
fx replace "pattern" "replacement" image.jpg  # ❌ CORRUPTION RISK

# Use hex editors or specialized tools for binary files
```

### Special Character Issues

```bash
# Use single quotes for strings with special characters
fx replace 'old@domain' 'new@domain' file.txt

# Escape special characters
fx replace "old\|new" "replacement" file.txt
```

### Restore Failed

If automatic restore fails:

```bash
# Check backup directory
# Backups are created by fx backup module
# Look for files with timestamp suffix
ls -la *_timestamp.*

# Manual restore from backup
cp file_timestamp.txt file.txt
```

## Best Practices

### Always Test First

```bash
# Test replacement on a single file
cp file.txt file_test.txt
fx replace "old" "new" file_test.txt
cat file_test.txt

# Only then replace in all files
fx replace "old" "new" *.txt
```

### Create Backup Before Batch Operations

```bash
# Always backup before bulk changes
fx backup project_dir --compress

# Then perform replacements
fx replace "old" "new" *.py

# Verify changes
git diff
```

### Use Version Control

```bash
# Before replacement, commit current state
git add .
git commit -m "Before replacement"

# Perform replacement
fx replace "old" "new" *.py

# Review changes
git diff

# If needed, revert
git checkout .
```

### Verify Replacements

```bash
# Count occurrences after replacement
grep -c "new_text" *.py

# View replacement context
grep -C 3 "new_text" file.txt

# Ensure no unintended changes
grep "old_text" file.txt  # Should return nothing
```

## See Also

- [`fx backup`](backup.md) - Create timestamped backups
- [`fx ff`](ff.md) - Find files by keyword
- [`fx files`](files.md) - Count files in directories

---

**Safety First!** `fx replace` protects your data with automatic backup and restore. 🛡️
