#!/usr/bin/env python3
"""Check cyclomatic complexity of Python source files.

Cyclomatic complexity is calculated using McCabe's formula:
  Complexity = 1 (base) + number of decision points

Decision points counted:
- if/elif/else (each elif adds 1, else does NOT add - it's part of if)
- for/while loops
- try statements (1 for the try itself + 1 for each except handler)
- with statements
- match statements (each case adds 1)
- Boolean operations (each and/or operator adds 1)

Boundary behavior:
- Nested functions/classes/lambda STOP recursion - each function is counted separately
- This means extracting a helper function WILL reduce the parent's complexity
- This aligns with standard McCabe calculation and refactoring best practices

Note on elif:
- elif is modeled as if nested in else, so each elif adds 1 complexity
- else itself does NOT add complexity (it's the default path)

Per-function thresholds:
- fx_bin/cli.py:organize: 50 (special case for large orchestrator function)
- All other functions: 15

Usage:
    python3 scripts/check_complexity.py fx_bin/cli.py
    python3 scripts/check_complexity.py fx_bin/cli.py fx_bin/organize_functional.py

Exit codes:
    0: All functions have complexity within their thresholds
    1: Some functions exceed their thresholds
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class ComplexityAnalyzer(ast.NodeVisitor):
    """AST visitor that calculates cyclomatic complexity per function."""

    def __init__(self, filename: str):
        self.filename = filename
        self.function_complexity: Dict[str, int] = {}
        self.class_stack: List[str] = []
        self.function_stack: List[str] = []

    def _get_full_name(self, name: str) -> str:
        """Get full qualified name including class path."""
        if self.class_stack:
            return f"{'.'.join(self.class_stack)}.{name}"
        return name

    def _count_decision_points(self, node: ast.AST) -> int:
        """Count decision points in a node.

        Stops at function/class/lambda boundaries - nested functions are
        counted separately, not included in parent function complexity.
        """
        count = 0

        # Count if/for/while/try/with/match statements
        if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.Match)):
            count += 1

        # Count boolean operations (and/or)
        if isinstance(node, ast.BoolOp):
            # Each 'and'/'or' operator adds a decision point
            count += len(node.values) - 1

        # Count match cases (each case is a branch)
        if isinstance(node, ast.Match):
            # Each case adds 1, subtract 1 for the first/default path
            # This gives us: N cases = N-1 additional decision points
            count += len(node.cases) - 1

        # Count except handlers
        if isinstance(node, ast.Try):
            count += len(node.handlers)

        # Recursively count in children, BUT stop at function/class/lambda boundaries
        for child in ast.iter_child_nodes(node):
            # Don't descend into nested functions/classes/lambda - they're counted separately
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
                continue
            count += self._count_decision_points(child)

        return count

    def _calculate_function_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity for a function body."""
        # Base complexity is 1
        # Add 1 for each decision point
        return 1 + self._count_decision_points(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        full_name = self._get_full_name(node.name)
        self.function_stack.append(node.name)

        complexity = self._calculate_function_complexity(node)
        self.function_complexity[full_name] = complexity

        # Don't recurse into nested functions - they're counted separately
        self.generic_visit(node)

        self.function_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        full_name = self._get_full_name(node.name)
        self.function_stack.append(node.name)

        complexity = self._calculate_function_complexity(node)
        self.function_complexity[full_name] = complexity

        self.generic_visit(node)
        self.function_stack.pop()

    def visit_ClassDef(self, node: ast.ClassDef):
        self.class_stack.append(node.name)
        self.generic_visit(node)
        self.class_stack.pop()


def check_file(filepath: Path) -> Tuple[int, Dict[str, int]]:
    """Check a single file for complexity violations.

    Returns:
        Tuple of (max_complexity, {function_name: complexity})
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()

        tree = ast.parse(source, filename=str(filepath))
        analyzer = ComplexityAnalyzer(str(filepath))
        analyzer.visit(tree)

        max_complexity = max(analyzer.function_complexity.values()) if analyzer.function_complexity else 0
        return max_complexity, analyzer.function_complexity
    except SyntaxError as e:
        print(f"Warning: Syntax error in {filepath}: {e}", file=sys.stderr)
        return 0, {}
    except Exception as e:
        print(f"Warning: Error parsing {filepath}: {e}", file=sys.stderr)
        return 0, {}


def get_function_threshold(filepath: Path, func_name: str) -> int:
    """Get complexity threshold for a specific function.

    Special cases:
    - fx_bin/cli.py:organize → 50 (large orchestrator function)
    - fx_bin/organize_functional.py:execute_organize → 50 (large orchestrator function)
    - All other functions → 15
    """
    if str(filepath).endswith("fx_bin/cli.py") and func_name == "organize":
        return 50
    if str(filepath).endswith("fx_bin/organize_functional.py") and func_name == "execute_organize":
        return 50
    return 15


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/check_complexity.py <file_or_directory> [<file_or_directory> ...]", file=sys.stderr)
        print("\nExample:", file=sys.stderr)
        print("  python3 scripts/check_complexity.py fx_bin/cli.py", file=sys.stderr)
        print("  python3 scripts/check_complexity.py fx_bin/cli.py fx_bin/organize_functional.py", file=sys.stderr)
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

    max_complexity_overall = 0
    all_violations = []

    for filepath in files:
        max_complexity, functions = check_file(filepath)
        max_complexity_overall = max(max_complexity_overall, max_complexity)

        # Check each function against its specific threshold
        violations = {}
        for func_name, cc in functions.items():
            threshold = get_function_threshold(filepath, func_name)
            if cc > threshold:
                violations[func_name] = (cc, threshold)

        all_violations.extend([(filepath, name, cc, thresh) for name, (cc, thresh) in violations.items()])

        if violations:
            print(f"{filepath}: max complexity {max_complexity} ✗")
            for func_name, (cc, thresh) in violations.items():
                print(f"  {func_name}: complexity {cc} (threshold: {thresh})")
        else:
            print(f"{filepath}: max complexity {max_complexity} ✓")

    print(f"\nOverall maximum complexity: {max_complexity_overall}")

    if all_violations:
        print(f"\n❌ Found {len(all_violations)} functions exceeding their thresholds")
        sys.exit(1)
    else:
        print(f"\n✅ All functions have complexity within their thresholds")
        sys.exit(0)


if __name__ == "__main__":
    main()
