"""Tests for ffmpeg_extract_frames tool."""

from pathlib import Path

import pytest

from ffmpeg_mcp_lite.tools.frames import ffmpeg_extract_frames


@pytest.fixture
def patched_output_dir(temp_dir: Path, monkeypatch) -> Path:
    """Redirect frames tool output to temp_dir.

    Patches the live config instance held by frames.py rather than reassigning
    config.config — the module imported the instance at load time, so reassignment
    would not affect it.
    """
    from ffmpeg_mcp_lite.tools import frames as frames_mod
    monkeypatch.setattr(frames_mod.config, "output_dir", temp_dir)
    return temp_dir


@pytest.mark.asyncio
async def test_extract_frames_by_interval(sample_video: Path, patched_output_dir: Path):
    """Test extracting frames at intervals."""
    result = await ffmpeg_extract_frames(str(sample_video), interval=1.0)

    assert "Extracted" in result
    assert "frames to:" in result
    output_dir = patched_output_dir / f"{sample_video.stem}_frames"
    assert any(output_dir.glob("*.jpg"))


@pytest.mark.asyncio
async def test_extract_frames_by_count(sample_video: Path, patched_output_dir: Path):
    """Test extracting specific number of frames."""
    result = await ffmpeg_extract_frames(str(sample_video), count=5)

    assert "Extracted" in result
    output_dir = patched_output_dir / f"{sample_video.stem}_frames"
    assert any(output_dir.glob("*.jpg"))


@pytest.mark.asyncio
async def test_extract_frames_png_format(sample_video: Path, patched_output_dir: Path):
    """Test extracting frames as PNG."""
    result = await ffmpeg_extract_frames(str(sample_video), interval=1.0, format="png")

    assert "Extracted" in result
    output_dir = patched_output_dir / f"{sample_video.stem}_frames"
    assert any(output_dir.glob("*.png"))


@pytest.mark.asyncio
async def test_extract_frames_webp_format(sample_video: Path, patched_output_dir: Path):
    """Test extracting frames as WebP."""
    result = await ffmpeg_extract_frames(str(sample_video), interval=1.0, format="webp")

    assert "Extracted" in result
    output_dir = patched_output_dir / f"{sample_video.stem}_frames"
    assert any(output_dir.glob("*.webp"))


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
