import pytest
from pathlib import Path
import json
import sys
from unittest.mock import patch

from morchaos.core import prompt_manager
from morchaos.cli import prompt_manager as cli_prompt_manager

# --- Tests for read_prompt function (from core.prompt_manager) ---

def test_read_prompt_string():
    source = "This is a test prompt."
    prompt = prompt_manager.read_prompt(source=source, file_path=None, prompt_name="test")
    assert prompt == source

def test_read_prompt_txt_file(tmp_path):
    file_path = tmp_path / "test_prompt.txt"
    file_path.write_text("This is a file prompt.")
    prompt = prompt_manager.read_prompt(source=None, file_path=file_path, prompt_name="test")
    assert prompt == "This is a file prompt."

def test_read_prompt_json_file(tmp_path):
    file_path = tmp_path / "test_prompt.json"
    json_content = {"prompt": "This is a JSON file prompt.", "other_data": "value"}
    file_path.write_text(json.dumps(json_content))
    prompt = prompt_manager.read_prompt(source=None, file_path=file_path, prompt_name="system")
    assert prompt == "This is a JSON file prompt."

def test_read_prompt_default():
    default_prompt = "Default prompt content."
    prompt = prompt_manager.read_prompt(source=None, file_path=None, prompt_name="test", default=default_prompt)
    assert prompt == default_prompt

def test_read_prompt_empty_string_raises_error():
    with pytest.raises(ValueError, match="Test prompt is empty."):
        prompt_manager.read_prompt(source=" ", file_path=None, prompt_name="test")

def test_read_prompt_empty_file_raises_error(tmp_path):
    file_path = tmp_path / "empty.txt"
    file_path.write_text(" ")
    with pytest.raises(ValueError, match="Test prompt is empty."):
        prompt_manager.read_prompt(source=None, file_path=file_path, prompt_name="test")

def test_read_prompt_missing_file_raises_error():
    with pytest.raises(ValueError, match="Test file 'non_existent.txt' not found."):
        prompt_manager.read_prompt(source=None, file_path=Path("non_existent.txt"), prompt_name="test")

def test_read_prompt_no_prompt_provided_raises_error():
    with pytest.raises(ValueError, match="No test prompt provided."):
        prompt_manager.read_prompt(source=None, file_path=None, prompt_name="test")

# --- Tests for convert_prompt_format function (from core.prompt_manager) ---

def test_convert_txt_to_json(tmp_path):
    input_file = tmp_path / "input.txt"
    input_file.write_text("Hello from TXT!")
    output_file = tmp_path / "output.json"
    prompt_manager.convert_prompt_format(input_file, output_file)
    assert output_file.is_file()
    content = json.loads(output_file.read_text())
    assert content == {"prompt": "Hello from TXT!"}

def test_convert_json_to_txt(tmp_path):
    input_file = tmp_path / "input.json"
    json_content = {"prompt": "Hello from JSON!", "meta": "data"}
    input_file.write_text(json.dumps(json_content))
    output_file = tmp_path / "output.txt"
    prompt_manager.convert_prompt_format(input_file, output_file)
    assert output_file.is_file()
    assert output_file.read_text() == "Hello from JSON!"

def test_convert_missing_input_file_raises_error(tmp_path):
    input_file = tmp_path / "non_existent.txt"
    output_file = tmp_path / "output.json"
    with pytest.raises(FileNotFoundError, match="Input file not found:"):
        prompt_manager.convert_prompt_format(input_file, output_file)

def test_convert_unsupported_format_raises_error(tmp_path):
    input_file = tmp_path / "input.xml"
    input_file.write_text("<prompt>XML content</prompt>")
    output_file = tmp_path / "output.json"
    with pytest.raises(ValueError, match="Unsupported input file format: .xml"):
        prompt_manager.convert_prompt_format(input_file, output_file)

# --- Tests for list_prompts function (from core.prompt_manager) ---

def test_list_prompts_empty_directory(tmp_path):
    prompts = prompt_manager.list_prompts(tmp_path)
    assert prompts == []

def test_list_prompts_with_files(tmp_path):
    (tmp_path / "prompt1.txt").write_text("p1")
    (tmp_path / "prompt2.json").write_text("{\"prompt\": \"p2\"}")
    (tmp_path / "image.png").write_bytes(b"123") # Non-prompt file
    prompts = prompt_manager.list_prompts(tmp_path)
    assert len(prompts) == 2
    assert Path(tmp_path / "prompt1.txt") in prompts
    assert Path(tmp_path / "prompt2.json") in prompts

def test_list_prompts_non_directory_raises_error(tmp_path):
    non_dir = tmp_path / "not_a_dir.txt"
    non_dir.write_text("content")
    with pytest.raises(NotADirectoryError, match="Directory not found:"):
        prompt_manager.list_prompts(non_dir)

# --- Tests for CLI prompt_manager (from cli.prompt_manager) ---

@pytest.fixture
def mock_convert_prompt_format(mocker):
    return mocker.patch('morchaos.cli.prompt_manager.convert_prompt_format')

@pytest.fixture
def mock_list_prompts(mocker):
    return mocker.patch('morchaos.cli.prompt_manager.list_prompts')

def test_cli_convert_command(mock_convert_prompt_format, mocker):
    mocker.patch('sys.argv', ['prompt-manager', 'convert', 'input.txt', 'output.json'])
    mocker.patch('sys.exit') # Prevent sys.exit from terminating test
    cli_prompt_manager.main()
    mock_convert_prompt_format.assert_called_once_with(Path('input.txt'), Path('output.json'))

def test_cli_list_command(mock_list_prompts, mocker, capsys):
    mock_list_prompts.return_value = [Path('dir/p1.txt'), Path('dir/p2.json')]
    mocker.patch('sys.argv', ['prompt-manager', 'list', 'dir'])
    mocker.patch('sys.exit')
    cli_prompt_manager.main()
    mock_list_prompts.assert_called_once_with(Path('dir'))
    captured = capsys.readouterr()
    assert "Prompts in 'dir':" in captured.out
    assert "- p1.txt" in captured.out
    assert "- p2.json" in captured.out

def test_cli_list_command_default_dir(mock_list_prompts, mocker, capsys):
    mock_list_prompts.return_value = [Path('./p1.txt')]
    mocker.patch('sys.argv', ['prompt-manager', 'list'])
    mocker.patch('sys.exit')
    cli_prompt_manager.main()
    mock_list_prompts.assert_called_once_with(Path('.'))
    captured = capsys.readouterr()
    assert "Prompts in '.'" in captured.out
    assert "- p1.txt" in captured.out



def test_cli_no_command_provided(mocker, capsys):
    mocker.patch('sys.argv', ['prompt-manager'])
    with pytest.raises(SystemExit) as excinfo:
        cli_prompt_manager.main()
    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "usage: prompt-manager" in captured.out
    assert "Available commands" in captured.out