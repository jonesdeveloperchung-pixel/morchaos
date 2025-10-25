import json
from pathlib import Path
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


def extract_nickname(filename: str) -> str:
    """
    Extracts a nickname from a filename by removing the 'prompts_' prefix and '.json' suffix.
    """
    if filename.startswith("prompts_") and filename.endswith(".json"):
        return filename[len("prompts_") : -len(".json")]
    return filename


def map_prompt_files(
    folder_path: Path, output_path: Path | None = None
) -> List[Dict[str, str]]:
    """
    Scans for .json files starting with 'prompts_' and maps them.
    If output_path is provided, saves the mapping to a JSON file.
    """
    if not folder_path.is_dir():
        raise NotADirectoryError(f"Folder not found: {folder_path}")

    # Ensure folder_path is absolute before iterating to get correct relative paths
    absolute_folder_path = folder_path.resolve()

    prompt_mappings = []
    for file in absolute_folder_path.iterdir():
        if (
            file.is_file()
            and file.name.startswith("prompts_")
            and file.name.endswith(".json")
        ):
            nickname = extract_nickname(file.name)
            # Store the relative path from the current working directory
            relative_path = file.relative_to(Path.cwd())
            prompt_mappings.append(
                {
                    "nickname": nickname,
                    "full_path": str(
                        relative_path
                    ),  # Store as string for JSON serialization
                }
            )

    if output_path:
        save_mapping_to_json(prompt_mappings, output_path)

    return prompt_mappings


def save_mapping_to_json(mapping: List[Dict[str, str]], output_path: Path):
    """
    Saves the mapping list to a JSON file.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)


def read_prompt(
    source: str | None,
    file_path: str | None,
    prompt_name: str,
    default: str | None = None,
) -> str:
    """
    Resolve a prompt either from a string or from a file.

    :param source: Prompt supplied directly (string)
    :param file_path: Path to a file containing the prompt
    :param prompt_name: "system" or "user" – used in error messages
    :param default: Default prompt if neither source nor file is supplied
    :return: Prompt string
    :raises ValueError: if prompt is empty or file cannot be read
    """
    if source is not None:
        prompt = source
    elif file_path is not None:
        path = Path(file_path)
        if not path.is_file():
            raise ValueError(
                f"{prompt_name.capitalize()} file '{file_path}' not found."
            )
        try:
            if prompt_name == "system" and path.suffix == ".json":
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    prompt = data.get("prompt", "")
            else:
                prompt = path.read_text(encoding="utf-8")
        except Exception as exc:
            raise ValueError(
                f"Could not read {prompt_name} file '{file_path}': {exc}"
            ) from exc
    elif default is not None:
        prompt = default
    else:
        raise ValueError(f"No {prompt_name} prompt provided.")

    if not prompt.strip():
        raise ValueError(f"{prompt_name.capitalize()} prompt is empty.")
    return prompt


def convert_prompt_format(input_path: Path, output_path: Path):
    """
    Converts a prompt file between .txt and .json formats.

    If input is .txt, converts to .json. If input is .json, converts to .txt.
    """
    if not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if input_path.suffix == ".txt":
        content = input_path.read_text(encoding="utf-8")
        output_path = output_path.with_suffix(".json")
        json_content = {"prompt": content}
        output_path.write_text(json.dumps(json_content, indent=2), encoding="utf-8")
    elif input_path.suffix == ".json":
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            content = data.get("prompt", "")
        output_path = output_path.with_suffix(".txt")
        output_path.write_text(content, encoding="utf-8")
    else:
        raise ValueError(
            f"Unsupported format: {input_path.suffix}. Only .txt and .json are supported."
        )


def list_prompts(directory: Path) -> List[Path]:
    """
    Lists all prompt files (.txt and .json) in a given directory.
    """
    if not directory.is_dir():
        raise NotADirectoryError(f"Directory not found: {directory}")

    prompts = []
    for item in directory.iterdir():
        if item.is_file() and item.suffix in [".txt", ".json"]:
            prompts.append(item)
    return prompts


def slug_from_url(url: str) -> str:
    """Generate a slug from the URL (i.e., valid filename)"""
    parsed = urlparse(url)
    return parsed.path.strip("/").replace("/", "_")


def extract_prompt_data(url: str) -> Dict[str, Any] | None:
    """Extract the title, description, and prompt from the page"""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract title
    title_tag = soup.find("h1")
    title = title_tag.text.strip() if title_tag else "Untitled"

    # Extract description (assuming it is in a 'p' tag or other recognizable container)
    description_tag = soup.find(
        "p", class_="mx-auto mt-6 max-w-xl text-xl leading-8 text-gray-300"
    )
    description = (
        description_tag.text.strip() if description_tag else "No description available"
    )

    # Extract prompt content (heuristic: using pre tag for prompt content)
    prompt_section = soup.find("pre", class_="whitespace-pre-wrap overflow-auto")
    prompt_text = (
        prompt_section.text.strip() if prompt_section else "No prompt content available"
    )

    # Extract category from URL (based on folder in the URL path)
    path_parts = urlparse(url).path.strip("/").split("/")
    category = path_parts[1] if len(path_parts) > 1 else "uncategorized"

    return {
        "title": title,
        "category": category,
        "url": url,
        "description": description,
        "prompt": prompt_text,
    }


def download_prompt_from_docsbot(url: str, output_dir: Path) -> Path | None:
    """
    Downloads a prompt from DocsBot.ai and saves it as a JSON file.
    """
    if not output_dir.is_dir():
        output_dir.mkdir(parents=True, exist_ok=True)

    data = extract_prompt_data(url)
    if data:
        slug = slug_from_url(url)
        filepath = output_dir / f"{slug}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved prompt from {url} to '{filepath}'.")
        return filepath
    else:
        logger.error(f"Failed to download prompt from {url}.")
        return None
