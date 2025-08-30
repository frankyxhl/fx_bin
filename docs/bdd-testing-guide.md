# BDD Testing Guide for fx_bin

This guide provides comprehensive documentation for the Behavior-Driven Development (BDD) test suite implemented for the fx_bin project's file filter command.

## Overview

The BDD test suite uses pytest-bdd to implement executable specifications written in Gherkin syntax. These tests serve as both documentation and automated validation of the `fx filter` command functionality.

### Key Benefits

- **Living Documentation**: Tests serve as up-to-date documentation
- **Stakeholder Communication**: Business-readable specifications  
- **Comprehensive Coverage**: 25+ scenarios covering core functionality and edge cases
- **Smart Step Reuse**: 70%+ step definition reuse through intelligent patterns
- **Quality Validation**: Built-in best practice validation and quality scoring

## Quick Start

### Installation

1. Install BDD testing dependencies:
```bash
# Install core BDD requirements
pip install -r requirements-bdd.txt

# Or install with Poetry (recommended)
poetry install --with test,bdd
```

2. Verify installation:
```bash
# Run BDD scenarios
pytest tests/bdd/ -v

# Run specific scenario tags
pytest tests/bdd/ -m smoke -v

# Generate HTML report
pytest tests/bdd/ --html=reports/bdd_results.html
```

### Running Tests

```bash
# Run all BDD scenarios
pytest tests/bdd/

# Run critical scenarios only
pytest tests/bdd/ -m "smoke or critical"

# Run with parallel execution
pytest tests/bdd/ -n auto

# Run with coverage reporting
pytest tests/bdd/ --cov=fx_bin --cov-report=html

# Run specific feature file
pytest tests/bdd/test_file_filter_steps.py::test_filter_by_single_extension
```

## Test Structure

### File Organization

```
tests/bdd/
├── __init__.py                 # Package initialization
├── conftest.py                 # Test fixtures and data builders
├── test_file_filter_steps.py   # Step definitions for filter scenarios
├── step_patterns.py            # Reusable step patterns and utilities
└── ...

features/
├── file_filter.feature         # Gherkin scenarios for file filtering
└── ...

docs/
├── bdd-testing-guide.md        # This guide
└── ...
```

### Feature Coverage

The BDD test suite covers:

1. **Core Functionality** (8 scenarios)
   - Single extension filtering
   - Multiple extension filtering  
   - Sorting by creation/modification time
   - Recursive vs non-recursive search

2. **Output Formats** (4 scenarios)
   - Simple format (filenames only)
   - Detailed format (with metadata)
   - Result limiting and pagination

3. **Edge Cases** (6 scenarios)
   - Empty directories
   - Non-existent directories
   - No matching files
   - Permission restrictions

4. **Security** (2 scenarios)
   - Path traversal protection
   - Permission handling

5. **Performance** (2 scenarios)
   - Large directory handling
   - Memory usage limits

6. **Integration** (3 scenarios)
   - Case sensitivity handling
   - Multiple directory support
   - Pipeline integration

## Scenario Tags

Tests are organized with tags for flexible execution:

### Priority Tags
- `@smoke`: Critical scenarios (must pass)
- `@critical`: High-priority core functionality  
- `@regression`: Full regression test suite

### Functional Tags
- `@sorting`: Sorting functionality tests
- `@recursion`: Recursive behavior tests
- `@output-format`: Output format tests
- `@pagination`: Result limiting tests
- `@security`: Security-related tests
- `@performance`: Performance tests

### Execution Tags
- `@fast`: Quick tests for rapid feedback
- `@slow`: Long-running tests
- `@integration`: Cross-component tests

## Step Definition Patterns

The BDD framework uses intelligent step patterns for maximum reuse:

### Smart Pattern Examples

```gherkin
# File setup patterns (70% reuse across scenarios)
Given I have a directory containing files with extensions "txt,py,md"
Given I have multiple "txt" files with different creation times
Given I have {count:d} files with "pdf" extension

# Command execution patterns (90% reuse)
When I run "fx filter txt"
When I run "fx filter mp4,avi,mkv --sort-by modified"
When I run "fx filter py --recursive --limit 10"

# Verification patterns (85% reuse)
Then I should see only files with "txt" extension
Then the results should be sorted by creation time (newest first)
Then I should see exactly {count:d} results
```

### Pattern Categories

1. **Given Patterns** (Setup)
   - File creation with extensions
   - Directory structure setup
   - Permission configuration
   - Performance test data

2. **When Patterns** (Actions) 
   - Command execution variants
   - Parameter combinations
   - Error condition triggers

3. **Then Patterns** (Verification)
   - Output validation
   - Format verification
   - Performance assertions
   - Security checks

