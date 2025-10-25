"""Directory creation and management utilities."""

import shutil
from pathlib import Path
from typing import Union, List

from ..core.logging import get_logger

log = get_logger(__name__)


def create_directory(
    path: Union[str, Path], parents: bool = True, exist_ok: bool = True
) -> Path:
    """Create a directory."""
    path = Path(path)
    path.mkdir(parents=parents, exist_ok=exist_ok)
    log.info(f"Created directory: {path}")
    return path


def remove_directory(path: Union[str, Path], force: bool = False) -> None:
    """Remove a directory."""
    path = Path(path)

    if not path.exists():
        log.warning(f"Directory does not exist: {path}")
        return

    if not path.is_dir():
        raise ValueError(f"Path is not a directory: {path}")

    if force:
        shutil.rmtree(path)
        log.info(f"Force removed directory: {path}")
    else:
        try:
            path.rmdir()  # Only works if empty
            log.info(f"Removed empty directory: {path}")
        except OSError:
            raise ValueError(f"Directory not empty (use force=True): {path}")


def remove_empty_directories(root: Union[str, Path]) -> List[Path]:
    """Remove all empty directories under root."""
    root = Path(root)
    removed = []

    # Walk bottom-up to remove nested empty directories
    for path in sorted(root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if path.is_dir():
            try:
                path.rmdir()  # Only succeeds if empty
                removed.append(path)
                log.info(f"Removed empty directory: {path}")
            except OSError:
                # Directory not empty, skip
                pass

    log.info(f"Removed {len(removed)} empty directories")
    return removed


def rename_path(source: Union[str, Path], new_name: str) -> Path:
    """Rename a file or directory."""
    source = Path(source)

    if not source.exists():
        raise FileNotFoundError(f"Source does not exist: {source}")

    dest = source.parent / new_name

    if dest.exists():
        raise FileExistsError(f"Destination already exists: {dest}")

    source.rename(dest)
    log.info(f"Renamed {source} to {dest}")
    return dest


def list_directory_contents(
    path: Union[str, Path], recursive: bool = False, include_hidden: bool = False
) -> List[Path]:
    """List directory contents."""
    path = Path(path)

    if not path.is_dir():
        raise ValueError(f"Path is not a directory: {path}")

    if recursive:
        pattern = "**/*" if include_hidden else "**/[!.]*"
        contents = list(path.glob(pattern))
    else:
        pattern = "*" if include_hidden else "[!.]*"
        contents = list(path.glob(pattern))

    return sorted(contents)
