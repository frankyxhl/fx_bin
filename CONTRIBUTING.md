# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

## Types of Contributions

### Report Bugs

Report bugs at https://github.com/frankyxhl/fx_bin/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

### Write Documentation

fx-bin could always use more documentation, whether as part of the
official fx-bin docs, in docstrings, or even on the web in blog posts,
articles, and such.

### Submit Feedback

The best way to send feedback is to file an issue at https://github.com/frankyxhl/fx_bin/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

## Get Started!

Ready to contribute? Here's how to set up `fx_bin` for local development.

1. Fork the `fx_bin` repo on GitHub.
2. Clone your fork locally:

    ```bash
    git clone git@github.com:your_name_here/fx_bin.git
    ```

3. Install your local copy using Poetry (recommended):

    ```bash
    cd fx_bin/
    poetry install --with dev
    poetry shell
    ```

    Or using pip:

    ```bash
    cd fx_bin/
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -e .
    pip install -r requirements_dev.txt
    ```

4. Create a branch for local development:

    ```bash
    git checkout -b name-of-your-bugfix-or-feature
    ```

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass the tests and code quality checks:

    ```bash
    # Run tests
    poetry run pytest
    
    # Run code quality checks
    poetry run black fx_bin/ tests/
    poetry run flake8 fx_bin/
    poetry run mypy fx_bin/
    
    # Run security checks
    poetry run bandit -r fx_bin/
    poetry run safety check
    ```

6. Commit your changes and push your branch to GitHub:

    ```bash
    git add .
    git commit -m "Your detailed description of your changes."
    git push origin name-of-your-bugfix-or-feature
    ```

7. Submit a pull request through the GitHub website.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.md.
3. The pull request should work for Python 3.11+ and ensure that the tests pass for all supported Python versions.
4. Make sure that security tests pass, especially if you're modifying file operations.

## Tips

To run a subset of tests:

```bash
# Run specific test file
poetry run pytest tests/test_cli.py -v

# Run only security tests
poetry run pytest tests/test_*security*.py -v

# Run fast tests only (exclude slow integration tests)
poetry run pytest -m "not slow"

# Run with coverage
poetry run pytest --cov=fx_bin --cov-report=html
```

## Development Workflow

### Code Quality Standards

- Follow PEP 8 style guidelines
- Use Black for code formatting
- Ensure flake8 linting passes
- Add type hints where appropriate
- Write comprehensive tests for new features
- Maintain or improve code coverage

### Security Considerations

- All file operations must include path traversal protection
- Validate and sanitize user inputs
- Add security tests for any new file handling code
- Run security scans before submitting PRs

### Testing Requirements

- Write unit tests for new functionality
- Add integration tests for complex features
- Include security tests for file operations
- Test edge cases and error conditions
- Ensure cross-platform compatibility

## Deploying

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed (including an entry in CHANGELOG.md).

```bash
# Update version and create tag
poetry version patch  # or minor/major
git add pyproject.toml
git commit -m "Bump version to $(poetry version -s)"
git tag v$(poetry version -s)
git push
git push --tags

# Build and publish
poetry build
poetry publish
```

## Development Environment Setup

### Prerequisites

- Python 3.11 or higher
- Poetry (recommended) or pip
- Git

### Recommended Tools

- **Code Editor**: VS Code with Python extension
- **Testing**: pytest for testing framework
- **Code Quality**: Black, flake8, mypy
- **Security**: bandit, safety

### Project Structure

```
fx_bin/
├── fx_bin/              # Main package
│   ├── cli.py           # Unified CLI entry point
│   ├── common.py        # Shared utilities
│   ├── size.py          # Size analyzer
│   ├── files.py         # File counter
│   ├── find_files.py    # File finder
│   ├── filter.py        # File filter
│   ├── replace.py       # Text replacement
│   ├── root.py          # Git root finder
│   └── today.py         # Daily workspace manager
├── tests/               # Test suite
├── docs/                # Documentation
└── pyproject.toml       # Project configuration
```

## Questions?

If you have any questions about contributing, feel free to:

- Open an issue for discussion
- Start a discussion on GitHub
- Contact the maintainers

Thank you for your interest in contributing to fx-bin!