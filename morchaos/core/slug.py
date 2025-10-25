"""String sanitization helpers for creating safe filenames."""

import re
import unicodedata
from pathlib import Path


def slugify(text: str, max_length: int = 255) -> str:
    """Convert a string to a safe filename."""
    # Normalize unicode characters
    text = unicodedata.normalize("NFKD", text)

    # Remove non-ASCII characters
    text = text.encode("ascii", "ignore").decode("ascii")

    # Replace spaces and special characters with underscores
    text = re.sub(r"[^\w\s-]", "_", text)
    text = re.sub(r"[-\s]+", "_", text)

    # Remove leading/trailing underscores
    text = text.strip("_")

    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length].rstrip("_")

    return text or "unnamed"


def safe_filename(filename: str) -> str:
    """Make a filename safe for the filesystem."""
    path = Path(filename)
    stem = slugify(path.stem)
    suffix = path.suffix

    # Clean the suffix too
    suffix = re.sub(r"[^\w.]", "", suffix)

    return f"{stem}{suffix}"
