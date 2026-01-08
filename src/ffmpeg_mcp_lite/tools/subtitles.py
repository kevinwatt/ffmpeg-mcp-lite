"""Add subtitles to video files."""

import asyncio
from pathlib import Path
from typing import Optional, Literal

from ..config import config


def get_subtitle_style(font_size: int, style_type: str) -> str:
    """Get ASS subtitle style string.

    Args:
        font_size: Font size
        style_type: Style type (outline, shadow, background, glow)

    Returns:
        ASS subtitle style string
    """
    base_style = (
        f"FontSize={font_size},"
        "FontName=Arial,"
        "PrimaryColour=&H00FFFFFF,"
        "Bold=0,"
        "Italic=0,"
        "Alignment=2,"
        "MarginV=30"
    )

    styles = {
        "outline": ",Outline=2,OutlineColour=&H00000000,BorderStyle=1,Shadow=1,ShadowColour=&H80000000",
        "shadow": ",Outline=1,OutlineColour=&H00000000,BorderStyle=1,Shadow=3,ShadowColour=&H80000000",
        "background": ",BorderStyle=3,BackColour=&H80000000,Outline=0,Shadow=0",
        "glow": ",Outline=3,OutlineColour=&H40000000,BorderStyle=1,Shadow=0",
    }

    return base_style + styles.get(style_type, styles["outline"])


async def ffmpeg_add_subtitles(
    file_path: str,
    subtitle_path: str,
    style: Literal["outline", "shadow", "background", "glow"] = "outline",
    font_size: int = 24,
    output_path: Optional[str] = None,
) -> str:
    """Add subtitles to a video file (burn-in/hardcode).

    Args:
        file_path: Path to the input video file
        subtitle_path: Path to the subtitle file (SRT, ASS, VTT)
        style: Subtitle style - "outline" (default), "shadow", "background", or "glow"
        font_size: Font size for subtitles (default: 24)
        output_path: Optional output file path. If not specified, saves to default output directory.

    Returns:
        Path to the output video with subtitles
    """
    video_path = Path(file_path).expanduser().resolve()
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {file_path}")
    if not video_path.is_file():
        raise ValueError(f"Not a file: {file_path}")

    sub_path = Path(subtitle_path).expanduser().resolve()
    if not sub_path.exists():
        raise FileNotFoundError(f"Subtitle file not found: {subtitle_path}")
    if not sub_path.is_file():
        raise ValueError(f"Not a file: {subtitle_path}")

    # Determine output path
    if output_path:
        out_path = Path(output_path).expanduser().resolve()
    else:
        output_dir = config.ensure_output_dir()
        out_path = output_dir / f"{video_path.stem}_subtitled{video_path.suffix}"

    # Get subtitle style
    subtitle_style = get_subtitle_style(font_size, style)

    # Escape paths for ffmpeg filter
    sub_path_escaped = str(sub_path).replace("'", "'\\''").replace(":", "\\:")
    subtitle_filter = f"subtitles='{sub_path_escaped}':force_style='{subtitle_style}'"

    cmd = [
        config.ffmpeg_path,
        "-i", str(video_path),
        "-vf", subtitle_filter,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-c:a", "copy",
        "-y",
        str(out_path),
    ]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg add subtitles failed: {stderr.decode()}")

    return f"Subtitles added successfully: {out_path}"
