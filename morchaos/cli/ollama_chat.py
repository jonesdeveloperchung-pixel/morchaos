import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict

from morchaos.core.ollama_chat import run_chat, health_check, list_models
from morchaos.core.prompt_manager import read_prompt
from morchaos.logger import init_logging, logger

PROMPT_MAP_FILE = Path("prompt_file_map.json")


def _load_prompt_map() -> Dict[str, str]:
    """Loads the prompt nickname to full filename mapping."""
    if PROMPT_MAP_FILE.is_file():
        with open(PROMPT_MAP_FILE, "r", encoding="utf-8") as f:
            mapping_list = json.load(f)
            return {item["nickname"]: item["full_path"] for item in mapping_list}
    return {}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Send a system + user prompt to an Ollama model."
    )

    # System prompt options (mutually exclusive)
    sys_group = parser.add_mutually_exclusive_group()
    sys_group.add_argument("-s", "--system", dest="system_prompt",
                           help="System prompt as a string.")
    sys_group.add_argument(
        "-sf",
        "--system-file",
        dest="system_file",
        help="File containing the system prompt (plain text or JSON) "
             "or a nickname from prompt_file_map.json.",
    )

    # User prompt options (mutually exclusive)
    user_group = parser.add_mutually_exclusive_group()
    user_group.add_argument("-p", "--prompt", dest="user_prompt",
                            help="User prompt as a string.")
    user_group.add_argument(
        "-uf",
        "--user-file",
        dest="user_file",
        help="File containing the user prompt or a nickname from prompt_file_map.json.",
    )

    # Optional debug flag
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Print stack traces on errors."
    )

    # Interactive mode
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Enable interactive chat mode."
    )

    # Optional model selector
    parser.add_argument("-m", "--model", default="gemma3:4b", help="Ollama model name.")

    # Optional URL and timeout
    parser.add_argument(
        "--url",
        "-u",
        default="http://localhost:11434",
        help="Base URL of the chat model API.",
    )
    parser.add_argument(
        "--timeout", "-t", type=int, default=120, help="Request timeout in seconds."
    )

    # Optional list models and health check
    parser.add_argument(
        "-l",
        "--list",
        dest="list_models",
        action="store_true",
        help="List available models and exit.",
    )
    parser.add_argument(
        "-H",
        "--health-check",
        action="store_true",
        help="Check if the endpoint is healthy and exit.",
    )

    return parser


def build_messages(system_prompt: str, user_prompt: str) -> list[dict[str, str]]:
    """Return the message list in the order required by Ollama."""
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def main():
    parser = build_parser()
    args = parser.parse_args()

    init_logging(level=20 if args.debug else 30)

    prompt_map = _load_prompt_map()

    if args.system_file and args.system_file in prompt_map:
        args.system_file = Path(prompt_map[args.system_file])
    elif args.system_file:
        args.system_file = Path(args.system_file)

    if args.user_file and args.user_file in prompt_map:
        args.user_file = Path(prompt_map[args.user_file])
    elif args.user_file:
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
            max_name_len = max(len(model["name"]) for model in models) if models else 0
            print(f"{'NAME':<{max_name_len}}  {'SIZE':>10}  {'MODIFIED':<20}")
            print(f"{'-' * max_name_len}  {'-' * 10}  {'-' * 20}")
            for model in models:
                name = model["name"]
                size = model["size"]
                modified_at = model["modified_at"]
                if isinstance(size, int):
                    if size < 1024:
                        size_str = f"{size} B"
                    elif size < 1024**2:
                        size_str = f"{size/1024:.2f} KB"
                    elif size < 1024**3:
                        size_str = f"{size/1024**2:.2f} MB"
                    else:
                        size_str = f"{size/1024**3:.2f} GB"
                else:
                    size_str = str(size)
                if isinstance(modified_at, str):
                    modified_str = modified_at.split("T")[0]
                elif hasattr(modified_at, "isoformat"):
                    modified_str = modified_at.isoformat().split("T")[0]
                else:
                    modified_str = str(modified_at)
                print(f"{name:<{max_name_len}}  {size_str:>10}  {modified_str:<20}")
        else:
            print("No models found or endpoint not available")
        sys.exit(0)

    try:
        system_prompt = read_prompt(
            source=args.system_prompt,
            file_path=args.system_file,
            prompt_name="system",
            default="You are a helpful assistant.",
        )
    except ValueError as err:
        parser.error(str(err))

    if args.interactive:
        messages = [{"role": "system", "content": system_prompt}]
        print("Entering interactive mode. Type 'exit' or 'quit' to end.")
        while True:
            try:
                user_input = input(">>> ")
                if user_input.lower() in ["exit", "quit"]:
                    break
                messages.append({"role": "user", "content": user_input})
                full_response = asyncio.run(
                    run_chat(messages, model=args.model, url=args.url, timeout=args.timeout)
                )
                if full_response:
                    messages.append({"role": "assistant", "content": full_response})
            except KeyboardInterrupt:
                print("\nExiting interactive mode.")
                break
            except RuntimeError as e:
                if args.debug:
                    logger.exception("Ollama chat failed")
                else:
                    logger.error(f"Ollama chat failed: {e}")
    else:
        try:
            user_prompt = read_prompt(
                source=args.user_prompt,
                file_path=args.user_file,
                prompt_name="user",
                default=None,
            )
        except ValueError as err:
            parser.error(str(err))

        if not user_prompt:
            parser.error("No user prompt provided. Use -p, --prompt, -uf, or -i.")

        messages = build_messages(system_prompt, user_prompt)

        try:
            asyncio.run(
                run_chat(messages, model=args.model, url=args.url, timeout=args.timeout)
            )
        except RuntimeError as e:
            if args.debug:
                logger.exception("Ollama chat failed")
            else:
                logger.error(f"Ollama chat failed: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
