"""YouTube video downloader using youtube-dl."""

import subprocess
import sys
from pathlib import Path
from typing import Union, Optional, List

from ..core.logging import get_logger

log = get_logger(__name__)


def check_youtube_dl() -> bool:
    """Check if youtube-dl is available."""
    try:
        subprocess.run(["youtube-dl", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False


def download_video(
    url: str,
    dest: Union[str, Path] = "./downloads",
    format_selector: str = "best",
    audio_only: bool = False,
) -> bool:
    """Download a YouTube video."""
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)

    if not check_youtube_dl():
        log.error("youtube-dl or yt-dlp not found. Please install one of them.")
        return False

    # Try yt-dlp first, then youtube-dl
    for cmd in ["yt-dlp", "youtube-dl"]:
        try:
            subprocess.run([cmd, "--version"], capture_output=True, check=True)
            downloader = cmd
            break
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    else:
        log.error("No YouTube downloader found")
        return False

    args = [
        downloader,
        "--output",
        str(dest / "%(title)s.%(ext)s"),
        "--format",
        "bestaudio" if audio_only else format_selector,
        url,
    ]

    try:
        log.info(f"Downloading {url} to {dest}")
        result = subprocess.run(args, capture_output=True, text=True)

        if result.returncode == 0:
            log.info("Download completed successfully")
            return True
        else:
            log.error(f"Download failed: {result.stderr}")
            return False

    except Exception as e:
        log.error(f"Error running {downloader}: {e}")
        return False


def download_playlist(
    url: str, dest: Union[str, Path] = "./downloads", format_selector: str = "best"
) -> bool:
    """Download a YouTube playlist."""
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)

    if not check_youtube_dl():
        log.error("youtube-dl or yt-dlp not found")
        return False

    # Determine which downloader to use
    downloader = "yt-dlp" if check_youtube_dl() else "youtube-dl"

    args = [
        downloader,
        "--output",
        str(dest / "%(playlist_index)s - %(title)s.%(ext)s"),
        "--format",
        format_selector,
        "--yes-playlist",
        url,
    ]

    try:
        log.info(f"Downloading playlist {url}")
        result = subprocess.run(args, capture_output=True, text=True)

        if result.returncode == 0:
            log.info("Playlist download completed")
            return True
        else:
            log.error(f"Playlist download failed: {result.stderr}")
            return False

    except Exception as e:
        log.error(f"Error downloading playlist: {e}")
        return False
