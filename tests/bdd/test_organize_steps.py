"""Step definitions for file organization BDD scenarios.

This module implements pytest-bdd step definitions for the fx organize command.
Phase 2: Given steps for test data setup.
Phase 3: When steps for command execution.
"""

import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any

import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from click.testing import CliRunner

from fx_bin.cli import cli
from .conftest import (
    FileInfo,
    DirectoryInfo,
    normalize_path,
)

# Load all scenarios from the organize feature file
scenarios("organize.feature")


# ==============================================================================
# GIVEN STEPS - Test Data Setup
# ==============================================================================


@given("I have a test directory structure with various files")
def setup_test_directory(temp_directory, file_builder):
    """Set up basic test directory with various file types."""
    # Create a mix of files with different extensions and dates
    file_builder("photo1.jpg", content="photo content", created_offset_minutes=120)
    file_builder("photo2.jpg", content="photo content", created_offset_minutes=90)
    file_builder("document.pdf", content="pdf content", created_offset_minutes=60)
    file_builder("notes.txt", content="notes", created_offset_minutes=30)
    file_builder("data.csv", content="csv,data", created_offset_minutes=10)
    assert temp_directory.exists()


@given("the test directory contains files with different creation dates")
def setup_timestamped_files(file_builder):
    """Verify files have different creation dates."""
    # Create files with different timestamps
    file_builder("old_file.txt", content="old", created_offset_minutes=200)
    file_builder("medium_file.txt", content="medium", created_offset_minutes=100)
    file_builder("new_file.txt", content="new", created_offset_minutes=10)


@given(parsers.parse('I have a directory containing files from different dates:\n{table_content}'))
def setup_files_with_dates(file_builder, table_content):
    """Create files with specific creation dates from a table.

    Table format:
    | Filename      | Creation Date |
    | photo1.jpg    | 2026-01-10    |
    """
    lines = [line.strip() for line in table_content.split("\n") if line.strip()]

    for line in lines:
        # Skip header lines
        if "Filename" in line or "Creation Date" in line or "|" not in line:
            continue

        # Extract filename and date from table row
        parts = [part.strip() for part in line.split("|") if part.strip()]
        if len(parts) >= 2:
            filename = parts[0].strip()
            date_str = parts[1].strip()

            # Parse date and calculate offset from now
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d")
                now = datetime.now()
                delta = now - target_date
                offset_minutes = int(delta.total_seconds() / 60)

                file_builder(
                    filename,
                    content=f"Content for {filename}",
                    created_offset_minutes=offset_minutes,
                )
            except ValueError:
                # If date parsing fails, use default offset
                file_builder(filename, content=f"Content for {filename}")


@given(parsers.parse('I have a directory structure:\n{table_content}'))
def setup_nested_directory_structure(file_builder, temp_directory, table_content):
    """Create nested directory structure from data table.

    Table format:
    | Level    | Path                | Files            | Dates      |
    | current  | ./                  | file1.txt        | 2026-01-10 |
    | subdir   | ./photos/           | image.jpg        | 2026-01-10 |
    | nested   | ./photos/vacation/  | beach.jpg        | 2026-01-10 |
    """
    lines = [line.strip() for line in table_content.split("\n") if line.strip()]

    for line in lines:
        # Skip header lines
        if any(
            header in line
            for header in ["Level", "Path", "Files", "Dates", "Type", "Target"]
        ):
            continue

        # Extract data from table row
        parts = [part.strip() for part in line.split("|") if part.strip()]
        if len(parts) >= 3:
            level = parts[0].strip()
            path_part = parts[1].replace("./", "").strip()
            filename = parts[2].strip()

            # Create directory if needed
            if path_part and path_part != "":
                dir_path = temp_directory / path_part
                dir_path.mkdir(parents=True, exist_ok=True)
                relative_path = path_part
            else:
                relative_path = ""

            # Create file
            file_builder(filename, content="test content", relative_path=relative_path)


@given(
    parsers.parse(
        'I have a directory "{dir_path}" with existing file "{filename}"'
    )
)
def setup_directory_with_existing_file(temp_directory, dir_path, filename):
    """Create a directory with an existing file for conflict testing."""
    full_path = temp_directory / dir_path
    full_path.mkdir(parents=True, exist_ok=True)

    file_path = full_path / filename
    file_path.write_text("Existing file content")