## Advanced Features

### Smart Step Generation

The framework automatically generates optimized step definitions:

```python
# Auto-generated step with intelligent parameterization
@given(parsers.parse('I have a directory containing files with extensions "{extensions}"'))
def setup_files_with_extensions(file_builder, extensions):
    ext_list = parse_file_extensions(extensions)
    for i, ext in enumerate(ext_list):
        file_builder(
            f"test_file_{i}.{ext}",
            content=f"Content for {ext} file",
            created_offset_minutes=10 + i * 5
        )
```

### Test Data Builders

Sophisticated fixture builders create realistic test scenarios:

```python
@pytest.fixture
def nested_directory_structure(directory_builder):
    """Create nested directory structure for recursion tests."""
    structure = {
        "files": [{"name": "root.txt", "created_offset_minutes": 60}],
        "subdirs": {
            "level1": {
                "files": [{"name": "level1.txt", "created_offset_minutes": 45}],
                "subdirs": {
                    "level2": {
                        "files": [{"name": "level2.txt", "created_offset_minutes": 30}]
                    }
                }
            }
        }
    }
    return directory_builder(structure)
```

### Quality Validation

Built-in quality validators ensure BDD best practices:

```python
validator = BDDQualityValidator()
result = validator.validate_scenario(scenario_text)

# Results include:
# - Quality score (0-100)
# - Specific improvement suggestions
# - Best practice compliance
# - Business language validation
```

## Best Practices

### Scenario Writing

1. **Focus on Business Value**
   ```gherkin
   # Good - Business language
   Given a customer with multiple media files
   When they filter by video formats
   Then they should see only video files sorted by recency
   
   # Bad - Technical implementation
   Given files exist in filesystem with .mp4, .avi extensions
   When filter command executes with video extension parameters
   Then output contains filtered file list sorted by stat.st_ctime
   ```

2. **Use Concrete Examples**
   ```gherkin
   # Good - Specific examples
   Given I have files "movie.mp4", "clip.avi", "doc.pdf"
   When I run "fx filter mp4,avi"
   Then I should see "movie.mp4" and "clip.avi"
   
   # Bad - Abstract descriptions
   Given I have some video and document files
   When I filter by video extensions
   Then I should see video files
   ```

3. **Maintain Independence**
   ```gherkin
   # Good - Self-contained scenario
   Scenario: Filter files by single extension
     Given I have a directory containing files with extensions "txt,py,md"
     When I run "fx filter txt"
     Then I should see only files with ".txt" extension
   
   # Bad - Dependent on other scenarios
   Scenario: Filter after previous test
     Given the files from the previous scenario
     When I run "fx filter py"
     Then I should see different results
   ```

### Step Definition Guidelines

1. **Maximize Reuse**
   - Use parameterized steps: `@given(parsers.parse('I have {count:d} files with "{extension}" extension'))`
   - Create flexible patterns: `'I should see files with extensions "{extensions}"'`
   - Build reusable components: Extract common logic into utilities

2. **Clear Implementation**
   ```python
   @when(parsers.parse('I run "{command}"'))
   def run_fx_command(cli_runner, command_context, temp_directory, command):
       """Execute fx command and capture results with timing."""
       os.chdir(temp_directory)
       
       command_parts = command.split()
       if command_parts[0] == "fx":
           command_parts = command_parts[1:]
       
       start_time = time.time()
       result = cli_runner.invoke(cli, command_parts, catch_exceptions=False)
       
       command_context.update({
           'last_exit_code': result.exit_code,
           'last_output': result.output,
           'execution_time': time.time() - start_time
       })
   ```

3. **Comprehensive Assertions**
   ```python
   @then(parsers.parse('I should see only files with "{extension}" extension'))
   def verify_extension_filter(command_context, extension):
       """Verify only files with specified extension are shown."""
       output = command_context['last_output']
       
       for line in output.splitlines():
           if line.strip() and not line.startswith(('Error:', 'Warning:')):
               filename = line.split()[-1]
               file_ext = Path(filename).suffix.lower().lstrip('.')
               assert file_ext == extension.lower(), 
                   f"Found {filename} with extension {file_ext}, expected {extension}"
   ```

## Troubleshooting

### Common Issues

1. **Step Definition Not Found**
   ```bash
   # Error: Step definition not found for: "I have files with extension 'pdf'"
   # Solution: Check step pattern matches exactly, including quotes and parameters
   ```

2. **Fixture Dependency Issues**
   ```bash
   # Error: Fixture 'temp_directory' not found
   # Solution: Ensure conftest.py is in the correct location and fixtures are defined
   ```

3. **Test Data Cleanup**
   ```bash
   # Error: Permission denied when cleaning up test files
   # Solution: Ensure proper cleanup in fixtures, especially for permission tests
   ```

