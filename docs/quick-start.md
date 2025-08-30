# fx_bin Quick Start Guide

**Get up to speed in < 2 minutes**

## Current State (2025-08-30)

**Status**: v1.2.0 Release Ready ✅  
**Branch**: main  
**New Feature**: `fx filter` command with comprehensive TDD/BDD testing  

## Immediate Next Steps

```bash
# 1. Commit the v1.2.0 release
git add .
git commit -m "feat: fx filter command v1.2.0 release with comprehensive TDD/BDD testing

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"

# 2. Create release tag
git tag -a v1.2.0 -m "v1.2.0: File Filter Command Release"

# 3. Build and publish
poetry build
poetry publish
```

## Project Overview

**fx_bin** is a Python utility collection providing command-line tools for file operations. Current version 1.2.0 adds powerful file filtering capabilities.

### Available Commands
```bash
fx files       # Count files in directories
fx size        # Analyze file/directory sizes  
fx ff          # Find files by keyword
fx filter      # Filter files by extension (NEW in v1.2.0)
fx replace     # Replace text in files
fx json2excel  # Convert JSON to Excel
fx list        # List all available commands
```

## What's New in v1.2.0

### fx filter Command
```bash
fx filter txt                    # Find .txt files
fx filter "mp4,avi,mkv"         # Multiple extensions
fx filter py --sort-by modified # Sort by modification time
fx filter txt --format detailed # Show file metadata
fx filter py --no-recursive     # Current directory only
```

### Testing Excellence
- **23 Unit Tests**: Complete TDD implementation
- **25+ BDD Scenarios**: Business-readable specifications in Gherkin
- **Comprehensive Coverage**: Edge cases, security, performance testing

## Development Environment

### Quick Setup
```bash
# Install dependencies
poetry install --with dev,test

# Run all tests
poetry run pytest

# Run BDD tests
poetry run pytest tests/bdd/ -v

# Run linting
poetry run flake8 fx_bin
```

### Key Files
```
fx_bin/
├── filter.py              # NEW: Filter command implementation
├── cli.py                 # Updated: Filter command integration
└── ...                    # Existing utilities

tests/
├── test_filter.py         # NEW: 23 unit tests
├── bdd/                   # NEW: BDD test infrastructure
└── ...                    # Existing tests

features/
└── file_filter.feature    # NEW: Gherkin scenarios

docs/
├── sessions/              # NEW: Session documentation
├── changelog/             # Release documentation
└── bdd-testing-guide.md   # NEW: BDD documentation
```

## Recent Decisions & Context

### Architecture Decisions
- **TDD + BDD Approach**: Comprehensive testing strategy provides confidence
- **Unified CLI**: Single `fx` command with subcommands for consistency
- **Click Framework**: Modern CLI framework for all commands

### Testing Strategy
- **Unit Tests First**: TDD methodology for core functionality
- **BDD for Business Logic**: Gherkin scenarios for stakeholder communication
- **Comprehensive Coverage**: Multiple testing layers for reliability

### Documentation Standards
- **Session Documentation**: Preserve context between sessions
- **Living Documentation**: BDD scenarios as executable specifications
- **Comprehensive Changelogs**: Detailed release notes for users

## Troubleshooting

### Common Issues
```bash
# Test failures
poetry run pytest tests/test_filter.py -v

# BDD test issues  
poetry run pytest tests/bdd/ -v --tb=short

# Linting errors
poetry run flake8 fx_bin/filter.py

# Module import issues
pip install -e .
```

### Environment Check
```bash
# Verify installation
fx --help
fx list

# Test new filter command
fx filter py --format count

# Check version
python -c "import fx_bin; print(fx_bin.__version__)"
```

## Context for Development

### Last Session (2025-08-30)
- **Completed**: v1.2.0 release documentation
- **Created**: Session docs, changelog, project status
- **Updated**: HISTORY.rst with comprehensive release notes
- **Ready**: For git tag, build, and PyPI publish

### Testing Infrastructure
- **Established**: BDD testing patterns with pytest-bdd
- **Documented**: Comprehensive testing guide available
- **Proven**: 23 unit tests + 25+ BDD scenarios all passing

### Next Development Focus
- **Performance**: Large directory optimization
- **Features**: Glob patterns, multiple directory support
- **Integration**: Better command pipeline integration

## Emergency Recovery

If you need to quickly understand the current state:

```bash
# Check current status
git status
git log --oneline -5

# Verify tests
poetry run pytest --co -q | wc -l  # Count tests
poetry run pytest -x              # Run until first failure

# Quick functionality check
fx filter txt --format count      # Should work without errors
```

**Documentation Location**: All context preserved in `docs/sessions/` and `docs/changelog/` directories.