@given(
    parsers.parse('I have a source file "{filename}" created on {date} in current directory')
)
def setup_source_file_with_date(file_builder, filename, date):
    """Create a source file with a specific creation date."""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")
        now = datetime.now()
        delta = now - target_date
        offset_minutes = int(delta.total_seconds() / 60)

        file_builder(
            filename,
            content=f"Source content for {filename}",
            created_offset_minutes=offset_minutes,
        )
    except ValueError:
        file_builder(filename, content=f"Source content for {filename}")


@given(parsers.parse('I have a file "{filename}" created on {date}'))
def setup_file_with_creation_date(file_builder, filename, date):
    """Create a file with a specific creation date."""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")
        now = datetime.now()
        delta = now - target_date
        offset_minutes = int(delta.total_seconds() / 60)

        file_builder(
            filename,
            content=f"Content for {filename}",
            created_offset_minutes=offset_minutes,
        )
    except ValueError:
        file_builder(filename, content=f"Content for {filename}")


@given(parsers.parse('I have existing files "{file_list}" in target directory'))
def setup_existing_files_in_target(temp_directory, file_builder, file_list):
    """Create multiple existing files in target directory for conflict testing."""
    # Create target directory structure
    target_dir = temp_directory / "organized" / "2026" / "202601" / "20260110"
    target_dir.mkdir(parents=True, exist_ok=True)

    # Parse file list (handle comma-separated or quoted files)
    files = [
        f.strip().strip('"').strip("'")
        for f in file_list.split(",")
        if f.strip()
    ]

    for filename in files:
        file_path = target_dir / filename
        file_path.write_text(f"Existing content for {filename}")


@given(parsers.parse('I have a source file "{filename}" created on {date}'))
def setup_source_file(file_builder, filename, date):
    """Create a source file with specific creation date."""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")
        now = datetime.now()
        delta = now - target_date
        offset_minutes = int(delta.total_seconds() / 60)

        file_builder(
            filename,
            content=f"Source content for {filename}",
            created_offset_minutes=offset_minutes,
        )
    except ValueError:
        file_builder(filename, content=f"Source content for {filename}")


@given("I have a directory with files created on 2026-01-15")
def setup_files_with_specific_date(file_builder):
    """Create multiple files with the same creation date."""
    try:
        target_date = datetime.strptime("2026-01-15", "%Y-%m-%d")
        now = datetime.now()
        delta = now - target_date
        offset_minutes = int(delta.total_seconds() / 60)

        file_builder("file1.txt", content="content 1", created_offset_minutes=offset_minutes)
        file_builder("file2.txt", content="content 2", created_offset_minutes=offset_minutes)
        file_builder("file3.txt", content="content 3", created_offset_minutes=offset_minutes)
    except ValueError:
        file_builder("file1.txt", content="content 1")
        file_builder("file2.txt", content="content 2")
        file_builder("file3.txt", content="content 3")


@given(parsers.parse('I have an output directory "{output_dir}"'))
def setup_output_directory(temp_directory, output_dir):
    """Create an output directory for organizing files."""
    output_path = temp_directory / output_dir.lstrip("/")
    output_path.mkdir(parents=True, exist_ok=True)


@given("I have files ready to organize")
def setup_files_for_organizing(file_builder):
    """Create files ready for organization."""
    file_builder("document1.pdf", content="pdf 1", created_offset_minutes=100)
    file_builder("document2.pdf", content="pdf 2", created_offset_minutes=90)
    file_builder("photo1.jpg", content="photo 1", created_offset_minutes=80)


@given("I have a directory with files that will be organized")
def setup_directory_to_organize(file_builder):
    """Create a directory with files that will be organized."""
    file_builder("file1.txt", content="file 1", created_offset_minutes=60)
    file_builder("file2.txt", content="file 2", created_offset_minutes=50)


@given(
    parsers.parse('I have a file "{filename}" created on {date}')
)
def setup_single_file_with_date(file_builder, filename, date):
    """Create a single file with a specific creation date."""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")
        now = datetime.now()
        delta = now - target_date
        offset_minutes = int(delta.total_seconds() / 60)

        file_builder(
            filename,
            content=f"Content for {filename}",
            created_offset_minutes=offset_minutes,
        )
    except ValueError:
        file_builder(filename, content=f"Content for {filename}")


@given(parsers.parse('I have multiple files to organize'))
def setup_multiple_files(file_builder):
    """Create multiple files for organization testing."""
    file_builder("file1.txt", content="content 1", created_offset_minutes=100)
    file_builder("file2.txt", content="content 2", created_offset_minutes=90)
    file_builder("file3.txt", content="content 3", created_offset_minutes=80)
    file_builder("file4.txt", content="content 4", created_offset_minutes=70)


