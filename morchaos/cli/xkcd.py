"""CLI for XKCD downloader."""

import argparse

from ..downloader.xkcd import download_all_comics, download_comic
from ..core.logging import get_logger, set_log_level


def main():
    """Main CLI entry point for XKCD downloader."""
    parser = argparse.ArgumentParser(description="Download XKCD comics")
    parser.add_argument("--dest", default="./xkcd", help="Destination directory")
    parser.add_argument("--start", type=int, default=1, help="Starting comic number")
    parser.add_argument("--end", type=int, help="Ending comic number (default: latest)")
    parser.add_argument("--single", type=int, help="Download single comic by number")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        set_log_level("DEBUG")

    log = get_logger(__name__)

    if args.single:
        log.info(f"Downloading XKCD comic {args.single}")
        download_comic(args.single, args.dest)
    else:
        log.info(f"Downloading XKCD comics {args.start} to {args.end or 'latest'}")
        download_all_comics(args.dest, args.start, args.end)

    log.info("Download completed")


if __name__ == "__main__":
    main()
