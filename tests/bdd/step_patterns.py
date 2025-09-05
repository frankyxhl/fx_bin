"""Reusable step definition patterns for BDD tests.

This module provides smart, reusable step patterns that can be applied
across different BDD scenarios with maximum code reuse and maintainability.
"""

from typing import List, Dict, Any, Optional, Callable
import re
from pathlib import Path
from dataclasses import dataclass
from pytest_bdd import parsers


# ==============================================================================
# STEP PATTERN TEMPLATES
# ==============================================================================


class StepPatternLibrary:
    """Library of reusable step definition patterns."""

    # Given step patterns
    GIVEN_PATTERNS = {
        "directory_with_files": 'I have a directory containing files with extensions "{extensions}"',
        "multiple_files_extension": 'I have multiple "{extension}" files with different {time_type} times',
        "specific_files": 'I have files "{file_list}"',
        "file_with_metadata": 'I have a file "{filename}" with known metadata',
        "count_files_extension": 'I have {count:d} files with "{extension}" extension',
        "empty_directory": "I have an empty directory",
        "directory_structure": "I have a directory structure",
        "restricted_permissions": "I have a directory with restricted permissions",
        "large_file_collection": "I have a directory with {count:d} files of various extensions",
        "mixed_case_files": 'I have files with extensions "{extensions}"',
    }

    # When step patterns
    WHEN_PATTERNS = {
        "run_command": 'I run "{command}"',
        "run_command_with_path": 'I run "{command}" {path}',
        "run_command_multiple_paths": 'I run "{command}" {dir1} {dir2}',
        "pipe_to_command": 'I pipe the results to "{command}"',
    }

    # Then step patterns
    THEN_PATTERNS = {
        "see_files_extension": 'I should see only files with "{extension}" extension',
        "see_multiple_extensions": 'I should see files with extensions "{extensions}"',
        "verify_sorting": "the results should be sorted by {sort_type} time ({order} first)",
        "verify_format": "the output should be in {format_type} format",
        "see_specific_count": "I should see exactly {count:d} results",
        "see_message": 'I should see a message "{message}"',
        "see_error": 'I should see an error message "{message}"',
        "exit_with_code": "the command should exit with status {exit_code:d}",
        "complete_within_time": "the command should complete within {seconds:d} seconds",
        "memory_usage_limit": "memory usage should remain under {memory:d}MB",
    }


# ==============================================================================
# SMART STEP GENERATORS
# ==============================================================================


class SmartStepGenerator:
    """Generates optimized step definitions with intelligent parameterization."""

    @staticmethod
    def generate_file_setup_step(extensions: List[str], count_range: tuple = (1, 50)):
        """Generate step for setting up files with specific extensions.

        Args:
            extensions: List of file extensions to support
            count_range: Min and max file counts to support

        Returns:
            Step definition function with intelligent parameterization
        """

        def step_implementation(file_builder, extensions_param, count=None):
            ext_list = [ext.strip().lower() for ext in extensions_param.split(",")]

            for i, ext in enumerate(ext_list):
                files_to_create = count or min(3, len(ext_list))
                for j in range(files_to_create):
                    file_builder(
                        f"test_{ext}_{j}.{ext}",
                        content=f"Sample {ext} content {j}",
                        created_offset_minutes=30 + i * 5 + j,
                    )

        return step_implementation

    @staticmethod
    def generate_command_execution_step(command_variants: List[str]):
        """Generate step for executing commands with variants.

        Args:
            command_variants: List of command patterns to support

        Returns:
            Step definition function with command parsing
        """

        def step_implementation(cli_runner, command_context, temp_directory, command):
            import os
            import time
            from fx_bin.cli import cli

            # Change to test directory
            os.chdir(temp_directory)

            # Parse and execute command
            command_parts = command.split()
            if command_parts[0] == "fx":
                command_parts = command_parts[1:]

            start_time = time.time()

            try:
                result = cli_runner.invoke(cli, command_parts, catch_exceptions=False)
                execution_time = time.time() - start_time

                command_context.update(
                    {
                        "last_exit_code": result.exit_code,
                        "last_output": result.output,
                        "last_error": None,
                        "execution_time": execution_time,
                    }
                )

            except Exception as e:
                execution_time = time.time() - start_time

                command_context.update(
                    {
                        "last_exit_code": 1,
                        "last_output": "",
                        "last_error": str(e),
                        "execution_time": execution_time,
                    }
                )

        return step_implementation

    @staticmethod
    def generate_output_verification_step(output_types: List[str]):
        """Generate step for verifying different output types.

        Args:
            output_types: Types of output to verify (simple, detailed, etc.)

        Returns:
            Step definition function with output parsing
        """

        def step_implementation(command_context, expected_format):
            output = command_context["last_output"]

            if expected_format == "simple":
                # Simple format: filenames only, no metadata
                for line in output.splitlines():
                    line = line.strip()
                    if line and not line.startswith(("Error:", "Warning:", "No files")):
                        assert not re.search(
                            r"\d{4}-\d{2}-\d{2}", line
                        ), f"Found timestamp: {line}"
                        assert not re.search(
                            r"\d+\s*(B|KB|MB|GB)", line
                        ), f"Found size: {line}"

            elif expected_format == "detailed":
                # Detailed format: should include metadata
                has_metadata = any(
                    re.search(r"\d{4}-\d{2}-\d{2}|\d+\s*(B|KB|MB|GB)", line)
                    for line in output.splitlines()
                )
                assert has_metadata, "Expected metadata in detailed format"

            else:
                raise ValueError(f"Unsupported format type: {expected_format}")

        return step_implementation


