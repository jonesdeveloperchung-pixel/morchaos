import pytest
import os
from unittest.mock import AsyncMock

from morchaos.cli import ollama_chat


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
            "-s",
            "You are a sarcastic Unix expert.",
            "-p",
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
            os.path.normpath(str(system_prompt_file)),
            "-p",
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
            "-p",
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
        "http://localhost:11434", 120
    )  # Default timeout


def test_list_models(mock_list_models_core, mocker, capsys):
    mock_list_models_core.return_value = [{"name": "model1", "size": 123, "modified_at": "2023-01-01"}, {"name": "model2", "size": 456, "modified_at": "2023-01-02"}]
    mocker.patch("sys.argv", ["ollama-chat", "--list"])
    with pytest.raises(SystemExit) as excinfo:
        ollama_chat.main()
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "Available models:" in captured.out
    assert "model1" in captured.out
    assert "model2" in captured.out
    mock_list_models_core.assert_called_once_with(
        "http://localhost:11434", 120
    )  # Default timeout
