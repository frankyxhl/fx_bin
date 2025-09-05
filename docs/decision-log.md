# Architectural Decision Log

This document records important architectural and design decisions made during fx_bin development.

## ADR-003: Test Suite Reorganization (2025-09-05)

**Status**: Accepted  
**Context**: Test suite grew organically without clear structure, making test discovery and maintenance difficult  
**Decision**: Reorganize tests into categorized folders based on test type  

**Rationale**:
- **Clear Separation**: Different test types have different purposes and requirements
- **Easier Navigation**: Developers can quickly find relevant tests
- **Better CI/CD**: Can run specific test categories independently
- **Test Isolation**: Separation helps identify test interdependencies

**Consequences**:
- ✅ Improved test organization and maintainability
- ✅ Clear separation of concerns (unit vs integration vs security)
- ✅ Easier to run specific test categories
- ✅ Better understanding of test coverage gaps
- ⚠️ Initial migration effort to move and update imports
- ⚠️ Need to update CI/CD configurations

**Implementation**:
- Created 5 test categories: unit/, integration/, security/, performance/, functional/
- Moved all test files to appropriate categories
- Consolidated duplicate test files
- Updated all import paths

---

## ADR-002: Separate CLI from Business Logic (2025-09-05)

**Status**: Accepted  
**Context**: Replace command had tightly coupled CLI and business logic causing "str expected, not tuple" error  
**Decision**: Refactor to separate core functionality from CLI handling  

**Rationale**:
- **Testability**: Pure functions easier to test without Click context
- **Reusability**: Core logic can be used programmatically
- **Maintainability**: Clear separation of concerns
- **Error Prevention**: Type safety between layers

**Consequences**:
- ✅ Fixed critical runtime error in replace command
- ✅ Improved testability - no need to mock Click context
- ✅ Better API for programmatic usage
- ✅ Cleaner code architecture
- ⚠️ Additional function layer (minimal overhead)

**Implementation**:
- Created `replace_files()` function for core logic
- CLI `replace()` function now delegates to `replace_files()`
- Updated all tests to use new function
- Pattern can be applied to other commands

---

## ADR-001: TDD + BDD Testing Strategy (2025-08-30)

**Status**: Accepted  
**Context**: Need comprehensive testing for new fx filter command  
**Decision**: Implement both TDD (Test-Driven Development) and BDD (Behavior-Driven Development)  

**Rationale**:
- **TDD**: Ensures code quality and test coverage from development start
- **BDD**: Provides business-readable specifications for stakeholders
- **Comprehensive Coverage**: Multiple testing layers reduce regression risk
- **Living Documentation**: BDD scenarios serve as executable specifications

**Consequences**:
- ✅ High confidence in feature reliability (23 unit tests + 25+ BDD scenarios)
- ✅ Business stakeholders can understand requirements through Gherkin
- ✅ Comprehensive edge case coverage including security and performance
- ⚠️ Increased development time for test creation and maintenance
- ⚠️ Additional dependencies (pytest-bdd) for BDD infrastructure

**Implementation**:
- Unit tests in `tests/test_filter.py` following TDD methodology
- BDD scenarios in `features/file_filter.feature` with Gherkin syntax
- Step definitions in `tests/bdd/` with smart pattern reuse
- Comprehensive documentation in `docs/bdd-testing-guide.md`

---

## ADR-002: Unified CLI Architecture (2024-08-24)

**Status**: Accepted (Previous Release)  
**Context**: Multiple individual command entries (fx_files, fx_size, etc.) created user confusion  
**Decision**: Consolidate all commands under single `fx` entry point with subcommands  

**Rationale**:
- **User Experience**: Single command easier to remember and discover
- **Consistency**: Standardized help system and option patterns
- **Maintenance**: Simpler package structure and distribution
- **Extensibility**: Easy to add new commands without new entry points

**Consequences**:
- ✅ Improved user experience and command discoverability
- ✅ Consistent CLI patterns across all utilities
- ✅ Simplified package installation and distribution
- ⚠️ Breaking change requiring user migration from legacy commands
- ✅ Backward compatibility maintained through legacy command support

---

## ADR-003: Click Framework for CLI (2024-08-24)

**Status**: Accepted (Previous Release)  
**Context**: Need modern, maintainable CLI framework  
**Decision**: Use Click framework for all command-line interfaces  

**Rationale**:
- **Modern Patterns**: Click provides contemporary CLI best practices
- **Automatic Help**: Built-in help generation and validation
- **Type Safety**: Parameter validation and type conversion
- **Testing Support**: CliRunner for comprehensive CLI testing
- **Extensibility**: Easy to add complex options and subcommands

**Consequences**:
- ✅ Consistent, professional CLI experience
- ✅ Automatic help generation and parameter validation
- ✅ Excellent testing support with CliRunner
- ✅ Easy to extend with new commands and options
- ➖ Additional dependency (minimal impact)

---

## ADR-004: Session Documentation Pattern (2025-08-30)

**Status**: Accepted  
**Context**: Need to preserve development context between sessions  
**Decision**: Implement structured session documentation in `docs/sessions/`  