# ==============================================================================
# STEP PATTERN REUSE ANALYZER
# ==============================================================================


@dataclass
class StepUsageStats:
    """Statistics for step definition usage and reuse."""

    pattern: str
    usage_count: int
    reuse_percentage: float
    scenarios_using: List[str]


class StepReuseAnalyzer:
    """Analyzes step definition patterns for optimization opportunities."""

    def __init__(self):
        self.step_usage: Dict[str, StepUsageStats] = {}

    def analyze_feature_file(self, feature_file_path: Path) -> Dict[str, Any]:
        """Analyze a feature file for step reuse opportunities.

        Args:
            feature_file_path: Path to the Gherkin feature file

        Returns:
            Dictionary with analysis results
        """
        content = feature_file_path.read_text()

        # Extract scenarios and steps
        scenarios = self._extract_scenarios(content)
        steps = self._extract_all_steps(content)

        # Analyze step patterns
        step_patterns = self._identify_step_patterns(steps)
        reuse_opportunities = self._find_reuse_opportunities(step_patterns)

        return {
            "total_scenarios": len(scenarios),
            "total_steps": len(steps),
            "unique_step_patterns": len(step_patterns),
            "reuse_percentage": self._calculate_reuse_percentage(step_patterns),
            "optimization_suggestions": reuse_opportunities,
        }

    def _extract_scenarios(self, content: str) -> List[str]:
        """Extract scenario names from feature file content."""
        scenarios = []
        for line in content.splitlines():
            line = line.strip()
            if line.startswith(("Scenario:", "Scenario Outline:")):
                scenarios.append(line)
        return scenarios

    def _extract_all_steps(self, content: str) -> List[str]:
        """Extract all step definitions from feature file content."""
        steps = []
        for line in content.splitlines():
            line = line.strip()
            if line.startswith(("Given", "When", "Then", "And", "But")):
                steps.append(line)
        return steps

    def _identify_step_patterns(self, steps: List[str]) -> Dict[str, List[str]]:
        """Identify similar step patterns that could be parameterized."""
        patterns = {}

        for step in steps:
            # Normalize step by replacing specific values with placeholders
            normalized = self._normalize_step(step)

            if normalized not in patterns:
                patterns[normalized] = []
            patterns[normalized].append(step)

        return patterns

    def _normalize_step(self, step: str) -> str:
        """Normalize a step by replacing specific values with placeholders."""
        # Replace quoted strings with placeholder
        normalized = re.sub(r'"[^"]*"', '"{placeholder}"', step)

        # Replace numbers with placeholder
        normalized = re.sub(r"\b\d+\b", "{number}", normalized)

        # Replace file extensions
        normalized = re.sub(r"\b\w+\.\w+\b", "{filename}", normalized)

        return normalized

    def _find_reuse_opportunities(self, patterns: Dict[str, List[str]]) -> List[str]:
        """Find opportunities for step definition reuse."""
        opportunities = []

        for pattern, instances in patterns.items():
            if len(instances) > 1:
                opportunities.append(
                    f"Pattern '{pattern}' used {len(instances)} times - "
                    f"consider parameterization"
                )

        return opportunities

    def _calculate_reuse_percentage(self, patterns: Dict[str, List[str]]) -> float:
        """Calculate the percentage of step reuse."""
        total_steps = sum(len(instances) for instances in patterns.values())
        unique_patterns = len(patterns)

        if total_steps == 0:
            return 0.0

        return ((total_steps - unique_patterns) / total_steps) * 100


# ==============================================================================
# BDD BEST PRACTICE VALIDATORS
# ==============================================================================


