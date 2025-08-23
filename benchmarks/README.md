# Performance Benchmarking Suite

This directory contains performance benchmarking tools for comparing the imperative and functional implementations of fx_bin utilities.

## Overview

The benchmark suite measures and compares:
- **Execution time**: How long operations take
- **Memory usage**: Peak and current memory consumption
- **CPU utilization**: Processing overhead
- **Functional overhead**: Cost of monadic abstractions

## Running Benchmarks

### Basic Usage

```bash
# Run all benchmarks
python benchmarks/benchmark_suite.py

# Run specific benchmark
python benchmarks/benchmark_suite.py --test replace

# Run with custom iterations
python benchmarks/benchmark_suite.py --iterations 10
```

### Available Benchmarks

1. **Text Replacement** (`replace` vs `replace_functional`)
   - Single file operations
   - Batch file operations
   - Backup/restore overhead

2. **JSON to Excel** (`pd` vs `pd_functional`)
   - JSON parsing performance
   - Excel writing speed
   - Validation overhead

3. **Folder Operations** (`common` vs `common_functional`)
   - Directory traversal
   - Size calculation
   - File counting

## Understanding Results

### Performance Metrics

- **Duration (ms)**: Time taken to complete operation
- **Memory Peak (MB)**: Maximum memory usage during operation
- **Memory Current (MB)**: Memory usage after operation
- **CPU Percent**: Average CPU utilization
- **Overhead Percent**: Functional vs imperative performance difference

### Interpreting Overhead

- **Negative overhead**: Functional version is faster (optimization opportunity)
- **0-5% overhead**: Negligible performance impact
- **5-10% overhead**: Acceptable for safety benefits
- **>10% overhead**: May need optimization

## Results Storage

Benchmark results are saved in `benchmarks/results/` with timestamps:
- `performance_analysis_YYYYMMDD.txt`: Detailed analysis reports
- `benchmark_results_YYYYMMDD.json`: Raw benchmark data

## Performance Optimization Tips

### For Functional Code

1. **Minimize monad nesting**: Deep composition can add overhead
2. **Use lazy evaluation**: IOResult delays execution until needed
3. **Batch operations**: Reduce context switching overhead
4. **Cache results**: Avoid recomputing pure functions

### For Imperative Code

1. **Profile hotspots**: Focus on frequently called functions
2. **Optimize I/O**: Batch file operations when possible
3. **Memory management**: Clear large objects when done
4. **Parallel processing**: Use for independent operations

## CI/CD Integration

The `tests/test_performance.py` file contains performance regression tests that run in CI/CD:

```bash
# Run performance tests only
poetry run pytest tests/test_performance.py

# Run with markers
poetry run pytest -m performance
```

## Historical Results

Important benchmark results are preserved in `benchmarks/results/`:
- `performance_analysis_20250823.txt`: Initial functional refactoring benchmarks
- `fx_bin_performance_analysis_final.txt`: Comprehensive analysis of v0.9.0

## Key Findings

Based on our benchmarks:

1. **Functional implementations show minimal overhead** (<0.1% average)
2. **Memory usage often improves** due to immutable data structures
3. **Safety benefits outweigh minimal performance costs**
4. **Some operations are actually faster** in functional style

## Contributing

When adding new benchmarks:

1. Add test cases to `benchmark_suite.py`
2. Follow the `BenchmarkResult` dataclass structure
3. Include both success and failure scenarios
4. Document any special setup requirements
5. Update this README with new benchmark descriptions

## Questions?

For questions about performance or optimization opportunities, please open an issue in the GitHub repository.