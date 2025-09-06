#!/usr/bin/env bash

# FX Root Wrapper - Makes 'fx root' actually change directory
# Add this to your shell configuration file

# For Bash/Zsh:
cat << 'BASH_ZSH_EOF'
# FX Wrapper - Makes 'fx root' change directory
fx() {
    if [[ "$1" == "root" ]]; then
        if [[ "$2" == "--cd" ]] || [[ "$2" == "-c" ]]; then
            # If user explicitly wants the path, use original command
            command fx "$@"
        elif [[ -z "$2" ]]; then
            # No additional arguments, do the directory change
            local root_dir
            root_dir=$(command fx root --cd 2>/dev/null)
            if [ $? -eq 0 ] && [ -n "$root_dir" ]; then
                cd "$root_dir"
                echo "Changed to Git root: $root_dir"
            else
                echo "No Git repository found in current directory or parent directories" >&2
                return 1
            fi
        else
            # Has other arguments, use original command
            command fx "$@"
        fi
    else
        # Not 'root' command, use original fx
        command fx "$@"
    fi
}

# Additional short aliases
alias fr="fx root"        # Even shorter: 'fr' to jump to root
alias cdr="fx root"       # Classic 'cdr' alias
alias cdroot="fx root"    # Descriptive alias
BASH_ZSH_EOF

echo ""
echo "For Fish shell:"
cat << 'FISH_EOF'
# FX Wrapper for Fish - Makes 'fx root' change directory
function fx
    if test "$argv[1]" = "root"
        if test -z "$argv[2]"
            set -l root_dir (command fx root --cd 2>/dev/null)
            if test $status -eq 0; and test -n "$root_dir"
                cd "$root_dir"
                echo "Changed to Git root: $root_dir"
            else
                echo "No Git repository found in current directory or parent directories" >&2
                return 1
            end
        else
            command fx $argv
        end
    else
        command fx $argv
    end
end

# Additional aliases
alias fr="fx root"
alias cdr="fx root"
alias cdroot="fx root"
FISH_EOF

echo ""
echo "For PowerShell:"
cat << 'POWERSHELL_EOF'
# FX Wrapper for PowerShell - Makes 'fx root' change directory
function fx {
    param([string[]]$Arguments)
    
    if ($Arguments[0] -eq "root" -and $Arguments.Count -eq 1) {
        $rootDir = & fx.exe root --cd 2>$null
        if ($LASTEXITCODE -eq 0 -and $rootDir) {
            Set-Location $rootDir
            Write-Host "Changed to Git root: $rootDir"
        } else {
            Write-Error "No Git repository found in current directory or parent directories"
        }
    } else {
        & fx.exe @Arguments
    }
}

# Additional aliases
Set-Alias -Name fr -Value "fx root"
Set-Alias -Name cdr -Value "fx root"
Set-Alias -Name cdroot -Value "fx root"
POWERSHELL_EOF