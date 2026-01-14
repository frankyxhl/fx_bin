# Command: fx ff

Find files whose names contain a keyword, with powerful filtering options and smart exclusions.

## Overview

`fx ff` provides fast file discovery with keyword matching, flexible exclusion patterns, and smart default settings. Perfect for debugging, code navigation, and project analysis.

**Key Features:**
- 🔍 Keyword and pattern-based file finding
- 🚀 First-match mode for quick lookups (`--first`)
- 🎯 Smart exclusions (.git, .venv, node_modules)
- 📝 Multiple exclusion patterns (repeatable)
- 🔄 Recursive search with symlink cycle detection

## Usage

```bash
fx ff [OPTIONS] KEYWORD
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|----------|-------------|
| `KEYWORD` | string | - | Keyword or pattern to search for (required) |
| `--first` | flag | False | Stop after first match (for speed) |
| `--include-ignored` | flag | False | Include default-ignored dirs (.git, .venv, node_modules) |
| `--exclude` | string | - | Exclude names or glob patterns (repeatable) |

## Examples

### Basic Usage

Find files containing "test" in their names:

```bash
fx ff test
```

Find configuration files:

```bash
fx ff config
```

Find all Python files (using partial match):

```bash
fx ff .py
```

### First Match Only

Return only the first match (faster):

```bash
fx ff test --first
```

Find first config file:

```bash
fx ff config --first
```

### Including Ignored Directories

Search in .git, .venv, node_modules:

```bash
fx ff test --include-ignored
```

### Excluding Directories and Patterns

Exclude specific directories:

```bash
fx ff test --exclude build --exclude cache
```

Exclude glob patterns:

```bash
fx ff api --exclude "*.pyc" --exclude "*.log"
```

Combine multiple exclusions:

```bash
fx ff src --exclude build --exclude cache --exclude "*.pyc"
```

### Real-World Scenarios

#### Scenario 1: Development Workflow

Find TODO markers in code:

```bash
fx ff TODO --exclude node_modules --exclude .git
```

Find test files:

```bash
fx ff test --exclude coverage --exclude .nyc_output
```

Find configuration files:

```bash
fx ff config --exclude backup
```

#### Scenario 2: Project Cleanup

Find backup files:

```bash
fx ff .bak
```

Find temporary files:

```bash
fx ff .tmp
```

Find log files:

```bash
fx ff .log --exclude archive
```

#### Scenario 3: Debugging

Find error-related files:

```bash
fx ff error
```

Find debug files:

```bash
fx ff debug
```

Find exception files:

```bash
fx ff exception
```

#### Scenario 4: Dependency Management

Find jQuery files:

```bash
fx ff jquery --exclude node_modules --exclude dist
```

Find React components:

```bash
fx ff Component --exclude node_modules --exclude build
```

Find library files:

```bash
fx ff lodash --exclude node_modules
```

#### Scenario 5: Configuration Discovery

Find all config files:

```bash
fx ff config --include-ignored
```

Find environment files:

```bash
fx ff .env --exclude node_modules
```

Find setting files:

```bash
fx ff settings --exclude backup
```

#### Scenario 6: Code Navigation

Find API files:

```bash
fx ff api --exclude build --exclude cache --exclude "*.pyc"
```

Find service files:

```bash
fx ff service --exclude node_modules --exclude dist
```

Find model files:

```bash
fx ff model --exclude node_modules --exclude __pycache__
```

#### Scenario 7: Test Discovery

Find unit tests:

```bash
fx ff "*unit*test*" --exclude node_modules --exclude __pycache__
```

Find integration tests:

```bash
fx ff "*integration*test*" --exclude node_modules
```

Find e2e tests:

```bash
fx ff "*e2e*test*" --exclude node_modules
```

#### Scenario 8: Code Review

Find implementation files:

```bash
fx ff impl --exclude test --exclude node_modules
```

Find interface files:

```bash
fx ff interface --exclude test --exclude node_modules
```

Find abstract files:

```bash
fx ff abstract --exclude test --exclude node_modules
```

## Tips and Tricks

### Combining with Other Commands

```bash
# Find and grep file contents
fx ff api | xargs grep -l "endpoint"

# Find and analyze sizes
fx ff .log | xargs fx size

# Find and filter
fx ff .py | xargs fx filter py --sort-by modified
```

### Finding by Extension

```bash
# Find all Python files
fx ff .py

# Find all JavaScript files
fx ff .js

# Find all markdown files
fx ff .md
```

### Quick File Lookup

```bash
# Find file and open it
vim $(fx ff my_file --first)

# Find file and display it
cat $(fx ff README --first)
```

### Complex Filtering

```bash
# Find "api" files but exclude multiple directories
fx ff api --exclude build --exclude cache --exclude "*.pyc" --exclude "*.log"

# Find test files excluding coverage reports
fx ff test --exclude coverage --exclude .nyc_output --exclude "*spec*"
```

### Pipeline Integration

```bash
# Chain multiple searches
fx ff config | xargs grep -l "database"

# Find and count
fx ff .py | wc -l

# Find and backup
fx ff important.txt | xargs fx backup
```

## Performance Tips

### Speed Up Searches

```bash
# Use --first for quick lookups
fx ff my_file --first

# Exclude large directories
fx ff api --exclude node_modules --exclude build

# Use specific keywords instead of broad patterns
fx ff "api_v1" --exclude "*.pyc"
```

### Optimize for Large Projects

```bash
# Exclude multiple heavy directories
fx ff test --exclude node_modules --exclude .venv --exclude dist --exclude build

# Use extension matching for faster results
fx ff .py --exclude __pycache__
```

## Common Issues

### Too Many Results

```bash
# Use --first for quick lookup
fx ff config --first

# Add exclusions
fx ff test --exclude node_modules --exclude build --exclude cache
```

### No Results Found

```bash
# Check spelling
fx ff configuration  # instead of config

# Try partial matches
fx ff .py  # instead of python

# Include ignored directories
fx ff my_file --include-ignored
```

### Slow Performance

```bash
# Exclude heavy directories
fx ff api --exclude node_modules --exclude .venv --exclude dist

# Use --first for quick match
fx ff my_file --first

# Be more specific with keyword
fx ff "api_v1_user" --exclude "*.pyc"
```

## See Also

- [`fx fff`](fff.md) - Find first file matching keyword
- [`fx filter`](filter.md) - Filter files by extension
- [`fx files`](files.md) - Count files in directories
- [`fx size`](size.md) - Analyze file/directory sizes

---

**Need more examples?** See [Use Cases](../use-cases/daily-workflow.md) for real-world workflows.
