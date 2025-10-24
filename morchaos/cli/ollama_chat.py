import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any

from morchaos.core.ollama_chat import run_chat, health_check, list_models
from morchaos.core.prompt_manager import read_prompt
from morchaos.logger import init_logging, logger

PROMPT_MAP_FILE = Path("prompt_file_map.json")

def _load_prompt_map() -> Dict[str, str]:
    """Loads the prompt nickname to full filename mapping."""
    if PROMPT_MAP_FILE.is_file():
        with open(PROMPT_MAP_FILE, 'r', encoding='utf-8') as f:
            mapping_list = json.load(f)
            return {item['nickname']: item['full_path'] for item in mapping_list}
    return {}

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Send a system + user prompt to an Ollama model."
    )

    # System prompt options (mutually exclusive)
    sys_group = parser.add_mutually_exclusive_group()
    sys_group.add_argument('-S', '--system-prompt',
                           help="System prompt as a string.")
    sys_group.add_argument('--sf', '--system-file', dest='system_file',
                           help="File containing the system prompt (plain text or JSON) or a nickname from prompt_file_map.json.")

    # User prompt options (mutually exclusive)
    user_group = parser.add_mutually_exclusive_group()
    user_group.add_argument('-U', '--user-prompt',
                           help="User prompt as a string.")
    user_group.add_argument('--uf', '--user-file', dest='user_file',
                           help="File containing the user prompt or a nickname from prompt_file_map.json.")

    # Optional debug flag
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help="Print stack traces on errors.")

    # Optional model selector
    parser.add_argument('-m', '--model',
                        default='gemma3:4b',
                        help="Ollama model name.")

    # Optional URL and timeout
    parser.add_argument('--url', '-u',
                        default='http://localhost:11434',
                        help='Base URL of the chat model API.')
    parser.add_argument('--timeout', '-t',
                        type=int, default=30,
                        help='Request timeout in seconds.')

    # Optional list models and health check
    parser.add_argument('--list-models', '-l',
                        action='store_true',
                        help='List available models and exit.')
    parser.add_argument('--health-check', '-H', # Changed to -H to avoid conflict with -h for help
                        action='store_true',
                        help='Check if the endpoint is healthy and exit.')

    return parser

def build_messages(system_prompt: str, user_prompt: str) -> list[dict[str, str]]:
    """Return the message list in the order required by Ollama."""
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_prompt}
    ]

def main():
    parser = build_parser()
    args = parser.parse_args()

    init_logging(level=20 if args.debug else 30) # Use debug flag for verbose logging

    prompt_map = _load_prompt_map()

    # Resolve system_file nickname if provided
    if args.system_file and args.system_file in prompt_map:
        args.system_file = Path(prompt_map[args.system_file])
    elif args.system_file: # If it's not a nickname, ensure it's a Path object
        args.system_file = Path(args.system_file)

    # Resolve user_file nickname if provided
    if args.user_file and args.user_file in prompt_map:
        args.user_file = Path(prompt_map[args.user_file])
    elif args.user_file: # If it's not a nickname, ensure it's a Path object
        args.user_file = Path(args.user_file)

    if args.health_check:
        if health_check(args.url, args.timeout):
            print(f"✓ Endpoint {args.url} is healthy")
            sys.exit(0)
        else:
            print(f"✗ Endpoint {args.url} is not responding", file=sys.stderr)
            sys.exit(1)

    if args.list_models:
        models = list_models(args.url, args.timeout)
        if models:
            print("Available models:")
            for model_name in models:
                print(f"  {model_name}")
        else:
            print("No models found or endpoint not available")
        sys.exit(0)

    try:
        system_prompt = read_prompt(
            source=args.system_prompt,
            file_path=args.system_file,
            prompt_name="system",
            default="You are a helpful assistant."
        )
        user_prompt = read_prompt(
            source=args.user_prompt,
            file_path=args.user_file,
            prompt_name="user",
            default=None  # user prompt is required
        )
    except ValueError as err:
        parser.error(str(err))

    messages = build_messages(system_prompt, user_prompt)

    try:
        asyncio.run(run_chat(messages, model=args.model, url=args.url, timeout=args.timeout))
    except RuntimeError as e:
        if args.debug:
            logger.exception("Ollama chat failed")
        else:
            logger.error(f"Ollama chat failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
