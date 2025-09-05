"""Performance tests for fx_bin utilities.

These tests ensure operations complete within reasonable time limits
and memory constraints.
"""

import os
import tempfile
import unittest
import time
import threading
from pathlib import Path
import psutil

# Silence loguru during tests
from loguru import logger

logger.remove()

from fx_bin.common import sum_folder_size, sum_folder_files_count, convert_size


class TestPerformanceLimits(unittest.TestCase):
    """Test performance limits and constraints."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        self.process = psutil.Process()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.test_dir)

    @unittest.skipIf(os.getenv("SKIP_SLOW_TESTS"), "Slow test skipped")
    def test_large_directory_performance(self):
        """Test performance with large number of files."""
        # Create directory with many files
        num_files = 1000
        large_dir = self.test_path / "large_dir"
        large_dir.mkdir()

        print(f"\nCreating {num_files} test files...")
        for i in range(num_files):
            (large_dir / f"file_{i:04d}.txt").write_text(f"content {i}")

        # Monitor memory usage
        initial_memory = self.process.memory_info().rss

        # Test size calculation performance
        start_time = time.time()
        total_size = sum_folder_size(str(large_dir))
        size_elapsed = time.time() - start_time

        # Test file counting performance
        start_time = time.time()
        file_count = sum_folder_files_count(str(large_dir))
        count_elapsed = time.time() - start_time

        peak_memory = self.process.memory_info().rss
        memory_increase = peak_memory - initial_memory

        # Performance assertions
        self.assertLess(
            size_elapsed, 2.0, f"Size calculation too slow: {size_elapsed:.2f}s"
        )
        self.assertLess(
            count_elapsed, 2.0, f"File counting too slow: {count_elapsed:.2f}s"
        )
        self.assertEqual(
            file_count, num_files, f"Expected {num_files} files, got {file_count}"
        )

        # Memory usage should be reasonable (not proportional to file count)
        max_memory_increase = 50 * 1024 * 1024  # 50MB
        self.assertLess(
            memory_increase,
            max_memory_increase,
            f"Memory usage too high: {memory_increase / 1024 / 1024:.1f}MB",
        )

        print(
            f"Performance: {num_files} files processed in {max(size_elapsed, count_elapsed):.2f}s"
        )
        print(f"Memory increase: {memory_increase / 1024 / 1024:.1f}MB")

    @unittest.skipIf(os.getenv("SKIP_SLOW_TESTS"), "Slow test skipped")
    def test_deep_directory_performance(self):
        """Test performance with deep directory nesting."""
        # Create deeply nested directory structure (reduced for macOS path limits)
        depth = 80  # Reduced from 100 to avoid macOS path length limits
        current_dir = self.test_path

        print(f"\nCreating {depth}-level deep directory...")
        for i in range(depth):
            # Use shorter directory names to avoid path length issues
            current_dir = current_dir / f"{i}"
            current_dir.mkdir()
            (current_dir / f"f{i}.txt").write_text(f"content at level {i}")

        start_time = time.time()
        total_size = sum_folder_size(str(self.test_path))
        elapsed = time.time() - start_time

        # Should complete without stack overflow
        self.assertGreater(total_size, 0, "Should process files in deep structure")
        self.assertLess(elapsed, 1.0, f"Deep directory scan too slow: {elapsed:.2f}s")

        print(f"Deep directory performance: {depth} levels in {elapsed:.2f}s")

    def test_file_replacement_performance(self):
        """Test file replacement performance with various file sizes."""
        from fx_bin.replace import work

        file_sizes = [1024, 10 * 1024, 100 * 1024, 1024 * 1024]  # 1KB to 1MB

        for size in file_sizes:
            with self.subTest(size=size):
                test_file = self.test_path / f"perf_test_{size}.txt"
                content = "test content " * (size // 13)  # Approximate size
                test_file.write_text(content)

                start_time = time.time()
                work("test", "demo", str(test_file))
                elapsed = time.time() - start_time

                # Performance should scale reasonably with file size
                max_time = max(0.1, size / (1024 * 1024) * 0.5)  # Max 0.5s per MB
                self.assertLess(
                    elapsed,
                    max_time,
                    f"Replacement too slow for {size} bytes: {elapsed:.2f}s",
                )

                # Verify replacement worked
                result = test_file.read_text()
                self.assertIn("demo content", result)

                print(f"Replacement performance: {size} bytes in {elapsed:.3f}s")

    def test_convert_size_performance(self):
        """Test convert_size function performance."""
        # Test with various sizes
        test_sizes = [0, 1, 1023, 1024, 1024**2, 1024**3, 1024**4, 2**63 - 1]

        start_time = time.time()
        for size in test_sizes * 1000:  # Repeat for timing
            result = convert_size(size)
            self.assertIsInstance(result, str)
        elapsed = time.time() - start_time

        # Should be very fast
        self.assertLess(elapsed, 0.1, f"convert_size too slow: {elapsed:.3f}s")

        print(
            f"convert_size performance: {len(test_sizes) * 1000} conversions in {elapsed:.3f}s"
        )

    def test_concurrent_performance(self):
        """Test performance under concurrent access."""
        # Create test structure
        num_dirs = 10
        files_per_dir = 50

        for i in range(num_dirs):
            subdir = self.test_path / f"concurrent_dir_{i}"
            subdir.mkdir()
            for j in range(files_per_dir):
                (subdir / f"file_{j}.txt").write_text(f"content {i}_{j}")

        results = []
        start_time = time.time()

        def worker():
            worker_start = time.time()
            size = sum_folder_size(str(self.test_path))
            count = sum_folder_files_count(str(self.test_path))
            worker_elapsed = time.time() - worker_start
            results.append((size, count, worker_elapsed))

        # Start multiple concurrent workers
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        # Wait for all to complete
        for thread in threads:
            thread.join()

        total_elapsed = time.time() - start_time

        # All should complete successfully
        self.assertEqual(len(results), 5, "Not all concurrent operations completed")

        # Results should be consistent
        expected_size, expected_count = results[0][:2]
        for size, count, _ in results:
            self.assertEqual(size, expected_size, "Inconsistent concurrent results")
            self.assertEqual(count, expected_count, "Inconsistent concurrent results")

        # Average worker time should be reasonable
        avg_worker_time = sum(r[2] for r in results) / len(results)
        self.assertLess(
            avg_worker_time,
            1.0,
            f"Concurrent operations too slow: {avg_worker_time:.2f}s avg",
        )

        print(f"Concurrent performance: 5 workers, avg {avg_worker_time:.3f}s each")


class TestMemoryUsage(unittest.TestCase):
    """Test memory usage constraints."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        self.process = psutil.Process()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.test_dir)

    def test_large_file_replacement_memory(self):
        """Test memory usage with large file replacement."""
        from fx_bin.replace import work

        # Create 5MB file
        large_file = self.test_path / "large_file.txt"
        content = "test line content\n" * (5 * 1024 * 1024 // 18)  # ~5MB
        large_file.write_text(content)

        initial_memory = self.process.memory_info().rss

        # Perform replacement
        work("test", "demo", str(large_file))

        peak_memory = self.process.memory_info().rss
        memory_increase = peak_memory - initial_memory

        # Memory increase should be reasonable (not loading entire file)
        max_acceptable_increase = 20 * 1024 * 1024  # 20MB
        self.assertLess(
            memory_increase,
            max_acceptable_increase,
            f"Memory usage too high: {memory_increase / 1024 / 1024:.1f}MB",
        )

        # Verify replacement worked
        result = large_file.read_text()
        self.assertIn("demo line content", result)
        self.assertNotIn("test", result)

        print(
            f"Large file memory usage: {memory_increase / 1024 / 1024:.1f}MB increase"
        )

    def test_directory_scanning_memory(self):
        """Test memory usage during directory scanning."""
        # Create many small files
        num_files = 2000
        for i in range(num_files):
            (self.test_path / f"file_{i}.txt").write_text(f"content {i}")

        initial_memory = self.process.memory_info().rss

        # Scan directory
        total_size = sum_folder_size(str(self.test_path))
        file_count = sum_folder_files_count(str(self.test_path))

        peak_memory = self.process.memory_info().rss
        memory_increase = peak_memory - initial_memory

        # Memory should not grow excessively with file count
        max_acceptable_increase = 30 * 1024 * 1024  # 30MB
        self.assertLess(
            memory_increase,
            max_acceptable_increase,
            f"Directory scanning memory too high: {memory_increase / 1024 / 1024:.1f}MB",
        )

        self.assertEqual(file_count, num_files)
        self.assertGreater(total_size, 0)

        print(
            f"Directory scan memory: {memory_increase / 1024 / 1024:.1f}MB for {num_files} files"
        )


class TestTimeout(unittest.TestCase):
    """Test timeout handling and hanging prevention."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.test_dir)

    def test_operations_complete_in_reasonable_time(self):
        """Test that operations don't hang indefinitely."""
        import signal

        # Create reasonable test structure
        for i in range(100):
            subdir = self.test_path / f"dir_{i}"
            subdir.mkdir()
            for j in range(10):
                (subdir / f"file_{j}.txt").write_text(f"content {i}_{j}")

        def timeout_handler(signum, frame):
            raise TimeoutError("Operation timed out")

        # Set timeout alarm (Unix only)
        if hasattr(signal, "SIGALRM"):
            original_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(5)  # 5 second timeout

            try:
                size = sum_folder_size(str(self.test_path))
                count = sum_folder_files_count(str(self.test_path))

                # Should complete within timeout
                self.assertGreater(size, 0)
                self.assertEqual(count, 1000)  # 100 dirs * 10 files

            except TimeoutError:
                self.fail("Operations timed out - possible hanging")
            finally:
                signal.alarm(0)  # Cancel alarm
                signal.signal(signal.SIGALRM, original_handler)
        else:
            # On systems without SIGALRM, use threading timeout
            import threading

            result = {}

            def worker():
                try:
                    size = sum_folder_size(str(self.test_path))
                    count = sum_folder_files_count(str(self.test_path))
                    result["success"] = True
                    result["size"] = size
                    result["count"] = count
                except Exception as e:
                    result["error"] = str(e)

            thread = threading.Thread(target=worker)
            thread.start()
            thread.join(timeout=5)  # 5 second timeout

            if thread.is_alive():
                self.fail("Operations timed out - possible hanging")

            self.assertTrue(
                result.get("success", False), f"Operation failed: {result.get('error')}"
            )


@unittest.skipIf(os.getenv("SKIP_PERFORMANCE_TESTS"), "Performance tests skipped")
class TestBenchmarks(unittest.TestCase):
    """Benchmark tests for performance baselines."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.test_dir)

    def test_baseline_performance(self):
        """Establish performance baselines."""
        # Create standard test structure
        num_files = 500
        file_size = 1024  # 1KB each

        for i in range(num_files):
            content = f"test content line {i}\n" * (file_size // 20)
            (self.test_path / f"benchmark_{i:03d}.txt").write_text(content)

        # Benchmark size calculation
        start_time = time.time()
        total_size = sum_folder_size(str(self.test_path))
        size_time = time.time() - start_time

        # Benchmark file counting
        start_time = time.time()
        file_count = sum_folder_files_count(str(self.test_path))
        count_time = time.time() - start_time

        # Benchmark file replacement
        test_file = self.test_path / "benchmark_replace.txt"
        test_file.write_text("test content " * 1000)

        from fx_bin.replace import work

        start_time = time.time()
        work("test", "demo", str(test_file))
        replace_time = time.time() - start_time

        # Print benchmarks (for reference)
        print(f"\n=== Performance Benchmarks ===")
        print(f"Files: {num_files}")
        print(f"Total size: {total_size} bytes")
        print(f"Size calculation: {size_time:.3f}s ({num_files/size_time:.0f} files/s)")
        print(f"File counting: {count_time:.3f}s ({num_files/count_time:.0f} files/s)")
        print(f"File replacement: {replace_time:.3f}s")

        # Basic performance checks
        self.assertLess(size_time, 1.0, "Size calculation baseline too slow")
        self.assertLess(count_time, 1.0, "File counting baseline too slow")
        self.assertLess(replace_time, 0.1, "File replacement baseline too slow")

        self.assertEqual(file_count, num_files)
        self.assertGreater(total_size, num_files * file_size * 0.8)  # Approximate size


if __name__ == "__main__":
    # Set environment variable to run slow tests
    if len(sys.argv) > 1 and "--slow" in sys.argv:
        os.environ.pop("SKIP_SLOW_TESTS", None)
        os.environ.pop("SKIP_PERFORMANCE_TESTS", None)
        sys.argv.remove("--slow")

    unittest.main()
