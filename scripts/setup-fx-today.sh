#!/usr/bin/env bash

# FX Today Setup Script - Adds shell integration for fx today command
# Supports: Bash, Zsh, Fish on macOS, Linux, Windows (Git Bash/WSL)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "FX Today Directory Switcher Setup"
echo "========================================="
echo ""

# Detect shell
detect_shell() {
    if [ -n "$BASH_VERSION" ]; then
        echo "bash"
    elif [ -n "$ZSH_VERSION" ]; then
        echo "zsh"
    elif [ -n "$FISH_VERSION" ]; then
        echo "fish"
    else
        # Try to detect from parent process
        parent_shell=$(ps -p $PPID -o comm= 2>/dev/null | tr -d ' ')
        case "$parent_shell" in
            *bash*) echo "bash" ;;
            *zsh*) echo "zsh" ;;
            *fish*) echo "fish" ;;
            *) echo "unknown" ;;
        esac
    fi
}

# Detect OS
detect_os() {
    case "$OSTYPE" in
        linux*)   echo "linux" ;;
        darwin*)  echo "macos" ;;
        msys*)    echo "windows" ;;
        cygwin*)  echo "windows" ;;
        win32*)   echo "windows" ;;
        *)        echo "unknown" ;;
    esac
}

SHELL_TYPE=$(detect_shell)
OS_TYPE=$(detect_os)

echo "Detected Shell: $SHELL_TYPE"
echo "Detected OS: $OS_TYPE"
echo ""

# Enhanced fx() function for bash/zsh that handles both root and today
BASH_ZSH_FUNCTION='# FX Enhanced - Makes fx root and fx today change directories
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
            echo "📅 Changed to today'\''s workspace: $today_dir"
        else
            echo "❌ Could not create/navigate to today'\''s workspace" >&2
            return 1
        fi
    else
        # All other cases: use original fx command
        command fx "$@"
    fi
}

# Convenient aliases
alias fr="fx root"       # Quick jump to Git root
alias ft="fx today"       # Quick jump to today'\''s workspace
alias cdr="fx root"       # Alternative for Git root
alias cdt="fx today"      # Alternative for today'\''s workspace'

# Fish function
FISH_FUNCTION='# FX Enhanced for Fish - Makes fx root and fx today change directories
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
            echo "📅 Changed to today'\''s workspace: $today_dir"
        else
            echo "❌ Could not create/navigate to today'\''s workspace" >&2
            return 1
        end
    else
        command fx $argv
    end
end

# Aliases
alias fr="fx root"
alias ft="fx today"
alias cdr="fx root"
alias cdt="fx today"'

# PowerShell function
POWERSHELL_FUNCTION='# FX Enhanced for PowerShell - Makes fx root and fx today change directories
function fx {
    param([string[]]$Arguments)
    
    if ($Arguments[0] -eq "root" -and $Arguments.Count -eq 1) {
        $rootDir = & fx.exe root --cd 2>$null
        if ($LASTEXITCODE -eq 0 -and $rootDir) {
            Set-Location $rootDir
            Write-Host "📍 Changed to Git root: $rootDir"
        } else {
            Write-Error "No Git repository found"
        }
    } elseif ($Arguments[0] -eq "today" -and $Arguments.Count -eq 1) {
        $todayDir = & fx.exe today --cd 2>$null
        if ($LASTEXITCODE -eq 0 -and $todayDir) {
            Set-Location $todayDir
            Write-Host "📅 Changed to today'\''s workspace: $todayDir"
        } else {
            Write-Error "Could not create/navigate to today'\''s workspace"
        }
    } else {
        & fx.exe @Arguments
    }
}

# Aliases
Set-Alias -Name fr -Value "fx root"
Set-Alias -Name ft -Value "fx today"
Set-Alias -Name cdr -Value "fx root"
Set-Alias -Name cdt -Value "fx today"'

# Install for bash
install_bash() {
    local rc_file="$HOME/.bashrc"
    
    # Check if using .bash_profile on macOS
    if [ "$OS_TYPE" = "macos" ] && [ -f "$HOME/.bash_profile" ]; then
        rc_file="$HOME/.bash_profile"
    fi
    
    echo "Installing for Bash in $rc_file..."
    
    # Check if fx function already exists
    if grep -q "fx()" "$rc_file" 2>/dev/null; then
        echo -e "${YELLOW}fx function already exists in $rc_file${NC}"
        echo "Please manually update it to include today command support"
        echo "Or remove the existing function and re-run this script"
        return
    fi
    
    # Add function
    echo "" >> "$rc_file"
    echo "$BASH_ZSH_FUNCTION" >> "$rc_file"
    
    echo -e "${GREEN}✓ Installed for Bash${NC}"
    echo "Run 'source $rc_file' or restart your terminal to use fx today"
}

