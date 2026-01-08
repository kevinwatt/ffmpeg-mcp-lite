"""Convert video/audio format."""

import asyncio
from pathlib import Path
from typing import Optional

from ..config import config


async def ffmpeg_convert(
    file_path: str,
    output_format: str,
    scale: Optional[str] = None,
    video_codec: Optional[str] = None,
    audio_codec: Optional[str] = None,
) -> str:
    """Convert video/audio to a different format.

    Args:
        file_path: Path to the input media file
        output_format: Target format (e.g., mp4, mkv, webm, mp3, wav)
        scale: Optional resolution scale (e.g., "1280:720", "1920:-1" for auto height)
        video_codec: Optional video codec (e.g., libx264, libx265, libvpx-vp9)
        audio_codec: Optional audio codec (e.g., aac, mp3, opus)

    Returns:
        Path to the converted file
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not path.is_file():
        raise ValueError(f"Not a file: {file_path}")

    output_dir = config.ensure_output_dir()
    output_path = output_dir / f"{path.stem}_converted.{output_format}"

    cmd = [
        config.ffmpeg_path,
        "-i", str(path),
        "-y",  # Overwrite output
    ]

    # Add video filters if scale is specified
    if scale:
        cmd.extend(["-vf", f"scale={scale}"])

    # Add codecs if specified
    if video_codec:
        cmd.extend(["-c:v", video_codec])
    if audio_codec:
        cmd.extend(["-c:a", audio_codec])

    cmd.append(str(output_path))

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg convert failed: {stderr.decode()}")

    return f"Converted successfully: {output_path}"
