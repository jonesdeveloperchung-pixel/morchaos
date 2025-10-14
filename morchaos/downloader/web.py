"""Generic HTTP downloader using requests."""

import time
from pathlib import Path
from typing import Optional, Dict, Any
import requests
from bs4 import BeautifulSoup

from ..core.logging import get_logger

log = get_logger(__name__)

DEFAULT_HEADERS = {
    'User-Agent': 'pyutils/1.0.0 (https://github.com/pyutils/pyutils)'
}

def get_page(url: str, headers: Optional[Dict[str, str]] = None, 
             timeout: int = 30, retries: int = 3) -> Optional[str]:
    """Download a web page with retry logic."""
    headers = {**DEFAULT_HEADERS, **(headers or {})}
    
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            log.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                log.error(f"Failed to download {url} after {retries} attempts")
                return None

def download_file(url: str, dest: Path, headers: Optional[Dict[str, str]] = None,
                 timeout: int = 30, chunk_size: int = 8192) -> bool:
    """Download a file to disk."""
    headers = {**DEFAULT_HEADERS, **(headers or {})}
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout, stream=True)
        response.raise_for_status()
        
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        with dest.open('wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
        
        log.info(f"Downloaded {url} to {dest}")
        return True
        
    except requests.RequestException as e:
        log.error(f"Failed to download {url}: {e}")
        return False

def parse_html(html: str) -> BeautifulSoup:
    """Parse HTML content with BeautifulSoup."""
    return BeautifulSoup(html, 'html.parser')