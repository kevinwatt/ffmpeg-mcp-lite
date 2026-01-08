"""Tests for ffmpeg_trim tool."""

from pathlib import Path

import pytest

from ffmpeg_mcp_lite.tools.trim import ffmpeg_trim


@pytest.mark.asyncio
async def test_trim_with_duration(sample_video: Path, temp_dir: Path, monkeypatch):
    """Test trimming video with duration."""
    monkeypatch.setenv("FFMPEG_OUTPUT_DIR", str(temp_dir))
    from ffmpeg_mcp_lite import config
    config.config = config.Config()

    result = await ffmpeg_trim(str(sample_video), start_time="0", duration="1")

    assert "Trimmed successfully" in result
    assert "_trimmed" in result


@pytest.mark.asyncio
async def test_trim_with_end_time(sample_video: Path, temp_dir: Path, monkeypatch):
    """Test trimming video with end time."""
    monkeypatch.setenv("FFMPEG_OUTPUT_DIR", str(temp_dir))
    from ffmpeg_mcp_lite import config
    config.config = config.Config()

    result = await ffmpeg_trim(str(sample_video), start_time="0", end_time="1")

    assert "Trimmed successfully" in result


@pytest.mark.asyncio
async def test_trim_mutual_exclusion():
    """Test that both end_time and duration cannot be specified."""
    with pytest.raises(ValueError, match="Cannot specify both"):
        await ffmpeg_trim("/some/file.mp4", start_time="0", end_time="1", duration="1")


@pytest.mark.asyncio
async def test_trim_requires_end_or_duration():
    """Test that either end_time or duration must be specified."""
    with pytest.raises(ValueError, match="Must specify either"):
        await ffmpeg_trim("/some/file.mp4", start_time="0")
