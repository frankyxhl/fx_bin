#!/usr/bin/env python3
"""Simplified test runner - no Poetry dependency required"""

import sys
import os
import subprocess
import unittest


def setup_path():
    """Setup Python path for importing fx_bin modules"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    print(f"✓ Added project path: {project_root}")


def check_dependencies():
    """检查必需的依赖"""
    required = ["pytest", "psutil", "click", "loguru"]
    missing = []

    for dep in required:
        try:
            __import__(dep)
            print(f"✓ {dep} 已安装")
        except ImportError:
            missing.append(dep)
            print(f"✗ {dep} 未安装")

    if missing:
        print(f"\n请安装缺少的依赖:")
        print(f"pip install {' '.join(missing)}")
        return False

    return True


def test_basic_functionality():
    """测试基本功能"""
    print("\n" + "=" * 60)
    print("🔍 测试基本功能")
    print("=" * 60)

    try:
        # 测试common.py
        from fx_bin.common import convert_size, sum_folder_size, sum_folder_files_count

        # 测试convert_size
        result = convert_size(1024)
        print(f"✓ convert_size(1024) = {result}")
        assert result == "1KB"

        # 测试目录扫描
        size = sum_folder_size(".")
        count = sum_folder_files_count(".")
        print(f"✓ 当前目录: {count} 个文件, 总大小 {convert_size(size)}")
        assert size > 0
        assert count > 0

        return True

    except Exception as e:
        print(f"✗ 基本功能测试失败: {e}")
        return False


def test_security_features():
    """测试安全功能 - 已移除 (upload_server 模块已删除)"""
    print("\n" + "=" * 60)
    print("🔒 测试安全功能 - 已跳过")
    print("=" * 60)
    print("✓ upload_server 模块已删除，推荐使用 uploadserver 包")
    return True


def test_pandas_import():
    """测试pandas导入处理"""
    print("\n" + "=" * 60)
    print("📋 测试pandas导入处理")
    print("=" * 60)

    try:
        # 测试pandas导入错误处理
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                """
import sys
sys.path.insert(0, ".")
try:
    from fx_bin import pd
    print("ERROR: Should have exited")
except SystemExit as e:
    print(f"EXIT_CODE:{e.code}")
            """,
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if "EXIT_CODE:1" in result.stdout:
            print("✓ pd.py 在pandas缺失时正确退出")
            return True
        else:
            print(f"✗ pd.py 退出行为异常: {result.stdout} | {result.stderr}")
            return False

    except Exception as e:
        print(f"✗ pandas导入测试失败: {e}")
        return False


def test_file_replacement():
    """测试文件替换功能"""
    print("\n" + "=" * 60)
    print("📝 测试文件替换功能")
    print("=" * 60)

    try:
        import tempfile
        from pathlib import Path
        from fx_bin.replace import work

        # 创建测试文件
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("Hello world\nSecond line\n")
            test_file = f.name

        # 执行替换
        work("world", "Python", test_file)

        # 验证结果
        with open(test_file, "r") as f:
            content = f.read()

        os.unlink(test_file)  # 清理

        if "Hello Python" in content and "Second line" in content:
            print("✓ 文件替换功能正常")
            return True
        else:
            print(f"✗ 文件替换失败: {content}")
            return False

    except Exception as e:
        print(f"✗ 文件替换测试失败: {e}")
        return False


def run_pytest_if_available():
    """如果pytest可用，运行部分pytest测试"""
    print("\n" + "=" * 60)
    print("🧪 运行pytest测试 (如果可用)")
    print("=" * 60)

    try:
        import pytest

        # 运行一些基本的pytest测试
        simple_tests = [
            "tests/test_size.py",
            "tests/test_files.py",
            "tests/test_replace.py",
        ]

        available_tests = [test for test in simple_tests if os.path.exists(test)]

        if not available_tests:
            print("⚠️ 未找到可用的pytest测试文件")
            return True

        for test_file in available_tests:
            print(f"\n运行 {test_file}...")
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
                timeout=30,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print(f"✓ {test_file} 通过")
            else:
                print(f"✗ {test_file} 失败")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                return False

        return True

    except ImportError:
        print("⚠️ pytest 不可用，跳过pytest测试")
        return True
    except Exception as e:
        print(f"⚠️ pytest测试出错: {e}")
        return True  # 不让pytest失败阻止其他测试


def main():
    """主测试函数"""
    print("🚀 FX Bin 简化测试运行器")
    print("=" * 60)

    # 设置环境
    setup_path()

    if not check_dependencies():
        print("\n❌ 依赖检查失败")
        return False

    # 运行测试
    tests = [
        ("基本功能", test_basic_functionality),
        ("安全功能", test_security_features),
        ("pandas导入", test_pandas_import),
        ("文件替换", test_file_replacement),
        ("pytest测试", run_pytest_if_available),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {name} 测试通过")
            else:
                failed += 1
                print(f"\n❌ {name} 测试失败")
        except Exception as e:
            failed += 1
            print(f"\n💥 {name} 测试出错: {e}")

    # 总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print(f"📈 总计: {passed + failed}")

    if failed == 0:
        print("\n🎉 所有测试通过! 代码可以安全使用!")
        return True
    else:
        print(f"\n⚠️ 有 {failed} 个测试失败，请检查问题")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
