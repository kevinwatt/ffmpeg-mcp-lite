"""Tests for ffmpeg_convert tool."""

from pathlib import Path

import pytest

from ffmpeg_mcp_lite.tools.convert import ffmpeg_convert


@pytest.mark.asyncio
async def test_convert_to_mkv(sample_video: Path, temp_dir: Path, monkeypatch):
    """Test converting video to MKV format."""
    monkeypatch.setenv("FFMPEG_OUTPUT_DIR", str(temp_dir))
    # Reload config to pick up env var
    from ffmpeg_mcp_lite import config
    config.config = config.Config()

    result = await ffmpeg_convert(str(sample_video), "mkv")

    assert "Converted successfully" in result
    assert "_converted.mkv" in result
    output_path = Path(result.split(": ")[1])
    assert output_path.exists()


@pytest.mark.asyncio
async def test_convert_with_scale(sample_video: Path, temp_dir: Path, monkeypatch):
    """Test converting video with scale option."""
    monkeypatch.setenv("FFMPEG_OUTPUT_DIR", str(temp_dir))
    from ffmpeg_mcp_lite import config
    config.config = config.Config()

    result = await ffmpeg_convert(str(sample_video), "mp4", scale="160:120")

    assert "Converted successfully" in result


@pytest.mark.asyncio
async def test_convert_file_not_found():
    """Test error handling for non-existent file."""
    with pytest.raises(FileNotFoundError):
        await ffmpeg_convert("/nonexistent/file.mp4", "mkv")
