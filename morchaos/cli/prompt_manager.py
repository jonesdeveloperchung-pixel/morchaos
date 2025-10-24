import argparse
import sys
from pathlib import Path
from typing import List

from morchaos.core.prompt_manager import convert_prompt_format, list_prompts, read_prompt, map_prompt_files, download_prompt_from_docsbot
from morchaos.logger import init_logging, logger

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage system prompts for Ollama chat."
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert prompt format (txt to json, or json to txt).")
    convert_parser.add_argument("input_file", type=Path, help="Path to the input prompt file.")
    convert_parser.add_argument("output_file", type=Path, help="Path for the output prompt file.")

    # List command
    list_parser = subparsers.add_parser("list", help="List prompt files in a directory.")
    list_parser.add_argument("directory", type=Path, default=Path("."), nargs="?",
                             help="Directory to list prompts from (default: current directory).")

    # Map command
    map_parser = subparsers.add_parser("map", help="Map prompt files to nickname/fullname pairs.")
    map_parser.add_argument("folder_path", type=Path,
                            default=Path("TODO/system_prompt_collection/docsbot_prompts"), nargs="?",
                            help="Folder to scan for prompt files (default: TODO/system_prompt_collection/docsbot_prompts).")
    map_parser.add_argument("--output-file", type=Path, default=Path("prompt_file_map.json"),
                            help="Output JSON file for the mapping (default: prompt_file_map.json).")

    # Download command
    download_parser = subparsers.add_parser("download", help="Download prompts from a source (e.g., docsbot.ai).")
    download_parser.add_argument("source_url", type=str, help="URL to download prompts from.")
    download_parser.add_argument("--output-dir", type=Path, default=Path("."),
                                 help="Directory to save downloaded prompts (default: current directory).")

    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()

    init_logging() # Initialize logging

    if args.command == "convert":
        try:
            convert_prompt_format(args.input_file, args.output_file)
            logger.info(f"Successfully converted '{args.input_file}' to '{args.output_file}'.")
        except (FileNotFoundError, ValueError) as e:
            logger.error(f"Error converting prompt: {e}")
            sys.exit(1)
    elif args.command == "list":
        try:
            prompts = list_prompts(args.directory)
            if prompts:
                print(f"Prompts in '{args.directory}':")
                for p in prompts:
                    print(f"- {p.name}")
            else:
                print(f"No prompt files found in '{args.directory}'.")
        except NotADirectoryError as e:
            logger.error(f"Error listing prompts: {e}")
            sys.exit(1)
    elif args.command == "map":
        try:
            mappings = map_prompt_files(args.folder_path, args.output_file)
            logger.info(f"✅ Mapped {len(mappings)} prompt files to '{args.output_file}'")
        except (NotADirectoryError, FileNotFoundError, ValueError) as e:
            logger.error(f"Error mapping prompt files: {e}")
            sys.exit(1)
    elif args.command == "download":
        try:
            downloaded_file = download_prompt_from_docsbot(args.source_url, args.output_dir)
            if downloaded_file:
                logger.info(f"Successfully downloaded prompt from {args.source_url} to '{downloaded_file}'.")
            else:
                logger.error(f"Failed to download prompt from {args.source_url}.")
                sys.exit(1)
        except Exception as e:
            logger.error(f"Error downloading prompt: {e}")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