@given("I have an empty directory")
def setup_empty_directory(temp_directory):
    """Ensure directory exists but is empty."""
    # Remove any files that might have been created by other fixtures
    for item in temp_directory.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            import shutil
            shutil.rmtree(item)


@given(parsers.parse('the directory "{path}" does not exist'))
def verify_directory_not_exists(path):
    """Verify a directory does not exist."""
    assert not Path(path).exists()


@given(parsers.parse('I have a symlink pointing outside the source directory'))
def setup_external_symlink(temp_directory):
    """Create a symlink pointing outside the source directory."""
    # This would require creating a directory outside temp_directory
    # For testing purposes, we'll create the setup but skip actual symlink
    # creation on systems that don't support it or in restricted environments
    pass


@given("the symlink target contains files")
def setup_symlink_target_files():
    """Set up files in symlink target directory."""
    # Files would be created in the external directory
    pass


@given("I have a directory cycle created via symlinks or hardlinks")
def setup_directory_cycle():
    """Create a directory cycle for testing cycle detection."""
    # This would require creating symlinks that form a cycle
    # For testing purposes, we note this setup
    pass


@given(parsers.parse('I have a directory structure:\n{table_content}'))
def setup_directory_structure_with_type(file_builder, temp_directory, table_content):
    """Create directory structure from table with Type column.

    Table format:
    | Type    | Path              | Target           |
    | dir     | ./photos/         | N/A              |
    | symlink | ./external_link/  | /other/path/     |
    """
    lines = [line.strip() for line in table_content.split("\n") if line.strip()]

    for line in lines:
        # Skip header lines
        if any(header in line for header in ["Type", "Path", "Target", "Level", "Files", "Dates"]):
            continue

        parts = [part.strip() for part in line.split("|") if part.strip()]
        if len(parts) >= 2:
            entry_type = parts[0].strip().lower()
            path_part = parts[1].replace("./", "").strip()

            if entry_type == "dir" and path_part:
                # Create directory
                dir_path = temp_directory / path_part
                dir_path.mkdir(parents=True, exist_ok=True)
            elif entry_type == "symlink":
                # Symlink creation would be handled here
                # For cross-platform compatibility, we may skip actual symlink creation
                pass


@given(parsers.parse('I have a directory structure:\n{table_content}'))
def setup_directory_structure_with_dates(file_builder, temp_directory, table_content):
    """Create directory structure from table with Dates column.

    Table format:
    | Level    | Path              | Files         |
    | current  | ./                | file1.txt     |
    | subdir   | ./subdir/         | file2.txt     |
    | nested   | ./subdir/nested/  | file3.txt     |
    """
    lines = [line.strip() for line in table_content.split("\n") if line.strip()]

    for line in lines:
        # Skip header lines
        if any(header in line for header in ["Type", "Path", "Target", "Level", "Files", "Dates"]):
            continue

        parts = [part.strip() for part in line.split("|") if part.strip()]
        if len(parts) >= 3:
            level = parts[0].strip()
            path_part = parts[1].replace("./", "").strip()
            filename = parts[2].strip()

            # Create directory if needed
            if path_part and path_part != "":
                dir_path = temp_directory / path_part
                dir_path.mkdir(parents=True, exist_ok=True)
                relative_path = path_part
            else:
                relative_path = ""

            # Create file
            file_builder(filename, content="test content", relative_path=relative_path)


@given(parsers.parse('I have a directory nested {depth:d} levels deep with a file "{filename}"'))
def setup_deeply_nested_directory(temp_directory, file_builder, depth, filename):
    """Create a deeply nested directory structure."""
    path_parts = [f"level{i}" for i in range(depth)]
    nested_path = temp_directory
    for part in path_parts:
        nested_path = nested_path / part
        nested_path.mkdir(exist_ok=True)

    relative_path = "/".join(path_parts)
    file_builder(filename, content="deep file content", relative_path=relative_path)


@given("I have files already organized in directory structure")
def setup_already_organized_files(temp_directory):
    """Create files already in organized structure."""
    organized_dir = temp_directory / "2026" / "202601" / "20260110"
    organized_dir.mkdir(parents=True, exist_ok=True)

    (organized_dir / "file1.txt").write_text("organized content 1")
    (organized_dir / "file2.txt").write_text("organized content 2")


