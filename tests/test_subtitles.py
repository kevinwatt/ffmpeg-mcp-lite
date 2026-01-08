"""Tests for ffmpeg_add_subtitles tool."""

from pathlib import Path

import pytest

from ffmpeg_mcp_lite.tools.subtitles import ffmpeg_add_subtitles


@pytest.fixture
def sample_srt(temp_dir: Path) -> Path:
    """Create a sample SRT subtitle file."""
    srt_path = temp_dir / "sample.srt"
    srt_content = """1
00:00:00,000 --> 00:00:02,000
Hello World

2
00:00:02,000 --> 00:00:04,000
This is a test subtitle
"""
    srt_path.write_text(srt_content)
    return srt_path


@pytest.mark.asyncio
async def test_add_subtitles_basic(sample_video: Path, sample_srt: Path, temp_dir: Path, monkeypatch):
    """Test adding subtitles to a video."""
    monkeypatch.setenv("FFMPEG_OUTPUT_DIR", str(temp_dir))
    from ffmpeg_mcp_lite import config
    config.config = config.Config()

    result = await ffmpeg_add_subtitles(str(sample_video), str(sample_srt))

    assert "Subtitles added successfully" in result
    assert "_subtitled" in result


@pytest.mark.asyncio
async def test_add_subtitles_with_style(sample_video: Path, sample_srt: Path, temp_dir: Path, monkeypatch):
    """Test adding subtitles with different styles."""
    monkeypatch.setenv("FFMPEG_OUTPUT_DIR", str(temp_dir))
    from ffmpeg_mcp_lite import config
    config.config = config.Config()

    result = await ffmpeg_add_subtitles(
        str(sample_video),
        str(sample_srt),
        style="shadow",
        font_size=32
    )

    assert "Subtitles added successfully" in result


@pytest.mark.asyncio
async def test_add_subtitles_custom_output(sample_video: Path, sample_srt: Path, temp_dir: Path):
    """Test adding subtitles with custom output path."""
    output_path = temp_dir / "custom_output.mp4"

    result = await ffmpeg_add_subtitles(
        str(sample_video),
        str(sample_srt),
        output_path=str(output_path)
    )

    assert "Subtitles added successfully" in result
    assert output_path.exists()


@pytest.mark.asyncio
async def test_add_subtitles_video_not_found():
    """Test error handling for non-existent video file."""
    with pytest.raises(FileNotFoundError):
        await ffmpeg_add_subtitles("/nonexistent/video.mp4", "/some/subtitle.srt")


@pytest.mark.asyncio
async def test_add_subtitles_subtitle_not_found(sample_video: Path):
    """Test error handling for non-existent subtitle file."""
    with pytest.raises(FileNotFoundError):
        await ffmpeg_add_subtitles(str(sample_video), "/nonexistent/subtitle.srt")
