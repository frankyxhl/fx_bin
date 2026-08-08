# Command: fx realpath (fx rp)

Get the absolute path of a file or directory.

## Overview

`fx realpath` resolves relative paths, symlinks, and `~` to the canonical
absolute path. The path must exist. `fx rp` is a shorter alias for the same
command.

**Key Features:**

- 📍 Canonical absolute path (symlinks resolved)
- 🏠 `~` expansion
- ⚡ `fx rp` short alias
- ❌ Fails clearly when the path does not exist

## Usage

```bash
fx realpath [PATH]
fx rp [PATH]
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `PATH` | string | `.` | File or directory to resolve (must exist) |

## Examples

```bash
# Current directory
fx realpath .

# Relative path
fx rp ../foo

# Home directory
fx rp ~/Downloads

# Use in scripts
open "$(fx rp ./build/report.html)"
```

## See Also

- [`fx root`](root.md) - Find Git project root
- [`fx ff`](ff.md) - Find files by keyword (prints absolute paths)

---

**Need more examples?** See [Use Cases](../use-cases/daily-workflow.md) for real-world workflows.
