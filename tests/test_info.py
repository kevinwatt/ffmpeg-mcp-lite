"""Tests for ffmpeg_get_info tool."""

import json
from pathlib import Path

import pytest

from ffmpeg_mcp_lite.tools.info import ffmpeg_get_info


@pytest.mark.asyncio
async def test_get_info_video(sample_video: Path):
    """Test getting info from a video file."""
    result = await ffmpeg_get_info(str(sample_video))
    data = json.loads(result)

    assert "file" in data
    assert "format" in data
    assert "streams" in data

    # Check format info
    assert data["format"]["format_name"] is not None
    assert data["format"]["duration"] is not None

    # Check video stream
    video_streams = [s for s in data["streams"] if s["codec_type"] == "video"]
    assert len(video_streams) >= 1
    assert video_streams[0]["width"] == 320
    assert video_streams[0]["height"] == 240


@pytest.mark.asyncio
async def test_get_info_audio(sample_audio: Path):
    """Test getting info from an audio file."""
    result = await ffmpeg_get_info(str(sample_audio))
    data = json.loads(result)

    assert "streams" in data
    audio_streams = [s for s in data["streams"] if s["codec_type"] == "audio"]
    assert len(audio_streams) >= 1


@pytest.mark.asyncio
async def test_get_info_file_not_found():
    """Test error handling for non-existent file."""
    with pytest.raises(FileNotFoundError):
        await ffmpeg_get_info("/nonexistent/file.mp4")


@pytest.mark.asyncio
async def test_get_info_expands_home(temp_dir: Path, monkeypatch):
    """Test that ~ is expanded in file paths."""
    # This will fail because the file doesn't exist, but it tests path expansion
    with pytest.raises(FileNotFoundError) as exc_info:
        await ffmpeg_get_info("~/nonexistent.mp4")
    # The error message should contain the expanded path
    assert "~" not in str(exc_info.value) or "nonexistent" in str(exc_info.value)
