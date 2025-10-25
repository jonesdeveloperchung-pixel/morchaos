"""XKCD comic downloader."""

import json
from pathlib import Path
from typing import Union, Optional, Dict, Any

from .web import get_page, download_file
from ..core.logging import get_logger
from ..core.slug import safe_filename

log = get_logger(__name__)

XKCD_API_URL = "https://xkcd.com/{}/info.0.json"
XKCD_LATEST_URL = "https://xkcd.com/info.0.json"


def get_comic_info(comic_id: int) -> Optional[Dict[str, Any]]:
    """Get comic information from XKCD API."""
    url = XKCD_API_URL.format(comic_id)
    content = get_page(url)

    if content is None:
        return None

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        log.error(f"Failed to parse JSON for comic {comic_id}")
        return None


def get_latest_comic_id() -> Optional[int]:
    """Get the ID of the latest comic."""
    content = get_page(XKCD_LATEST_URL)
    if content is None:
        return None

    try:
        data = json.loads(content)
        return data.get("num")
    except json.JSONDecodeError:
        log.error("Failed to parse latest comic info")
        return None


def download_comic(comic_id: int, dest: Union[str, Path]) -> bool:
    """Download a single XKCD comic."""
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)

    comic_info = get_comic_info(comic_id)
    if comic_info is None:
        log.warning(f"Could not get info for comic {comic_id}")
        return False

    img_url = comic_info.get("img")
    if not img_url:
        log.warning(f"No image URL for comic {comic_id}")
        return False

    # Create filename: "001_comic_title.png"
    title = comic_info.get("title", "untitled")
    ext = Path(img_url).suffix or ".png"
    filename = f"{comic_id:03d}_{safe_filename(title)}{ext}"
    target = dest / filename

    if target.exists():
        log.info(f"Comic {comic_id} already downloaded")
        return True

    log.info(f"Downloading comic {comic_id}: {title}")
    return download_file(img_url, target)


def download_all_comics(
    dest: Union[str, Path] = "./xkcd", start: int = 1, end: Optional[int] = None
) -> None:
    """Download all XKCD comics."""
    dest = Path(dest)

    if end is None:
        end = get_latest_comic_id()
        if end is None:
            log.error("Could not determine latest comic ID")
            return

    log.info(f"Downloading comics {start} to {end}")

    for comic_id in range(start, end + 1):
        # Comic 404 doesn't exist (it's a joke)
        if comic_id == 404:
            continue

        download_comic(comic_id, dest)
