import pytest
from pathlib import Path
import json
import sys
from unittest.mock import patch, Mock
import requests

from morchaos.core import prompt_manager
from morchaos.cli import prompt_manager as cli_prompt_manager

# --- Tests for extract_nickname function (from core.prompt_manager) ---

def test_extract_nickname_valid_filename():
    filename = "prompts_analysis_problem-decomposer.json"
    nickname = prompt_manager.extract_nickname(filename)
    assert nickname == "analysis_problem-decomposer"

def test_extract_nickname_no_prefix():
    filename = "analysis_problem-decomposer.json"
    nickname = prompt_manager.extract_nickname(filename)
    assert nickname == "analysis_problem-decomposer.json"

def test_extract_nickname_no_suffix():
    filename = "prompts_analysis_problem-decomposer"
    nickname = prompt_manager.extract_nickname(filename)
    assert nickname == "prompts_analysis_problem-decomposer"

def test_extract_nickname_other_suffix():
    filename = "prompts_analysis_problem-decomposer.txt"
    nickname = prompt_manager.extract_nickname(filename)
    assert nickname == "prompts_analysis_problem-decomposer.txt"

# --- Tests for map_prompt_files function (from core.prompt_manager) ---

def test_map_prompt_files_empty_folder(tmp_path):
    mappings = prompt_manager.map_prompt_files(tmp_path)
    assert mappings == []

def test_map_prompt_files_with_prompts(tmp_path):
    (tmp_path / "prompts_test1.json").write_text("{}")
    (tmp_path / "prompts_test2.json").write_text("{}")
    (tmp_path / "other_file.txt").write_text("content")
    (tmp_path / "prompts_not_json.txt").write_text("content")

    # Mock Path.cwd() to be tmp_path for relative_to calculation
    with patch('pathlib.Path.cwd', return_value=tmp_path):
        mappings = prompt_manager.map_prompt_files(tmp_path)

    assert len(mappings) == 2
    assert {"nickname": "test1", "full_path": "prompts_test1.json"} in mappings
    assert {"nickname": "test2", "full_path": "prompts_test2.json"} in mappings

def test_map_prompt_files_with_output(tmp_path):
    (tmp_path / "prompts_test.json").write_text("{}")
    output_file = tmp_path / "mapping.json"

    with patch('pathlib.Path.cwd', return_value=tmp_path):
        mappings = prompt_manager.map_prompt_files(tmp_path, output_file)

    assert output_file.is_file()
    loaded_mapping = json.loads(output_file.read_text())
    assert loaded_mapping == [{
        "nickname": "test",
        "full_path": "prompts_test.json"
    }]
    assert mappings == [{
        "nickname": "test",
        "full_path": "prompts_test.json"
    }]

def test_map_prompt_files_non_directory_raises_error(tmp_path):
    non_dir = tmp_path / "not_a_dir.txt"
    non_dir.write_text("content")
    with pytest.raises(NotADirectoryError, match="Folder not found:"):
        prompt_manager.map_prompt_files(non_dir)

# --- Tests for save_mapping_to_json function (from core.prompt_manager) ---

def test_save_mapping_to_json(tmp_path):
    mapping = [
        {"nickname": "nick1", "full_path": "path/to/file1.json"},
        {"nickname": "nick2", "full_path": "path/to/file2.json"},
    ]
    output_file = tmp_path / "output_map.json"
    prompt_manager.save_mapping_to_json(mapping, output_file)
    assert output_file.is_file()
    loaded_content = json.loads(output_file.read_text())
    assert loaded_content == mapping

# --- Tests for download_prompt_from_docsbot function (from core.prompt_manager) ---

@pytest.fixture
def mock_requests_get(mocker):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = """
        <h1>Test Title</h1>
        <p class="mx-auto mt-6 max-w-xl text-xl leading-8 text-gray-300">Test Description</p>
        <pre class="whitespace-pre-wrap overflow-auto">Test Prompt Content</pre>
    """
    mock_response.raise_for_status = Mock() # Mock raise_for_status
    mock_get = mocker.patch('requests.get', return_value=mock_response)
    return mock_get

