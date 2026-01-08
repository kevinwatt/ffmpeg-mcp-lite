"""Compress video files."""

import asyncio
from pathlib import Path
from typing import Optional, Literal

from ..config import config


async def ffmpeg_compress(
    file_path: str,
    quality: Literal["low", "medium", "high"] = "medium",
    scale: Optional[str] = None,
    preset: Literal["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"] = "medium",
) -> str:
    """Compress a video file to reduce file size.

    Args:
        file_path: Path to the input video file
        quality: Compression quality level - "low" (smallest file), "medium", or "high" (best quality)
        scale: Optional resolution scale (e.g., "1280:720", "1920:-1" for auto height)
        preset: Encoding speed preset - faster presets = larger files, slower = smaller files

    Returns:
        Path to the compressed file
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not path.is_file():
        raise ValueError(f"Not a file: {file_path}")

    # CRF values: lower = better quality, higher = smaller file
    crf_map = {
        "low": 28,      # Smaller file, lower quality
        "medium": 23,   # Balanced
        "high": 18,     # Larger file, higher quality
    }
    crf = crf_map[quality]

    output_dir = config.ensure_output_dir()
    output_path = output_dir / f"{path.stem}_compressed.mp4"

    cmd = [
        config.ffmpeg_path,
        "-i", str(path),
        "-y",  # Overwrite output
        "-c:v", "libx264",
        "-crf", str(crf),
        "-preset", preset,
        "-c:a", "aac",
        "-b:a", "128k",
    ]

    # Add scale filter if specified
    if scale:
        cmd.extend(["-vf", f"scale={scale}"])

    cmd.append(str(output_path))

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg compress failed: {stderr.decode()}")

    # Get file sizes for comparison
    original_size = path.stat().st_size
    compressed_size = output_path.stat().st_size
    reduction = (1 - compressed_size / original_size) * 100

    return (
        f"Compressed successfully: {output_path}\n"
        f"Original: {original_size / 1024 / 1024:.2f} MB\n"
        f"Compressed: {compressed_size / 1024 / 1024:.2f} MB\n"
        f"Reduction: {reduction:.1f}%"
    )
