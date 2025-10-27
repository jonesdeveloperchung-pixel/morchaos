"""Core functions for ASCII art generation from text, images, and videos."""

import logging
import sys
import time
from pathlib import Path
from typing import List, Optional

try:
    import pyfiglet
    from pyfiglet import FigletFont
except ImportError:
    raise ImportError("Missing dependency: pyfiglet. Install with 'pip install pyfiglet'")

try:
    from PIL import Image
except ImportError:
    raise ImportError("Missing dependency: Pillow. Install with 'pip install Pillow'")

try:
    import cv2
    import numpy as np
except ImportError:
    raise ImportError("Missing dependency: opencv-python, numpy. Install with 'pip install opencv-python numpy'")

try:
    from pydub import AudioSegment
    from pydub.playback import play
except ImportError:
    raise ImportError("Missing dependency: pydub. Install with 'pip install pydub'")


logger = logging.getLogger(__name__)

# ASCII characters used for image conversion
ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]


def get_available_fonts() -> List[str]:
    """Get a list of available pyfiglet fonts."""
    return FigletFont.getFonts()


def generate_text_art(
    text: str,
    font: str = "banner3-D",
    width: int = 80,
    justify: str = "left",
) -> Optional[str]:
    """Generate ASCII art from text."""
    if font not in get_available_fonts():
        logger.error(f"Font '{font}' not found.")
        return None

    try:
        return pyfiglet.figlet_format(text, font=font, width=width, justify=justify)
    except Exception as e:
        logger.error(f"Could not render ASCII art with font {font}: {e}")
        return None


def generate_image_art(
    image_path: Path,
    width: int = 80,
    height: Optional[int] = None,
    chars: List[str] = ASCII_CHARS,
    brightness: float = 1.0,
    color_mode: str = "text",
) -> Optional[str]:
    """Convert an image to ASCII art."""
    if not image_path.is_file():
        logger.error(f"Image file not found: {image_path}")
        return None

    try:
        img = cv2.imread(str(image_path))
        if img is None:
            logger.error(f"Failed to read image file: {image_path}")
            return None

        if height is None:
            aspect_ratio = img.shape[0] / img.shape[1]
            if color_mode == "ansi":
                height = int(aspect_ratio * width * 0.5)
            else:
                height = int(aspect_ratio * width * 0.55)

        resized_img = cv2.resize(img, (width, height))

        if color_mode == "ansi":
            ascii_art = ""
            for row in resized_img:
                ascii_art += "".join([_pixel_to_ansi(pixel) for pixel in row])
                ascii_art += "\n"
        else:
            grayscale_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)
            pixels = grayscale_img.flatten()
            ascii_str = "".join([chars[max(0, min(len(chars) - 1, int(pixel * brightness * len(chars) / 256)))] for pixel in pixels])
            ascii_art = "\n".join([ascii_str[i:i+width] for i in range(0, len(ascii_str), width)])
        return ascii_art
    except Exception as e:
        logger.error(f"Failed to process image {image_path}: {e}")
        return None


def _pixel_to_ansi(pixel, source_format: str = "bgr") -> str:
    """Convert a pixel to an RGB ANSI color code."""
    if source_format == "bgr":
        b, g, r = pixel
    else: # rgb
        r, g, b = pixel
    return f"\033[48;2;{r};{g};{b}m "

def play_video_art(video_path: Path, width: int = 80, height: int = 40, fps: int = 10, brightness: float = 1.0, color_mode: str = "text"):
    """Play a video as ASCII art in the terminal."""
    if not video_path.is_file():
        logger.error(f"Video file not found: {video_path}")
        return

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        logger.error(f"Could not open video file: {video_path}")
        return

    try:
        audio = AudioSegment.from_file(str(video_path))
        play(audio)
    except Exception as e:
        logger.warning(f"Could not play audio: {e}")

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            resized_frame = cv2.resize(frame, (width, height))

            if color_mode == "ansi":
                ascii_frame = ""
                for row in resized_frame:
                    ascii_frame += "".join([_pixel_to_ansi(pixel) for pixel in row])
                    ascii_frame += "\n"
            else:
                gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
                ascii_frame = ""
                for row in gray_frame:
                    ascii_frame += "".join([ASCII_CHARS[max(0, min(len(ASCII_CHARS) - 1, int(pixel * brightness * len(ASCII_CHARS) / 256)))] for pixel in row])
                    ascii_frame += "\n"

            sys.stdout.write("\033[2J")
            sys.stdout.write("\033[H")
            sys.stdout.write(ascii_frame)
            sys.stdout.flush()

            time.sleep(1 / fps)

    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()


def convert_video_to_ascii_video(video_path: Path, output_path: Path, width: int = 80, height: int = 40, fps: int = 10, brightness: float = 1.0, color_mode: str = "text"):
    """Convert a video to an ASCII art video file."""
    if not video_path.is_file():
        logger.error(f"Video file not found: {video_path}")
        return

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        logger.error(f"Could not open video file: {video_path}")
        return

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    if color_mode == "ansi":
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    else:
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height), isColor=False)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            resized_frame = cv2.resize(frame, (width, height))

            if color_mode == "ansi":
                out.write(resized_frame)
            else:
                gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
                ascii_frame_data = np.zeros((height, width), np.uint8)
                for i, row in enumerate(gray_frame):
                    for j, pixel in enumerate(row):
                        ascii_frame_data[i, j] = ord(ASCII_CHARS[max(0, min(len(ASCII_CHARS) - 1, int(pixel * brightness * len(ASCII_CHARS) / 256)))])
                out.write(cv2.cvtColor(ascii_frame_data, cv2.COLOR_GRAY2BGR))

    finally:
        cap.release()
        out.release()
