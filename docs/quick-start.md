# fx_bin Quick Start Guide

**Get up to speed in < 2 minutes**

## Current State (2025-08-30)

**Status**: v1.3.2 Ready - All Tests Passing ✅  
**Branch**: main  
**Critical Fix**: BDD test isolation issues resolved - 301 tests passing (0 failures)  

## Immediate Next Steps

```bash
# 1. Commit the test fixes and enhancements
git add -A
git commit -m "fix: v1.3.2 - BDD test isolation and comprehensive test fixes

- Fixed test isolation issues causing 21 failures
- Added comprehensive BDD step definitions
- Implemented --limit option and multi-path support
- Fixed all flake8 linting errors
- All 301 tests now passing consistently

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"

# 2. Create release tag
git tag -a v1.3.2 -m "v1.3.2: Test Suite Fix - BDD isolation and enhancements"

# 3. Build and publish
poetry build
poetry publish
```

## Project Overview

**fx_bin** is a Python utility collection providing command-line tools for file operations. Current version 1.3.2 includes comprehensive test fixes and CLI enhancements.

### Available Commands
```bash
fx files       # Count files in directories
fx size        # Analyze file/directory sizes  
fx ff          # Find files by keyword
fx filter      # Filter files by extension (v1.2.0)
fx replace     # Replace text in files
fx json2excel  # Convert JSON to Excel
fx list        # List all available commands
```

## What's New in v1.3.2

### Test Suite Fixes
- **Test Isolation**: Fixed BDD tests changing working directory without restoration
- **Complete Pass Rate**: All 301 tests now passing (was 21 failures)
- **BDD Step Definitions**: Added comprehensive table parsing and directory validation
- **Code Quality**: Fixed all flake8 linting errors and applied black formatting

### CLI Enhancements
- **--limit Option**: Limit number of results in fx filter
- **Multi-path Support**: Process multiple directories in one command
- **Glob Patterns**: Wildcard support using fnmatch integration

## Features from v1.3.0

### BDD Testing Infrastructure
```bash
# Run BDD scenarios
poetry run pytest tests/bdd/ -v

# Run critical scenarios only  
poetry run pytest tests/bdd/ -m "smoke or critical"

# Run with detailed BDD report
poetry run pytest tests/bdd/ --html=reports/bdd.html
```

### Enhanced Test Organization
- **pytest-bdd 7.3.0+**: Complete BDD framework integration
- **18+ Test Markers**: Comprehensive test categorization (smoke, critical, performance, etc.)
- **Smart Step Patterns**: 70%+ step definition reuse across scenarios
- **Advanced Fixtures**: Sophisticated test data builders and realistic scenarios

## fx filter Command (from v1.2.0)

### fx filter Command (Enhanced in v1.3.2)
```bash
fx filter txt                    # Find .txt files
fx filter "mp4,avi,mkv"         # Multiple extensions
fx filter py --sort-by modified # Sort by modification time
fx filter txt --format detailed # Show file metadata
fx filter py --no-recursive     # Current directory only
fx filter py --limit 10         # NEW: Limit results to 10 files
fx filter txt dir1 dir2 dir3    # NEW: Search multiple directories
fx filter "*.test.py"           # NEW: Glob pattern support
```

### Testing Excellence (v1.3.0)
- **Production BDD Framework**: pytest-bdd with intelligent step patterns
- **23 Unit Tests**: Complete TDD implementation (maintained)
- **25+ BDD Scenarios**: Business-readable specifications in Gherkin
- **Quality Validation**: Built-in BDD best practice compliance scoring
- **Smart Fixtures**: Advanced test data builders with cleanup strategies
- **Comprehensive Coverage**: Edge cases, security, performance testing with BDD validation

## Development Environment

