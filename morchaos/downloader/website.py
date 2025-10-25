"""Generic website crawler and link extractor."""

from pathlib import Path
from typing import List, Set, Union
from urllib.parse import urljoin, urlparse

from .web import get_page, download_file, parse_html
from ..core.logging import get_logger
from ..core.slug import safe_filename

log = get_logger(__name__)


def extract_links(html: str, base_url: str, same_domain: bool = True) -> List[str]:
    """Extract all links from HTML."""
    soup = parse_html(html)
    links = []
    base_domain = urlparse(base_url).netloc

    for a in soup.find_all("a", href=True):
        href = a["href"]
        full_url = urljoin(base_url, href)

        if same_domain:
            if urlparse(full_url).netloc != base_domain:
                continue

        links.append(full_url)

    return links


def crawl_website(
    start_url: str, max_depth: int = 2, max_pages: int = 100
) -> List[str]:
    """Crawl a website and return all discovered URLs."""
    visited: Set[str] = set()
    to_visit = [(start_url, 0)]  # (url, depth)
    all_urls = []

    while to_visit and len(visited) < max_pages:
        url, depth = to_visit.pop(0)

        if url in visited or depth > max_depth:
            continue

        visited.add(url)
        all_urls.append(url)

        log.info(f"Crawling {url} (depth {depth})")

        html = get_page(url)
        if html is None:
            continue

        if depth < max_depth:
            links = extract_links(html, url)
            for link in links:
                if link not in visited:
                    to_visit.append((link, depth + 1))

    return all_urls


def download_website(
    url: str, dest: Union[str, Path], include_assets: bool = False
) -> bool:
    """Download a website's HTML and optionally its assets."""
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)

    html = get_page(url)
    if html is None:
        return False

    # Save the main HTML file
    parsed_url = urlparse(url)
    filename = parsed_url.path.split("/")[-1] or "index.html"
    if not filename.endswith(".html"):
        filename += ".html"

    html_file = dest / safe_filename(filename)

    try:
        with html_file.open("w", encoding="utf-8") as f:
            f.write(html)
        log.info(f"Saved HTML to {html_file}")

        if include_assets:
            # Download CSS, JS, and images
            soup = parse_html(html)

            # Download stylesheets
            for link in soup.find_all("link", rel="stylesheet"):
                href = link.get("href")
                if href:
                    asset_url = urljoin(url, href)
                    asset_name = Path(urlparse(asset_url).path).name
                    if asset_name:
                        download_file(asset_url, dest / safe_filename(asset_name))

            # Download scripts
            for script in soup.find_all("script", src=True):
                src = script.get("src")
                if src:
                    asset_url = urljoin(url, src)
                    asset_name = Path(urlparse(asset_url).path).name
                    if asset_name:
                        download_file(asset_url, dest / safe_filename(asset_name))

        return True

    except Exception as e:
        log.error(f"Failed to save website: {e}")
        return False
