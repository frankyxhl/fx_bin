#!/usr/bin/env bash

# FX Root Setup Script - Cross-platform shell function installer
# Supports: Bash, Zsh, Fish on macOS, Linux, Windows (Git Bash/WSL)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "FX Root Directory Switcher Setup"
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

# Function definition for bash/zsh
BASH_ZSH_FUNCTION='# FX Root - Jump to Git project root
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
alias cdroot="fxroot"'

# Function definition for fish
FISH_FUNCTION='# FX Root - Jump to Git project root
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

# Aliases for convenience
alias cdr="fxroot"
alias cdroot="fxroot"'

# PowerShell function for Windows
POWERSHELL_FUNCTION='# FX Root - Jump to Git project root
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
Set-Alias -Name cdroot -Value fxroot'

# Install for bash
install_bash() {
    local rc_file="$HOME/.bashrc"
    
    # Check if using .bash_profile on macOS
    if [ "$OS_TYPE" = "macos" ] && [ -f "$HOME/.bash_profile" ]; then
        rc_file="$HOME/.bash_profile"
    fi
    
    echo "Installing for Bash in $rc_file..."
    
    # Check if already installed
    if grep -q "fxroot()" "$rc_file" 2>/dev/null; then
        echo -e "${YELLOW}fxroot function already exists in $rc_file${NC}"
        echo "Updating..."
        # Remove old version
        sed -i.bak '/# FX Root - Jump to Git project root/,/alias cdroot="fxroot"/d' "$rc_file"
    fi
    
    # Add function
    echo "" >> "$rc_file"
    echo "$BASH_ZSH_FUNCTION" >> "$rc_file"
    
    echo -e "${GREEN}✓ Installed for Bash${NC}"
    echo "Run 'source $rc_file' or restart your terminal to use fxroot"
}

# Install for zsh
install_zsh() {
    local rc_file="$HOME/.zshrc"
    
    echo "Installing for Zsh in $rc_file..."
    
    # Check if already installed
    if grep -q "fxroot()" "$rc_file" 2>/dev/null; then
        echo -e "${YELLOW}fxroot function already exists in $rc_file${NC}"
        echo "Updating..."
        # Remove old version
        sed -i.bak '/# FX Root - Jump to Git project root/,/alias cdroot="fxroot"/d' "$rc_file"
    fi
    
    # Add function
    echo "" >> "$rc_file"
    echo "$BASH_ZSH_FUNCTION" >> "$rc_file"
    
    echo -e "${GREEN}✓ Installed for Zsh${NC}"
    echo "Run 'source $rc_file' or restart your terminal to use fxroot"
}

# Install for fish
install_fish() {
    local fish_dir="$HOME/.config/fish"
    local functions_dir="$fish_dir/functions"
    
    # Create directories if they don't exist
    mkdir -p "$functions_dir"
    
    echo "Installing for Fish..."
    
    # Create function file
    echo "$FISH_FUNCTION" > "$functions_dir/fxroot.fish"
    
    # Add aliases to config
    local config_file="$fish_dir/config.fish"
    if ! grep -q "alias cdr=" "$config_file" 2>/dev/null; then
        echo "" >> "$config_file"
        echo "# FX Root aliases" >> "$config_file"
        echo 'alias cdr="fxroot"' >> "$config_file"
        echo 'alias cdroot="fxroot"' >> "$config_file"
    fi
    
    echo -e "${GREEN}✓ Installed for Fish${NC}"
    echo "Restart your terminal or run 'source $config_file' to use fxroot"
}

# Install for PowerShell (Windows)
install_powershell() {
    local profile_file="$HOME/Documents/WindowsPowerShell/Microsoft.PowerShell_profile.ps1"
    
    # For PowerShell Core
    if [ -d "$HOME/Documents/PowerShell" ]; then
        profile_file="$HOME/Documents/PowerShell/Microsoft.PowerShell_profile.ps1"
    fi
    
    echo "Installing for PowerShell..."
    
    # Create profile directory if it doesn't exist
    mkdir -p "$(dirname "$profile_file")"
    
    # Check if already installed
    if grep -q "function fxroot" "$profile_file" 2>/dev/null; then
        echo -e "${YELLOW}fxroot function already exists in PowerShell profile${NC}"
        echo "Please manually update $profile_file"
    else
        echo "" >> "$profile_file"
        echo "$POWERSHELL_FUNCTION" >> "$profile_file"
        echo -e "${GREEN}✓ Installed for PowerShell${NC}"
        echo "Restart PowerShell to use fxroot"
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
    echo "  fxroot   - Jump to Git project root"
    echo "  cdr      - Alias for fxroot"
    echo "  cdroot   - Alias for fxroot"
    echo ""
    echo "Example usage:"
    echo "  $ cd deep/nested/directory"
    echo "  $ fxroot"
    echo "  Changed to Git root: /path/to/project"
    echo "========================================="
}

# Run main function
main