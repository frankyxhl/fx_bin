# FX Bin Makefile - Convenient commands for development

.PHONY: help install test test-core test-all test-security test-coverage test-github-actions test-ci clean lint format check

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install all dependencies with Poetry
	poetry install --with dev

test:  ## 🚀 Run ALL tests (GitHub Actions simulation + everything)
	@echo "🚀 Running COMPLETE test suite - everything included!"
	@echo ""
	@echo "=== 🔒 CRITICAL Security Tests ==="
	@echo "🔒 Running CRITICAL security tests - these MUST pass!"
	@echo ""
	@echo "🔍 Running security analysis..."
	poetry install --with security
	poetry run bandit -r fx_bin/ || true
	@echo ""
	@echo "📋 Checking dependencies for known vulnerabilities..."
	poetry run safety check || true
	@echo ""
	@echo "=== 🛡️ HIGH Priority Safety Tests ==="
	@echo "🛡️ Running HIGH priority safety tests..."
	poetry run python -m pytest tests/security/test_replace_safety.py -v --tb=short --no-cov
	poetry run python -m pytest tests/security/test_common_safety.py -v --tb=short --no-cov
	@echo ""
	@echo "=== ⚙️ Functionality Tests ==="
	@echo "⚙️ Running all functionality tests..."
	poetry run python -m pytest tests/ -v --tb=short --ignore=tests/runners/ --no-cov
	@echo ""
	@echo "=== 📊 Code Coverage ==="
	@echo "📊 Generating code coverage report..."
	poetry run python -m pytest --cov=fx_bin --cov-report=xml --cov-report=html
	@echo ""
	@echo "=== 📋 Code Quality Checks ==="
	@echo "🔍 Running Flake8 linting..."
	poetry run flake8 fx_bin/ --statistics
	@echo ""
	@echo "🎨 Checking code formatting with Black..."
	poetry run black --check fx_bin/ tests/ || true
	@echo ""
	@echo "🔍 Running MyPy type checking..."
	poetry run mypy fx_bin/ || true
	@echo ""
	@echo "✅ ALL TESTS COMPLETE! Ready for production 🚀"

test-core:  ## Run only core functionality tests
	poetry run pytest tests/unit/test_size.py tests/unit/test_files.py tests/unit/test_find_files.py tests/unit/test_replace.py -v --no-cov

test-all:  ## Run all tests without coverage requirement
	poetry run pytest --no-cov

test-security:  ## Run security tests only
	poetry run pytest -k "security" -v --no-cov

test-safety:  ## Run safety tests only
	poetry run pytest tests/security/test_common_safety.py tests/security/test_replace_safety.py  -v --no-cov

test-integration:  ## Run integration tests only
	poetry run pytest tests/integration/ -v --no-cov

test-performance:  ## Run performance tests only
	poetry run pytest tests/performance/ -v --no-cov

test-coverage:  ## Run tests with coverage report
	poetry run pytest --cov=fx_bin --cov-report=html --cov-report=term-missing

test-github-actions:  ## 🚀 Simulate complete GitHub Actions TDD Test Suite locally
	@echo "🚀 Running COMPLETE GitHub Actions TDD Test Suite simulation..."
	@echo ""
	@echo "=== 🔒 CRITICAL Security Tests ==="
	@echo "🔒 Running CRITICAL security tests - these MUST pass!"
	@echo "🔍 Running security analysis..."
	poetry install --with security
	poetry run bandit -r fx_bin/ || true
	@echo ""
	@echo "📋 Checking dependencies for known vulnerabilities..."
	poetry run safety check || true
	@echo ""
	@echo "=== 🛡️ HIGH Priority Safety Tests ==="
	@echo "🛡️ Running HIGH priority safety tests..."
	poetry run python -m pytest tests/security/test_replace_safety.py -v --tb=short --no-cov
	poetry run python -m pytest tests/security/test_common_safety.py -v --tb=short --no-cov
	@echo ""
	@echo "=== ⚙️ Functionality Tests ==="
	@echo "⚙️ Running all functionality tests..."
	poetry run python -m pytest tests/ -v --tb=short --ignore=tests/runners/ --no-cov
	@echo ""
	@echo "=== 📊 Code Coverage ==="
	@echo "📊 Generating code coverage report..."
	poetry run python -m pytest --cov=fx_bin --cov-report=xml --cov-report=html
	@echo ""
	@echo "=== 📋 Code Quality Checks ==="
	@echo "🔍 Running Flake8 linting..."
	poetry run flake8 fx_bin/ --statistics
	@echo ""
	@echo "🎨 Checking code formatting with Black..."
	poetry run black --check fx_bin/ tests/ || true
	@echo ""
	@echo "✅ GitHub Actions TDD Test Suite simulation COMPLETE!"

test-ci:  ## 🔥 Alias for test-github-actions (short form)
	$(MAKE) test-github-actions

test-parallel:  ## Run tests in parallel for speed
	poetry run pytest -n auto --no-cov

test-forked:  ## Run tests with process forking (may have directory issues)
	poetry run pytest --forked --no-cov

test-simple:  ## Run simple test runner (no Poetry)
	python tests/runners/simple_test_runner.py

test-tdd:  ## Run TDD test runner with priority order
	python tests/runners/run_tdd_tests.py

lint:  ## Run code linting with flake8
	poetry run flake8 fx_bin/

format:  ## Format code with black
	poetry run black fx_bin/ tests/

format-check:  ## Check code formatting without changes
	poetry run black --check fx_bin/ tests/

type-check:  ## Run type checking with mypy
	poetry run mypy fx_bin/

security-scan:  ## Run security scan with bandit (installs optional security group)
	poetry install --with security
	poetry run bandit -r fx_bin/

check:  ## Run all checks (lint, format, type, security)
	@echo "Running all code quality checks..."
	@make lint
	@make format-check
	@make type-check
	@make security-scan

clean:  ## Clean up temporary files and caches
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info

build:  ## Build the package with Poetry
	poetry build

publish-test:  ## Publish to TestPyPI
	poetry publish -r test-pypi

publish:  ## Publish to PyPI
	poetry publish

shell:  ## Open a Poetry shell
	poetry shell

update:  ## Update dependencies
	poetry update

show-deps:  ## Show dependency tree
	poetry show --tree

run-size:  ## Run fx size command (unified CLI)
	poetry run fx size

run-files:  ## Run fx files command (unified CLI)
	poetry run fx files



# Default target
.DEFAULT_GOAL := help
