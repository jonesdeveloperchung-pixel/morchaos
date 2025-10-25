"""Image downloader and scraper."""

import re
from pathlib import Path
from typing import List, Union, Optional
from urllib.parse import urljoin, urlparse

from .web import get_page, download_file, parse_html
from ..core.logging import get_logger
from ..core.slug import safe_filename

log = get_logger(__name__)


def extract_image_urls(html: str, base_url: str) -> List[str]:
    """Extract all image URLs from HTML."""
    soup = parse_html(html)
    urls = []

    for img in soup.find_all("img"):
        src = img.get("src")
        if src:
            # Convert relative URLs to absolute
            full_url = urljoin(base_url, src)
            urls.append(full_url)

    return urls


def is_valid_image_url(url: str) -> bool:
    """Check if URL points to a valid image."""
    parsed = urlparse(url)
    path = parsed.path.lower()

    # Check for common image extensions
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"}
    return any(path.endswith(ext) for ext in image_extensions)


def download_images_from_page(
    url: str, dest: Union[str, Path], filter_size: bool = True
) -> List[str]:
    """Download all images from a web page."""
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)

    html = get_page(url)
    if html is None:
        log.error(f"Could not fetch page: {url}")
        return []

    image_urls = extract_image_urls(html, url)
    valid_urls = [u for u in image_urls if is_valid_image_url(u)]

    log.info(f"Found {len(valid_urls)} images on {url}")

    downloaded = []
    for img_url in valid_urls:
        try:
            filename = Path(urlparse(img_url).path).name
            if not filename:
                filename = f"image_{len(downloaded)}.jpg"

            target = dest / safe_filename(filename)

            # Avoid overwriting files
            counter = 1
            while target.exists():
                stem = target.stem
                suffix = target.suffix
                target = dest / f"{stem}_{counter}{suffix}"
                counter += 1

            if download_file(img_url, target):
                downloaded.append(str(target))

        except Exception as e:
            log.warning(f"Failed to download {img_url}: {e}")

    log.info(f"Downloaded {len(downloaded)} images")
    return downloaded


def search_and_download_images(
    query: str, dest: Union[str, Path], max_images: int = 20
) -> List[str]:
    """Search for images and download them (basic implementation)."""
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)

    # This is a simplified implementation
    # In practice, you'd use proper image search APIs
    log.warning("Basic image search - consider using proper APIs for production")

    search_url = f"https://www.google.com/search?q={query}&tbm=isch"
    return download_images_from_page(search_url, dest)
