"""Get video/audio file information."""

import asyncio
import json
from pathlib import Path
from typing import Any

from ..config import config


async def ffmpeg_get_info(file_path: str) -> str:
    """Get video/audio file metadata using ffprobe.

    Args:
        file_path: Path to the media file

    Returns:
        JSON string with media metadata including duration, resolution,
        codecs, bitrate, and stream information
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not path.is_file():
        raise ValueError(f"Not a file: {file_path}")

    cmd = [
        config.ffprobe_path,
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        str(path),
    ]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {stderr.decode()}")

    data = json.loads(stdout.decode())

    # Extract key information for a cleaner response
    streams: list[dict[str, Any]] = []
    result: dict[str, Any] = {
        "file": str(path),
        "format": {},
        "streams": streams,
    }

    if "format" in data:
        fmt = data["format"]
        result["format"] = {
            "format_name": fmt.get("format_name"),
            "duration": fmt.get("duration"),
            "size": fmt.get("size"),
            "bit_rate": fmt.get("bit_rate"),
        }

    for stream in data.get("streams", []):
        stream_info = {
            "index": stream.get("index"),
            "codec_type": stream.get("codec_type"),
            "codec_name": stream.get("codec_name"),
        }

        if stream.get("codec_type") == "video":
            stream_info.update({
                "width": stream.get("width"),
                "height": stream.get("height"),
                "fps": stream.get("r_frame_rate"),
                "pix_fmt": stream.get("pix_fmt"),
            })
        elif stream.get("codec_type") == "audio":
            stream_info.update({
                "sample_rate": stream.get("sample_rate"),
                "channels": stream.get("channels"),
                "bit_rate": stream.get("bit_rate"),
            })

        streams.append(stream_info)

    return json.dumps(result, indent=2)
