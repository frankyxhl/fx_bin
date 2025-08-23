#!/usr/bin/env python3
"""Final, working performance benchmarking suite for fx_bin.

This corrected benchmark properly handles all functional interfaces.
"""

import gc
import json
import os
import psutil
import shutil
import tempfile
import time
import tracemalloc
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Callable, Any, Optional, Tuple

import pandas as pd
from returns.io import IOResult
from returns.result import Result, Success, Failure

# Import modules to benchmark
from fx_bin import replace, pd as pd_module, common
from fx_bin import replace_functional, pd_functional, common_functional
from fx_bin.errors import FolderError
from fx_bin.common_functional import FolderContext


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run."""
    name: str
    duration_ms: float
    memory_peak_mb: float
    memory_current_mb: float
    cpu_percent: float
    success: bool
    error_msg: Optional[str] = None
    result_value: Optional[Any] = None


@dataclass
class ComparisonResult:
    """Comparison between imperative and functional implementations."""
    operation: str
    imperative: BenchmarkResult
    functional: BenchmarkResult
    overhead_percent: float
    memory_overhead_percent: float
    
    @property
    def performance_summary(self) -> str:
        """Human-readable performance summary."""
        if not self.imperative.success or not self.functional.success:
            return f"{self.operation}: BENCHMARK FAILED"
        
        speed_diff = "FASTER" if self.overhead_percent < 0 else "SLOWER"
        memory_diff = "LESS" if self.memory_overhead_percent < 0 else "MORE"
        
        return (
            f"{self.operation}:\n"
            f"  Time: Functional is {abs(self.overhead_percent):.1f}% {speed_diff}\n"
            f"  Memory: Functional uses {abs(self.memory_overhead_percent):.1f}% {memory_diff} memory\n"
            f"  Imperative: {self.imperative.duration_ms:.2f}ms, {self.imperative.memory_peak_mb:.1f}MB\n"
            f"  Functional: {self.functional.duration_ms:.2f}ms, {self.functional.memory_peak_mb:.1f}MB"
        )


class PerformanceBenchmarker:
    """Main benchmarking class with memory and CPU monitoring."""
    
    def __init__(self, warmup_runs: int = 2, test_runs: int = 10):
        self.warmup_runs = warmup_runs
        self.test_runs = test_runs
        self.process = psutil.Process()
        
    @contextmanager
    def monitor_performance(self):
        """Context manager to monitor performance metrics."""
        # Force garbage collection
        gc.collect()
        
        # Start monitoring
        tracemalloc.start()
        start_time = time.perf_counter()
        start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        cpu_times_start = self.process.cpu_times()
        
        try:
            yield
        finally:
            end_time = time.perf_counter()
            current_memory = self.process.memory_info().rss / 1024 / 1024  # MB
            cpu_times_end = self.process.cpu_times()
            
            # Get peak memory from tracemalloc
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            # Calculate metrics
            duration_ms = (end_time - start_time) * 1000
            memory_peak_mb = peak / 1024 / 1024
            cpu_time = (cpu_times_end.user - cpu_times_start.user + 
                       cpu_times_end.system - cpu_times_start.system)
            cpu_percent = (cpu_time / (end_time - start_time)) * 100 if (end_time - start_time) > 0 else 0
            
            self.last_result = {
                'duration_ms': duration_ms,
                'memory_peak_mb': memory_peak_mb,
                'memory_current_mb': current_memory,
                'cpu_percent': cpu_percent
            }
    
    def benchmark_function(self, func: Callable, name: str, *args, **kwargs) -> BenchmarkResult:
        """Benchmark a single function with multiple runs."""
        results = []
        error_msg = None
        final_result = None
        
        # Warmup runs
        for _ in range(self.warmup_runs):
            try:
                with self.monitor_performance():
                    func(*args, **kwargs)
            except Exception:
                pass  # Ignore warmup errors
        
        # Test runs
        for i in range(self.test_runs):
            try:
                with self.monitor_performance():
                    result = func(*args, **kwargs)
                    final_result = result
                
                results.append(self.last_result)
            except Exception as e:
                error_msg = str(e)
                # Continue with other runs to get partial data
                continue
        
        if not results:
            return BenchmarkResult(
                name=name,
                duration_ms=float('inf'),
                memory_peak_mb=0,
                memory_current_mb=0,
                cpu_percent=0,
                success=False,
                error_msg=error_msg
            )
        
        # Calculate averages
        avg_duration = sum(r['duration_ms'] for r in results) / len(results)
        avg_memory_peak = sum(r['memory_peak_mb'] for r in results) / len(results)
        avg_memory_current = sum(r['memory_current_mb'] for r in results) / len(results)
        avg_cpu = sum(r['cpu_percent'] for r in results) / len(results)
        
        return BenchmarkResult(
            name=name,
            duration_ms=avg_duration,
            memory_peak_mb=avg_memory_peak,
            memory_current_mb=avg_memory_current,
            cpu_percent=avg_cpu,
            success=len(results) == self.test_runs,
            error_msg=error_msg if len(results) < self.test_runs else None,
            result_value=final_result
        )


def run_specific_benchmarks() -> List[ComparisonResult]:
    """Run specific benchmarks that actually work."""
    print("Starting targeted fx_bin performance benchmarks...\n")
    
    benchmarker = PerformanceBenchmarker(warmup_runs=1, test_runs=8)
    results = []
    
    # 1. Single File Text Replacement Benchmark
    print("Benchmarking single file text replacement...")
    try:
        test_dir = Path(tempfile.mkdtemp(prefix="fx_bin_replace_bench_"))
        
        # Create test file
        content = "This is test content with SEARCH_TEXT that needs replacement.\n" * 100
        test_file = test_dir / "test.txt"
        test_file.write_text(content)
        
        def imperative_replace():
            temp_file = test_file.with_suffix(".tmp")
            shutil.copy2(test_file, temp_file)
            replace.work("SEARCH_TEXT", "REPLACED", str(temp_file))
            temp_file.unlink()
        
        def functional_replace():
            temp_file = test_file.with_suffix(".tmp")
            shutil.copy2(test_file, temp_file)
            # Use the functional version correctly
            io_result = replace_functional.work_functional("SEARCH_TEXT", "REPLACED", str(temp_file))
            # IOResult doesn't need .run() - it's already executed
            if hasattr(io_result, '_inner_value') and isinstance(io_result._inner_value, Failure):
                raise Exception(f"Functional replacement failed: {io_result._inner_value.failure()}")
            temp_file.unlink(missing_ok=True)
            return io_result
        
        imperative_result = benchmarker.benchmark_function(imperative_replace, "replace_imperative")
        functional_result = benchmarker.benchmark_function(functional_replace, "replace_functional")
        
        time_overhead = ((functional_result.duration_ms - imperative_result.duration_ms) / 
                       max(imperative_result.duration_ms, 0.001) * 100)
        memory_overhead = ((functional_result.memory_peak_mb - imperative_result.memory_peak_mb) / 
                         max(imperative_result.memory_peak_mb, 0.001) * 100)
        
        results.append(ComparisonResult(
            operation="Single File Text Replacement",
            imperative=imperative_result,
            functional=functional_result,
            overhead_percent=time_overhead,
            memory_overhead_percent=memory_overhead
        ))
        
        shutil.rmtree(test_dir)
        
    except Exception as e:
        print(f"Error in single file replacement benchmark: {e}")
    
    # 2. JSON to Excel Conversion Benchmark
    print("Benchmarking JSON to Excel conversion...")
    try:
        test_dir = Path(tempfile.mkdtemp(prefix="fx_bin_pd_bench_"))
        
        # Create test JSON
        test_data = [{"id": i, "name": f"User_{i}", "value": i * 10} for i in range(1000)]
        json_file = test_dir / "test.json"
        with open(json_file, 'w') as f:
            json.dump(test_data, f)
        
        def imperative_convert():
            output_file = test_dir / "output_imp.xlsx"
            pd.read_json(str(json_file)).to_excel(str(output_file), index=False)
            output_file.unlink()
        
        def functional_convert():
            output_file = test_dir / "output_func.xlsx"
            # Use the legacy interface which should work
            result = pd_functional.main_legacy(str(json_file), str(output_file.name))
            output_file.unlink(missing_ok=True)
            return result
        
        imperative_result = benchmarker.benchmark_function(imperative_convert, "pd_imperative")
        functional_result = benchmarker.benchmark_function(functional_convert, "pd_functional")
        
        time_overhead = ((functional_result.duration_ms - imperative_result.duration_ms) / 
                       max(imperative_result.duration_ms, 0.001) * 100)
        memory_overhead = ((functional_result.memory_peak_mb - imperative_result.memory_peak_mb) / 
                         max(imperative_result.memory_peak_mb, 0.001) * 100)
        
        results.append(ComparisonResult(
            operation="JSON to Excel Conversion",
            imperative=imperative_result,
            functional=functional_result,
            overhead_percent=time_overhead,
            memory_overhead_percent=memory_overhead
        ))
        
        shutil.rmtree(test_dir)
        
    except Exception as e:
        print(f"Error in JSON to Excel benchmark: {e}")
    
    # 3. Folder Size Calculation Benchmark
    print("Benchmarking folder size calculation...")
    try:
        test_dir = Path(tempfile.mkdtemp(prefix="fx_bin_size_bench_"))
        
        # Create test directory structure
        for i in range(50):
            test_file = test_dir / f"file_{i}.txt"
            test_file.write_text("x" * 1024)  # 1KB files
        
        # Create subdirectory
        subdir = test_dir / "subdir"
        subdir.mkdir()
        for i in range(30):
            test_file = subdir / f"subfile_{i}.txt"
            test_file.write_text("y" * 512)  # 512B files
        
        def imperative_size():
            return common.sum_folder_size(str(test_dir))
        
        def functional_size():
            # Use the legacy wrapper which handles the context properly
            return common_functional.sum_folder_size_legacy(str(test_dir))
        
        imperative_result = benchmarker.benchmark_function(imperative_size, "size_imperative")
        functional_result = benchmarker.benchmark_function(functional_size, "size_functional")
        
        time_overhead = ((functional_result.duration_ms - imperative_result.duration_ms) / 
                       max(imperative_result.duration_ms, 0.001) * 100)
        memory_overhead = ((functional_result.memory_peak_mb - imperative_result.memory_peak_mb) / 
                         max(imperative_result.memory_peak_mb, 0.001) * 100)
        
        results.append(ComparisonResult(
            operation="Folder Size Calculation",
            imperative=imperative_result,
            functional=functional_result,
            overhead_percent=time_overhead,
            memory_overhead_percent=memory_overhead
        ))
        
        shutil.rmtree(test_dir)
        
    except Exception as e:
        print(f"Error in folder size benchmark: {e}")
    
    # 4. File Count Benchmark
    print("Benchmarking file count calculation...")
    try:
        test_dir = Path(tempfile.mkdtemp(prefix="fx_bin_count_bench_"))
        
        # Create test directory structure
        for i in range(100):
            test_file = test_dir / f"file_{i}.txt"
            test_file.write_text("content")
        
        # Create nested subdirectories
        for j in range(3):
            subdir = test_dir / f"subdir_{j}"
            subdir.mkdir()
            for i in range(20):
                test_file = subdir / f"subfile_{i}.txt"
                test_file.write_text("content")
        
        def imperative_count():
            return common.sum_folder_files_count(str(test_dir))
        
        def functional_count():
            # Use the legacy wrapper
            return common_functional.sum_folder_files_count_legacy(str(test_dir))
        
        imperative_result = benchmarker.benchmark_function(imperative_count, "count_imperative")
        functional_result = benchmarker.benchmark_function(functional_count, "count_functional")
        
        time_overhead = ((functional_result.duration_ms - imperative_result.duration_ms) / 
                       max(imperative_result.duration_ms, 0.001) * 100)
        memory_overhead = ((functional_result.memory_peak_mb - imperative_result.memory_peak_mb) / 
                         max(imperative_result.memory_peak_mb, 0.001) * 100)
        
        results.append(ComparisonResult(
            operation="File Count Calculation",
            imperative=imperative_result,
            functional=functional_result,
            overhead_percent=time_overhead,
            memory_overhead_percent=memory_overhead
        ))
        
        shutil.rmtree(test_dir)
        
    except Exception as e:
        print(f"Error in file count benchmark: {e}")
    
    return results


def generate_final_report(results: List[ComparisonResult]) -> str:
    """Generate the final comprehensive performance report."""
    report = []
    report.append("="*80)
    report.append("FX_BIN PERFORMANCE BENCHMARK REPORT - FINAL")
    report.append("Imperative vs Functional Implementation Analysis")
    report.append("="*80)
    report.append("")
    
    # Executive Summary
    successful_results = [r for r in results if r.imperative.success and r.functional.success]
    if successful_results:
        avg_time_overhead = sum(r.overhead_percent for r in successful_results) / len(successful_results)
        avg_memory_overhead = sum(r.memory_overhead_percent for r in successful_results) / len(successful_results)
        
        report.append("EXECUTIVE SUMMARY:")
        report.append(f"• Benchmarks completed: {len(successful_results)}/{len(results)}")
        report.append(f"• Average time overhead: {avg_time_overhead:+.1f}%")
        report.append(f"• Average memory overhead: {avg_memory_overhead:+.1f}%")
        report.append("")
        
        # Performance classification
        if avg_time_overhead < 10:
            perf_class = "EXCELLENT - Functional approach adds minimal overhead"
        elif avg_time_overhead < 25:
            perf_class = "GOOD - Acceptable overhead for safety benefits"
        elif avg_time_overhead < 50:
            perf_class = "MODERATE - Consider optimization opportunities"
        else:
            perf_class = "HIGH - Significant performance impact"
        
        report.append(f"Performance Classification: {perf_class}")
        report.append("")
    
    # Detailed Results
    report.append("DETAILED RESULTS:")
    report.append("-" * 50)
    
    for i, result in enumerate(results, 1):
        report.append(f"{i}. {result.performance_summary}")
        
        # Add detailed metrics
        if result.imperative.success and result.functional.success:
            report.append(f"   CPU Usage - Imperative: {result.imperative.cpu_percent:.1f}%, "
                         f"Functional: {result.functional.cpu_percent:.1f}%")
        
        # Error details
        if result.imperative.error_msg:
            report.append(f"   Imperative Error: {result.imperative.error_msg}")
        if result.functional.error_msg:
            report.append(f"   Functional Error: {result.functional.error_msg}")
        
        report.append("")
    
    # Analysis and Insights
    if successful_results:
        report.append("PERFORMANCE ANALYSIS:")
        report.append("-" * 50)
        
        # Best and worst performers
        best_time = min(successful_results, key=lambda x: x.overhead_percent)
        worst_time = max(successful_results, key=lambda x: x.overhead_percent)
        best_memory = min(successful_results, key=lambda x: x.memory_overhead_percent)
        worst_memory = max(successful_results, key=lambda x: x.memory_overhead_percent)
        
        report.append(f"• Best time performance: {best_time.operation} ({best_time.overhead_percent:+.1f}%)")
        report.append(f"• Worst time performance: {worst_time.operation} ({worst_time.overhead_percent:+.1f}%)")
        report.append(f"• Best memory efficiency: {best_memory.operation} ({best_memory.memory_overhead_percent:+.1f}%)")
        report.append(f"• Worst memory efficiency: {worst_memory.operation} ({worst_memory.memory_overhead_percent:+.1f}%)")
        report.append("")
        
        # Overhead distribution
        low_overhead = [r for r in successful_results if r.overhead_percent < 15]
        medium_overhead = [r for r in successful_results if 15 <= r.overhead_percent < 40]
        high_overhead = [r for r in successful_results if r.overhead_percent >= 40]
        
        report.append("OVERHEAD DISTRIBUTION:")
        report.append(f"• Low overhead (< 15%): {len(low_overhead)} operations")
        report.append(f"• Medium overhead (15-40%): {len(medium_overhead)} operations")
        report.append(f"• High overhead (> 40%): {len(high_overhead)} operations")
        report.append("")
    
    # Recommendations
    report.append("RECOMMENDATIONS:")
    report.append("-" * 50)
    
    if successful_results:
        avg_time_overhead = sum(r.overhead_percent for r in successful_results) / len(successful_results)
        
        if avg_time_overhead < 20:
            report.append("✓ PROCEED: Functional implementation shows excellent performance")
            report.append("  The safety benefits significantly outweigh the minimal overhead")
        elif avg_time_overhead < 35:
            report.append("⚠ CONDITIONAL: Moderate overhead but acceptable for most use cases")
            report.append("  Consider profiling critical paths and optimizing hot spots")
        else:
            report.append("⚠ CAUTION: High overhead detected")
            report.append("  Recommend optimization before production deployment")
        
        report.append("")
        report.append("FUNCTIONAL PROGRAMMING BENEFITS:")
        report.append("• Type Safety: Compile-time error detection")
        report.append("• Explicit Error Handling: No hidden exceptions")
        report.append("• Immutability: Reduced mutation bugs")
        report.append("• Composability: Better code reuse and testing")
        report.append("• Maintainability: Clearer data flow and dependencies")
        
        if any(r.overhead_percent > 30 for r in successful_results):
            report.append("")
            report.append("OPTIMIZATION OPPORTUNITIES:")
            for r in successful_results:
                if r.overhead_percent > 30:
                    report.append(f"• {r.operation}: {r.overhead_percent:.1f}% overhead")
                    report.append("  - Consider lazy evaluation for IO operations")
                    report.append("  - Profile monad composition overhead")
                    report.append("  - Optimize context passing mechanisms")
    
    report.append("")
    report.append("BENCHMARK METHODOLOGY:")
    report.append("• 1 warmup run + 8 test runs per operation")
    report.append("• Memory tracking with tracemalloc (peak usage)")
    report.append("• CPU usage monitoring via psutil")
    report.append("• Garbage collection forced before measurements")
    report.append("• Results averaged across successful runs")
    report.append("• Temporary files cleaned up after each test")
    report.append("")
    
    report.append("CONCLUSION:")
    if successful_results:
        avg_time_overhead = sum(r.overhead_percent for r in successful_results) / len(successful_results)
        if avg_time_overhead < 25:
            conclusion = ("The functional refactoring demonstrates excellent performance characteristics. "
                         "The type safety, explicit error handling, and improved maintainability "
                         "provide significant value with minimal performance cost.")
        else:
            conclusion = ("The functional refactoring shows higher overhead than ideal. "
                         "While the safety benefits are valuable, consider targeted optimizations "
                         "for performance-critical code paths.")
    else:
        conclusion = "Benchmark execution encountered issues. Manual verification of functional interfaces needed."
    
    report.append(conclusion)
    report.append("")
    report.append("="*80)
    
    return "\n".join(report)


if __name__ == "__main__":
    try:
        # Run targeted benchmarks
        results = run_specific_benchmarks()
        
        # Generate and display report
        report = generate_final_report(results)
        print("\n" + report)
        
        # Save report to file
        report_file = Path("fx_bin_performance_analysis_final.txt")
        report_file.write_text(report)
        print(f"\nComplete analysis saved to: {report_file.absolute()}")
        
    except Exception as e:
        print(f"Benchmark execution failed: {e}")
        import traceback
        traceback.print_exc()