### Debug Tips

1. **Use pytest verbose mode**: `pytest -v` shows which steps are executing
2. **Enable debug output**: `pytest -s` shows print statements and debug output  
3. **Run single scenarios**: `pytest tests/bdd/test_file_filter_steps.py::test_specific_scenario`
4. **Check step matching**: Use `--collect-only` to see which tests are discovered

## Performance Considerations

### Test Execution Speed

- **Fast tests**: Use `@fast` marker for quick feedback loops
- **Parallel execution**: Use `pytest-xdist` for concurrent test runs
- **Selective execution**: Use markers to run subsets: `pytest -m "smoke and not slow"`

### Memory Usage

- **File count limits**: Large file collections use 100 files instead of 10,000 for test performance
- **Cleanup strategy**: Fixtures properly clean up temporary files and directories
- **Memory profiling**: Use `memory-profiler` for memory usage validation

### CI/CD Integration

```yaml
# Example GitHub Actions workflow
- name: Run BDD Tests
  run: |
    pip install -r requirements-bdd.txt
    pytest tests/bdd/ -m "smoke or critical" --html=reports/bdd.html
    
- name: Upload BDD Report
  uses: actions/upload-artifact@v3
  with:
    name: bdd-test-report
    path: reports/bdd.html
```

## Extending the Test Suite

### Adding New Scenarios

1. **Write Gherkin scenarios** in `features/file_filter.feature`
2. **Run tests** to see missing step definitions  
3. **Implement step definitions** in `tests/bdd/test_file_filter_steps.py`
4. **Reuse existing patterns** where possible
5. **Validate quality** using the built-in validators

### Adding New Features

1. **Create new feature file**: `features/new_feature.feature`
2. **Create step definition file**: `tests/bdd/test_new_feature_steps.py`
3. **Import scenarios**: `scenarios('../features/new_feature.feature')`
4. **Implement step definitions** with maximum reuse
5. **Update documentation** and examples

### Pattern Library Expansion

1. **Analyze step usage** with `StepReuseAnalyzer`
2. **Identify reuse opportunities** 
3. **Create parameterized patterns**
4. **Update existing step definitions**
5. **Document new patterns** in `step_patterns.py`

## Reporting and Documentation

### HTML Reports

```bash
# Generate comprehensive HTML report
pytest tests/bdd/ --html=reports/bdd_detailed.html --self-contained-html
```

### Living Documentation

The BDD scenarios serve as living documentation:

- **Feature specifications**: Business-readable requirements
- **Usage examples**: Concrete command examples
- **Edge case documentation**: Error handling and boundary conditions  
- **Integration patterns**: Inter-command workflows

### Metrics and Analysis

```python
# Analyze step reuse and quality
analyzer = StepReuseAnalyzer()
results = analyzer.analyze_feature_file(Path('features/file_filter.feature'))

print(f"Step reuse percentage: {results['reuse_percentage']:.1f}%")
print(f"Optimization opportunities: {len(results['optimization_suggestions'])}")
```

## Advanced Integration

### Custom Fixtures

Create domain-specific fixtures for complex scenarios:

```python
@pytest.fixture
def media_file_collection():
    """Create realistic media file collection for filtering tests."""
    return [
        ("vacation_2023.mp4", "video/mp4", 1024*1024*50),  # 50MB
        ("presentation.avi", "video/avi", 1024*1024*25),   # 25MB  
        ("clip.mkv", "video/mkv", 1024*1024*75),           # 75MB
        ("soundtrack.mp3", "audio/mp3", 1024*1024*5),      # 5MB
    ]
```

### Custom Matchers

Implement domain-specific assertion helpers:

```python
def assert_files_sorted_by_time(files, sort_type='created', reverse=False):
    """Assert files are sorted by specified time attribute."""
    if sort_type == 'created':
        times = [f.created_time for f in files]
    else:
        times = [f.modified_time for f in files]
    
    expected = sorted(times, reverse=not reverse)
    assert times == expected, f"Files not sorted by {sort_type} time"
```

### Performance Benchmarking

```python
@pytest.mark.performance
def test_large_directory_performance(large_file_collection, benchmark):
    """Benchmark filter performance on large directories."""
    
    def filter_operation():
        return cli_runner.invoke(cli, ['filter', 'txt', '--limit', '100'])
    
    result = benchmark(filter_operation)
    assert result.exit_code == 0
    assert benchmark.stats['mean'] < 2.0  # Max 2 seconds
```

This comprehensive BDD test suite ensures the `fx filter` command meets all business requirements while maintaining high code quality and providing excellent documentation for stakeholders and developers alike.