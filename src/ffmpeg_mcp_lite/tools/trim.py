"""Trim video segments."""

import asyncio
from pathlib import Path
from typing import Optional

from ..config import config


async def ffmpeg_trim(
    file_path: str,
    start_time: str,
    end_time: Optional[str] = None,
    duration: Optional[str] = None,
) -> str:
    """Trim a video to extract a specific segment.

    Args:
        file_path: Path to the input video file
        start_time: Start time (e.g., "00:01:30" or "90" for 90 seconds)
        end_time: End time (e.g., "00:02:00"). Mutually exclusive with duration.
        duration: Duration of the clip (e.g., "30" for 30 seconds). Mutually exclusive with end_time.

    Returns:
        Path to the trimmed file
    """
    if end_time and duration:
        raise ValueError("Cannot specify both end_time and duration. Use one or the other.")
    if not end_time and not duration:
        raise ValueError("Must specify either end_time or duration.")

    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not path.is_file():
        raise ValueError(f"Not a file: {file_path}")

    output_dir = config.ensure_output_dir()
    output_path = output_dir / f"{path.stem}_trimmed{path.suffix}"

    cmd = [
        config.ffmpeg_path,
        "-i", str(path),
        "-ss", start_time,
        "-y",  # Overwrite output
    ]

    if end_time:
        cmd.extend(["-to", end_time])
    elif duration:
        cmd.extend(["-t", duration])

    # Use copy codec for faster processing when possible
    cmd.extend(["-c", "copy"])
    cmd.append(str(output_path))

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg trim failed: {stderr.decode()}")

    return f"Trimmed successfully: {output_path}"
