"""Tests for ffmpeg_extract_frames tool."""

from pathlib import Path

import pytest

from ffmpeg_mcp_lite.tools.frames import ffmpeg_extract_frames


@pytest.mark.asyncio
async def test_extract_frames_by_interval(sample_video: Path, temp_dir: Path, monkeypatch):
    """Test extracting frames at intervals."""
    monkeypatch.setenv("FFMPEG_OUTPUT_DIR", str(temp_dir))
    from ffmpeg_mcp_lite import config
    config.config = config.Config()

    result = await ffmpeg_extract_frames(str(sample_video), interval=1.0)

    assert "Extracted" in result
    assert "frames to:" in result


@pytest.mark.asyncio
async def test_extract_frames_by_count(sample_video: Path, temp_dir: Path, monkeypatch):
    """Test extracting specific number of frames."""
    monkeypatch.setenv("FFMPEG_OUTPUT_DIR", str(temp_dir))
    from ffmpeg_mcp_lite import config
    config.config = config.Config()

    result = await ffmpeg_extract_frames(str(sample_video), count=5)

    assert "Extracted" in result


@pytest.mark.asyncio
async def test_extract_frames_png_format(sample_video: Path, temp_dir: Path, monkeypatch):
    """Test extracting frames as PNG."""
    monkeypatch.setenv("FFMPEG_OUTPUT_DIR", str(temp_dir))
    from ffmpeg_mcp_lite import config
    config.config = config.Config()

    result = await ffmpeg_extract_frames(str(sample_video), interval=1.0, format="png")

    assert "Extracted" in result


@pytest.mark.asyncio
async def test_extract_frames_mutual_exclusion():
    """Test that both interval and count cannot be specified."""
    with pytest.raises(ValueError, match="Cannot specify both"):
        await ffmpeg_extract_frames("/some/file.mp4", interval=1.0, count=5)


@pytest.mark.asyncio
async def test_extract_frames_requires_interval_or_count():
    """Test that either interval or count must be specified."""
    with pytest.raises(ValueError, match="Must specify either"):
        await ffmpeg_extract_frames("/some/file.mp4")