# Install for zsh
install_zsh() {
    local rc_file="$HOME/.zshrc"
    
    # Check if it's a symlink to dotfiles
    if [ -L "$rc_file" ]; then
        local target=$(readlink "$rc_file")
        echo -e "${YELLOW}Note: $rc_file is a symlink to $target${NC}"
        echo "The function will be added to: $target"
        rc_file="$target"
    fi
    
    echo "Installing for Zsh..."
    
    # Check if fx function already exists
    if grep -q "fx()" "$rc_file" 2>/dev/null; then
        echo -e "${YELLOW}fx function already exists in $rc_file${NC}"
        echo ""
        echo "To add today command support, update your existing fx() function to include:"
        echo '    elif [[ "$1" == "today" ]] && [[ -z "$2" ]]; then'
        echo '        local today_dir'
        echo '        today_dir=$(command fx today --cd 2>/dev/null)'
        echo '        if [ $? -eq 0 ] && [ -n "$today_dir" ]; then'
        echo '            cd "$today_dir"'
        echo '            echo "📅 Changed to today'\''s workspace: $today_dir"'
        echo '        else'
        echo '            echo "❌ Could not create/navigate to today'\''s workspace" >&2'
        echo '            return 1'
        echo '        fi'
        echo ""
        echo "And add these aliases:"
        echo '    alias ft="fx today"'
        echo '    alias cdt="fx today"'
        return
    fi
    
    # Add function
    echo "" >> "$rc_file"
    echo "$BASH_ZSH_FUNCTION" >> "$rc_file"
    
    echo -e "${GREEN}✓ Installed for Zsh${NC}"
    echo "Run 'source $rc_file' or restart your terminal to use fx today"
}

# Install for fish
install_fish() {
    local fish_dir="$HOME/.config/fish"
    local functions_dir="$fish_dir/functions"
    
    # Create directories if they don't exist
    mkdir -p "$functions_dir"
    
    echo "Installing for Fish..."
    
    # Create function file
    echo "$FISH_FUNCTION" > "$functions_dir/fx.fish"
    
    # Add aliases to config if not present
    local config_file="$fish_dir/config.fish"
    if ! grep -q "alias ft=" "$config_file" 2>/dev/null; then
        echo "" >> "$config_file"
        echo "# FX aliases" >> "$config_file"
        echo 'alias ft="fx today"' >> "$config_file"
        echo 'alias cdt="fx today"' >> "$config_file"
    fi
    
    echo -e "${GREEN}✓ Installed for Fish${NC}"
    echo "Restart your terminal or run 'source $config_file' to use fx today"
}

# Install for PowerShell
install_powershell() {
    local profile_file="$HOME/Documents/WindowsPowerShell/Microsoft.PowerShell_profile.ps1"
    
    # For PowerShell Core
    if [ -d "$HOME/Documents/PowerShell" ]; then
        profile_file="$HOME/Documents/PowerShell/Microsoft.PowerShell_profile.ps1"
    fi
    
    echo "Installing for PowerShell..."
    
    # Create profile directory if it doesn't exist
    mkdir -p "$(dirname "$profile_file")"
    
    # Check if fx function already exists
    if grep -q "function fx" "$profile_file" 2>/dev/null; then
        echo -e "${YELLOW}fx function already exists in PowerShell profile${NC}"
        echo "Please manually update $profile_file to include today command support"
    else
        echo "" >> "$profile_file"
        echo "$POWERSHELL_FUNCTION" >> "$profile_file"
        echo -e "${GREEN}✓ Installed for PowerShell${NC}"
        echo "Restart PowerShell to use fx today"
    fi
}

# Main installation
main() {
    # Check if fx-bin is installed
    if ! command -v fx &> /dev/null; then
        echo -e "${RED}Error: fx-bin is not installed or not in PATH${NC}"
        echo "Please install fx-bin first: pip install fx-bin"
        exit 1
    fi
    
    echo "Choose installation option:"
    echo "1) Install for current shell ($SHELL_TYPE)"
    echo "2) Install for all supported shells"
    echo "3) Install for specific shell"
    echo ""
    read -p "Enter choice (1-3): " choice
    
    case $choice in
        1)
            case $SHELL_TYPE in
                bash) install_bash ;;
                zsh) install_zsh ;;
                fish) install_fish ;;
                *)
                    echo -e "${RED}Unknown shell: $SHELL_TYPE${NC}"
                    echo "Please choose option 3 and select your shell manually"
                    exit 1
                    ;;
            esac
            ;;
        2)
            echo "Installing for all supported shells..."
            [ -f "$HOME/.bashrc" ] || [ -f "$HOME/.bash_profile" ] && install_bash
            [ -f "$HOME/.zshrc" ] && install_zsh
            [ -d "$HOME/.config/fish" ] && install_fish
            [ "$OS_TYPE" = "windows" ] && install_powershell
            ;;
        3)
            echo "Select shell:"
            echo "1) Bash"
            echo "2) Zsh"
            echo "3) Fish"
            echo "4) PowerShell (Windows)"
            read -p "Enter choice (1-4): " shell_choice
            
            case $shell_choice in
                1) install_bash ;;
                2) install_zsh ;;
                3) install_fish ;;
                4) install_powershell ;;
                *) echo -e "${RED}Invalid choice${NC}"; exit 1 ;;
            esac
            ;;
        *)
            echo -e "${RED}Invalid choice${NC}"
            exit 1
            ;;
    esac
    
    echo ""
    echo "========================================="
    echo -e "${GREEN}Installation complete!${NC}"
    echo ""
    echo "Available commands:"
    echo "  fx today  - Jump to today's workspace (~/Downloads/YYYYMMDD)"
    echo "  ft        - Alias for fx today"
    echo "  cdt       - Another alias for fx today"
    echo ""
    echo "Example usage:"
    echo "  $ fx today"
    echo "  📅 Changed to today's workspace: /Users/you/Downloads/20250906"
    echo ""
    echo "Custom options:"
    echo "  $ fx today --base ~/Projects    # Use different base directory"
    echo "  $ fx today --format %Y-%m-%d     # Use different date format"
    echo "========================================="
}

# Run main function
main