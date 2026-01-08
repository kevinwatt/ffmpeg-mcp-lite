"""Extract frames from video files."""

import asyncio
from pathlib import Path
from typing import Optional, Literal

from ..config import config


async def ffmpeg_extract_frames(
    file_path: str,
    interval: Optional[float] = None,
    count: Optional[int] = None,
    format: Literal["jpg", "png", "bmp"] = "jpg",
) -> str:
    """Extract frames from a video as images.

    Args:
        file_path: Path to the input video file
        interval: Extract one frame every N seconds (e.g., 1.0 for one frame per second)
        count: Total number of frames to extract (evenly distributed). Mutually exclusive with interval.
        format: Output image format (jpg, png, bmp)

    Returns:
        Path to the directory containing extracted frames
    """
    if interval and count:
        raise ValueError("Cannot specify both interval and count. Use one or the other.")
    if not interval and not count:
        raise ValueError("Must specify either interval or count.")

    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not path.is_file():
        raise ValueError(f"Not a file: {file_path}")

    # Create output directory for frames
    output_dir = config.ensure_output_dir() / f"{path.stem}_frames"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_pattern = output_dir / f"frame_%04d.{format}"

    cmd = [
        config.ffmpeg_path,
        "-i", str(path),
        "-y",  # Overwrite output
    ]

    if interval:
        # Extract frame every N seconds
        cmd.extend(["-vf", f"fps=1/{interval}"])
    elif count:
        # Get video duration first to calculate interval
        probe_cmd = [
            config.ffprobe_path,
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ]
        probe_proc = await asyncio.create_subprocess_exec(
            *probe_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await probe_proc.communicate()

        if probe_proc.returncode != 0:
            raise RuntimeError(f"ffprobe failed: {stderr.decode()}")

        duration = float(stdout.decode().strip())
        # Calculate fps to get exactly 'count' frames
        fps = count / duration
        cmd.extend(["-vf", f"fps={fps}"])

    cmd.append(str(output_pattern))

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg extract frames failed: {stderr.decode()}")

    # Count extracted frames
    frame_count = len(list(output_dir.glob(f"*.{format}")))

    return f"Extracted {frame_count} frames to: {output_dir}"
