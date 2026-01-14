# Performance Optimization

Tips and techniques for optimizing fx-bin performance in large projects and high-volume workflows.

## Overview

While fx-bin is designed for performance out of the box, large projects and high-volume workflows may benefit from specific optimization strategies. This guide covers performance best practices and optimization techniques.

## Performance Characteristics

### Command Performance Comparison

| Command | Speed | Memory Usage | Best For |
|----------|--------|--------------|-----------|
| `fx files` | ⚡ Fast | Low | File counting |
| `fx size` | ⚡ Fast | Low-Medium | Size analysis |
| `fx ff` | ⚡ Fast | Low | File finding |
| `fx fff` | 🚀 Ultra Fast | Low | Quick lookup |
| `fx filter` | ⚡ Fast | Low-Medium | File filtering |
| `fx replace` | ⚡ Fast | Medium | Text replacement |
| `fx backup` | ⚡ Fast | Medium-High | Backup creation |
| `fx organize` | ⚡ Fast | Medium-High | File organization |
| `fx root` | 🚀 Ultra Fast | Low | Navigation |
| `fx today` | 🚀 Ultra Fast | Low | Workspace creation |

## Optimization Strategies

### 1. Reduce Search Scope

Limit search scope for better performance:

```bash
# ❌ Slow: Search entire project
fx ff config

# ✅ Fast: Search specific directory
fx ff config src/

# ❌ Slow: Count all files recursively
fx files . --recursive

# ✅ Fast: Count files in specific directory
fx files src/ --recursive
```

### 2. Use First Match Mode

Use `--first` for quick lookups:

```bash
# ❌ Slow: Full search
fx ff config

# ✅ Fast: First match only
fx ff config --first

# Or use fff command
fx fff config
```

### 3. Exclude Large Directories

Exclude heavy directories from search:

```bash
# ❌ Slow: Search everything
fx ff api

# ✅ Fast: Exclude heavy directories
fx ff api --exclude node_modules --exclude .venv --exclude dist --exclude build
```

### 4. Use Specific Patterns

Use specific patterns instead of wildcards:

```bash
# ❌ Slow: Broad wildcard
fx ff .*

# ✅ Fast: Specific extension
fx ff .py

# ✅ Fast: Specific keyword
fx ff config
```

### 5. Limit Results

Limit output for large result sets:

```bash
# ❌ Slow: All results
fx size . --recursive

# ✅ Fast: Limited results
fx size . --recursive --limit 20

# ❌ Slow: All files
fx filter py --sort-by modified --reverse

# ✅ Fast: Limited files
fx filter py --sort-by modified --reverse --limit 10
```

### 6. Use Dry-Run Mode

Preview operations before execution:

```bash
# Preview organization
fx organize ~/Data --dry-run

# Preview replacement
# Note: fx replace doesn't have dry-run, use grep first
grep -r "old_text" . --include="*.py" | wc -l
```

## Large Project Optimization

### 1. Batch Processing

Process large projects in batches:

```bash
#!/bin/bash
# Process in batches

# Split processing by directory
for dir in src/ tests/ docs/; do
  echo "Processing: $dir"
  fx ff config "$dir"
done
```

### 2. Parallel Processing

Use parallel execution where possible:

```bash
#!/bin/bash
# Parallel file finding

# Find in multiple directories in parallel
find . -maxdepth 1 -type d | parallel "fx ff config {} --exclude node_modules"
```

### 3. Caching Results

Cache frequently accessed information:

```bash
#!/bin/bash
# Cache file counts

CACHE_FILE=".fx_cache.txt"

# Check cache age
if [ -f "$CACHE_FILE" ]; then
  CACHE_AGE=$(( $(date +%s) - $(stat -c %Y "$CACHE_FILE") ))
  if [ $CACHE_AGE -lt 3600 ]; then
    # Cache is less than 1 hour old
    cat "$CACHE_FILE"
    exit 0
  fi
fi

# Update cache
fx files . --recursive > "$CACHE_FILE"
cat "$CACHE_FILE"
```

## Memory Optimization

### 1. Avoid Large Output

Avoid storing large command outputs in variables:

