"""Tests for source code duplicate detection module."""

import pytest
from pathlib import Path
from morchaos.core.source import normalize_hash, find_source_duplicates


def test_normalize_hash(tmp_path):
    """Test source code normalization and hashing."""
    # Create test files with different whitespace
    file1 = tmp_path / "test1.py"
    file2 = tmp_path / "test2.py"
    file3 = tmp_path / "test3.py"

    file1.write_text("print('hello')")
    file2.write_text("print( 'hello' )")  # Extra spaces
    file3.write_text("print('world')")  # Different content

    hash1 = normalize_hash(file1)
    hash2 = normalize_hash(file2)
    hash3 = normalize_hash(file3)

    # Same content with different whitespace should have same hash
    assert hash1 == hash2
    # Different content should have different hash
    assert hash1 != hash3


def test_normalize_hash_with_comments(tmp_path):
    """Test normalization with comments."""
    file1 = tmp_path / "test1.py"
    file2 = tmp_path / "test2.py"

    file1.write_text("print('hello')  # This is a comment")
    file2.write_text("print('hello')")

    hash1 = normalize_hash(file1)
    hash2 = normalize_hash(file2)

    # Comments should be removed, so hashes should be equal
    assert hash1 == hash2


def test_normalize_hash_nonexistent_file():
    """Test normalize_hash with nonexistent file."""
    with pytest.raises(ValueError):
        normalize_hash(Path("/nonexistent/file.py"))


def test_find_source_duplicates(tmp_path):
    """Test finding source code duplicates."""
    # Create test files
    (tmp_path / "file1.py").write_text("print('hello')")
    (tmp_path / "file2.py").write_text("print( 'hello' )")  # Whitespace diff
    (tmp_path / "file3.js").write_text("console.log('hello');")
    (tmp_path / "file4.txt").write_text("print('hello')")  # Different extension

    # Find duplicates in Python files
    duplicates = find_source_duplicates(tmp_path, [".py"])

    # Should find the two Python files as duplicates
    assert len(duplicates) == 1
    duplicate_group = list(duplicates.values())[0]
    assert len(duplicate_group) == 2

    # Check that both Python files are in the group
    file_names = {path.name for path in duplicate_group}
    assert file_names == {"file1.py", "file2.py"}


def test_find_source_duplicates_multiple_extensions(tmp_path):
    """Test finding duplicates across multiple file types."""
    (tmp_path / "file1.py").write_text("print('hello')")
    (tmp_path / "file2.js").write_text("console.log('hello');")
    (tmp_path / "file3.java").write_text('System.out.println("hello");')

    duplicates = find_source_duplicates(tmp_path, [".py", ".js", ".java"])

    # No duplicates expected since content is different
    assert len(duplicates) == 0


def test_find_source_duplicates_nonexistent_dir():
    """Test find_source_duplicates with nonexistent directory."""
    with pytest.raises(FileNotFoundError):
        find_source_duplicates(Path("/nonexistent"))
