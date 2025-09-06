# FX Root - Cross-Platform Directory Switching Setup

## Problem
`fx root` only displays the Git root directory path but cannot actually change to it because child processes cannot modify the parent shell's working directory.

## Solution
Create shell functions that wrap `fx root --cd` to enable actual directory switching.

## Quick Setup

### Automatic Installation (Recommended)

```bash
# Make script executable and run
chmod +x scripts/setup-fx-root.sh
./scripts/setup-fx-root.sh
```

The script will:
1. Detect your shell and OS
2. Add the `fxroot` function to your shell configuration
3. Create convenient aliases (`cdr`, `cdroot`)

### Manual Installation

Choose your shell below and add the corresponding code to your configuration file:

#### Bash (~/.bashrc or ~/.bash_profile on macOS)

```bash
# FX Root - Jump to Git project root
fxroot() {
    local root_dir
    root_dir=$(fx root --cd 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$root_dir" ]; then
        cd "$root_dir"
        echo "Changed to Git root: $root_dir"
    else
        echo "No Git repository found in current directory or parent directories" >&2
        return 1
    fi
}

# Alias for convenience
alias cdr="fxroot"
alias cdroot="fxroot"
```

#### Zsh (~/.zshrc)

```zsh
# FX Root - Jump to Git project root
fxroot() {
    local root_dir
    root_dir=$(fx root --cd 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$root_dir" ]; then
        cd "$root_dir"
        echo "Changed to Git root: $root_dir"
    else
        echo "No Git repository found in current directory or parent directories" >&2
        return 1
    fi
}

# Alias for convenience
alias cdr="fxroot"
alias cdroot="fxroot"
```

#### Fish (~/.config/fish/functions/fxroot.fish)

```fish
# FX Root - Jump to Git project root
function fxroot
    set -l root_dir (fx root --cd 2>/dev/null)
    if test $status -eq 0; and test -n "$root_dir"
        cd "$root_dir"
        echo "Changed to Git root: $root_dir"
    else
        echo "No Git repository found in current directory or parent directories" >&2
        return 1
    end
end
```

Add aliases to ~/.config/fish/config.fish:
```fish
# FX Root aliases
alias cdr="fxroot"
alias cdroot="fxroot"
```

#### PowerShell (Windows)

Add to your PowerShell profile (`$PROFILE`):

```powershell
# FX Root - Jump to Git project root
function fxroot {
    $rootDir = fx root --cd 2>$null
    if ($LASTEXITCODE -eq 0 -and $rootDir) {
        Set-Location $rootDir
        Write-Host "Changed to Git root: $rootDir"
    } else {
        Write-Error "No Git repository found in current directory or parent directories"
    }
}

# Aliases for convenience
Set-Alias -Name cdr -Value fxroot
Set-Alias -Name cdroot -Value fxroot
```

To find your PowerShell profile location:
```powershell
echo $PROFILE
```

#### Windows Command Prompt (cmd.exe)

Create a batch file `fxroot.bat` in a directory in your PATH:

```batch
@echo off
for /f "delims=" %%i in ('fx root --cd 2^>nul') do set ROOT_DIR=%%i
if "%ROOT_DIR%"=="" (
    echo No Git repository found in current directory or parent directories >&2
    exit /b 1
) else (
    cd /d "%ROOT_DIR%"
    echo Changed to Git root: %ROOT_DIR%
)
```

## Usage

After installation and reloading your shell:

```bash
# Navigate to any subdirectory in a Git project
$ cd deep/nested/project/directory

# Jump to Git root using any of these commands
$ fxroot
Changed to Git root: /Users/username/projects/my-project

# Or use the shorter aliases
$ cdr
Changed to Git root: /Users/username/projects/my-project

$ cdroot
Changed to Git root: /Users/username/projects/my-project
```

## Features

- **Cross-platform**: Works on macOS, Linux, and Windows
- **Multi-shell support**: Bash, Zsh, Fish, PowerShell, and CMD
- **Error handling**: Graceful failure when not in a Git repository
- **Convenient aliases**: `cdr` and `cdroot` for quick access
- **Visual feedback**: Shows the directory you've changed to

## Troubleshooting

### Command not found: fx
Make sure fx-bin is installed and in your PATH:
```bash
pip install fx-bin
# or
pipx install fx-bin
```

### Function not working after installation
1. Reload your shell configuration:
   - Bash: `source ~/.bashrc`
   - Zsh: `source ~/.zshrc`
   - Fish: `source ~/.config/fish/config.fish`
   - PowerShell: `. $PROFILE`
2. Or simply restart your terminal

### Permission denied on setup script
```bash
chmod +x scripts/setup-fx-root.sh
```

## Comparison with Other Tools

| Tool | Command | Cross-Platform | Setup Required |
|------|---------|---------------|----------------|
| fxroot | `fxroot` or `cdr` | ✅ Yes | Shell function |
| git | `cd $(git rev-parse --show-toplevel)` | ✅ Yes | None |
| z/autojump | `z projectname` | ✅ Yes | Separate tool |
| cdgit | `cdgit` | ❌ Unix only | Separate tool |

## Why Use fxroot?

1. **Simpler syntax**: Just type `cdr` instead of complex git commands
2. **Better error handling**: Clear messages when not in a Git repo
3. **Integrated with fx-bin**: Part of your existing fx toolkit
4. **Cross-platform**: Same command works everywhere
5. **No dependencies**: Uses existing fx-bin installation