class BDDQualityValidator:
    """Validates BDD scenarios against best practices."""

    def __init__(self):
        self.quality_rules = [
            self._check_scenario_independence,
            self._check_step_clarity,
            self._check_business_language,
            self._check_scenario_focus,
            self._validate_given_when_then_structure,
        ]

    def validate_scenario(self, scenario_text: str) -> Dict[str, Any]:
        """Validate a single scenario against quality rules."""
        issues = []
        score = 100

        for rule in self.quality_rules:
            rule_issues = rule(scenario_text)
            issues.extend(rule_issues)
            score -= len(rule_issues) * 10  # Deduct points for issues

        return {
            "score": max(0, score),
            "issues": issues,
            "quality_level": self._get_quality_level(score),
        }

    def _check_scenario_independence(self, scenario: str) -> List[str]:
        """Check if scenario is independent."""
        issues = []

        # Look for dependencies on other scenarios
        dependency_keywords = ["previous", "after", "before", "depends on"]
        if any(keyword in scenario.lower() for keyword in dependency_keywords):
            issues.append("Scenario appears to depend on other scenarios")

        return issues

    def _check_step_clarity(self, scenario: str) -> List[str]:
        """Check if steps are clear and specific."""
        issues = []

        # Look for vague language
        vague_terms = ["some", "various", "multiple", "several", "many"]
        for term in vague_terms:
            if term in scenario.lower() and not re.search(
                rf'{term}\s+"\w+"', scenario.lower()
            ):
                issues.append(f"Vague term '{term}' used without specificity")

        return issues

    def _check_business_language(self, scenario: str) -> List[str]:
        """Check if scenario uses business language."""
        issues = []

        # Look for technical implementation details
        technical_terms = ["database", "SQL", "API", "HTTP", "JSON", "XML"]
        for term in technical_terms:
            if term in scenario:
                issues.append(
                    f"Technical term '{term}' found - consider business language"
                )

        return issues

    def _check_scenario_focus(self, scenario: str) -> List[str]:
        """Check if scenario focuses on a single business rule."""
        issues = []

        # Count the number of different assertions (Then steps)
        then_count = len(re.findall(r"^\s*(Then|And)\s+", scenario, re.MULTILINE))

        if then_count > 5:
            issues.append(f"Scenario has {then_count} assertions - consider splitting")

        return issues

    def _validate_given_when_then_structure(self, scenario: str) -> List[str]:
        """Validate proper Given-When-Then structure."""
        issues = []

        # Check for multiple When steps (usually indicates multiple actions)
        when_count = len(re.findall(r"^\s*When\s+", scenario, re.MULTILINE))

        if when_count > 1:
            issues.append(
                "Multiple When steps found - scenario should have single action"
            )

        # Check for missing Then steps
        then_count = len(re.findall(r"^\s*Then\s+", scenario, re.MULTILINE))

        if then_count == 0:
            issues.append(
                "No Then steps found - scenario should have observable outcome"
            )

        return issues

    def _get_quality_level(self, score: int) -> str:
        """Get quality level based on score."""
        if score >= 90:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 50:
            return "Fair"
        else:
            return "Needs Improvement"


# ==============================================================================
# FIXTURE BUILDERS FOR COMMON PATTERNS
# ==============================================================================


class FixtureBuilder:
    """Builds common fixture patterns for BDD tests."""

    @staticmethod
    def create_file_collection_fixture(extensions: List[str], count_per_type: int = 3):
        """Create fixture for file collections by extension."""

        def fixture(file_builder):
            files = {}

            for i, ext in enumerate(extensions):
                for j in range(count_per_type):
                    key = f"{ext}_{j}"
                    files[key] = file_builder(
                        f"sample_{j}.{ext}",
                        content=f"Sample {ext} content {j}",
                        created_offset_minutes=60 + i * 10 + j,
                    )

            return files

        return fixture

    @staticmethod
    def create_directory_structure_fixture(structure: Dict[str, Any]):
        """Create fixture for complex directory structures."""

        def fixture(directory_builder):
            return directory_builder(structure)

        return fixture

    @staticmethod
    def create_performance_test_fixture(file_count: int, extensions: List[str]):
        """Create fixture for performance testing with many files."""

        def fixture(file_builder):
            files = []

            for i in range(file_count):
                ext = extensions[i % len(extensions)]
                test_file = file_builder(
                    f"perf_test_{i:04d}.{ext}",
                    content=f"Performance test content {i}",
                    created_offset_minutes=file_count - i,  # Spread over time
                )
                files.append(test_file)

            return files

        return fixture


# ==============================================================================
# UTILITIES
# ==============================================================================


