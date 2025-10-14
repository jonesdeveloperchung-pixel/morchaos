"""Pytest configuration and fixtures for morchaos tests."""

import pytest
from pathlib import Path
from unittest.mock import Mock


@pytest.fixture
def tmp_dir(tmp_path):
    """Return a temporary directory with a deterministic file tree."""
    # Create test directory structure
    (tmp_path / "subdir1").mkdir()
    (tmp_path / "subdir2").mkdir()
    (tmp_path / "ignored_dir").mkdir()

    # Create test files
    (tmp_path / "file1.txt").write_text("Hello World")
    (tmp_path / "file2.txt").write_text("Hello World")  # Duplicate
    (tmp_path / "file3.txt").write_text("Different content")
    (tmp_path / "subdir1" / "file4.txt").write_text("Hello World")  # Another duplicate
    (tmp_path / "subdir2" / "file5.py").write_text("print('hello')")
    (tmp_path / "subdir2" / "file6.py").write_text(
        "print( 'hello' )"
    )  # Whitespace diff

    return tmp_path


@pytest.fixture
def mock_requests():
    """Mock requests module for chatbot tests."""
    mock_response = Mock()
    mock_response.json.return_value = {"response": "Test response"}
    mock_response.raise_for_status.return_value = None
    mock_response.iter_lines.return_value = [
        '{"response": "Test", "done": false}',
        '{"response": " response", "done": true}',
    ]

    mock_session = Mock()
    mock_session.post.return_value = mock_response
    mock_session.get.return_value = mock_response

    return mock_session


@pytest.fixture
def mock_psutil():
    """Mock psutil module for system info tests."""
    mock_psutil = Mock()

    # Mock CPU info
    mock_psutil.cpu_count.side_effect = lambda logical=True: 8 if logical else 4
    mock_psutil.cpu_percent.return_value = 25.5
    mock_psutil.cpu_freq.return_value = Mock(max=3000, min=800, current=2400)

    # Mock memory info
    mock_memory = Mock()
    mock_memory.total = 16 * 1024**3  # 16GB
    mock_memory.available = 8 * 1024**3  # 8GB
    mock_memory.used = 8 * 1024**3  # 8GB
    mock_memory.free = 8 * 1024**3  # 8GB
    mock_memory.percent = 50.0
    mock_psutil.virtual_memory.return_value = mock_memory

    mock_swap = Mock()
    mock_swap.total = 4 * 1024**3  # 4GB
    mock_swap.used = 1 * 1024**3  # 1GB
    mock_swap.free = 3 * 1024**3  # 3GB
    mock_swap.percent = 25.0
    mock_psutil.swap_memory.return_value = mock_swap

    return mock_psutil
