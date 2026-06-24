"""Tests for ffmpeg_analyze_audio tool."""

from pathlib import Path

import pytest

from ffmpeg_mcp_lite.tools.analyze_audio import ffmpeg_analyze_audio


@pytest.fixture
def patched_output_dir(temp_dir: Path, monkeypatch) -> Path:
    """Redirect the tool's default output dir to temp_dir.

    Patches the live config instance held by analyze_audio.py rather than
    reassigning config.config — the module imported the instance at load
    time, so reassignment would not affect it.
    """
    from ffmpeg_mcp_lite.tools import analyze_audio as analyze_audio_mod
    monkeypatch.setattr(analyze_audio_mod.config, "output_dir", temp_dir)
    return temp_dir


@pytest.mark.asyncio
async def test_analyze_audio_default_output_dir(sample_audio: Path, patched_output_dir: Path):
    """Test analyzing audio with the default output location."""
    result = await ffmpeg_analyze_audio(str(sample_audio))

    assert "Audio analysis" in result
    assert "Verdict" in result

    outdir = patched_output_dir / f"{sample_audio.stem}_analysis"
    assert (outdir / "summary.txt").exists()
    assert (outdir / "ebur128.log").exists()
    assert (outdir / "astats.log").exists()
    assert (outdir / "energy-envelope.csv").exists()
    assert (outdir / "spectrogram.png").exists()
    assert (outdir / "waveform.png").exists()


@pytest.mark.asyncio
async def test_analyze_audio_custom_output_dir(sample_audio: Path, temp_dir: Path):
    """Test analyzing audio with an explicit output_dir."""
    outdir = temp_dir / "custom_analysis"

    result = await ffmpeg_analyze_audio(str(sample_audio), output_dir=str(outdir))

    assert "Audio analysis" in result
    assert (outdir / "summary.txt").exists()


@pytest.mark.asyncio
async def test_analyze_audio_from_video(sample_video: Path, patched_output_dir: Path):
    """Test analyzing the audio track of a video file."""
    result = await ffmpeg_analyze_audio(str(sample_video))

    assert "Audio analysis" in result
    outdir = patched_output_dir / f"{sample_video.stem}_analysis"
    assert (outdir / "summary.txt").exists()


@pytest.mark.asyncio
async def test_analyze_audio_file_not_found():
    """Test error handling for non-existent file."""
    with pytest.raises(FileNotFoundError):
        await ffmpeg_analyze_audio("/nonexistent/file.mp3")
