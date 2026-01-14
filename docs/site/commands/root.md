# Command: fx root

Find Git project root directory for navigation and script integration.

## Overview

`fx root` finds the root directory of a Git repository by searching upward from the current directory. It's perfect for navigation, script integration, and ensuring operations run from the project root.

**Key Features:**
- 🎯 Finds .git directory by searching upward
- 📏 Provides path-only output for shell integration
- 🔄 Useful for shell aliases and scripts
- ⚡ Fast directory traversal
- 🔍 Handles non-Git directories gracefully

## Usage

```bash
fx root [OPTIONS]
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|----------|-------------|
| `--cd` / `-c` | flag | False | Output path suitable for cd command (no extra text) |

## Examples

### Basic Usage

Show Git project root with description:

```bash
fx root
```

**Output:**
```
Git project root: /home/user/projects/my_project
```

### Path-Only Output

Output just the path for shell usage:

```bash
fx root --cd
```

**Output:**
```
/home/user/projects/my_project
```

### Shell Integration

Change to project root:

```bash
cd "$(fx root --cd)"
```

### Real-World Scenarios

#### Scenario 1: Script Integration

Ensure script runs from project root:

```bash
#!/bin/bash
# Deployment script

# Navigate to project root
PROJECT_ROOT=$(fx root --cd)
if [ $? -ne 0 ]; then
  echo "Error: Not in a Git repository"
  exit 1
fi

cd "$PROJECT_ROOT"

# Perform operations from root
pytest
make build
```

#### Scenario 2: Git Operations

Run Git operations from project root:

```bash
# Always run from root
cd "$(fx root --cd)" && git status
cd "$(fx root --cd)" && git pull
cd "$(fx root --cd)" && git log --oneline -10
```

#### Scenario 3: Build Scripts

Build from project root:

```bash
#!/bin/bash
# Build script

# Navigate to project root
cd "$(fx root --cd)"

# Clean and build
make clean
make build
make test
```

#### Scenario 4: Environment Configuration

Load environment files from project root:

```bash
# Load .env from project root
cd "$(fx root --cd)" && source .env

# Or export from project root
export $(cd "$(fx root --cd)" && cat .env | xargs)
```

#### Scenario 5: Project Statistics

Analyze project from root:

```bash
#!/bin/bash
# Project stats script

ROOT=$(fx root --cd)

# Count Python files
echo "Python files: $(fx files "$ROOT" --pattern "*.py" --recursive | tail -1 | awk '{print $1}')"

# Count total lines of code
echo "Total LOC: $(find "$ROOT" -name "*.py" -exec wc -l {} + | tail -1)"
```

## Tips and Tricks

### Shell Aliases

Create aliases in `.bashrc` or `.zshrc`:

```bash
# Navigate to project root
alias gr='cd "$(fx root --cd)"'

# Show project root
alias root='fx root'

# Run command from project root
alias grun='cd "$(fx root --cd)" && '

# Examples
gr                 # cd to project root
root               # show project root
grun pytest         # run pytest from project root
```

### Shell Functions

Create reusable functions:

```bash
# .bashrc or .zshrc

# Run command from project root
run_from_root() {
  local root=$(fx root --cd)
  if [ $? -ne 0 ]; then
    echo "Error: Not in a Git repository"
    return 1
  fi
  (cd "$root" && "$@")
}

# Usage examples
run_from_root pytest
run_from_root npm test
run_from_root make build
```

### Error Handling in Scripts

```bash
#!/bin/bash
# Safe project root navigation

# Get project root with error handling
PROJECT_ROOT=$(fx root --cd 2>/dev/null)

if [ -z "$PROJECT_ROOT" ]; then
  echo "Error: Not in a Git repository"
  echo "Please run this command from within a Git repository"
  exit 1
fi

echo "Project root: $PROJECT_ROOT"
cd "$PROJECT_ROOT"

# Continue with operations...
```

### Combining with Other Commands

```bash
# Find files from project root
fx root --cd | xargs fx ff README

# Count files from project root
fx root --cd | xargs fx files --recursive

# Analyze sizes from project root
fx root --cd | xargs fx size --recursive
```

### Relative Path Resolution

```bash
# Get absolute path to file from root
ROOT=$(fx root --cd)
FILE="$ROOT/src/main.py"

# Use absolute path
cat "$FILE"
```

## Integration Examples

### Git Aliases

Add to `.gitconfig`:

```ini
[alias]
    # Run fx root from git
    root = "!fx root"

    # Show files from root
    files = "!fx root --cd | xargs fx files --recursive"

    # Show git root
    show-root = "!fx root"
