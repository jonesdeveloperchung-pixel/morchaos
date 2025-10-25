"""CLI for Archive.org downloader."""

import argparse

from ..downloader.archive_org import download_games
from ..core.logging import get_logger, set_log_level


def main():
    """Main CLI entry point for Archive.org downloader."""
    parser = argparse.ArgumentParser(description="Download games from Archive.org")
    parser.add_argument(
        "--url", default="https://dos.zczc.cz/games/", help="URL to scrape for games"
    )
    parser.add_argument("--dest", default="./games", help="Destination directory")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        set_log_level("DEBUG")

    log = get_logger(__name__)
    log.info(f"Starting Archive.org download to {args.dest}")

    download_games(args.url, args.dest)
    log.info("Download completed")


if __name__ == "__main__":
    main()
