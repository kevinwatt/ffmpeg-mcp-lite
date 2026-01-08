"""Merge/concatenate video files."""

import asyncio
import tempfile
from pathlib import Path
from typing import Optional

from ..config import config


async def ffmpeg_merge(
    file_paths: list[str],
    output_path: Optional[str] = None,
) -> str:
    """Concatenate multiple video files into one.

    Args:
        file_paths: List of paths to video files to merge (in order)
        output_path: Optional output file path. If not specified, saves to default output directory.

    Returns:
        Path to the merged file
    """
    if len(file_paths) < 2:
        raise ValueError("Need at least 2 files to merge")

    # Validate all input files
    paths = []
    for fp in file_paths:
        path = Path(fp).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"File not found: {fp}")
        if not path.is_file():
            raise ValueError(f"Not a file: {fp}")
        paths.append(path)

    # Determine output path
    if output_path:
        out_path = Path(output_path).expanduser().resolve()
    else:
        output_dir = config.ensure_output_dir()
        out_path = output_dir / f"{paths[0].stem}_merged{paths[0].suffix}"

    # Create concat file list
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for path in paths:
            # Escape single quotes in path
            escaped_path = str(path).replace("'", "'\\''")
            f.write(f"file '{escaped_path}'\n")
        concat_file = f.name

    try:
        cmd = [
            config.ffmpeg_path,
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c", "copy",
            "-y",  # Overwrite output
            str(out_path),
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            raise RuntimeError(f"ffmpeg merge failed: {stderr.decode()}")

        return f"Merged {len(paths)} files successfully: {out_path}"
    finally:
        # Clean up temp file
        Path(concat_file).unlink(missing_ok=True)
