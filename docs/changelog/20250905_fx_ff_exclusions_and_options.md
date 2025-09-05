# Session Changelog: 2025-09-05 - fx ff exclusions and options

## Summary
Introduced practical defaults and options to the `fx ff` finder to improve speed and control in real repositories.

## Changes
- Default exclusions: `.git`, `.venv`, `node_modules` are pruned during traversal.
- New options:
  - `--include-ignored`: include the default-ignored directories when needed.
  - `--exclude NAME`: repeatable; supports glob patterns (e.g., `*.log`, `build*`).
- CLI help updated with new examples.
- Documentation updated: README.md, README.rst, and docs/quick-start.md.
- Tests added: `tests/test_ff_exclude.py`.

## Rationale
Skipping heavy directories drastically reduces I/O for common project layouts, providing a noticeable speed gain over micro-optimizing loops. The `--exclude` flag offers fine-grained control without adding complexity.

## Migration
No breaking changes. Existing `fx ff KEYWORD` continues to work. Use `--include-ignored` or `--exclude` as needed.

