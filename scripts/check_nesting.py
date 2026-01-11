#!/usr/bin/env python3
"""Check nesting depth in Python source files.

Uses AST analysis to count nesting levels. Nesting depth is defined as:
- Each if/for/while/try/with/match/lambda adds 1 level
- Note: else is part of if node, not counted separately
- Function/class definitions are NOT counted (only control flow)
- Nested functions/classes inside functions reset the counter

Usage:
    python scripts/check_nesting.py fx_bin/cli.py
    python scripts/check_nesting.py fx_bin/cli.py fx_bin/organize_functional.py
    python scripts/check_nesting.py fx_bin/

Exit codes:
    0: All files have nesting <= 4
    1: Some files exceed 4 levels
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple


class NestingAnalyzer(ast.NodeVisitor):
    """AST visitor that counts maximum nesting depth."""

    def __init__(self, filename: str):
        self.filename = filename
        self.max_depth = 0
        self.current_depth = 0
        self.violations: List[Tuple[int, int, str]] = []  # (line, depth, code_snippet)

    def _get_code_snippet(self, node: ast.AST) -> str:
        """Get a short code snippet for reporting."""
        if hasattr(node, 'lineno'):
            return f"{node.__class__.__name__}"
        return ""

    def _enter_nested_scope(self, node: ast.AST):
        """Enter a nested scope (if/for/while/try/with/match)."""
        self.current_depth += 1
        if self.current_depth > self.max_depth:
            self.max_depth = self.current_depth

        if self.current_depth > 4:
            snippet = self._get_code_snippet(node)
            if hasattr(node, 'lineno'):
                self.violations.append((node.lineno, self.current_depth, snippet))

    def _exit_nested_scope(self, node: ast.AST):
        """Exit a nested scope."""
        self.current_depth -= 1

    # Control flow nodes that increase nesting
    def visit_If(self, node: ast.If):
        self._enter_nested_scope(node)
        self.generic_visit(node)
        self._exit_nested_scope(node)

    def visit_For(self, node: ast.For):
        self._enter_nested_scope(node)
        self.generic_visit(node)
        self._exit_nested_scope(node)

    def visit_While(self, node: ast.While):
        self._enter_nested_scope(node)
        self.generic_visit(node)
        self._exit_nested_scope(node)

    def visit_Try(self, node: ast.Try):
        self._enter_nested_scope(node)
        self.generic_visit(node)
        self._exit_nested_scope(node)

    def visit_With(self, node: ast.With):
        self._enter_nested_scope(node)
        self.generic_visit(node)
        self._exit_nested_scope(node)

    def visit_Match(self, node: ast.Match):
        self._enter_nested_scope(node)
        self.generic_visit(node)
        self._exit_nested_scope(node)

    # Function/Class definitions reset depth counter
    def visit_FunctionDef(self, node: ast.FunctionDef):
        outer_depth = self.current_depth
        self.current_depth = 0  # Reset for function body
        self.generic_visit(node)
        self.current_depth = outer_depth  # Restore outer depth

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        outer_depth = self.current_depth
        self.current_depth = 0
        self.generic_visit(node)
        self.current_depth = outer_depth

    def visit_ClassDef(self, node: ast.ClassDef):
        outer_depth = self.current_depth
        self.current_depth = 0
        self.generic_visit(node)
        self.current_depth = outer_depth

    # Lambda expressions are counted as nested
    def visit_Lambda(self, node: ast.Lambda):
        self._enter_nested_scope(node)
        self.generic_visit(node)
        self._exit_nested_scope(node)


def check_file(filepath: Path) -> Tuple[int, List[Tuple[int, int, str]]]:
    """Check a single file for nesting violations.

    Returns:
        Tuple of (max_depth, violations)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()

        tree = ast.parse(source, filename=str(filepath))
        analyzer = NestingAnalyzer(str(filepath))
        analyzer.visit(tree)

        return analyzer.max_depth, analyzer.violations
    except SyntaxError as e:
        print(f"Warning: Syntax error in {filepath}: {e}", file=sys.stderr)
        return 0, []
    except Exception as e:
        print(f"Warning: Error parsing {filepath}: {e}", file=sys.stderr)
        return 0, []


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/check_nesting.py <file_or_directory> [<file_or_directory> ...]", file=sys.stderr)
        print("\nExample:", file=sys.stderr)
        print("  python scripts/check_nesting.py fx_bin/cli.py", file=sys.stderr)
        print("  python scripts/check_nesting.py fx_bin/cli.py fx_bin/organize_functional.py", file=sys.stderr)
        print("  python scripts/check_nesting.py fx_bin/", file=sys.stderr)
        sys.exit(2)

    files = []
    for arg in sys.argv[1:]:
        target = Path(arg)
        if target.is_file():
            files.append(target)
        elif target.is_dir():
            files.extend(sorted(target.rglob("*.py")))
        else:
            print(f"Error: {target} is not a valid file or directory", file=sys.stderr)
            sys.exit(2)

    max_nesting_overall = 0
    all_violations = []

    for filepath in files:
        max_depth, violations = check_file(filepath)
        max_nesting_overall = max(max_nesting_overall, max_depth)
        all_violations.extend([(filepath, *v) for v in violations])

        if violations:
            print(f"{filepath}: max depth {max_depth} ✗")
            for line, depth, snippet in violations:
                print(f"  Line {line}: depth {depth} ({snippet})")
        else:
            print(f"{filepath}: max depth {max_depth} ✓")

    print(f"\nOverall maximum nesting: {max_nesting_overall}")

    if all_violations:
        print(f"\n❌ Found {len(all_violations)} violations (nesting > 4)")
        sys.exit(1)
    else:
        print("\n✅ All files have nesting ≤ 4")
        sys.exit(0)


if __name__ == "__main__":
    main()
