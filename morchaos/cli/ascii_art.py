"""CLI for ASCII art generation."""

import click
from pathlib import Path

from ..core.ascii_art import (
    generate_text_art,
    get_available_fonts,
    generate_image_art,
    play_video_art,
    convert_video_to_ascii_video,
)
from ..logger import init_logging

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS, epilog="""
Usage Examples:
  ascii-art text "Hello" --font slant
  ascii-art image /path/to/image.jpg --width 100 --brightness 1.2
  ascii-art play /path/to/video.mp4 --width 120
  ascii-art video /path/to/video.mp4 /path/to/output.mp4 --width 120
""")
def cli():
    """A comprehensive toolkit for creating and displaying ASCII art from text, images, and videos."""
    init_logging()


@cli.command()
@click.argument("text", required=False)
@click.option("--font", default="banner3-D", help="Font to use for the text.")
@click.option("--width", default=80, help="The maximum width of the output.")
@click.option("--justify", default="left", type=click.Choice(["left", "center", "right"]),
help="Justification of the text.")
@click.option("--preview-fonts", is_flag=True, help="Preview all available fonts with a sample text.")
def text(text, font, width, justify, preview_fonts):
    """
    Generate ASCII art from text or preview available fonts.
    """
    if preview_fonts:
        sample_text = text if text else "Hello"
        available_fonts = get_available_fonts()
        for font_name in available_fonts:
            click.echo(f"\n--- Font: {font_name} ---")
            art = generate_text_art(sample_text, font=font_name, width=width, justify=justify)
            if art:
                click.echo(art)
        return

    if not text:
        click.echo("Error: TEXT is required unless --preview-fonts is used.", err=True)
        return

    art = generate_text_art(text, font, width, justify)
    if art:
        click.echo(art)


@cli.command()
@click.argument("image_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--width", default=80, help="The width of the generated ASCII art.")
@click.option("--height", default=None, type=int, help="The height of the generated ASCII art. If not provided, it is calculated automatically.")
@click.option("--brightness", default=1.0, type=float, help="Brightness adjustment factor (e.g., 0.5 for darker, 1.5 for brighter).")
@click.option("--color-mode", default="text", type=click.Choice(["text", "ansi"]), help="Color mode for the output.")
def image(image_path, width, height, brightness, color_mode):
    """
    Convert an image to ASCII art.
    """
    art = generate_image_art(image_path, width, height, brightness=brightness, color_mode=color_mode)
    if art:
        click.echo(art)


@cli.command()
@click.argument("video_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--width", default=80, help="The width of the output video frames.")
@click.option("--height", default=40, help="The height of the output video frames.")
@click.option("--fps", default=10, help="Frames per second for the output video.")
@click.option("--brightness", default=1.0, type=float, help="Brightness adjustment factor.")
@click.option("--color-mode", default="text", type=click.Choice(["text", "ansi"]), help="Color mode for the output.")
@click.argument("output_path", type=click.Path(path_type=Path))
def video(video_path, output_path, width, height, fps, brightness, color_mode):
    """
    Convert a video file to an ASCII art video file.
    """
    convert_video_to_ascii_video(video_path, output_path, width, height, fps, brightness=brightness, color_mode=color_mode)


@cli.command()
@click.argument("video_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--width", default=80, help="The width of the ASCII animation in the terminal.")
@click.option("--height", default=40, help="The height of the ASCII animation in the terminal.")
@click.option("--fps", default=10, help="Frames per second for the animation.")
@click.option("--brightness", default=1.0, type=float, help="Brightness adjustment factor.")
@click.option("--color-mode", default="text", type=click.Choice(["text", "ansi"]), help="Color mode for the output.")
def play(video_path, width, height, fps, brightness, color_mode):
    """
    Play a video or GIF as an ASCII art animation in the terminal.
    """
    play_video_art(video_path, width, height, fps, brightness=brightness, color_mode=color_mode)


if __name__ == "__main__":
    cli()