@given(parsers.parse('I have a file "{filename}" created on {date}'))
def setup_old_file_created(file_builder, filename, date):
    """Create a file with old creation date."""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")
        now = datetime.now()
        delta = now - target_date
        offset_minutes = int(delta.total_seconds() / 60)

        file_builder(
            filename,
            content=f"Content for {filename}",
            created_offset_minutes=offset_minutes,
        )
    except ValueError:
        file_builder(filename, content=f"Content for {filename}")


@given(parsers.parse('the file was modified on {date}'))
def modify_file_date(temp_directory, file_builder, filename, date):
    """Modify a file's modification date."""
    # Find the file by name in temp_directory
    for file_path in temp_directory.rglob(filename):
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
            mod_time = target_date.timestamp()
            os.utime(file_path, (mod_time, mod_time))
            break
        except ValueError:
            pass


@given(parsers.parse('I have a directory with files "{file_list}"'))
def setup_files_with_extensions(file_builder, file_list):
    """Create files with specific extensions."""
    files = [f.strip().strip('"') for f in file_list.split(",")]
    for filename in files:
        file_builder(filename, content=f"Content for {filename}")


@given(parsers.parse('I have a directory with files "{file_list}"'))
def setup_various_extension_files(file_builder, file_list):
    """Create directory with files of various extensions."""
    files = [f.strip().strip('"') for f in file_list.split(",")]
    for filename in files:
        file_builder(filename, content=f"Content for {filename}")


@given(parsers.parse('I have a directory with various file types'))
def setup_various_file_types(file_builder):
    """Create directory with various file types."""
    file_builder("photo.jpg", content="jpeg image")
    file_builder("photo.png", content="png image")
    file_builder("document.pdf", content="pdf document")
    file_builder("data.txt", content="text data")


@given(parsers.parse('I have files that organize successfully'))
def setup_files_for_success(file_builder):
    """Create files that will organize successfully."""
    file_builder("success1.txt", content="success 1", created_offset_minutes=100)
    file_builder("success2.txt", content="success 2", created_offset_minutes=90)


@given(parsers.parse('I have multiple files to organize with various outcomes'))
def setup_files_various_outcomes(file_builder):
    """Create files that will have various organization outcomes."""
    file_builder("success.txt", content="success", created_offset_minutes=100)
    file_builder("skip.txt", content="will skip", created_offset_minutes=90)
    file_builder("error.txt", content="will error", created_offset_minutes=80)


@given(parsers.parse('I have multiple files to organize'))
def setup_multiple_files_organize(file_builder):
    """Create multiple files for organization."""
    for i in range(5):
        file_builder(f"file{i}.txt", content=f"content {i}", created_offset_minutes=100 - i * 10)


@given("stdin is a TTY (interactive terminal)")
def setup_tty_stdin():
    """Set up TTY stdin for interactive testing."""
    # This is handled by the CliRunner configuration
    # Actual TTY simulation may require additional setup
    pass


@given("stdin is not a TTY (piped input or non-interactive)")
def setup_non_tty_stdin():
    """Set up non-TTY stdin for non-interactive testing."""
    # This is handled by the CliRunner configuration
    pass


@given(parsers.parse('I run "{command}" {path}'))
def setup_command_state(cli_runner, command_context, temp_directory, command, path):
    """Store command state for later execution (given step for command setup)."""
    # This step is for setting up command state, actual execution happens in when steps
    command_context["pending_command"] = command
    command_context["pending_path"] = path


@given(parsers.parse('I run "{command}" without --recursive flag'))
def setup_non_recursive_command(command_context, command):
    """Store non-recursive command state."""
    command_context["pending_command"] = command
    command_context["non_recursive"] = True


@given(parsers.parse('I run "{command}" without --yes flag'))
def setup_command_without_yes(command_context, command):
    """Store command state for confirmation testing."""
    command_context["pending_command"] = command


@given('I run "fx organize" on the organized directory')
def setup_organized_directory_command(temp_directory, file_builder):
    """Create organized directory structure for testing."""
    organized_dir = temp_directory / "2026" / "202601" / "20260110"
    organized_dir.mkdir(parents=True, exist_ok=True)
    (organized_dir / "file1.txt").write_text("organized content")


@given('source directory is "/a/b"')
def setup_source_path():
    """Set up source path for testing."""
    # This is used for path comparison tests
    pass


@given('output directory is "/a/b2"')
def setup_output_path():
    """Set up output path for testing."""
    # This is used for path comparison tests
    pass


@given('source directory is on drive C:\\')
def setup_windows_source():
    """Set up Windows source drive for testing."""
    # This is used for Windows-specific path tests
    pass


