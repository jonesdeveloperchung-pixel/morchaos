"""File and directory moving utilities."""

import shutil
import time
from pathlib import Path
from typing import Union, List

from ..core.logging import get_logger

log = get_logger(__name__)


def move_path(source: Union[str, Path], dest: Union[str, Path]) -> Path:
    """Move a file or directory."""
    source = Path(source)
    dest = Path(dest)

    if not source.exists():
        raise FileNotFoundError(f"Source does not exist: {source}")

    # If dest is a directory, move source into it
    if dest.is_dir():
        dest = dest / source.name

    log.info(f"Moving {source} to {dest}")

    # Create parent directory if needed
    dest.parent.mkdir(parents=True, exist_ok=True)

    shutil.move(str(source), str(dest))
    log.info(f"Moved to: {dest}")
    return dest


def move_files_by_age(
    source_dir: Union[str, Path],
    dest_dir: Union[str, Path],
    days_old: int,
    pattern: str = "*",
) -> List[Path]:
    """Move files older than specified days."""
    source_dir = Path(source_dir)
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    cutoff_time = time.time() - (days_old * 24 * 60 * 60)
    moved_files = []

    for file_path in source_dir.glob(pattern):
        if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
            dest_path = dest_dir / file_path.name

            # Handle name conflicts
            counter = 1
            while dest_path.exists():
                stem = file_path.stem
                suffix = file_path.suffix
                dest_path = dest_dir / f"{stem}_{counter}{suffix}"
                counter += 1

            try:
                shutil.move(str(file_path), str(dest_path))
                moved_files.append(dest_path)
                log.info(f"Moved old file: {file_path} -> {dest_path}")
            except Exception as e:
                log.error(f"Failed to move {file_path}: {e}")

    log.info(f"Moved {len(moved_files)} files older than {days_old} days")
    return moved_files


def copy_path(source: Union[str, Path], dest: Union[str, Path]) -> Path:
    """Copy a file or directory."""
    source = Path(source)
    dest = Path(dest)

    if not source.exists():
        raise FileNotFoundError(f"Source does not exist: {source}")

    # If dest is a directory, copy source into it
    if dest.is_dir():
        dest = dest / source.name

    log.info(f"Copying {source} to {dest}")

    # Create parent directory if needed
    dest.parent.mkdir(parents=True, exist_ok=True)

    if source.is_file():
        shutil.copy2(str(source), str(dest))
    else:
        shutil.copytree(str(source), str(dest), dirs_exist_ok=True)

    log.info(f"Copied to: {dest}")
    return dest
