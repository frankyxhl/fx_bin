#!/usr/bin/env python3
"""TDD Test Runner for FX Bin

This script demonstrates the Test-Driven Development approach by running
tests in priority order: Security first, then safety, then functionality.
"""

import sys
import os
import subprocess
import time


def run_command(cmd, description, critical=True):
    """Run a command and handle results."""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")

    start_time = time.time()
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=120
        )
        elapsed = time.time() - start_time

        if result.returncode == 0:
            print(f"✅ {description} - PASSED ({elapsed:.1f}s)")
            if result.stdout.strip():
                print("Output:")
                print(result.stdout)
            return True
        else:
            print(f"❌ {description} - FAILED ({elapsed:.1f}s)")
            if result.stdout.strip():
                print("STDOUT:")
                print(result.stdout)
            if result.stderr.strip():
                print("STDERR:")
                print(result.stderr)

            if critical:
                print(f"\n🚨 CRITICAL FAILURE: {description}")
                print("TDD requires this test to pass before proceeding!")
                return False
            return False

    except subprocess.TimeoutExpired:
        print(f"⏱️ {description} - TIMEOUT (>120s)")
        return False
    except Exception as e:
        print(f"💥 {description} - ERROR: {e}")
        return False


def main():
    """Run TDD test suite in priority order."""
    print("🚀 FX Bin TDD Test Runner")
    print("Following Test-Driven Development principles:")
    print("1. Security tests (CRITICAL - must pass)")
    print("2. Safety tests (HIGH - must pass)")
    print("3. Functionality tests (MEDIUM)")
    print("4. Performance tests (LOW - informational)")

    # Check if dependencies are available
    print("\n📋 Checking dependencies...")
    try:
        import fx_bin

        print("✅ fx_bin module available")
    except ImportError:
        print("❌ fx_bin module not available - check Python path")
        return False

    # Phase 1: CRITICAL Security Tests
    print("\n🔒 PHASE 1: CRITICAL SECURITY TESTS")
    print("These tests MUST pass - they validate security vulnerabilities are fixed.")

    security_tests = []

    security_passed = 0
    for cmd, desc in security_tests:
        if run_command(cmd, desc, critical=True):
            security_passed += 1
        else:
            print(f"\n🚨 SECURITY TEST FAILED: {desc}")
            print("This is a CRITICAL security vulnerability!")
            print("TDD requires all security tests to pass before proceeding.")
            return False

    print(
        f"\n🔐 Security Phase Complete: {security_passed}/{len(security_tests)} tests passed"
    )

    # Phase 2: HIGH Priority Safety Tests
    print("\n🛡️ PHASE 2: HIGH PRIORITY SAFETY TESTS")
    print("These tests validate file operations are safe and don't cause data loss.")

    safety_tests = [
        (
            "python3 -m unittest tests.test_replace_safety.TestReplaceFileSafety.test_file_descriptor_no_leak -v",
            "File Descriptor Leak Prevention",
        ),
        (
            "python3 -m unittest tests.test_replace_safety.TestReplaceFileSafety.test_atomic_file_replacement -v",
            "Atomic File Operations",
        ),
        (
            "python3 -m unittest tests.test_common_safety.TestRecursiveDirectorySafety.test_symlink_loop_detection -v",
            "Symlink Loop Protection",
        ),
        (
            "python3 -m unittest tests.test_common_safety.TestRecursiveDirectorySafety.test_max_recursion_depth_limit -v",
            "Recursion Depth Limits",
        ),
    ]

    safety_passed = 0
    for cmd, desc in safety_tests:
        if run_command(cmd, desc, critical=True):
            safety_passed += 1
        else:
            print(f"\n⚠️ SAFETY TEST FAILED: {desc}")
            print("This could cause data loss or system instability!")
            return False

    print(
        f"\n🛡️ Safety Phase Complete: {safety_passed}/{len(safety_tests)} tests passed"
    )

    # Phase 3: MEDIUM Priority Functionality Tests
    print("\n⚙️ PHASE 3: FUNCTIONALITY TESTS")
    print("These tests validate core functionality works correctly.")

    functionality_tests = [
        ("python3 -m unittest tests.test_replace -v", "Replace Module Functionality"),
        ("python3 -m unittest tests.test_size -v", "Size Module Functionality"),
        ("python3 -m unittest tests.test_files -v", "Files Module Functionality"),
        (
            "python3 -m unittest tests.test_find_files -v",
            "Find Files Module Functionality",
        ),
        (
            "python3 -m unittest tests.test_integration.TestCLIIntegration -v",
            "CLI Integration",
        ),
    ]

    functionality_passed = 0
    for cmd, desc in functionality_tests:
        if run_command(cmd, desc, critical=False):
            functionality_passed += 1

    print(
        f"\n⚙️ Functionality Phase Complete: {functionality_passed}/{len(functionality_tests)} tests passed"
    )

    # Phase 4: LOW Priority Performance Tests (Informational)
    print("\n🏃 PHASE 4: PERFORMANCE TESTS (INFORMATIONAL)")
    print("These tests measure performance and provide benchmarks.")

    performance_tests = [
        (
            "python3 -m unittest tests.test_performance.TestPerformanceLimits.test_convert_size_performance -v",
            "Size Conversion Performance",
        ),
        (
            "python3 -m unittest tests.test_performance.TestMemoryUsage.test_directory_scanning_memory -v",
            "Memory Usage Limits",
        ),
    ]

    performance_passed = 0
    for cmd, desc in performance_tests:
        if run_command(cmd, desc, critical=False):
            performance_passed += 1

    print(
        f"\n🏃 Performance Phase Complete: {performance_passed}/{len(performance_tests)} tests passed"
    )

    # Final Summary
    print("\n" + "=" * 80)
    print("📊 TDD TEST SUITE SUMMARY")
    print("=" * 80)

    total_tests = (
        len(security_tests)
        + len(safety_tests)
        + len(functionality_tests)
        + len(performance_tests)
    )
    total_passed = (
        security_passed + safety_passed + functionality_passed + performance_passed
    )

    print(f"🔒 Security Tests:     {security_passed}/{len(security_tests)} passed")
    print(f"🛡️ Safety Tests:       {safety_passed}/{len(safety_tests)} passed")
    print(
        f"⚙️ Functionality Tests: {functionality_passed}/{len(functionality_tests)} passed"
    )
    print(
        f"🏃 Performance Tests:   {performance_passed}/{len(performance_tests)} passed"
    )
    print(f"📈 Overall:            {total_passed}/{total_tests} tests passed")

    if security_passed == len(security_tests) and safety_passed == len(safety_tests):
        print("\n✅ TDD SUCCESS: All critical security and safety tests passed!")
        print("🚢 Code is ready for deployment!")

        if functionality_passed == len(functionality_tests):
            print("🌟 BONUS: All functionality tests also passed!")

        return True
    else:
        print("\n❌ TDD FAILURE: Critical tests failed!")
        print("🚫 Code is NOT ready for deployment!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
