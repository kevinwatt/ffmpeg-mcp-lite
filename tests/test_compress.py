"""Tests for ffmpeg_compress tool."""

from pathlib import Path

import pytest

from ffmpeg_mcp_lite.tools.compress import ffmpeg_compress


@pytest.mark.asyncio
async def test_compress_medium_quality(sample_video: Path, temp_dir: Path, monkeypatch):
    """Test compressing video with medium quality."""
    monkeypatch.setenv("FFMPEG_OUTPUT_DIR", str(temp_dir))
    from ffmpeg_mcp_lite import config
    config.config = config.Config()

    result = await ffmpeg_compress(str(sample_video), quality="medium")

    assert "Compressed successfully" in result
    assert "_compressed.mp4" in result
    assert "Reduction:" in result


@pytest.mark.asyncio
async def test_compress_low_quality(sample_video: Path, temp_dir: Path, monkeypatch):
    """Test compressing video with low quality for smaller file."""
    monkeypatch.setenv("FFMPEG_OUTPUT_DIR", str(temp_dir))
    from ffmpeg_mcp_lite import config
    config.config = config.Config()

    result = await ffmpeg_compress(str(sample_video), quality="low", preset="fast")

    assert "Compressed successfully" in result


@pytest.mark.asyncio
async def test_compress_file_not_found():
    """Test error handling for non-existent file."""
    with pytest.raises(FileNotFoundError):
        await ffmpeg_compress("/nonexistent/file.mp4")
