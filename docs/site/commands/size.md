# Command: fx size

Analyze file and directory sizes with human-readable output.

## Overview

`fx size` provides detailed size analysis for files and directories with flexible output options. Perfect for disk usage analysis, cleanup planning, and understanding storage distribution.

**Key Features:**
- 📊 Human-readable size units (B, KB, MB, GB)
- 📈 Sortable output (ascending/descending)
- 🎯 Limit results to top N entries
- 📁 Include hidden files optionally
- 🔄 Recursive directory size calculation

## Usage

```bash
fx size [OPTIONS] [PATHS...]
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|----------|-------------|
| `PATHS` | path | `.` | One or more paths to analyze (default: current directory) |
| `--limit` | integer | unlimited | Number of results to show |
| `--unit` | string | auto | Size unit (B, KB, MB, GB) |
| `--sort` | string | desc | Sort order (asc/desc) |
| `--all` | flag | False | Include hidden files (starting with `.`) |

## Examples

### Basic Usage

Show sizes in the current directory:

```bash
fx size .
```

**Output:**
```
1.2 MB    fx_bin/
456 KB     docs/
12.3 KB    README.md
Total: 1.7 MB
```

Analyze specific directories:

```bash
fx size /path/to/dir1 /path/to/dir2
```

### Limiting Results

Show top 10 largest files:

```bash
fx size . --limit 10
```

Show top 5 largest directories:

```bash
fx size . --limit 5
```

### Size Units

Display sizes in MB:

```bash
fx size . --unit MB
```

Display sizes in KB:

```bash
fx size . --unit KB
```

Display sizes in GB:

```bash
fx size . --unit GB
```

### Sorting

Sort by size ascending (smallest first):

```bash
fx size . --sort asc
```

Sort by size descending (largest first - default):

```bash
fx size . --sort desc
```

### Hidden Files

Include hidden files in analysis:

```bash
fx size . --all
```

### Real-World Scenarios

#### Scenario 1: Find Large Files

Find the 20 largest files in a project:

```bash
fx size . --limit 20 --sort desc
```

#### Scenario 2: Analyze Log Files

Find largest log files:

```bash
# Find log files
fx ff .log --exclude archive

# Analyze their sizes
fx ff .log --exclude archive | xargs fx size | sort -rn | head -10
```

#### Scenario 3: Cleanup Planning

Identify directories taking most space:

```bash
# Find top 10 largest directories
fx size . --recursive --limit 10

# Analyze specific directories
fx size node_modules/
fx size .venv/
fx size dist/
```

#### Scenario 4: Disk Usage Summary

Get total size of current directory:

```bash
# Get total (last line shows total)
fx size . | tail -1

# Or count specific file types
fx size . --pattern "*.py" --pattern "*.js"
```

#### Scenario 5: Compare Directories

Compare sizes of multiple directories:

```bash
# Compare three directories
echo "Project A: $(fx size project_a | tail -1)"
echo "Project B: $(fx size project_b | tail -1)"
echo "Project C: $(fx size project_c | tail -1)"
```

## Tips and Tricks

### Combining with Other Commands

```bash
# Find and analyze large Python files
find . -name "*.py" -exec fx size {} \; | sort -rn | head -20

# Analyze only files matching a pattern
fx size . --pattern "*.log"
```

### Finding Space Hogs

```bash
# Find directories over 100MB
for dir in */; do
  size=$(fx size "$dir" | tail -1 | awk '{print $1}')
  if [[ $size == *"GB"* ]] || [[ $size == *"10"*"MB"* ]]; then
    echo "$dir: $size"
  fi
done
```

### Recursive Size Calculation

```bash
# Get total size of all subdirectories
for dir in */; do
  echo "$dir: $(fx size "$dir" --recursive | tail -1)"
done
```

### Size Comparison Script

```bash
#!/bin/bash
# Compare sizes before and after operations
before_size=$(fx size . --recursive | tail -1)

# ... perform operations ...

after_size=$(fx size . --recursive | tail -1)

echo "Before: $before_size"
echo "After:  $after_size"
```

## Performance Notes

- **Large directories**: Efficiently handles directories with thousands of files
- **Symlink handling**: Symlinks are not followed (prevents infinite loops)
- **Size calculation**: Uses accurate file system information
- **Caching**: No caching - always reads current state

## Common Issues

### Permission Denied

```bash
# Use sudo to analyze protected directories
sudo fx size /protected/path

# Or check permissions
ls -la /path/to/directory
```

### Slow Performance

For very large directory trees:

```bash
# Use limit to reduce output
fx size . --limit 10

# Use pattern to filter
fx size . --pattern "*.py"

# Use specific paths instead of full recursion
fx size src/ tests/ docs/
```

### Inaccurate Sizes

If sizes seem incorrect:

```bash
# Check for hidden files
fx size . --all

# Verify with system command
du -sh .

# Use recursive mode for directories
fx size . --recursive
```

## See Also

- [`fx files`](files.md) - Count files in directories
- [`fx ff`](ff.md) - Find files by keyword
- [`fx filter`](filter.md) - Filter files by extension
- [`fx organize`](organize.md) - Organize files by date

---

**Need more examples?** See [Use Cases](../use-cases/daily-workflow.md) for real-world workflows.