```bash
# ❌ Bad: Store large output
FILES=$(fx ff .)
for file in $FILES; do
  echo "$file"
done

# ✅ Good: Stream output
fx ff . | while read file; do
  echo "$file"
done
```

### 2. Process Files Individually

Process files one at a time:

```bash
# ❌ Bad: Load all files into array
FILES=($(fx ff .py --exclude __pycache__))
for file in "${FILES[@]}"; do
  python -m py_compile "$file"
done

# ✅ Good: Process files individually
fx ff .py --exclude __pycache__ | while read file; do
  python -m py_compile "$file"
done
```

## Disk I/O Optimization

### 1. Minimize Disk Access

Minimize disk access patterns:

```bash
# ❌ Bad: Multiple passes
fx ff config
fx ff api
fx ff service

# ✅ Good: Single pass with broader pattern
fx ff "config|api|service"
```

### 2. Use Compression Wisely

Use compression only for large directories:

```bash
# ❌ Bad: Compress small directory
fx backup small_dir/ --compress

# ✅ Good: Compress large directory
fx backup large_project/ --compress

# ✅ Good: No compression for single files
fx backup file.txt
```

## Performance Testing

### Benchmark Commands

```bash
#!/bin/bash
# benchmark_fx.sh

# Time fx commands
echo "=== Performance Benchmark ==="
echo ""

echo "1. fx ff (full search)"
time fx ff api

echo ""
echo "2. fx ff --first"
time fx ff api --first

echo ""
echo "3. fx fff"
time fx fff api

echo ""
echo "4. fx files"
time fx files . --recursive

echo ""
echo "5. fx filter"
time fx filter py --sort-by modified --reverse --limit 10
```

### Memory Profiling

```bash
#!/bin/bash
# memory_profile.sh

# Profile memory usage
echo "=== Memory Profile ==="
echo ""

# Track memory usage
for cmd in "fx ff ." "fx files ." "fx filter py"; do
  echo "Command: $cmd"
  /usr/bin/time -v $cmd 2>&1 | grep "Maximum resident set size"
  echo ""
done
```

## Performance Best Practices

### 1. Use Appropriate Commands

```bash
# For quick lookup: Use fff
fx fff config

# For browsing: Use ff
fx ff config

# For counting: Use files
fx files . --pattern "*.py"

# For analysis: Use size
fx size . --recursive --limit 10
```

### 2. Filter Aggressively

```bash
# Always exclude heavy directories
fx ff api --exclude node_modules --exclude .venv --exclude dist --exclude build --exclude __pycache__
```

### 3. Use Limits

```bash
# Always limit results for large output
fx size . --recursive --limit 20
fx filter py --sort-by modified --reverse --limit 10
```

### 4. Profile Before Optimization

```bash
# Always profile before optimizing
time fx ff .

# Measure baseline
# Apply optimization
# Measure improvement
```

## Troubleshooting Performance

### Slow File Finding

```bash
# If fx ff is slow:

# 1. Check what directories are being searched
# Add verbose output if available
fx ff . --verbose

# 2. Exclude heavy directories
fx ff . --exclude node_modules --exclude .venv --exclude dist

# 3. Use --first for quick lookup
fx ff . --first

# 4. Be more specific with pattern
fx ff "api_v1" instead of "api"
```

### Slow File Counting

```bash
# If fx files is slow:

# 1. Reduce recursion depth
fx files . --recursive --max-depth 2

# 2. Use pattern to filter
fx files . --pattern "*.py" --recursive

# 3. Count specific directories
fx files src/ --recursive
```

### Slow File Organization

```bash
# If fx organize is slow:

# 1. Preview with dry-run
fx organize . --dry-run

# 2. Use filtering
fx organize . -i "*.jpg" -i "*.png" --recursive

# 3. Process in batches
fx organize batch1/
fx organize batch2/
fx organize batch3/

# 4. Use quiet mode
fx organize . --recursive --quiet
```

## Related Commands

- [`fx ff`](../commands/ff.md) - Find files by keyword
- [`fx files`](../commands/files.md) - Count files
- [`fx filter`](../commands/filter.md) - Filter files by extension
- [`fx organize`](../commands/organize.md) - Organize files by date

---

**Optimize for speed!** Use these techniques to get maximum performance from fx-bin. 🚀