**Rationale**:
- **Context Preservation**: Maintain development continuity across sessions
- **Decision Tracking**: Record architectural and implementation decisions
- **Knowledge Transfer**: Enable future developers to understand project history
- **Quality Assurance**: Document what was completed vs. planned

**Consequences**:
- ✅ Clear development history and decision tracking
- ✅ Easy context recovery for future sessions
- ✅ Comprehensive project knowledge preservation
- ✅ Template established for consistent documentation
- ⚠️ Additional documentation overhead per session

**Implementation**:
- Structured session files in `docs/sessions/` with metadata
- Session index for quick navigation and search
- Project status tracking for current state awareness
- Quick-start guide for rapid context recovery

---

## ADR-005: Extension-based Filtering Implementation (2025-08-30)

**Status**: Accepted  
**Context**: Need flexible file filtering capabilities  
**Decision**: Implement extension-based filtering with multiple format and sorting options  

**Rationale**:
- **User Demand**: File filtering by extension is common use case
- **Flexibility**: Multiple extensions, sorting options, output formats
- **Performance**: Efficient filtering without external dependencies
- **Cross-platform**: Consistent behavior across operating systems
- **Security**: Path validation and traversal protection

**Consequences**:
- ✅ Powerful filtering capabilities meeting user needs
- ✅ Cross-platform compatibility with creation time handling
- ✅ Security-first design with input validation
- ✅ Flexible output formats (simple, detailed, count)
- ➖ Additional complexity in time handling across platforms

**Technical Decisions**:
- Case-insensitive extension matching for user convenience
- Creation time vs modification time sorting with fallback handling
- Human-readable file size formatting in detailed output
- Comprehensive error handling for file system operations

---

## ADR-006: Documentation-Driven Release Process (2025-08-30)

**Status**: Accepted  
**Context**: Need comprehensive release documentation for user adoption  
**Decision**: Implement detailed release documentation with multiple formats  

**Rationale**:
- **User Adoption**: Comprehensive documentation improves feature adoption
- **Developer Onboarding**: Clear documentation enables faster development
- **Quality Assurance**: Documented features are better tested and maintained
- **Stakeholder Communication**: BDD scenarios provide business-readable specifications

**Consequences**:
- ✅ High-quality documentation improves user experience
- ✅ Clear release notes help users understand new features
- ✅ BDD scenarios serve as both tests and documentation
- ✅ Established template for future releases
- ⚠️ Increased release preparation time

**Implementation**:
- Comprehensive HISTORY.rst updates with detailed feature descriptions
- Detailed changelog entries in `docs/changelog/`
- Session documentation preserving development context
- BDD scenarios as living documentation

---

## ADR-007: Security-First Dependency Management (2025-08-30)

**Status**: Accepted  
**Context**: Black ReDoS vulnerability (CVE) discovered affecting versions < 24.3.0  
**Decision**: Implement immediate patching process for security vulnerabilities with patch releases  

**Rationale**:
- **Security Priority**: Security vulnerabilities require immediate attention
- **Patch Versioning**: Security-only fixes warrant patch version increment (x.x.PATCH)
- **Comprehensive Updates**: Both pyproject.toml and requirements files need updates
- **Verification Required**: Security scans (Bandit, Safety) must validate fixes

**Consequences**:
- ✅ Rapid response to security vulnerabilities
- ✅ Clear versioning strategy for security fixes
- ✅ Comprehensive security validation process
- ✅ Established precedent for future security responses
- ⚠️ Requires monitoring dependency security advisories
- ⚠️ May require urgent patch releases outside normal schedule

**Implementation**:
- Update affected dependencies in pyproject.toml
- Update all requirements*.txt files with same dependency
- Run security validation: Bandit for code, Safety for dependencies
- Document security fix in HISTORY.rst with CVE details
- Release as patch version (e.g., 1.3.0 → 1.3.1)

**Technical Details**:
- Black ^24.0.0 → ^24.3.0 to fix ReDoS vulnerability
- Security scans: Bandit (0 issues), Safety (55 tests passed)
- All core tests must pass after dependency update
- Development-only dependencies still require security attention

---

## ADR-008: Test Isolation Management Strategy (2025-08-30)

**Status**: Accepted  
**Context**: BDD tests were causing test suite failures due to working directory changes  
**Decision**: Implement explicit working directory restoration using finally blocks  

**Rationale**:
- **Test Independence**: Each test must run in isolation without side effects
- **Global State Management**: Working directory is global state requiring careful handling
- **Guaranteed Cleanup**: Finally blocks ensure restoration even on test failures
- **Explicit Over Implicit**: Clear restoration code is easier to debug than hidden state

**Consequences**:
- ✅ All 301 tests now pass consistently (was 21 failures)
- ✅ Test execution order no longer affects results
- ✅ Clear pattern for handling global state in tests
- ✅ Easy to debug and understand cleanup logic
- ⚠️ Must remember to add finally blocks to new tests
- ⚠️ Slightly more verbose test code

