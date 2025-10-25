"""Image processing and base64 conversion utilities."""

from pathlib import Path
from typing import Union, Optional

from .base64 import encode_file, decode_to_file
from ..core.logging import get_logger

log = get_logger(__name__)


def image_to_base64(image_path: Union[str, Path]) -> str:
    """Convert image file to base64 string."""
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    # Check if it's likely an image file
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}
    if image_path.suffix.lower() not in image_extensions:
        log.warning(f"File may not be an image: {image_path}")

    return encode_file(image_path)


def base64_to_image(data: str, output_path: Union[str, Path]) -> Path:
    """Convert base64 string to image file."""
    output_path = Path(output_path)
    decode_to_file(data, output_path)
    log.info(f"Saved image to: {output_path}")
    return output_path


def get_image_data_url(
    image_path: Union[str, Path], mime_type: Optional[str] = None
) -> str:
    """Get data URL for image (for HTML embedding)."""
    image_path = Path(image_path)

    if mime_type is None:
        # Guess MIME type from extension
        ext = image_path.suffix.lower()
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".bmp": "image/bmp",
            ".webp": "image/webp",
            ".svg": "image/svg+xml",
        }
        mime_type = mime_types.get(ext, "image/jpeg")

    base64_data = image_to_base64(image_path)
    return f"data:{mime_type};base64,{base64_data}"


def extract_image_from_data_url(data_url: str, output_path: Union[str, Path]) -> Path:
    """Extract image from data URL."""
    if not data_url.startswith("data:"):
        raise ValueError("Invalid data URL")

    # Parse data URL: data:mime/type;base64,data
    header, data = data_url.split(",", 1)

    if "base64" not in header:
        raise ValueError("Only base64 data URLs are supported")

    return base64_to_image(data, output_path)