def test_download_prompt_from_docsbot_success(tmp_path, mock_requests_get):
    url = "https://docsbot.ai/prompts/category/test-slug"
    output_dir = tmp_path / "downloads"
    downloaded_file = prompt_manager.download_prompt_from_docsbot(url, output_dir)

    assert downloaded_file is not None
    assert downloaded_file.is_file()
    assert downloaded_file.name == "prompts_category_test-slug.json"
    
    content = json.loads(downloaded_file.read_text())
    assert content["title"] == "Test Title"
    assert content["category"] == "category"
    assert content["prompt"] == "Test Prompt Content"
    mock_requests_get.assert_called_once_with(url)

def test_download_prompt_from_docsbot_failure(tmp_path, mocker):
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Network error"))
    output_dir = tmp_path / "downloads"
    downloaded_file = prompt_manager.download_prompt_from_docsbot("https://docsbot.ai/prompts/fail", output_dir)
    assert downloaded_file is None
    # Directory should be created even if download fails, as it's done before the request
    assert output_dir.is_dir()

# --- Tests for CLI prompt_manager map command (from cli.prompt_manager) ---

@pytest.fixture
def mock_map_prompt_files(mocker):
    return mocker.patch('morchaos.cli.prompt_manager.map_prompt_files')

@pytest.fixture
def mock_list_prompts(mocker):
    return mocker.patch('morchaos.cli.prompt_manager.list_prompts')

@pytest.fixture
def mock_download_prompt_from_docsbot(mocker):
    return mocker.patch('morchaos.cli.prompt_manager.download_prompt_from_docsbot')

@pytest.fixture
def mock_convert_prompt_format(mocker):
    return mocker.patch('morchaos.cli.prompt_manager.convert_prompt_format')

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
    assert "Prompts in '.':" in captured.out
    assert "- p1.txt" in captured.out

def test_cli_map_command_default_paths(mock_map_prompt_files, mocker):
    mocker.patch('sys.argv', ['prompt-manager', 'map'])
    mocker.patch('sys.exit')
    cli_prompt_manager.main()
    mock_map_prompt_files.assert_called_once_with(
        Path("TODO/system_prompt_collection/docsbot_prompts"),
        Path("prompt_file_map.json")
    )

def test_cli_map_command_custom_paths(mock_map_prompt_files, mocker):
    mocker.patch('sys.argv', [
        'prompt-manager', 'map',
        'my_prompts_folder',
        '--output-file', 'custom_map.json'
    ])
    mocker.patch('sys.exit')
    cli_prompt_manager.main()
    mock_map_prompt_files.assert_called_once_with(
        Path('my_prompts_folder'),
        Path('custom_map.json')
    )

def test_cli_map_command_error_handling(mock_map_prompt_files, mocker, capsys):
    mock_map_prompt_files.side_effect = NotADirectoryError("Test error")
    mocker.patch('sys.argv', ['prompt-manager', 'map', 'non_existent_folder'])
    with pytest.raises(SystemExit) as excinfo:
        cli_prompt_manager.main()
    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "Error mapping prompt files: Test error" in captured.err

def test_cli_download_command_success(mock_download_prompt_from_docsbot, mocker, capsys):
    mock_download_prompt_from_docsbot.return_value = Path("downloads/prompts_test.json")
    mocker.patch('sys.argv', ['prompt-manager', 'download', 'http://example.com/prompts', '--output-dir', 'downloads'])
    mocker.patch('sys.exit')
    cli_prompt_manager.main()
    mock_download_prompt_from_docsbot.assert_called_once_with('http://example.com/prompts', Path('downloads'))
    captured = capsys.readouterr()
    assert r"Successfully downloaded prompt from http://example.com/prompts to 'downloads\prompts_test.json'." in captured.err

def test_cli_download_command_failure(mock_download_prompt_from_docsbot, mocker, capsys):
    mock_download_prompt_from_docsbot.return_value = None
    mocker.patch('sys.argv', ['prompt-manager', 'download', 'http://example.com/fail'])
    with pytest.raises(SystemExit) as excinfo:
        cli_prompt_manager.main()
    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "Failed to download prompt from http://example.com/fail." in captured.err

def test_cli_no_command_provided(mocker, capsys):
    mocker.patch('sys.argv', ['prompt-manager'])
    with pytest.raises(SystemExit) as excinfo:
        cli_prompt_manager.main()
    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "usage: prompt-manager" in captured.out
    assert "Available commands" in captured.out
