"""CLI for YouTube downloader."""

import argparse

from ..downloader.youtube import download_video, download_playlist
from ..core.logging import get_logger, set_log_level


def main():
    """Main CLI entry point for YouTube downloader."""
    parser = argparse.ArgumentParser(description="Download YouTube videos")
    parser.add_argument("url", help="YouTube video or playlist URL")
    parser.add_argument("--dest", default="./downloads", help="Destination directory")
    parser.add_argument("--format", default="best", help="Video format selector")
    parser.add_argument("--audio-only", action="store_true", help="Download audio only")
    parser.add_argument("--playlist", action="store_true", help="Download as playlist")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        set_log_level("DEBUG")

    log = get_logger(__name__)

    if args.playlist:
        log.info(f"Downloading YouTube playlist: {args.url}")
        success = download_playlist(args.url, args.dest, args.format)
    else:
        log.info(f"Downloading YouTube video: {args.url}")
        success = download_video(args.url, args.dest, args.format, args.audio_only)

    if success:
        log.info("Download completed successfully")
    else:
        log.error("Download failed")
        exit(1)


if __name__ == "__main__":
    main()