def extract_step_parameters(step_text: str, pattern: str) -> Dict[str, str]:
    """Extract parameters from step text using pattern."""
    # Convert pytest-bdd pattern to regex
    regex_pattern = pattern.replace("{", "(?P<").replace("}", '>[^"\\s]+)')
    regex_pattern = regex_pattern.replace('"{', '"(?P<').replace('}"', '>[^"]*)"')

    match = re.match(regex_pattern, step_text)
    if match:
        return match.groupdict()

    return {}


def validate_step_definition_coverage(
    feature_file: Path, step_files: List[Path]
) -> Dict[str, Any]:
    """Validate that all steps in feature file have corresponding definitions."""
    # Read feature file and extract steps
    feature_content = feature_file.read_text()
    feature_steps = []

    for line in feature_content.splitlines():
        line = line.strip()
        if line.startswith(("Given", "When", "Then", "And", "But")):
            feature_steps.append(line)

    # Read step definition files and extract patterns
    defined_patterns = []

    for step_file in step_files:
        content = step_file.read_text()

        # Extract pytest-bdd step patterns
        patterns = re.findall(r'@(?:given|when|then)\([\'"]([^\'"]*)[\'"]', content)
        patterns.extend(re.findall(r'parsers\.parse\([\'"]([^\'"]*)[\'"]', content))

        defined_patterns.extend(patterns)

    # Check coverage
    undefined_steps = []
    for step in feature_steps:
        if not any(step_matches_pattern(step, pattern) for pattern in defined_patterns):
            undefined_steps.append(step)

    coverage_percentage = (
        (len(feature_steps) - len(undefined_steps)) / len(feature_steps)
    ) * 100

    return {
        "total_steps": len(feature_steps),
        "defined_steps": len(feature_steps) - len(undefined_steps),
        "undefined_steps": undefined_steps,
        "coverage_percentage": coverage_percentage,
    }


def step_matches_pattern(step: str, pattern: str) -> bool:
    """Check if a step matches a given pattern."""
    # Simple pattern matching - in real implementation would be more sophisticated
    # Convert pattern placeholders to wildcards
    regex_pattern = pattern
    regex_pattern = re.sub(r"\{[^}]*\}", r".*", regex_pattern)
    regex_pattern = regex_pattern.replace('"', r'[\'"]')

    return bool(re.search(regex_pattern, step, re.IGNORECASE))


# ==============================================================================
# DOCUMENTATION GENERATORS
# ==============================================================================


class BDDDocumentationGenerator:
    """Generates living documentation from BDD scenarios."""

    def generate_feature_summary(self, feature_file: Path) -> str:
        """Generate a summary document for a feature file."""
        content = feature_file.read_text()

        # Extract feature information
        feature_match = re.search(r"Feature:\s*(.+)", content)
        feature_name = feature_match.group(1) if feature_match else "Unnamed Feature"

        # Extract scenarios
        scenarios = []
        for match in re.finditer(
            r"^\s*(@[\w-]+\s+)*Scenario:\s*(.+)", content, re.MULTILINE
        ):
            tags = match.group(1).strip() if match.group(1) else ""
            name = match.group(2).strip()
            scenarios.append((tags, name))

        # Generate summary
        summary = f"""# {feature_name}

## Overview
Total scenarios: {len(scenarios)}

## Scenario Coverage
"""

        for tags, name in scenarios:
            priority = (
                "🔥 Critical"
                if "@critical" in tags
                else "⚠️  Important" if "@smoke" in tags else "📋 Standard"
            )
            summary += f"- {priority}: {name}\n"

        return summary

    def generate_step_library_docs(self, step_files: List[Path]) -> str:
        """Generate documentation for step definition library."""
        docs = """# Step Definition Library

This document describes the reusable step definitions available for BDD tests.

## Given Steps (Setup)
"""

        for step_file in step_files:
            content = step_file.read_text()

            # Extract Given steps
            given_patterns = re.findall(r'@given\([\'"]([^\'"]*)[\'"]', content)
            for pattern in given_patterns:
                docs += f"- `{pattern}`\n"

        docs += "\n## When Steps (Actions)\n"

        for step_file in step_files:
            content = step_file.read_text()

            # Extract When steps
            when_patterns = re.findall(r'@when\([\'"]([^\'"]*)[\'"]', content)
            for pattern in when_patterns:
                docs += f"- `{pattern}`\n"

        docs += "\n## Then Steps (Assertions)\n"

        for step_file in step_files:
            content = step_file.read_text()

            # Extract Then steps
            then_patterns = re.findall(r'@then\([\'"]([^\'"]*)[\'"]', content)
            for pattern in then_patterns:
                docs += f"- `{pattern}`\n"

        return docs
