"""Tests for file utilities module."""

import pytest
from pathlib import Path
from morchaos.core.file_utils import safe_path, remove_temp_dirs, sanitize_filename


def test_safe_path_valid():
    """Test safe_path with valid paths."""
    # Test with string path
    result = safe_path(".")
    assert isinstance(result, Path)
    assert result.is_absolute()

    # Test with Path object
    path_obj = Path(".")
    result = safe_path(path_obj)
    assert isinstance(result, Path)
    assert result.is_absolute()


def test_safe_path_invalid():
    """Test safe_path with invalid paths."""
    with pytest.raises(ValueError):
        safe_path("")


def test_remove_temp_dirs(tmp_dir):
    """Test temporary directory removal."""
    # Create temp directories
    (tmp_dir / "temp1").mkdir()
    (tmp_dir / "temp2").mkdir()
    (tmp_dir / "subdir" / "temp3").mkdir(parents=True)
    (tmp_dir / "keep_this").mkdir()

    # Remove temp directories
    removed = remove_temp_dirs(tmp_dir, ["temp*"])

    assert removed == 3
    assert not (tmp_dir / "temp1").exists()
    assert not (tmp_dir / "temp2").exists()
    assert not (tmp_dir / "subdir" / "temp3").exists()
    assert (tmp_dir / "keep_this").exists()


def test_remove_temp_dirs_nonexistent():
    """Test remove_temp_dirs with nonexistent root."""
    with pytest.raises(FileNotFoundError):
        remove_temp_dirs(Path("/nonexistent"), ["temp*"])


def test_sanitize_filename():
    """Test filename sanitization."""
    # Test invalid characters
    assert sanitize_filename("file<>name") == "file__name"
    assert sanitize_filename('file"name') == "file_name"
    assert sanitize_filename("file|name") == "file_name"

    # Test whitespace and dots
    assert sanitize_filename("  filename  ") == "filename"
    assert sanitize_filename("..filename..") == "filename"

    # Test empty filename
    assert sanitize_filename("") == "unnamed_file"
    assert sanitize_filename("   ") == "unnamed_file"

    # Test valid filename
    assert sanitize_filename("valid_filename.txt") == "valid_filename.txt"
