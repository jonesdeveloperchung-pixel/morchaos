"""Archive.org game downloader."""

import re
from pathlib import Path
from typing import List, Dict, Union

from .web import get_page, download_file, parse_html
from ..core.logging import get_logger
from ..core.slug import safe_filename

log = get_logger(__name__)

DOS_GAME_URL = "https://dos.zczc.cz"
GAMES_PAGE = f"{DOS_GAME_URL}/games/"

def get_gamelist(page_html: str) -> List[Dict[str, str]]:
    """Parse the Archive.org games page and return a list of game dicts."""
    soup = parse_html(page_html)
    gamelist = []

    for li in soup.find_all("li"):
        a = li.find("a")
        if a and a.get('href'):
            gamelist.append({
                "name": a.text.strip(),
                "url": f"{DOS_GAME_URL}{a['href']}",
            })
    return gamelist

def get_downloadable_address(page_html: str) -> str:
    """Extract the direct download link from the game's page."""
    match = re.search(r'const\s+game_url\s*=\s*"([^"]+)"', page_html)
    if not match:
        raise ValueError("Could not find game_url on page")
    return match.group(1)

def download_game(game: Dict[str, str], dest: Union[str, Path]) -> bool:
    """Download a single game file into dest."""
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    
    page_html = get_page(game["url"])
    if page_html is None:
        log.warning(f"Skipping {game['name']} – page not available")
        return False

    try:
        url = get_downloadable_address(page_html)
        file_name = Path(url).name
        target = dest / safe_filename(file_name)

        if target.exists():
            log.info(f"{target} already downloaded")
            return True

        log.info(f"Downloading {game['name']} to {target}")
        return download_file(url, target)
        
    except Exception as e:
        log.error(f"Failed to download {game['name']}: {e}")
        return False

def download_games(url: str = GAMES_PAGE, dest: Union[str, Path] = "./games") -> None:
    """High-level helper that downloads all current games."""
    dest = Path(dest)
    page_html = get_page(url)
    if page_html is None:
        log.error("Could not fetch game list – aborting")
        return

    gamelist = get_gamelist(page_html)
    log.info(f"Found {len(gamelist)} games to download")
    
    for game in gamelist:
        download_game(game, dest)