**Implementation**:
```python
def test_function():
    original_dir = os.getcwd()
    try:
        # Test operations that might change directory
        os.chdir(temp_dir)
        # ... test logic ...
    finally:
        os.chdir(original_dir)  # ALWAYS restore
```

**Technical Details**:
- Applied to ~15 BDD step definitions that change directories
- Pattern works for both passing and failing tests
- Alternative approaches considered: pytest fixtures, context managers
- Chosen for simplicity and explicit visibility of cleanup

**Lessons Learned**:
- Test individual files before full suite to identify isolation issues
- BDD tests commonly change working directory for file operations
- Always restore global state (cwd, env vars, sys.path) in tests
- Incremental testing strategy helps identify isolation problems early

---

## ADR-009: BDD Step Definition Architecture (2025-08-30)

**Status**: Accepted  
**Context**: Need comprehensive BDD step definitions for complex scenarios  
**Decision**: Implement custom table parsing and directory structure validation  

**Rationale**:
- **Gherkin Tables**: Need to parse and validate table-formatted test data
- **Directory Trees**: Complex directory structures require validation
- **Pattern Matching**: Glob patterns need fnmatch integration
- **Multi-path Support**: CLI commands need to handle multiple paths

**Consequences**:
- ✅ Complete BDD scenario coverage with table support
- ✅ Flexible validation of complex output formats
- ✅ Reusable parsing utilities for future scenarios
- ✅ Support for advanced CLI features (glob, multi-path)
- ⚠️ Custom parsing code requires maintenance
- ⚠️ More complex than built-in pytest-bdd features

**Implementation**:
```python
def parse_table(table_string):
    lines = table_string.strip().split('\n')
    headers = [h.strip() for h in lines[0].split('|')[1:-1]]
    rows = []
    for line in lines[1:]:
        row = [cell.strip() for cell in line.split('|')[1:-1]]
        rows.append(dict(zip(headers, row)))
    return rows
```

**Technical Details**:
- Table parser handles Gherkin pipe-delimited format
- Directory structure validator compares expected vs actual trees
- Glob pattern support via fnmatch.fnmatch()
- Multi-path iteration in CLI command implementation

---

## ADR-010: Consistent Column Width for Tabular Output (2025-08-30)

**Status**: Accepted  
**Context**: File sizes in fx filter detailed output were misaligned due to inconsistent column widths  
**Decision**: Standardize all size units to consistent 9-character width formatting  

**Rationale**:
- **Visual Consistency**: Aligned columns improve readability and professional appearance
- **User Experience**: International users reported alignment issues affecting usability
- **Standard Practice**: Right-aligned numeric data is industry standard for tables
- **Width Choice**: 9 characters handles up to "999.9 GB" while minimizing wasted space

**Consequences**:
- ✅ Perfect visual alignment across all file size units
- ✅ Improved readability for users scanning file lists
- ✅ Consistent user experience across different file size ranges
- ✅ Simple implementation with minimal code changes
- ➖ Slightly more horizontal space used (1 extra character for B/KB)

**Implementation**:
```python
# Before: Mixed widths
if size_gb >= 1: return f"{size_gb:>9.1f} GB"  # 9 chars
elif size_mb >= 1: return f"{size_mb:>9.1f} MB"  # 9 chars
elif size_kb >= 1: return f"{size_kb:>8.1f} KB"  # 8 chars - MISALIGNED!
else: return f"{size:>8} B"  # 8 chars - MISALIGNED!

# After: Consistent 9-character width
if size_gb >= 1: return f"{size_gb:>9.1f} GB"
elif size_mb >= 1: return f"{size_mb:>9.1f} MB"
elif size_kb >= 1: return f"{size_kb:>9.1f} KB"  # Now 9 chars
else: return f"{size:>9} B"  # Now 9 chars
```

**Technical Details**:
- Applied to `_format_file_size_aligned` function in filter.py
- All 36 filter tests updated to match new formatting
- Doctest examples corrected with proper skip directives
- Version bumped to 1.3.3 for this formatting fix

**Lessons Learned**:
- Small formatting inconsistencies (even 1 character) significantly impact UX
- International users provide valuable feedback on alignment issues
- Comprehensive test coverage makes format changes safe to implement
- Consistent column widths are critical for readable tabular output

---

## Decision Criteria

### Evaluation Framework
When making architectural decisions, we consider:

1. **User Experience**: Does this improve the end-user experience?
2. **Maintainability**: Can this be easily maintained and extended?
3. **Performance**: Does this maintain or improve performance?
4. **Security**: Are security implications properly addressed?
5. **Compatibility**: Does this maintain backward compatibility?
6. **Testing**: Can this be thoroughly tested?
7. **Documentation**: Can this be clearly documented?

### Quality Gates
- All new features must have comprehensive test coverage (unit + integration)
- All architectural changes require documentation update
- Security implications must be explicitly addressed
- Performance impact must be measured and documented
- Backward compatibility must be maintained or migration path provided

### Review Process
- Architectural decisions documented before implementation
- Code reviews ensure adherence to established patterns  
- Testing validates implementation against decisions
- Documentation updated to reflect current architecture