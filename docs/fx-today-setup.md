# FX Today - Daily Workspace Management Setup

## Overview
`fx today` creates and navigates to a date-organized workspace directory, typically `~/Downloads/YYYYMMDD`, helping you organize daily work files.

## Quick Setup

### Automatic Installation (Recommended)

```bash
# Make script executable and run
chmod +x scripts/setup-fx-today.sh
./scripts/setup-fx-today.sh
```

The script will:
1. Detect your shell and OS
2. Add/update the `fx()` function to support `fx today`
3. Create convenient aliases (`ft`, `cdt`)

### Manual Installation

Add the following to your shell configuration file:

#### Bash (~/.bashrc or ~/.bash_profile on macOS)

```bash
# FX Enhanced - Makes fx root and fx today change directories
fx() {
    if [[ "$1" == "root" ]] && [[ -z "$2" ]]; then
        # Special case: fx root with no arguments changes directory
        local root_dir
        root_dir=$(command fx root --cd 2>/dev/null)
        if [ $? -eq 0 ] && [ -n "$root_dir" ]; then
            cd "$root_dir"
            echo "📍 Changed to Git root: $root_dir"
        else
            echo "❌ No Git repository found" >&2
            return 1
        fi
    elif [[ "$1" == "today" ]] && [[ -z "$2" ]]; then
        # Special case: fx today with no arguments changes directory
        local today_dir
        today_dir=$(command fx today --cd 2>/dev/null)
        if [ $? -eq 0 ] && [ -n "$today_dir" ]; then
            cd "$today_dir"
            echo "📅 Changed to today's workspace: $today_dir"
        else
            echo "❌ Could not create/navigate to today's workspace" >&2
            return 1
        fi
    else
        # All other cases: use original fx command
        command fx "$@"
    fi
}

# Convenient aliases
alias ft="fx today"       # Quick jump to today's workspace
alias cdt="fx today"      # Alternative alias
```

#### Zsh (~/.zshrc)

Same as Bash configuration above.

#### Fish (~/.config/fish/functions/fx.fish)

```fish
# FX Enhanced for Fish - Makes fx root and fx today change directories
function fx
    if test "$argv[1]" = "root"; and test -z "$argv[2]"
        set -l root_dir (command fx root --cd 2>/dev/null)
        if test $status -eq 0; and test -n "$root_dir"
            cd "$root_dir"
            echo "📍 Changed to Git root: $root_dir"
        else
            echo "❌ No Git repository found" >&2
            return 1
        end
    else if test "$argv[1]" = "today"; and test -z "$argv[2]"
        set -l today_dir (command fx today --cd 2>/dev/null)
        if test $status -eq 0; and test -n "$today_dir"
            cd "$today_dir"
            echo "📅 Changed to today's workspace: $today_dir"
        else
            echo "❌ Could not create/navigate to today's workspace" >&2
            return 1
        end
    else
        command fx $argv
    end
end
```

Add aliases to ~/.config/fish/config.fish:
```fish
alias ft="fx today"
alias cdt="fx today"
```

#### PowerShell (Windows)

Add to your PowerShell profile (`$PROFILE`):

```powershell
# FX Enhanced for PowerShell
function fx {
    param([string[]]$Arguments)
    
    if ($Arguments[0] -eq "today" -and $Arguments.Count -eq 1) {
        $todayDir = & fx.exe today --cd 2>$null
        if ($LASTEXITCODE -eq 0 -and $todayDir) {
            Set-Location $todayDir
            Write-Host "📅 Changed to today's workspace: $todayDir"
        } else {
            Write-Error "Could not create/navigate to today's workspace"
        }
    } else {
        & fx.exe @Arguments
    }
}

# Aliases
Set-Alias -Name ft -Value "fx today"
Set-Alias -Name cdt -Value "fx today"
```

## Usage

After installation and reloading your shell:

### Basic Usage

```bash
# Navigate to today's workspace (creates if doesn't exist)
$ fx today
📅 Changed to today's workspace: /Users/username/Downloads/20250906

# Using aliases
$ ft
📅 Changed to today's workspace: /Users/username/Downloads/20250906

$ cdt
📅 Changed to today's workspace: /Users/username/Downloads/20250906
```

### Custom Base Directory

