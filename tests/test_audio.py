"""Tests for ffmpeg_extract_audio tool."""

from pathlib import Path

import pytest

from ffmpeg_mcp_lite.tools.audio import ffmpeg_extract_audio


@pytest.mark.asyncio
async def test_extract_audio_mp3(sample_video: Path, temp_dir: Path, monkeypatch):
    """Test extracting audio as MP3."""
    monkeypatch.setenv("FFMPEG_OUTPUT_DIR", str(temp_dir))
    from ffmpeg_mcp_lite import config
    config.config = config.Config()

    result = await ffmpeg_extract_audio(str(sample_video), audio_format="mp3")

    assert "Audio extracted successfully" in result
    assert ".mp3" in result


@pytest.mark.asyncio
async def test_extract_audio_aac_with_bitrate(sample_video: Path, temp_dir: Path, monkeypatch):
    """Test extracting audio as AAC with specific bitrate."""
    monkeypatch.setenv("FFMPEG_OUTPUT_DIR", str(temp_dir))
    from ffmpeg_mcp_lite import config
    config.config = config.Config()

    result = await ffmpeg_extract_audio(str(sample_video), audio_format="aac", bitrate="192k")

    assert "Audio extracted successfully" in result
    assert ".aac" in result


@pytest.mark.asyncio
async def test_extract_audio_file_not_found():
    """Test error handling for non-existent file."""
    with pytest.raises(FileNotFoundError):
        await ffmpeg_extract_audio("/nonexistent/file.mp4")
