# Command: fx files

Count files in directories with powerful filtering options.

## Overview

`fx files` provides a fast and efficient way to count files and directories with pattern matching and recursive search capabilities. It's perfect for project statistics, file auditing, and understanding project structure.

**Key Features:**
- 📊 Fast file counting with glob pattern matching
- 🔍 Recursive directory traversal
- 📈 Detailed statistics display
- 🎯 Include/exclude filters for precise control
- 📁 Directory and file counting

## Usage

```bash
fx files [OPTIONS] [PATHS...]
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|----------|-------------|
| `PATHS` | path | `.` | One or more paths to analyze (default: current directory) |
| `--pattern` | string | `*` | Glob pattern to match files (e.g., `*.py`, `test_*`) |
| `--exclude` | string | - | Pattern to exclude files (repeatable) |
| `--recursive` | flag | True | Search subdirectories recursively |
| `--detailed` | flag | False | Show detailed statistics including directories |

## Examples

### Basic Usage

Count files in the current directory:

```bash
fx files .
```

**Output:**
```
      1 .git
      2 README.md
     45 docs/
    125 fx_bin/
    173 Total
```

Count files in a specific directory:

```bash
fx files /path/to/directory
```

Count files in multiple directories:

```bash
fx files /path/to/dir1 /path/to/dir2 /path/to/dir3
```

### Pattern Matching

Count only Python files:

```bash
fx files . --pattern "*.py"
```

Count test files:

```bash
fx files . --pattern "*test*.py"
```

Count all image files:

```bash
fx files . --pattern "*.{jpg,jpeg,png,gif}"
```

### Excluding Files

Count files excluding test files:

```bash
fx files . --exclude "*test*"
```

Exclude multiple patterns:

```bash
fx files . --exclude "*test*" --exclude "*.pyc" --exclude "__pycache__"
```

Count documentation files excluding README:

```bash
fx files . --pattern "*.md" --exclude "README.md"
```

### Recursive vs Non-Recursive

Count files recursively (default):

```bash
fx files . --recursive
```

Count files only in current directory:

```bash
fx files . --no-recursive
```

Count files with maximum depth of 2 levels:

```bash
fx files . --recursive --max-depth 2
```

### Detailed Statistics

Show detailed statistics including directories:

```bash
fx files . --detailed
```

**Output:**
```
Directories: 25
Files: 173
Hidden: 5
Total: 198
```

### Real-World Scenarios

#### Scenario 1: Project Statistics

Count all files in a project:

```bash
fx files . --recursive --detailed
```

Count by file type:

```bash
# Count Python files
fx files . --pattern "*.py" --recursive

# Count JavaScript files
fx files . --pattern "*.{js,jsx,ts,tsx}" --recursive

# Count Markdown files
fx files . --pattern "*.md" --recursive
```

#### Scenario 2: Audit Large Directories

Find directories with many files:

```bash
# Count files in subdirectories
for dir in */; do
  echo "$dir: $(fx files "$dir" --recursive | tail -1 | awk '{print $1}')"
done
```

Or use `fx size` for size analysis:

```bash
fx size . --recursive --limit 10
```

#### Scenario 3: Clean Test Count

Count test files:

```bash
# Count all test files
fx files . --pattern "*test*.py" --recursive

# Count by test type
fx files tests/ --pattern "*test*.py" --recursive
```

#### Scenario 4: Documentation Audit

Count documentation files:

```bash
# Count Markdown files
fx files . --pattern "*.md" --recursive

# Count excluding generated docs
fx files docs/ --pattern "*.md" --exclude "*generated*" --recursive
```

#### Scenario 5: Source Code Distribution

Analyze project composition:

```bash
# Count by language
echo "Python: $(fx files . --pattern '*.py' --recursive | tail -1 | awk '{print $1}')"
echo "JavaScript: $(fx files . --pattern '*.{js,jsx,ts,tsx}' --recursive | tail -1 | awk '{print $1}')"
echo "Markdown: $(fx files . --pattern '*.md' --recursive | tail -1 | awk '{print $1}')"
```

## Tips and Tricks

### Combining with Other Commands

```bash
# Find directories with most files
find . -type d -exec fx files {} \; | sort -rn | head -10

# Count files matching a pattern
find . -name "*.py" | xargs fx files
```

### Using in Scripts

```bash
#!/bin/bash
# Count files and exit with error if too few
count=$(fx files . --pattern "*.py" --recursive | tail -1 | awk '{print $1}')
if [ "$count" -lt 10 ]; then
  echo "Error: Expected at least 10 Python files, found $count"
  exit 1
fi
echo "OK: Found $count Python files"
```

### Monitoring File Count Changes

```bash
# Count before and after operations
before=$(fx files . --recursive | tail -1 | awk '{print $1}')
# ... perform operations ...
after=$(fx files . --recursive | tail -1 | awk '{print $1}')
echo "Files changed: $((after - before))"
```

## Performance Notes

- **Large directories**: `fx files` is optimized for performance and handles directories with thousands of files efficiently
- **Symlink handling**: Symlinks are not followed by default (prevents infinite loops)
- **Permission errors**: Files with permission errors are silently skipped
- **Hidden files**: Hidden files (starting with `.`) are counted by default

## Common Issues

### Permission Denied

If you see permission errors:

```bash
# Use sudo (not recommended)
sudo fx files /protected/path

# Or check directory permissions
ls -la /path/to/directory
```

### Slow Performance

For very large directories:

```bash
# Use pattern to reduce search scope
fx files . --pattern "*.py" --recursive

# Use max-depth to limit recursion
fx files . --recursive --max-depth 2
```

### Incorrect Counts

If counts seem wrong:

```bash
# Use detailed mode to debug
fx files . --recursive --detailed

# Check for hidden files
ls -la | grep "^\."
```

## See Also

- [`fx size`](size.md) - Analyze file/directory sizes
- [`fx filter`](filter.md) - Filter files by extension
- [`fx ff`](ff.md) - Find files by keyword
- [`fx organize`](organize.md) - Organize files by date

---

**Need more examples?** See [Use Cases](../use-cases/daily-workflow.md) for real-world workflows.
