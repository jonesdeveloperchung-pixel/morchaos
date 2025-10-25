"""Zip file creation utilities."""

import zipfile
from pathlib import Path
from typing import Union, List, Optional

from ..core.logging import get_logger

log = get_logger(__name__)


def zip_path(
    source: Union[str, Path],
    dest: Optional[Union[str, Path]] = None,
    compression: int = zipfile.ZIP_DEFLATED,
) -> Path:
    """Zip a file or directory."""
    source = Path(source)

    if dest is None:
        dest = source.parent / f"{source.name}.zip"
    else:
        dest = Path(dest)
        if dest.is_dir():
            dest = dest / f"{source.name}.zip"

    log.info(f"Creating zip file: {dest}")

    with zipfile.ZipFile(dest, "w", compression) as zipf:
        if source.is_file():
            zipf.write(source, source.name)
        elif source.is_dir():
            for file_path in source.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(source)
                    zipf.write(file_path, arcname)
        else:
            raise ValueError(f"Source path does not exist: {source}")

    log.info(f"Created zip file: {dest}")
    return dest


def zip_files(
    files: List[Union[str, Path]],
    dest: Union[str, Path],
    compression: int = zipfile.ZIP_DEFLATED,
) -> Path:
    """Zip multiple files into a single archive."""
    dest = Path(dest)

    log.info(f"Creating zip file with {len(files)} files: {dest}")

    with zipfile.ZipFile(dest, "w", compression) as zipf:
        for file_path in files:
            file_path = Path(file_path)
            if file_path.is_file():
                zipf.write(file_path, file_path.name)
            else:
                log.warning(f"Skipping non-existent file: {file_path}")

    log.info(f"Created zip file: {dest}")
    return dest


def extract_zip(zip_path: Union[str, Path], dest: Union[str, Path]) -> Path:
    """Extract a zip file."""
    zip_path = Path(zip_path)
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)

    log.info(f"Extracting {zip_path} to {dest}")

    with zipfile.ZipFile(zip_path, "r") as zipf:
        zipf.extractall(dest)

    log.info(f"Extracted to: {dest}")
    return dest
