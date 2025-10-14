"""Tests for chatbot module."""

import pytest
from unittest.mock import Mock, patch
from morchaos.core.chatbot import Chatbot


def test_chatbot_init():
    """Test chatbot initialization."""
    chatbot = Chatbot()
    assert chatbot.base_url == "http://localhost:11434"
    assert chatbot.timeout == 30

    chatbot = Chatbot("http://example.com:11434", timeout=60)
    assert chatbot.base_url == "http://example.com:11434"
    assert chatbot.timeout == 60


@patch("morchaos.core.chatbot.requests.Session")
def test_chatbot_ask_success(mock_session_class):
    """Test successful chatbot request."""
    # Setup mock
    mock_session = Mock()
    mock_response = Mock()
    mock_response.json.return_value = {"response": "Hello there!"}
    mock_response.raise_for_status.return_value = None
    mock_session.post.return_value = mock_response
    mock_session_class.return_value = mock_session

    # Test
    chatbot = Chatbot()
    response = chatbot.ask("Hello")

    assert response == "Hello there!"
    mock_session.post.assert_called_once()


@patch("morchaos.core.chatbot.requests.Session")
def test_chatbot_ask_streaming(mock_session_class):
    """Test streaming chatbot request."""
    # Setup mock
    mock_session = Mock()
    mock_response = Mock()
    mock_response.iter_lines.return_value = [
        '{"response": "Hello", "done": false}',
        '{"response": " there!", "done": true}',
    ]
    mock_response.raise_for_status.return_value = None
    mock_session.post.return_value = mock_response
    mock_session_class.return_value = mock_session

    # Test
    chatbot = Chatbot()
    response = chatbot.ask("Hello", stream=True)

    assert response == "Hello there!"


def test_chatbot_ask_empty_prompt():
    """Test chatbot with empty prompt."""
    chatbot = Chatbot()

    with pytest.raises(ValueError, match="Prompt cannot be empty"):
        chatbot.ask("")

    with pytest.raises(ValueError, match="Prompt cannot be empty"):
        chatbot.ask("   ")


@patch("morchaos.core.chatbot.requests.Session")
def test_chatbot_connection_error(mock_session_class):
    """Test chatbot connection error."""
    # Setup mock to raise connection error
    mock_session = Mock()
    mock_session.post.side_effect = ConnectionError("Connection failed")
    mock_session_class.return_value = mock_session

    # Test
    chatbot = Chatbot()

    with pytest.raises(ConnectionError):
        chatbot.ask("Hello")


@patch("morchaos.core.chatbot.requests.Session")
def test_chatbot_health_check(mock_session_class):
    """Test chatbot health check."""
    # Setup mock
    mock_session = Mock()
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session

    # Test successful health check
    chatbot = Chatbot()
    assert chatbot.health_check() is True

    # Test failed health check
    mock_session.get.side_effect = Exception("Connection failed")
    assert chatbot.health_check() is False


@patch("morchaos.core.chatbot.requests.Session")
def test_chatbot_list_models(mock_session_class):
    """Test listing available models."""
    # Setup mock
    mock_session = Mock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "models": [{"name": "llama3.2:latest"}, {"name": "gemma3:1b"}]
    }
    mock_response.raise_for_status.return_value = None
    mock_session.get.return_value = mock_response
    mock_session_class.return_value = mock_session

    # Test
    chatbot = Chatbot()
    models = chatbot.list_models()

    assert models == ["llama3.2:latest", "gemma3:1b"]
