# Shell Integration

Integrate fx-bin commands into your shell environment for maximum productivity.

## Overview

Shell integration allows you to use fx-bin commands directly in your shell for faster navigation, quick operations, and efficient workflows. This guide covers aliases, functions, and environment configuration.

## Shell Aliases

### Bash (.bashrc)

```bash
# --- Navigation ---
# Navigate to project root
alias gr='cd "$(fx root --cd)"'

# Create daily workspace
alias ft='fx today --base ~/Projects'

# Navigate to today's workspace
alias ftcd='cd "$(fx today --base ~/Projects --cd)"'

# --- File Operations ---
# Find files
alias fff='fx ff'

# Find first file
alias fff='fx fff'

# Filter files
alias ffilter='fx filter'

# Count files
alias fcount='fx files'

# Analyze sizes
alias fsize='fx size'

# --- Utility ---
# Show project root
alias proot='fx root'

# Show today's workspace
alias today='fx today --base ~/Projects'
```

### Zsh (.zshrc)

```bash
# --- Navigation ---
# Navigate to project root
alias gr='cd "$(fx root --cd)"'

# Create daily workspace
alias ft='fx today --base ~/Projects'

# Navigate to today's workspace
alias ftcd='cd "$(fx today --base ~/Projects --cd)"'

# --- File Operations ---
# Find files
alias ffind='fx ff'

# Find first file
alias fff='fx fff'

# Filter files
alias ffilter='fx filter'

# Count files
alias fcount='fx files'

# Analyze sizes
alias fsize='fx size'

# --- Utility ---
# Show project root
alias proot='fx root'

# Show today's workspace
alias today='fx today --base ~/Projects'
```

### Fish (config.fish)

```fish
# --- Navigation ---
# Navigate to project root
alias gr "cd (fx root --cd)"

# Create daily workspace
alias ft "fx today --base ~/Projects"

# Navigate to today's workspace
alias ftcd "cd (fx today --base ~/Projects --cd)"

# --- File Operations ---
# Find files
alias ffind "fx ff"

# Find first file
alias fff "fx fff"

# Filter files
alias ffilter "fx filter"

# Count files
alias fcount "fx files"

# Analyze sizes
alias fsize "fx size"

# --- Utility ---
# Show project root
alias proot "fx root"

# Show today's workspace
alias today "fx today --base ~/Projects"
```

## Shell Functions

### Bash/Zsh Functions

```bash
# .bashrc or .zshrc

# --- Navigation Functions ---

# Run command from project root
run_from_root() {
  local root=$(fx root --cd 2>/dev/null)
  if [ -z "$root" ]; then
    echo "Error: Not in a Git repository"
    return 1
  fi
  (cd "$root" && "$@")
}

# Open file in first matching editor
edit_first() {
  local file=$(fx fff "$1" 2>/dev/null)
  if [ -z "$file" ]; then
    echo "Error: File '$1' not found"
    return 1
  fi
  vim "$file"
}

# --- File Operation Functions ---

# Count files by type
count_by_type() {
  local pattern=$1
  echo "Count of '$pattern' files:"
  fx files . --pattern "$pattern" --recursive | tail -1 | awk '{print "  " $1}'
}

# Find and show file size
find_size() {
  local keyword=$1
  local file=$(fx fff "$keyword" 2>/dev/null)
  if [ -n "$file" ]; then
    echo "$file: $(fx size "$file" | head -1)"
  fi
}

# Filter and sort files
filter_sorted() {
  local ext=$1
  fx filter "$ext" --sort-by modified --reverse --show-path
}

# --- Utility Functions ---

# Project summary
project_summary() {
  echo "=== Project Summary ==="

  # Project root
  local root=$(fx root --cd 2>/dev/null)
  echo "Project root: ${root:-$(pwd)}"

  # File counts
  echo ""
  echo "File counts:"
  count_by_type "*.py"
  count_by_type "*.js"
  count_by_type "*.md"

  # Recent files
  echo ""
  echo "Recent files (last 10):"
  filter_sorted "py,js,md" | head -10
}

# Quick stats
qstats() {
  echo "=== Quick Stats ==="
  echo "Python files: $(fx files . --pattern '*.py' --recursive | tail -1 | awk '{print $1}')"
  echo "JS files: $(fx files . --pattern '*.{js,jsx,ts,tsx}' --recursive | tail -1 | awk '{print $1}')"
  echo "Total files: $(fx files . --recursive | tail -1 | awk '{print $1}')"
}
```

