# Command: fx fff

Find first file matching KEYWORD. Returns only the first match and exits immediately for speed.

## Overview

`fx fff` is a fast alias for `fx ff KEYWORD --first`. It returns only the first matching file and exits immediately, making it perfect for quick file lookups in scripts and command chains.

**Key Features:**
- ⚡ Ultra-fast first-match lookup
- 🎯 Perfect for shell scripts and aliases
- 🔄 Returns single result immediately
- 📝 Uses smart exclusions (.git, .venv, node_modules)

## Usage

```bash
fx fff KEYWORD
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|----------|-------------|
| `KEYWORD` | string | - | Keyword or pattern to search for (required) |

## Examples

### Basic Usage

Find first file with "test" in name:

```bash
fx fff test
```

Find first configuration file:

```bash
fx fff config
```

Find first Python file:

```bash
fx fff .py
```

### Real-World Scenarios

#### Scenario 1: Quick File Lookup

Open the first README file found:

```bash
vim $(fx fff README)
```

Display the first config file:

```bash
cat $(fx fff config)
```

#### Scenario 2: Script Integration

Check if a specific file exists:

```bash
#!/bin/bash
file=$(fx fff my_script.py)
if [ -n "$file" ]; then
  python "$file"
else
  echo "Script not found"
  exit 1
fi
```

#### Scenario 3: Alias Creation

Create quick aliases in `.bashrc` or `.zshrc`:

```bash
# Find and open Python files
alias pycat='cat $(fx fff .py)'
alias pyvim='vim $(fx fff .py)'

# Find and open config files
alias confcat='cat $(fx fff config)'
alias confvim='vim $(fx fff config)'
```

#### Scenario 4: Command Chain Integration

Find and grep first matching file:

```bash
fx fff api | xargs grep -l "endpoint"
```

Find and analyze first matching file:

```bash
fx fff .log | xargs fx size
```

#### Scenario 5: Service Discovery

Find and display first service file:

```bash
cat $(fx fff service)
```

Find and copy first model file:

```bash
cp $(fx fff model) /backup/
```

## Tips and Tricks

### Shell Script Best Practices

```bash
#!/bin/bash
# Safe file lookup with error handling
file=$(fx fff my_file 2>/dev/null)

if [ -z "$file" ]; then
  echo "Error: File not found"
  exit 1
fi

# Use the file
cat "$file"
```

### Combining with Other Commands

```bash
# Find and open
vim $(fx fff README)

# Find and grep
fx fff api | xargs grep "endpoint"

# Find and backup
fx fff important.txt | xargs fx backup

# Find and count
wc -l $(fx fff .py)
```

### Creating Aliases

Add to `.bashrc` or `.zshrc`:

```bash
# Quick file operations
alias fxcat='cat $(fx fff)'
alias fxvim='vim $(fx fff)'
alias fxdiff='git diff $(fx fff)'

# Language-specific
alias pyfind='fx fff .py'
alias jsfind='fx fff .js'
alias mdfind='fx fff .md'
```

### Error Handling in Scripts

```bash
#!/bin/bash
# Check if file exists before using
file=$(fx fff my_file)

if [ ! -f "$file" ]; then
  echo "Error: File '$file' not found"
  exit 1
fi

# File exists, proceed
cat "$file"
```

## Performance Notes

- **Speed**: Returns immediately after first match (no full traversal)
- **Smart defaults**: Excludes heavy directories (.git, .venv, node_modules)
- **Efficiency**: Perfect for quick lookups in scripts

## Common Issues

### No Results Found

```bash
# Check if file exists
fx fff my_file

# Try broader search
fx ff my_file  # Uses full search
```

### Wrong File Returned

```bash
# Be more specific with keyword
fx fff "api_v1_user"  # Instead of "api"

# Check what files match
fx ff my_file  # See all matches
```

### Script Errors

```bash
# Always check if file exists
file=$(fx fff my_file)
if [ -z "$file" ]; then
  echo "File not found"
  exit 1
fi
```

## Comparison with fx ff

| Feature | `fx fff` | `fx ff` |
|---------|-----------|---------|
| Returns | First match only | All matches |
| Speed | Ultra-fast (stops immediately) | Full traversal |
| Use case | Scripts, quick lookups | Browsing, analysis |
| Output | Single path | Multiple paths |

## See Also

- [`fx ff`](ff.md) - Find files by keyword (full search)
- [`fx filter`](filter.md) - Filter files by extension
- [`fx files`](files.md) - Count files in directories

---

**Need speed?** Use `fx fff` for instant file lookup! 🚀
