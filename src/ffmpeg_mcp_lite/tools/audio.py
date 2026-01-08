"""Extract audio from video files."""

import asyncio
from pathlib import Path
from typing import Optional, Literal

from ..config import config


async def ffmpeg_extract_audio(
    file_path: str,
    audio_format: Literal["mp3", "aac", "wav", "flac", "ogg", "opus"] = "mp3",
    bitrate: Optional[str] = None,
) -> str:
    """Extract audio track from a video file.

    Args:
        file_path: Path to the input video file
        audio_format: Output audio format (mp3, aac, wav, flac, ogg, opus)
        bitrate: Audio bitrate (e.g., "128k", "192k", "320k"). If not specified, uses format default.

    Returns:
        Path to the extracted audio file
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not path.is_file():
        raise ValueError(f"Not a file: {file_path}")

    output_dir = config.ensure_output_dir()
    output_path = output_dir / f"{path.stem}.{audio_format}"

    # Codec mapping
    codec_map = {
        "mp3": "libmp3lame",
        "aac": "aac",
        "wav": "pcm_s16le",
        "flac": "flac",
        "ogg": "libvorbis",
        "opus": "libopus",
    }

    cmd = [
        config.ffmpeg_path,
        "-i", str(path),
        "-vn",  # No video
        "-y",   # Overwrite output
        "-c:a", codec_map[audio_format],
    ]

    if bitrate:
        cmd.extend(["-b:a", bitrate])

    cmd.append(str(output_path))

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg extract audio failed: {stderr.decode()}")

    return f"Audio extracted successfully: {output_path}"