### Fish Functions

```fish
# config.fish

# --- Navigation Functions ---

# Run command from project root
function run_from_root
  set -l root (fx root --cd 2>/dev/null)
  if test -z "$root"
    echo "Error: Not in a Git repository"
    return 1
  end
  cd $root; and $argv
end

# Open file in first matching editor
function edit_first
  set -l file (fx fff $argv[1] 2>/dev/null)
  if test -z "$file"
    echo "Error: File '$argv[1]' not found"
    return 1
  end
  vim $file
end

# --- File Operation Functions ---

# Count files by type
function count_by_type
  set -l pattern $argv[1]
  echo "Count of '$pattern' files:"
  fx files . --pattern $pattern --recursive | tail -1 | awk '{print "  " $1}'
end

# Find and show file size
function find_size
  set -l keyword $argv[1]
  set -l file (fx fff $keyword 2>/dev/null)
  if test -n "$file"
    echo "$file: "(fx size $file | head -1)
  end
end

# --- Utility Functions ---

# Project summary
function project_summary
  echo "=== Project Summary ==="

  # Project root
  set -l root (fx root --cd 2>/dev/null)
  echo "Project root: $root"

  # File counts
  echo ""
  echo "File counts:"
  count_by_type "*.py"
  count_by_type "*.js"
  count_by_type "*.md"
end
```

## Prompt Integration

### Bash Prompt

```bash
# .bashrc

# Show Git root in prompt
show_git_root() {
  local root=$(fx root --cd 2>/dev/null)
  if [ -n "$root" ]; then
    echo "[$(basename $root)]"
  fi
}

PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w$(show_git_root)\$ '
```

### Zsh Prompt

```zsh
# .zshrc

# Show Git root in prompt
show_git_root() {
  local root=$(fx root --cd 2>/dev/null)
  if [ -n "$root" ]; then
    echo "[$(basename $root)]"
  fi
}

PROMPT='%n@%m:%~$(show_git_root)%# '
```

## Key Bindings

### Vim Key Bindings

```vim
" .vimrc

" Navigate to project root
noremap <Leader>gr :cd <C-R>=system('fx root --cd')<CR><CR>

" Find and open file
noremap <Leader>ff :execute 'e ' . system('fx fff ' . input('Keyword: '))<CR>

" Find and grep file
noremap <Leader>fg :execute 'vimgrep ' . input('Search: ') . ' ' . system('fx fff ' . input('Keyword: '))<CR>
```

## Use Examples

### Daily Workflow

```bash
# Start daily workspace
ft

# Navigate to project
gr

# Check project stats
qstats

# Find recent files
filter_sorted "py,js"

# Count files
fcount
```

### Code Navigation

```bash
# Find and edit Python file
edit_first config

# Find first README
edit_first README

# Count Python files
count_by_type "*.py"
```

### Project Management

```bash
# Run tests from root
run_from_root pytest

# Run build from root
run_from_root make build

# Show project summary
project_summary

# Show git root
proot
```

## Related Commands

- [`fx root`](../commands/root.md) - Find Git project root
- [`fx today`](../commands/today.md) - Create daily workspace
- [`fx ff`](../commands/ff.md) - Find files by keyword

---

**Supercharge your shell!** Integrate fx-bin for maximum productivity. ⚡
