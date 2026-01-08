"""Configuration management for FFmpeg MCP Server."""

import os
from pathlib import Path


class Config:
    """Configuration settings loaded from environment variables."""

    def __init__(self) -> None:
        self.ffmpeg_path = os.environ.get("FFMPEG_PATH", "ffmpeg")
        self.ffprobe_path = os.environ.get("FFPROBE_PATH", "ffprobe")
        self.output_dir = Path(
            os.environ.get("FFMPEG_OUTPUT_DIR", "~/Downloads")
        ).expanduser()

    def ensure_output_dir(self) -> Path:
        """Ensure output directory exists and return it."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        return self.output_dir


config = Config()
