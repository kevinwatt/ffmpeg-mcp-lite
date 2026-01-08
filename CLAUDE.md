# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FFmpeg MCP Server (`ffmpeg-mcp-lite`) - An MCP (Model Context Protocol) server providing video and audio processing capabilities through FFmpeg.

- **Repository**: https://github.com/kevinwatt/ffmpeg-mcp-lite
- **PyPI**: https://pypi.org/project/ffmpeg-mcp-lite/

## Technology Stack

- **Language**: Python 3.10+
- **Framework**: FastMCP (from `mcp` package)
- **Package Manager**: uv
- **External Dependencies**: FFmpeg, FFprobe

## Development Commands

```bash
# Install dependencies
uv sync

# Run the MCP server
uv run ffmpeg-mcp-lite

# Run tests
uv run pytest

# Run a single test
uv run pytest tests/test_info.py -v

# Type checking
uv run mypy src/

# Linting
uv run ruff check src/
```

## Architecture

### Project Structure

```
src/ffmpeg_mcp_lite/
├── __init__.py      # Package entry, exports main()
├── __main__.py      # Module entry point
├── server.py        # MCP server initialization and tool registration
├── config.py        # Configuration management (env vars, defaults)
└── tools/           # One file per tool
    ├── info.py      # ffmpeg_get_info
    ├── convert.py   # ffmpeg_convert (with scale)
    ├── compress.py  # ffmpeg_compress (with scale)
    ├── trim.py      # ffmpeg_trim
    ├── audio.py     # ffmpeg_extract_audio
    ├── merge.py     # ffmpeg_merge
    ├── frames.py    # ffmpeg_extract_frames
    └── subtitles.py # ffmpeg_add_subtitles
```

### Available Tools (8 total)

| Tool | Description |
|------|-------------|
| `ffmpeg_get_info` | Get video/audio metadata |
| `ffmpeg_convert` | Convert format (with optional scale) |
| `ffmpeg_compress` | Compress video (with optional scale) |
| `ffmpeg_trim` | Trim video segment |
| `ffmpeg_extract_audio` | Extract audio track |
| `ffmpeg_merge` | Concatenate videos |
| `ffmpeg_extract_frames` | Extract frames as images |
| `ffmpeg_add_subtitles` | Burn-in subtitles to video |

### Tool Naming Convention

All tools use `ffmpeg_` prefix to avoid conflicts with other MCP servers.

### FFmpeg Execution Pattern

Use `asyncio.create_subprocess_exec` for all FFmpeg/FFprobe calls. See `.claude/skills/mcp-builder/SKILL.md` for code patterns.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FFMPEG_PATH` | Path to ffmpeg binary | `ffmpeg` |
| `FFPROBE_PATH` | Path to ffprobe binary | `ffprobe` |
| `FFMPEG_OUTPUT_DIR` | Default output directory | `~/Downloads` |

## Version Management

Update version in two places:
1. `pyproject.toml` - `version` field
2. `src/ffmpeg_mcp_lite/__init__.py` - `__version__` variable
