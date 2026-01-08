# FFmpeg MCP Server Development Guide

## Overview

This skill guides the development of `ffmpeg-mcp-lite`, an MCP server that provides video and audio processing capabilities through FFmpeg.

**Repository**: https://github.com/kevinwatt/ffmpeg-mcp-lite
**PyPI**: https://pypi.org/project/ffmpeg-mcp-lite/

---

## Project Specifications

### Technology Stack
- **Language**: Python 3.10+
- **Framework**: FastMCP (from mcp package)
- **Package Manager**: uv
- **CLI Tool**: FFmpeg / FFprobe

### Tool Naming Convention
All tools use `ffmpeg_` prefix to avoid conflicts with other MCP servers.

---

## Implemented Tools

### Core Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `ffmpeg_get_info` | Get video/audio metadata | `file_path` |
| `ffmpeg_convert` | Convert format (with optional scale) | `file_path`, `output_format`, `scale?`, `video_codec?`, `audio_codec?` |
| `ffmpeg_compress` | Compress video (with optional scale) | `file_path`, `quality`, `scale?`, `preset?` |
| `ffmpeg_trim` | Trim video segment | `file_path`, `start_time`, `end_time?`, `duration?` |
| `ffmpeg_extract_audio` | Extract audio track | `file_path`, `audio_format`, `bitrate?` |
| `ffmpeg_merge` | Concatenate videos | `file_paths`, `output_path?` |
| `ffmpeg_extract_frames` | Extract frames as images | `file_path`, `interval?`, `count?`, `format?` |
| `ffmpeg_add_subtitles` | Burn-in subtitles to video | `file_path`, `subtitle_path`, `style?`, `font_size?`, `output_path?` |

---

## Project Structure

```
ffmpeg-mcp-lite/
├── src/ffmpeg_mcp/
│   ├── __init__.py
│   ├── __main__.py
│   ├── server.py          # MCP server core
│   ├── config.py          # Configuration
│   └── tools/
│       ├── __init__.py
│       ├── info.py        # ffmpeg_get_info
│       ├── convert.py     # ffmpeg_convert
│       ├── compress.py    # ffmpeg_compress
│       ├── trim.py        # ffmpeg_trim
│       ├── audio.py       # ffmpeg_extract_audio
│       ├── merge.py       # ffmpeg_merge
│       ├── frames.py      # ffmpeg_extract_frames
│       └── subtitles.py   # ffmpeg_add_subtitles
├── tests/
│   ├── conftest.py
│   ├── test_info.py
│   ├── test_convert.py
│   ├── test_compress.py
│   ├── test_trim.py
│   ├── test_audio.py
│   ├── test_merge.py
│   ├── test_frames.py
│   └── test_subtitles.py
├── pyproject.toml
├── README.md
├── CLAUDE.md
└── LICENSE
```

---

## Implementation Patterns

### FastMCP Tool Registration

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ffmpeg-mcp")

@mcp.tool()
async def ffmpeg_get_info(file_path: str) -> str:
    """Get video/audio file information.

    Args:
        file_path: Path to the media file

    Returns:
        JSON string with media metadata
    """
    # Implementation
    pass
```

### FFmpeg Async Execution

```python
import asyncio

async def run_ffmpeg(cmd: list[str]) -> tuple[bytes, bytes]:
    """Run FFmpeg command asynchronously."""
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {stderr.decode()}")
    return stdout, stderr
```

### File Validation Pattern

```python
from pathlib import Path

def validate_file(file_path: str) -> Path:
    """Validate file exists and is readable."""
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not path.is_file():
        raise ValueError(f"Not a file: {file_path}")
    return path
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FFMPEG_PATH` | Path to ffmpeg binary | `ffmpeg` |
| `FFPROBE_PATH` | Path to ffprobe binary | `ffprobe` |
| `FFMPEG_OUTPUT_DIR` | Default output directory | `~/Downloads` |

---

## Development Commands

```bash
# Install dependencies
uv sync

# Run the MCP server
uv run ffmpeg-mcp

# Run tests
uv run pytest

# Type checking
uv run mypy src/

# Linting
uv run ruff check src/
```

---

## Quality Checklist

- [x] All tools have clear docstrings with Args and Returns
- [x] Input validation for all parameters
- [x] Proper async/await for subprocess calls
- [x] Actionable error messages
- [x] File path expansion (~, relative paths)
- [x] Output file naming convention
- [x] 31 test cases passing
- [x] mypy type checking passing
- [x] Published to PyPI

---

## Reference

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [FFprobe Documentation](https://ffmpeg.org/ffprobe.html)
