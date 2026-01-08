"""Tests for ffmpeg_merge tool."""

from pathlib import Path

import pytest

from ffmpeg_mcp_lite.tools.merge import ffmpeg_merge


@pytest.mark.asyncio
async def test_merge_videos(sample_video: Path, temp_dir: Path, monkeypatch):
    """Test merging two video files."""
    monkeypatch.setenv("FFMPEG_OUTPUT_DIR", str(temp_dir))
    from ffmpeg_mcp_lite import config
    config.config = config.Config()

    # Use the same video twice for testing
    result = await ffmpeg_merge([str(sample_video), str(sample_video)])

    assert "Merged 2 files successfully" in result
    assert "_merged" in result


@pytest.mark.asyncio
async def test_merge_custom_output(sample_video: Path, temp_dir: Path):
    """Test merging with custom output path."""
    output_path = temp_dir / "custom_merged.mp4"

    result = await ffmpeg_merge(
        [str(sample_video), str(sample_video)],
        output_path=str(output_path)
    )

    assert "Merged 2 files successfully" in result
    assert output_path.exists()


@pytest.mark.asyncio
async def test_merge_requires_two_files():
    """Test that at least 2 files are required."""
    with pytest.raises(ValueError, match="at least 2 files"):
        await ffmpeg_merge(["/some/file.mp4"])


@pytest.mark.asyncio
async def test_merge_file_not_found():
    """Test error handling for non-existent file."""
    with pytest.raises(FileNotFoundError):
        await ffmpeg_merge(["/nonexistent/file1.mp4", "/nonexistent/file2.mp4"])
