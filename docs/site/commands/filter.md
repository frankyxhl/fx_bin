# Command: fx filter

Filter files by extension with intelligent sorting capabilities.

## Overview

`fx filter` provides powerful file filtering by extension with time-based sorting (creation or modification) and flexible output formats. Perfect for analyzing recent files, organizing by time, and content discovery.

**Key Features:**
- 🎯 Filter by single or multiple extensions
- 📅 Sort by creation or modification time
- 🔄 Reverse sort order (newest first)
- 📝 Multiple output formats (simple, detailed)
- 📊 Show relative paths or full paths
- 🔢 Limit results for targeted analysis

## Usage

```bash
fx filter [OPTIONS] EXTENSION [PATHS...]
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|----------|-------------|
| `EXTENSION` | string | - | File extension to filter (e.g., `py`, `jpg,png`) |
| `PATHS` | path | `.` | One or more paths to search (default: current directory) |
| `--recursive` / `--no-recursive` | flag | True | Search recursively in subdirectories |
| `--sort-by` | string | None | Sort by 'created' or 'modified' time |
| `--reverse` | flag | False | Reverse sort order (newest first for time sorts) |
| `--format` | string | detailed | Output format: 'simple' or 'detailed' |
| `--show-path` | flag | False | Show relative file paths instead of just filenames |
| `--limit` | integer | None | Limit number of results returned |

## Examples

### Basic Usage

Find Python files:

```bash
fx filter py
```

Find multiple extensions:

```bash
fx filter "jpg,png,gif"
```

### Sorting by Time

Find Python files sorted by modification time:

```bash
fx filter py --sort-by modified
```

Find newest Python files first:

```bash
fx filter py --sort-by modified --reverse
```

Find files sorted by creation time:

```bash
fx filter py --sort-by created
```

### Output Formats

Simple output (just filenames):

```bash
fx filter py --format simple
```

Detailed output (timestamp, size, relative time):

```bash
fx filter py --format detailed
```

### Path Display

Show relative file paths:

```bash
fx filter py --show-path
```

### Limiting Results

Show only 10 most recent Python files:

```bash
fx filter py --sort-by modified --reverse --limit 10
```

### Recursive vs Non-Recursive

Search recursively (default):

```bash
fx filter py --recursive
```

Search only in current directory:

```bash
fx filter py --no-recursive
```

### Real-World Scenarios

#### Scenario 1: Recent Code Changes

Find recently modified Python files:

```bash
fx filter py --sort-by modified --reverse --limit 10
```

Find recently modified JavaScript files:

```bash
fx filter "js,jsx,ts,tsx" --sort-by modified --reverse --limit 10
```

#### Scenario 2: Data Analysis

Find recently created CSV files:

```bash
fx filter csv --sort-by created --reverse --limit 10
```

Find recent JSON data files:

```bash
fx filter json --sort-by created --reverse --limit 10
```

#### Scenario 3: Document Management

Find recent Markdown documents:

```bash
fx filter md --sort-by modified --reverse
```

Find recent PDF documents:

```bash
fx filter "pdf,docx" --sort-by created --reverse
```

#### Scenario 4: Log Analysis

Find recent log files:

```bash
fx filter log --sort-by modified --reverse --limit 20
```

Find recent log files with paths:

```bash
fx filter log --sort-by modified --reverse --show-path --limit 20
```

#### Scenario 5: Image Management

Find recent images:

```bash
fx filter "jpg,jpeg,png,gif,webp" --sort-by created --reverse --limit 50
```

Find recent screenshots:

```bash
fx filter "png,jpg" --sort-by created --reverse --limit 10 --show-path
```

#### Scenario 6: Configuration Discovery

Find recent config files:

```bash
fx filter "yaml,yml,json,toml" --sort-by modified --reverse
```

Find recent environment files:

```bash
fx filter env --sort-by created --reverse
```

## Tips and Tricks

### Combining with Other Commands

```bash
# Find recent Python files and count lines
fx filter py --sort-by modified --reverse --limit 10 | xargs wc -l

# Find recent logs and analyze
fx filter log --sort-by modified --reverse --limit 10 | xargs fx size

# Find recent files and grep
fx filter py --sort-by modified --reverse --limit 5 | xargs grep "TODO"
```

### Time-Based Workflows

```bash
# Find files modified in last 24 hours
fx filter py --sort-by modified --reverse | head -20

# Find files created this week
fx filter "jpg,png" --sort-by created --reverse | head -50

# Daily review of changes
fx filter "py,js,md" --sort-by modified --reverse --limit 30
```

### Multi-Type Filtering

```bash
# Find all source code files
fx filter "py,js,ts,java,cpp" --sort-by modified --reverse

# Find all documentation
fx filter "md,txt,rst" --sort-by created --reverse

# Find all configuration files
fx filter "yaml,yml,json,toml,ini" --sort-by modified --reverse
```

### Path-Specific Filtering

```bash
# Filter specific directories
fx filter py src/ tests/ --sort-by modified --reverse

# Filter multiple directories
fx filter log ~/logs/ /var/log/ --sort-by modified --reverse --show-path
```

### Script Integration

```bash
#!/bin/bash
# Find and process recent files
files=$(fx filter py --sort-by modified --reverse --limit 10 --format simple)

for file in $files; do
  echo "Processing: $file"
  python -m py_compile "$file"
done
```

## Performance Notes

- **Large directories**: Efficiently handles directories with thousands of files
- **Sorting overhead`: Sorting adds minimal overhead; use only when needed
- **Recursive search**: Recursive search is optimized for performance
- **Time resolution**: Uses file system timestamps with OS-specific resolution

## Common Issues

### No Results Found

```bash
# Check extension spelling
fx filter python  # Should be "py"

# Try with paths
fx filter py ~/my_project/

# Check if files exist
ls -la *.py
```

### Too Many Results

```bash
# Limit results
fx filter py --limit 20

# Add path to narrow scope
fx filter py src/ tests/

# Use more specific extensions
fx filter "py" --sort-by modified --reverse --limit 10
```

### Sorting Not Working

```bash
# Make sure to specify sort type
fx filter py --sort-by modified

# Use reverse for newest first
fx filter py --sort-by modified --reverse
```

### Path Display Issues

```bash
# Show relative paths
fx filter py --show-path

# Use absolute paths with cd
cd /path/to/dir && fx filter py --show-path
```

## See Also

- [`fx files`](files.md) - Count files in directories
- [`fx ff`](ff.md) - Find files by keyword
- [`fx size`](size.md) - Analyze file/directory sizes
- [`fx organize`](organize.md) - Organize files by date

---

**Need more examples?** See [Use Cases](../use-cases/daily-workflow.md) for real-world workflows.
