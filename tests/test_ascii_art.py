"""Tests for ASCII art generation module."""

import pytest
from pathlib import Path
from PIL import Image

from morchaos.core.ascii_art import (
    generate_text_art,
    get_available_fonts,
    generate_image_art,
)


def test_get_available_fonts():
    """Test that get_available_fonts returns a list of strings."""
    fonts = get_available_fonts()
    assert isinstance(fonts, list)
    assert all(isinstance(font, str) for font in fonts)
    assert "banner3-D" in fonts


def test_generate_text_art():
    """Test text to ASCII art generation."""
    art = generate_text_art("Hello", font="banner3-D")
    assert isinstance(art, str)
    assert len(art) > 0


def test_generate_text_art_invalid_font():
    """Test that generate_text_art returns None for an invalid font."""
    art = generate_text_art("Hello", font="invalid-font-for-sure")
    assert art is None


@pytest.fixture
def create_test_image(tmp_path: Path) -> Path:
    """Create a simple black and white test image."""
    image_path = tmp_path / "test_image.png"
    img = Image.new("L", (10, 10), color="white")
    for x in range(10):
        for y in range(5):
            img.putpixel((x, y), 0)  # Black top half
    img.save(image_path)
    return image_path


def test_generate_image_art(create_test_image):
    """Test image to ASCII art generation."""
    image_path = create_test_image
    art = generate_image_art(image_path, width=10)
    assert isinstance(art, str)
    # Basic check for content
    assert "@" in art or "#" in art # Assuming these are dark characters
    assert "." in art or "," in art # Assuming these are light characters


def test_generate_image_art_nonexistent_file():
    """Test that generate_image_art returns None for a nonexistent file."""
    art = generate_image_art(Path("/nonexistent/image.png"))
    assert art is None
