import pytest
from unittest.mock import AsyncMock, patch
import sys
import argparse
from pathlib import Path

from morchaos.cli import ollama_chat
from morchaos.core.ollama_chat import run_chat, health_check, list_models


@pytest.fixture
def mock_run_chat_core(mocker):
    return mocker.patch("morchaos.cli.ollama_chat.run_chat", new_callable=AsyncMock)


@pytest.fixture
def mock_health_check_core(mocker):
    return mocker.patch("morchaos.cli.ollama_chat.health_check")


@pytest.fixture
def mock_list_models_core(mocker):
    return mocker.patch("morchaos.cli.ollama_chat.list_models")


def test_ollama_chat_inline_prompts(mock_run_chat_core, mocker):
    mocker.patch(
        "sys.argv",
        [
            "ollama-chat",
            "-S",
            "You are a sarcastic Unix expert.",
            "-U",
            "Explain virtual memory.",
        ],
    )
    ollama_chat.main()
    mock_run_chat_core.assert_called_once()
    call_args, call_kwargs = mock_run_chat_core.call_args
    messages = call_args[0]
    assert messages[0] == {
        "role": "system",
        "content": "You are a sarcastic Unix expert.",
    }
    assert messages[1] == {"role": "user", "content": "Explain virtual memory."}
    assert call_kwargs["model"] == "gemma3:4b"


def test_ollama_chat_file_based_system_prompt(tmp_path, mock_run_chat_core, mocker):
    system_prompt_file = tmp_path / "system_prompt.txt"
    system_prompt_file.write_text("You are a poetic assistant.")
    mocker.patch(
        "sys.argv",
        [
            "ollama-chat",
            "--sf",
            str(system_prompt_file),
            "-U",
            "What is a closure in Python?",
        ],
    )
    ollama_chat.main()
    mock_run_chat_core.assert_called_once()
    call_args, call_kwargs = mock_run_chat_core.call_args
    messages = call_args[0]
    assert messages[0] == {"role": "system", "content": "You are a poetic assistant."}
    assert messages[1] == {"role": "user", "content": "What is a closure in Python?"}
    assert call_kwargs["model"] == "gemma3:4b"


def test_ollama_chat_default_system_prompt(mock_run_chat_core, mocker):
    mocker.patch(
        "sys.argv",
        [
            "ollama-chat",
            "-U",
            "Show me the Linux kernel source.",
        ],
    )
    ollama_chat.main()
    mock_run_chat_core.assert_called_once()
    call_args, call_kwargs = mock_run_chat_core.call_args
    messages = call_args[0]
    assert messages[0] == {"role": "system", "content": "You are a helpful assistant."}
    assert messages[1] == {
        "role": "user",
        "content": "Show me the Linux kernel source.",
    }
    assert call_kwargs["model"] == "gemma3:4b"


def test_health_check(mock_health_check_core, mocker, capsys):
    mock_health_check_core.return_value = True
    mocker.patch("sys.argv", ["ollama-chat", "--health-check"])
    with pytest.raises(SystemExit) as excinfo:
        ollama_chat.main()
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "✓ Endpoint http://localhost:11434 is healthy" in captured.out
    mock_health_check_core.assert_called_once_with(
        "http://localhost:11434", 30
    )  # Default timeout


def test_list_models(mock_list_models_core, mocker, capsys):
    mock_list_models_core.return_value = ["model1", "model2"]
    mocker.patch("sys.argv", ["ollama-chat", "--list-models"])
    with pytest.raises(SystemExit) as excinfo:
        ollama_chat.main()
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "Available models:" in captured.out
    assert "model1" in captured.out
    assert "model2" in captured.out
    mock_list_models_core.assert_called_once_with(
        "http://localhost:11434", 30
    )  # Default timeout
