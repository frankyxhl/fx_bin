#!/usr/bin/env bash

# Test script for fxroot functionality

echo "Testing fx root command..."
echo "============================"
echo ""

# Test 1: Check if fx root works
echo "Test 1: Basic fx root command"
fx root
if [ $? -eq 0 ]; then
    echo "✓ fx root works"
else
    echo "✗ fx root failed"
fi
echo ""

# Test 2: Check if fx root --cd works
echo "Test 2: fx root --cd command"
ROOT_DIR=$(fx root --cd)
if [ $? -eq 0 ] && [ -n "$ROOT_DIR" ]; then
    echo "✓ fx root --cd returns: $ROOT_DIR"
else
    echo "✗ fx root --cd failed"
fi
echo ""

# Test 3: Test the function directly (if sourced)
echo "Test 3: Testing shell function (manual test required)"
echo "To test the fxroot function:"
echo "1. Run: source ~/.bashrc (or ~/.zshrc for zsh)"
echo "2. Navigate to a subdirectory: cd fx_bin"
echo "3. Run: fxroot"
echo "4. You should be back at: $(fx root --cd)"
echo ""

# Test 4: Check if in Git repository
echo "Test 4: Git repository check"
if [ -d ".git" ]; then
    echo "✓ Current directory is a Git repository"
else
    # Try to find git root
    FOUND_ROOT=$(fx root --cd 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "✓ Git root found at: $FOUND_ROOT"
    else
        echo "✗ Not in a Git repository"
    fi
fi
echo ""

echo "============================"
echo "Testing complete!"
echo ""
echo "Next steps:"
echo "1. Run './scripts/setup-fx-root.sh' to install the shell function"
echo "2. Restart your terminal or source your shell config"
echo "3. Use 'fxroot', 'cdr', or 'cdroot' to jump to Git root"