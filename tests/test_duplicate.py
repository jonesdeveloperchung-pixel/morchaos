"""Tests for duplicate detection module."""

import pytest
from pathlib import Path
from morchaos.core.duplicate import find_duplicates, act_on_duplicates


def test_find_duplicates(tmp_dir):
    """Test duplicate file detection."""
    duplicates = find_duplicates(tmp_dir)

    # Should find duplicates (file1.txt, file2.txt, file4.txt have same content)
    assert len(duplicates) == 1

    # Get the duplicate group
    duplicate_group = list(duplicates.values())[0]
    assert len(duplicate_group) == 3

    # Check that all files in the group have "Hello World" content
    for file_path in duplicate_group:
        assert file_path.read_text() == "Hello World"


def test_find_duplicates_with_extensions(tmp_dir):
    """Test duplicate detection with specific extensions."""
    duplicates = find_duplicates(tmp_dir, extensions=[".py"])

    # Should find Python files (even with whitespace differences, they're different hashes)
    # Since we're using SHA-256, whitespace differences create different hashes
    assert len(duplicates) == 0  # No exact duplicates in .py files


def test_find_duplicates_with_ignore_dirs(tmp_dir):
    """Test duplicate detection with ignored directories."""
    duplicates = find_duplicates(tmp_dir, ignore_dirs=["subdir1"])

    # Should find fewer duplicates since subdir1 is ignored
    assert len(duplicates) == 1
    duplicate_group = list(duplicates.values())[0]
    assert len(duplicate_group) == 2  # Only file1.txt and file2.txt


def test_find_duplicates_nonexistent_dir():
    """Test duplicate detection with nonexistent directory."""
    with pytest.raises(FileNotFoundError):
        find_duplicates(Path("/nonexistent"))


def test_act_on_duplicates_delete(tmp_dir):
    """Test deleting duplicate files."""
    duplicates = find_duplicates(tmp_dir)

    # Count files before deletion
    initial_files = list(tmp_dir.rglob("*.txt"))
    initial_count = len(initial_files)

    # Delete duplicates
    processed = act_on_duplicates(duplicates, "delete")

    # Should have deleted 2 files (keeping the first one from each group)
    assert processed == 2

    # Count files after deletion
    remaining_files = list(tmp_dir.rglob("*.txt"))
    assert len(remaining_files) == initial_count - 2


def test_act_on_duplicates_move(tmp_dir):
    """Test moving duplicate files."""
    duplicates = find_duplicates(tmp_dir)
    target_dir = tmp_dir / "duplicates"

    # Move duplicates
    processed = act_on_duplicates(duplicates, "move", target_dir)

    # Should have moved 2 files
    assert processed == 2
    assert target_dir.exists()

    # Check that files were moved to target directory
    moved_files = list(target_dir.glob("*.txt"))
    assert len(moved_files) == 2


def test_act_on_duplicates_move_without_target():
    """Test move action without target directory."""
    with pytest.raises(ValueError):
        act_on_duplicates({}, "move", None)