```bash
# Use Projects instead of Downloads
$ fx today --base ~/Projects
📅 Changed to today's workspace: /Users/username/Projects/20250906

# For shell integration (cd command)
$ cd "$(fx today --base ~/Projects --cd)"
```

### Custom Date Format

```bash
# Use dashes in date format
$ fx today --format %Y-%m-%d
📅 Changed to today's workspace: /Users/username/Downloads/2025-09-06

# Use underscores
$ fx today --format %Y_%m_%d
📅 Changed to today's workspace: /Users/username/Downloads/2025_09_06

# Month name format
$ fx today --format %B_%d_%Y
📅 Changed to today's workspace: /Users/username/Downloads/September_06_2025
```

### Other Options

```bash
# Verbose output
$ fx today --verbose
Creating directory: /Users/username/Downloads/20250906
Directory created successfully
Today's workspace: /Users/username/Downloads/20250906

# Dry run (see what would be created)
$ fx today --dry-run
Would create: /Users/username/Downloads/20250906

# Output path only (for scripting)
$ fx today --cd
/Users/username/Downloads/20250906

# Combine options
$ fx today --base ~/Work --format %Y/%m/%d --verbose
Creating directory: /Users/username/Work/2025/09/06
Directory created successfully
Today's workspace: /Users/username/Work/2025/09/06
```

## Features

- **Automatic Directory Creation**: Creates the workspace if it doesn't exist
- **Idempotent**: Safe to run multiple times - won't duplicate or fail
- **Cross-platform**: Works on macOS, Linux, and Windows
- **Multi-shell Support**: Bash, Zsh, Fish, PowerShell, and CMD
- **Customizable**: Base directory and date format can be configured
- **Shell Integration**: Actually changes your shell's directory
- **Convenient Aliases**: `ft` and `cdt` for quick access

## Configuration

You can set defaults by creating aliases with your preferred options:

```bash
# Always use Projects folder
alias today='fx today --base ~/Projects'

# Use a specific date format
alias today='fx today --format %Y-%m-%d'

# Combine multiple options
alias workday='fx today --base ~/Work --format %Y/%m/%d'
```

## Troubleshooting

### Command not found: fx
Make sure fx-bin is installed and in your PATH:
```bash
pip install fx-bin
# or
pipx install fx-bin
```

### Shell function not working after installation
1. Reload your shell configuration:
   - Bash: `source ~/.bashrc`
   - Zsh: `source ~/.zshrc`
   - Fish: `source ~/.config/fish/config.fish`
   - PowerShell: `. $PROFILE`
2. Or simply restart your terminal

### Permission denied creating directory
Check that you have write permissions to the base directory:
```bash
ls -la ~/Downloads
# If needed, fix permissions:
chmod u+w ~/Downloads
```

### Directory not created in expected location
Verify the base directory exists:
```bash
# Check if base directory exists
ls -la ~/Downloads

# Create if missing
mkdir -p ~/Downloads
```

## Integration with Other Commands

### Combine with fx root
```bash
# Go to project root
fx root

# Go to today's workspace
fx today

# Quick switching with aliases
cdr  # to project root
cdt  # to today's workspace
```

### Use in Scripts
```bash
#!/bin/bash
# Archive today's downloads
TODAY_DIR=$(fx today --cd)
tar -czf "$TODAY_DIR.tar.gz" "$TODAY_DIR"
```

### Cron Jobs
```bash
# Clean up old daily directories (keep last 30 days)
0 0 * * * find ~/Downloads -name "202*" -type d -mtime +30 -exec rm -rf {} \;
```

## Why Use fx today?

1. **Organization**: Automatically organizes daily work by date
2. **No More Clutter**: Downloads folder stays organized
3. **Easy Archive**: Each day's work is in its own folder
4. **Quick Access**: Jump to today's workspace instantly
5. **Consistency**: Same organization pattern across all your machines
6. **Flexibility**: Customize base directory and date format as needed

## Similar to Your Existing Workflow

This command is designed to match the common shell function pattern:
```bash
today() {
    local today_dir="${HOME}/Downloads/$(date +%Y%m%d)"
    [[ -d "$today_dir" ]] || mkdir -p "$today_dir"
    cd "$today_dir"
}
```

But with added benefits:
- Cross-platform support
- Error handling
- Customization options
- Integration with fx ecosystem