```

### IDE Integration

**VS Code**:
```bash
# Open VS Code from project root
fx root --cd | xargs code .
```

**JetBrains IDEs**:
```bash
# Open IntelliJ from project root
fx root --cd | xargs idea .
```

**Vim/Neovim**:
```bash
# Edit file relative to project root
function v {
  local root=$(fx root --cd)
  if [ -z "$root" ]; then
    echo "Not in a Git repository"
    return 1
  fi
  vim "$root/$1"
}

# Usage: v src/main.py
```

### Makefile Integration

```makefile
# Makefile that always runs from project root

ROOT := $(shell fx root --cd)

.PHONY: test build clean

test:
	cd $(ROOT) && pytest

build:
	cd $(ROOT) && make build

clean:
	cd $(ROOT) && make clean
```

## Behavior Notes

### Search Direction

`fx root` searches **upward** from the current directory:

```bash
# In: /home/user/projects/my_project/src/
fx root
# Returns: /home/user/projects/my_project

# In: /home/user/projects/my_project/src/subdir/
fx root
# Returns: /home/user/projects/my_project
```

### .git Directory Detection

Finds the first parent directory containing a `.git` folder:

```bash
# Directory structure:
# /home/user/projects/my_project/
# ├── .git/
# ├── src/
# │   └── subdir/
# └── README.md

# In any directory under my_project, returns the root
```

### Non-Git Directories

If not in a Git repository:

```bash
# With --cd flag (silent exit, exit code 1)
fx root --cd
# Returns: nothing, exit code 1

# Without --cd flag (error message)
fx root
# Returns: "Error: No git repository found in current directory or parent directories"
```

### Multiple Git Repositories

Finds the nearest `.git` directory:

```bash
# Structure:
# /home/user/projects/
# ├── outer_repo/
# │   ├── .git/
# │   └── inner_repo/
# │       └── .git/

# In outer_repo/inner_repo/, returns inner_repo
cd outer_repo/inner_repo
fx root
# Returns: /home/user/projects/outer_repo/inner_repo
```

## Performance Notes

- **Speed**: Fast directory traversal (stops at first .git found)
- **Symlinks**: Does not follow symlinks (uses real path)
- **Permission errors**: Skips directories without read permission
- **Cache**: No caching (always reads current state)

## Common Issues

### Not in a Git Repository

```bash
# Error message
fx root
# Error: No git repository found in current directory or parent directories

# Solution: Initialize git or navigate to a Git repository
git init
# Or
cd /path/to/git/repository
```

### Permission Denied

```bash
# If parent directories are not readable
fx root
# Error: Permission denied

# Solution: Check permissions
ls -la /path/to/directory

# Or use sudo (not recommended)
sudo fx root
```

### Wrong Repository Detected

If in nested Git repository:

```bash
# In inner repo, returns inner repo root
cd outer/inner
fx root
# Returns: /path/to/outer/inner

# To get outer repo root, navigate up
cd ../
fx root
# Returns: /path/to/outer
```

### Script Exit Code

```bash
# In scripts, check exit code
if fx root --cd 2>/dev/null; then
  echo "In Git repository"
else
  echo "Not in Git repository"
  exit 1
fi
```

## Best Practices

### Use in Project Scripts

```bash
#!/bin/bash
# Always determine project root at script start
PROJECT_ROOT=$(fx root --cd)

# Use PROJECT_ROOT variable throughout script
cd "$PROJECT_ROOT"

# Perform operations
pytest
make build
```

### Handle Errors Gracefully

```bash
#!/bin/bash
# Always check for Git repository
PROJECT_ROOT=$(fx root --cd 2>/dev/null)

if [ -z "$PROJECT_ROOT" ]; then
  echo "Error: This script must be run from within a Git repository"
  exit 1
fi

# Continue with operations
cd "$PROJECT_ROOT"
```

### Create Shell Aliases

```bash
# .bashrc or .zshrc

# Quick navigation
alias gr='cd "$(fx root --cd)"'

# Quick info
alias root='fx root'

# Command from root
alias grun='cd "$(fx root --cd)" && '
```

### Use in CI/CD Pipelines

```yaml
# GitHub Actions example
- name: Run tests from project root
  run: |
    cd "$(fx root --cd)"
    pytest

- name: Build from project root
  run: |
    cd "$(fx root --cd)"
    make build
```

## See Also

- [`fx today`](today.md) - Create daily workspace directory
- [`fx realpath`](../index.md) - Get absolute path of file or directory
- [`fx ff`](ff.md) - Find files by keyword

---

**Navigate with ease!** Use `fx root` to always know where you are in your Git project. 🎯
