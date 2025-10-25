"""Duplicate file detection and removal."""

from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Union, Literal

from ..core.logging import get_logger
from ..core.utils import calculate_file_hash

log = get_logger(__name__)

KeepStrategy = Literal["longer", "shorter", "first"]


def find_duplicates(
    paths: List[Union[str, Path]], algorithm: str = "md5"
) -> Dict[str, List[Path]]:
    """Find duplicate files by hash."""
    hash_to_files = defaultdict(list)

    for path in paths:
        path = Path(path)
        if path.is_file():
            try:
                file_hash = calculate_file_hash(path, algorithm)
                hash_to_files[file_hash].append(path)
            except Exception as e:
                log.warning(f"Could not hash {path}: {e}")
        elif path.is_dir():
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    try:
                        file_hash = calculate_file_hash(file_path, algorithm)
                        hash_to_files[file_hash].append(file_path)
                    except Exception as e:
                        log.warning(f"Could not hash {file_path}: {e}")

    # Return only groups with duplicates
    return {h: files for h, files in hash_to_files.items() if len(files) > 1}


def remove_duplicates(
    duplicate_groups: Dict[str, List[Path]],
    strategy: KeepStrategy = "longer",
    dry_run: bool = False,
) -> List[Path]:
    """Remove duplicate files according to strategy."""
    removed_files = []

    for file_hash, files in duplicate_groups.items():
        if len(files) <= 1:
            continue

        # Determine which file to keep
        if strategy == "longer":
            keep_file = max(files, key=lambda f: len(f.name))
        elif strategy == "shorter":
            keep_file = min(files, key=lambda f: len(f.name))
        else:  # 'first'
            keep_file = files[0]

        # Remove the others
        for file_path in files:
            if file_path != keep_file:
                log.info(f"{'Would remove' if dry_run else 'Removing'}: {file_path}")
                if not dry_run:
                    try:
                        file_path.unlink()
                        removed_files.append(file_path)
                    except Exception as e:
                        log.error(f"Failed to remove {file_path}: {e}")
                else:
                    removed_files.append(file_path)

    return removed_files


def find_and_remove_duplicates(
    paths: List[Union[str, Path]],
    strategy: KeepStrategy = "longer",
    dry_run: bool = False,
) -> List[Path]:
    """Find and remove duplicate files in one operation."""
    log.info(f"Scanning for duplicates in {len(paths)} paths")

    duplicates = find_duplicates(paths)
    total_duplicates = sum(len(files) - 1 for files in duplicates.values())

    log.info(f"Found {len(duplicates)} groups with {total_duplicates} duplicate files")

    if total_duplicates == 0:
        return []

    return remove_duplicates(duplicates, strategy, dry_run)