### Quick Setup
```bash
# Install dependencies
poetry install --with dev,test

# Run all tests
poetry run pytest

# Run BDD tests (NEW v1.3.0 infrastructure)
poetry run pytest tests/bdd/ -v

# Run by test category
poetry run pytest -m smoke           # Critical scenarios
poetry run pytest -m performance     # Performance tests
poetry run pytest -m edge_cases       # Edge case validation

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
├── test_filter.py         # 23 unit tests (v1.2.0)
├── bdd/                   # ENHANCED: Production BDD infrastructure (v1.3.0)
│   ├── conftest.py        # 400+ lines of sophisticated fixtures
│   ├── step_patterns.py   # 590+ lines of reusable patterns
│   └── test_file_filter_steps.py  # Smart step definitions
└── ...                    # Existing tests

features/
└── file_filter.feature    # ENHANCED: 25+ Gherkin scenarios with proper tagging

docs/
├── sessions/              # Session documentation (established)
├── changelog/             # Release documentation
└── bdd-testing-guide.md   # COMPREHENSIVE: 480+ lines BDD guide (v1.3.0)
```

## Recent Decisions & Context

### Architecture Decisions
- **Production BDD Framework**: pytest-bdd with smart patterns and quality validation
- **TDD + BDD Approach**: Mature testing strategy with stakeholder communication
- **Unified CLI**: Single `fx` command with subcommands for consistency
- **Click Framework**: Modern CLI framework for all commands

### Testing Strategy
- **Unit Tests First**: TDD methodology for core functionality (established)
- **Production BDD**: pytest-bdd framework with intelligent step patterns
- **Living Documentation**: Gherkin scenarios as executable specifications
- **Quality Validation**: Built-in BDD best practice compliance scoring
- **Smart Fixtures**: Advanced test data builders for realistic scenarios
- **Comprehensive Coverage**: Multiple testing layers with marker-based execution

### Documentation Standards
- **Session Documentation**: Preserve context between sessions
- **Living Documentation**: BDD scenarios as executable specifications
- **Comprehensive Changelogs**: Detailed release notes for users

## Troubleshooting

### Common Issues
```bash
# Test failures
poetry run pytest tests/test_filter.py -v

# BDD test issues (v1.3.0 infrastructure)
poetry run pytest tests/bdd/ -v --tb=short

# Test specific BDD categories
poetry run pytest tests/bdd/ -m smoke -v
poetry run pytest tests/bdd/ -m "not slow" -v

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
- **Fixed**: BDD test isolation issues causing 21 test failures
- **Root Cause**: Tests changing working directory without restoration
- **Solution**: Added finally blocks to guarantee directory restoration
- **Implemented**: Missing BDD step definitions for table parsing
- **Enhanced**: fx filter with --limit option and multi-path support
- **Code Quality**: Fixed all flake8 errors and applied black formatting
- **Result**: All 301 tests passing consistently (0 failures)

### Testing Infrastructure (v1.3.0)
- **Production BDD Framework**: Complete pytest-bdd infrastructure with smart patterns
- **Advanced Fixtures**: Sophisticated test data builders and cleanup strategies
- **Quality Validation**: Built-in BDD best practice compliance scoring
- **Comprehensive Documentation**: 480+ lines BDD testing guide
- **Proven Foundation**: 23 unit tests + BDD framework ready for execution

### Next Development Focus
- **BDD Validation**: Execute and validate all BDD scenarios with new infrastructure
- **Test Integration**: Integrate BDD tests into CI/CD pipeline
- **Pattern Expansion**: Add BDD scenarios for remaining commands
- **Performance Testing**: Execute performance-tagged BDD scenarios

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
fx filter py --limit 5            # Test new limit option
fx filter txt /path1 /path2       # Test multi-path support

# Test BDD infrastructure (v1.3.0)
poetry run pytest tests/bdd/ --collect-only  # Should discover scenarios
poetry run pytest tests/bdd/ -m smoke --dry-run  # Should run without errors
```

**Documentation Location**: All context preserved in `docs/sessions/` and `docs/changelog/` directories.