"""BDD test fixtures and configuration for pytest-bdd.

This module provides comprehensive fixtures for testing the fx filter command
with focus on realistic test scenarios and proper cleanup.
"""

import os
import tempfile
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import pytest
from dataclasses import dataclass
from click.testing import CliRunner


@dataclass
class FileInfo:
    """Represents a test file with metadata."""

    name: str
    path: Path
    extension: str
    created_time: float
    modified_time: float
    size: int
    content: str = ""


@dataclass
class DirectoryInfo:
    """Represents a test directory structure."""

    path: Path
    files: List[FileInfo]
    subdirectories: List["DirectoryInfo"]


@pytest.fixture
def cli_runner():
    """Provide Click CLI runner for testing commands."""
    return CliRunner()


@pytest.fixture
def temp_directory():
    """Create and cleanup temporary directory for tests."""
    temp_dir = tempfile.mkdtemp(prefix="fx_filter_test_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def file_builder(temp_directory):
    """Builder for creating test files with specific attributes."""
    created_files = []

    def create_file(
        name: str,
        content: str = "test content",
        relative_path: str = "",
        created_offset_minutes: int = 0,
        modified_offset_minutes: int = 0,
        size_bytes: int = None,
    ) -> FileInfo:
        """Create a test file with specified attributes.

        Args:
            name: File name including extension
            content: File content
            relative_path: Path relative to temp directory
            created_offset_minutes: Minutes to subtract from current time for creation
            modified_offset_minutes: Minutes to subtract from current time for modification
            size_bytes: Specific file size (if None, determined by content)
        """
        file_dir = temp_directory / relative_path if relative_path else temp_directory
        file_dir.mkdir(parents=True, exist_ok=True)

        file_path = file_dir / name

        # Write content
        if size_bytes is not None and size_bytes > len(content):
            # Pad content to reach desired size
            content = content + "x" * (size_bytes - len(content))

        file_path.write_text(content)

        # Set timestamps
        now = time.time()
        # For more precision, use seconds instead of minutes * 60
        created_time = now - (created_offset_minutes * 60)
        # Use created_offset_minutes for modified_time if modified_offset_minutes is 0
        # This allows tests to set file dates using created_offset_minutes
        if modified_offset_minutes == 0 and created_offset_minutes != 0:
            modified_time = created_time
        else:
            modified_time = now - (modified_offset_minutes * 60)

        os.utime(file_path, (created_time, modified_time))

        # Get extension
        extension = file_path.suffix.lower().lstrip(".")

        test_file = FileInfo(
            name=name,
            path=file_path,
            extension=extension,
            created_time=created_time,
            modified_time=modified_time,
            size=file_path.stat().st_size,
            content=content,
        )

        created_files.append(test_file)
        return test_file

    yield create_file

    # Cleanup is handled by temp_directory fixture


@pytest.fixture
def directory_builder(temp_directory, file_builder):
    """Builder for creating complex directory structures."""

    def create_structure(structure: Dict[str, Any]) -> DirectoryInfo:
        """Create directory structure from specification.

        Args:
            structure: Dict describing directory structure
                {
                    "files": [{"name": "file.txt", "extension": "txt", ...}],
                    "subdirs": {
                        "subdir1": {"files": [...], "subdirs": {...}}
                    }
                }
        """

        def _create_recursive(spec: Dict[str, Any], base_path: Path) -> DirectoryInfo:
            files = []
            subdirs = []

            # Create files
            for file_spec in spec.get("files", []):
                relative_path = str(base_path.relative_to(temp_directory))
                if relative_path == ".":
                    relative_path = ""

                test_file = file_builder(
                    name=file_spec["name"],
                    content=file_spec.get("content", "test content"),
                    relative_path=relative_path,
                    created_offset_minutes=file_spec.get("created_offset_minutes", 0),
                    modified_offset_minutes=file_spec.get("modified_offset_minutes", 0),
                    size_bytes=file_spec.get("size_bytes"),
                )
                files.append(test_file)

            # Create subdirectories
            for subdir_name, subdir_spec in spec.get("subdirs", {}).items():
                subdir_path = base_path / subdir_name
                subdir_path.mkdir(exist_ok=True)
                subdir = _create_recursive(subdir_spec, subdir_path)
                subdirs.append(subdir)

            return DirectoryInfo(path=base_path, files=files, subdirectories=subdirs)

        return _create_recursive(structure, temp_directory)

    return create_structure


@pytest.fixture
def standard_test_files(file_builder):
    """Create standard set of test files for common scenarios."""
    files = {}

    # Text files with different timestamps
    files["old_doc"] = file_builder(
        "old_document.txt",
        content="Old document content",
        created_offset_minutes=120,  # 2 hours ago
        modified_offset_minutes=60,  # 1 hour ago
    )

    files["new_doc"] = file_builder(
        "new_document.txt",
        content="New document content",
        created_offset_minutes=30,  # 30 minutes ago
        modified_offset_minutes=15,  # 15 minutes ago
    )

    files["recent_doc"] = file_builder(
        "recent_document.txt",
        content="Most recent content",
        created_offset_minutes=5,  # 5 minutes ago
        modified_offset_minutes=2,  # 2 minutes ago
    )

    # Python files
    files["script"] = file_builder(
        "script.py", content="print('Hello, World!')", created_offset_minutes=90
    )

    files["module"] = file_builder(
        "module.py", content="def function(): pass", created_offset_minutes=45
    )

    # Media files
    files["video1"] = file_builder(
        "movie.mp4",
        content="fake video content",
        size_bytes=1024 * 1024,  # 1MB
        created_offset_minutes=180,
    )

    files["video2"] = file_builder(
        "clip.avi",
        content="fake avi content",
        size_bytes=2 * 1024 * 1024,  # 2MB
        created_offset_minutes=150,
    )

    files["video3"] = file_builder(
        "episode.mkv",
        content="fake mkv content",
        size_bytes=500 * 1024,  # 500KB
        created_offset_minutes=240,
    )

    # Documents
    files["pdf"] = file_builder(
        "document.pdf", content="fake pdf content", created_offset_minutes=75
    )

    files["doc"] = file_builder(
        "report.docx", content="fake word document", created_offset_minutes=100
    )

    return files


@pytest.fixture
def nested_directory_structure(directory_builder):
    """Create nested directory structure for recursion tests."""
    structure = {
        "files": [
            {
                "name": "root.txt",
                "content": "root level file",
                "created_offset_minutes": 60,
            }
        ],
        "subdirs": {
            "level1": {
                "files": [
                    {
                        "name": "level1.txt",
                        "content": "first level file",
                        "created_offset_minutes": 45,
                    },
                    {
                        "name": "level1.py",
                        "content": "# first level python",
                        "created_offset_minutes": 40,
                    },
                ],
                "subdirs": {
                    "level2": {
                        "files": [
                            {
                                "name": "level2.txt",
                                "content": "second level file",
                                "created_offset_minutes": 30,
                            },
                            {
                                "name": "deep.py",
                                "content": "# deep python file",
                                "created_offset_minutes": 25,
                            },
                        ],
                        "subdirs": {
                            "level3": {
                                "files": [
                                    {
                                        "name": "level3.txt",
                                        "content": "third level file",
                                        "created_offset_minutes": 15,
                                    },
                                    {
                                        "name": "deepest.py",
                                        "content": "# deepest file",
                                        "created_offset_minutes": 10,
                                    },
                                ]
                            }
                        },
                    }
                },
            },
            "parallel": {
                "files": [
                    {
                        "name": "parallel.txt",
                        "content": "parallel branch file",
                        "created_offset_minutes": 35,
                    },
                    {
                        "name": "side.py",
                        "content": "# side branch python",
                        "created_offset_minutes": 20,
                    },
                ]
            },
        },
    }

    return directory_builder(structure)


@pytest.fixture
def large_file_collection(file_builder):
    """Create large collection of files for performance testing."""
    files = []
    extensions = ["txt", "py", "js", "html", "css", "md", "json", "xml"]

    for i in range(100):  # Reduced from 10,000 for test performance
        ext = extensions[i % len(extensions)]
        name = f"file_{i:04d}.{ext}"

        test_file = file_builder(
            name=name,
            content=f"Content for file {i}",
            created_offset_minutes=i,  # Spread over time
            modified_offset_minutes=i // 2,
        )
        files.append(test_file)

    return files


@pytest.fixture
def mixed_case_files(file_builder):
    """Create files with mixed case extensions."""
    return [
        file_builder("Document.PDF", "fake pdf", created_offset_minutes=30),
        file_builder("Image.JPG", "fake jpg", created_offset_minutes=25),
        file_builder("Script.PY", "print('test')", created_offset_minutes=20),
        file_builder("data.JSON", '{"test": true}', created_offset_minutes=15),
        file_builder("style.CSS", "body { margin: 0; }", created_offset_minutes=10),
    ]


@pytest.fixture
def permission_test_dir(temp_directory):
    """Create directory with restricted permissions for testing."""
    restricted_dir = temp_directory / "restricted"
    restricted_dir.mkdir()

    # Create some files
    (restricted_dir / "accessible.txt").write_text("accessible content")
    (restricted_dir / "restricted.txt").write_text("restricted content")

    # Make directory read-only (on systems that support it)
    try:
        os.chmod(restricted_dir, 0o444)  # Read-only
        yield restricted_dir
    except (OSError, PermissionError):
        # Skip permission tests on systems that don't support chmod
        pytest.skip("Permission testing not supported on this system")
    finally:
        # Restore permissions for cleanup
        try:
            os.chmod(restricted_dir, 0o755)
        except (OSError, PermissionError):
            pass


@pytest.fixture
def command_context():
    """Provide context for command execution and result validation."""
    return {
        "last_exit_code": None,
        "last_output": None,
        "last_error": None,
        "execution_time": None,
    }


# Utility functions for step definitions


def normalize_path(path_str: str) -> str:
    """Normalize file path for cross-platform compatibility."""
    return str(Path(path_str)).replace("\\", "/")


def parse_file_extensions(extensions_str: str) -> List[str]:
    """Parse comma-separated extension string."""
    return [ext.strip().lower() for ext in extensions_str.split(",")]


def files_match_extensions(files: List[FileInfo], extensions: List[str]) -> bool:
    """Check if files match the specified extensions."""
    file_extensions = {f.extension.lower() for f in files}
    target_extensions = {ext.lower() for ext in extensions}
    return file_extensions.issubset(target_extensions)


def files_sorted_by_creation_time(files: List[FileInfo], reverse: bool = False) -> bool:
    """Check if files are sorted by creation time."""
    if len(files) <= 1:
        return True

    times = [f.created_time for f in files]
    if reverse:
        return times == sorted(times)  # Oldest first
    else:
        return times == sorted(times, reverse=True)  # Newest first


def files_sorted_by_modification_time(
    files: List[FileInfo], reverse: bool = False
) -> bool:
    """Check if files are sorted by modification time."""
    if len(files) <= 1:
        return True

    times = [f.modified_time for f in files]
    if reverse:
        return times == sorted(times)  # Oldest first
    else:
        return times == sorted(times, reverse=True)  # Newest first