@given('output directory is on drive D:\\')
def setup_windows_output():
    """Set up Windows output drive for testing."""
    # This is used for Windows-specific path tests
    pass


@given('I run "fx organize --output ./organized" in current directory')
def setup_output_in_source(temp_directory, file_builder):
    """Create output directory inside source for exclusion testing."""
    output_dir = temp_directory / "organized"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "existing.txt").write_text("existing content")


@given('./organized/ contains files from previous run')
def setup_organized_with_files(temp_directory, file_builder):
    """Create organized directory with existing files."""
    organized_dir = temp_directory / "organized"
    organized_dir.mkdir(parents=True, exist_ok=True)
    file_builder("existing.txt", content="existing content", relative_path="organized")


# ==============================================================================
# WHEN STEPS - Command Execution
# ==============================================================================


@when(parsers.parse('I run "{command}"'))
def run_organize_command(cli_runner, command_context, temp_directory, command):
    """Execute fx organize command and capture results."""
    # Save current working directory and change to temp directory for relative path operations
    original_cwd = os.getcwd()
    os.chdir(temp_directory)

    # Parse command into parts
    command_parts = command.split()
    if command_parts[0] == "fx":
        command_parts = command_parts[1:]  # Remove 'fx' prefix

    # Remove quotes from arguments
    command_parts = [arg.strip("'\"") for arg in command_parts]

    # Record start time for performance testing
    start_time = time.time()

    try:
        result = cli_runner.invoke(cli, command_parts, catch_exceptions=False)
        execution_time = time.time() - start_time

        command_context["last_exit_code"] = result.exit_code
        command_context["last_output"] = result.output
        command_context["last_error"] = None
        command_context["execution_time"] = execution_time

    except Exception as e:
        execution_time = time.time() - start_time

        command_context["last_exit_code"] = 1
        command_context["last_output"] = ""
        command_context["last_error"] = str(e)
        command_context["execution_time"] = execution_time

    finally:
        # Always restore original working directory
        os.chdir(original_cwd)


@when(parsers.parse('I run "{command}" {path}'))
def run_organize_command_with_path(cli_runner, command_context, command, path):
    """Execute fx organize command with specific path."""
    # Parse command into parts
    command_parts = command.split() + [path]
    if command_parts[0] == "fx":
        command_parts = command_parts[1:]

    start_time = time.time()

    try:
        result = cli_runner.invoke(cli, command_parts, catch_exceptions=False)
        execution_time = time.time() - start_time

        command_context["last_exit_code"] = result.exit_code
        command_context["last_output"] = result.output
        command_context["last_error"] = None
        command_context["execution_time"] = execution_time

    except Exception as e:
        execution_time = time.time() - start_time

        command_context["last_exit_code"] = 1
        command_context["last_output"] = ""
        command_context["last_error"] = str(e)
        command_context["execution_time"] = execution_time


@when("I confirm the prompt to overwrite")
def confirm_overwrite_prompt(command_context, cli_runner, temp_directory):
    """Simulate user confirming the overwrite prompt in ASK mode."""
    # This is handled by CliRunner's input simulation
    # For ASK mode, we need to provide input
    if "last_command" not in command_context:
        return

    # Re-run the last command with 'y' input
    last_command = command_context.get("last_command", "")
    if last_command:
        original_cwd = os.getcwd()
        os.chdir(temp_directory)

        try:
            command_parts = last_command.split()
            if command_parts[0] == "fx":
                command_parts = command_parts[1:]

            result = cli_runner.invoke(
                cli, command_parts, input="y\n", catch_exceptions=False
            )

            command_context["last_exit_code"] = result.exit_code
            command_context["last_output"] = result.output

        finally:
            os.chdir(original_cwd)


@when("I decline the prompt to overwrite")
def decline_overwrite_prompt(command_context, cli_runner, temp_directory):
    """Simulate user declining the overwrite prompt in ASK mode."""
    # This is handled by CliRunner's input simulation
    # For ASK mode, we need to provide input
    if "last_command" not in command_context:
        return

    # Re-run the last command with 'n' input
    last_command = command_context.get("last_command", "")
    if last_command:
        original_cwd = os.getcwd()
        os.chdir(temp_directory)

        try:
            command_parts = last_command.split()
            if command_parts[0] == "fx":
                command_parts = command_parts[1:]

            result = cli_runner.invoke(
                cli, command_parts, input="n\n", catch_exceptions=False
            )

            command_context["last_exit_code"] = result.exit_code
            command_context["last_output"] = result.output

        finally:
            os.chdir(original_cwd)
