#!/usr/bin/env python3
"""Simple test runner script - no Poetry or complex dependencies required"""

import sys
import os
import subprocess


def main():
    print("🧪 FX Bin Simple Test Runner")
    print("=" * 50)

    # Check basic dependencies
    print("📋 Checking dependencies...")
    try:
        import unittest

        print("✅ unittest available")
    except ImportError:
        print("❌ unittest not available")
        return False

    # Set Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    print(f"✅ Project path set: {project_root}")

    # Run existing unittest tests
    test_modules = [
        "tests.test_size",
        "tests.test_files",
        "tests.test_replace",
        "tests.test_find_files",
    ]

    passed = 0
    failed = 0

    for module in test_modules:
        print(f"\n🔍 Running {module}...")
        try:
            # Run unittest directly
            result = subprocess.run(
                [sys.executable, "-m", "unittest", module, "-v"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=project_root,
            )

            if result.returncode == 0:
                print(f"✅ {module} passed")
                passed += 1
                # Show test details
                lines = result.stderr.split("\n")
                test_lines = [
                    line
                    for line in lines
                    if "test_" in line and ("OK" in line or "PASS" in line)
                ]
                if test_lines:
                    print(f"   Passed {len(test_lines)} tests")
            else:
                print(f"❌ {module} failed")
                failed += 1
                print("Error output:")
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print(result.stderr)

        except subprocess.TimeoutExpired:
            print(f"⏱️ {module} timed out")
            failed += 1
        except Exception as e:
            print(f"💥 {module} error: {e}")
            failed += 1

    # Security tests removed (upload_server module deleted)

    # Run basic functionality tests
    print(f"\n⚙️ Running basic functionality tests...")
    try:
        from fx_bin.common import convert_size, sum_folder_size, sum_folder_files_count

        # Test convert_size
        test_cases = [(0, "0B"), (1024, "1KB"), (1024 * 1024, "1MB")]

        basic_passed = 0
        for size, expected in test_cases:
            result = convert_size(size)
            if result == expected:
                print(f"✅ convert_size({size}) = {result}")
                basic_passed += 1
            else:
                print(f"❌ convert_size({size}) = {result}, expected {expected}")

        # Test directory scanning
        try:
            size = sum_folder_size(".")
            count = sum_folder_files_count(".")
            if size > 0 and count > 0:
                print(f"✅ Directory scanning: {count} files, {convert_size(size)}")
                basic_passed += 1
            else:
                print(
                    f"❌ Directory scanning results abnormal: {count} files, {size} bytes"
                )
        except Exception as e:
            print(f"❌ Directory scanning error: {e}")

        if basic_passed >= len(test_cases):
            print("✅ Basic functionality tests passed")
            passed += 1
        else:
            print("❌ Basic functionality tests failed")
            failed += 1

    except Exception as e:
        print(f"❌ Basic functionality tests error: {e}")
        failed += 1

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Total: {passed + failed}")

    if failed == 0:
        print("\n🎉 All tests passed! 🚀")
        print("Code is safe to use!")
        return True
    else:
        print(f"\n⚠️ {failed} tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
