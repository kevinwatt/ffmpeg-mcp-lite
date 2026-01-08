# 🎬 ffmpeg-mcp

<div align="center">

**A powerful MCP server for video and audio processing through FFmpeg**

[![PyPI version](https://img.shields.io/pypi/v/ffmpeg-mcp-lite.svg)](https://pypi.org/project/ffmpeg-mcp-lite/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-%3E%3D3.10-blue)](https://www.python.org/)

Integrate FFmpeg with Claude, Dive, and other MCP-compatible AI systems. Convert, compress, trim videos, extract audio, and more — all through natural language.

[Features](#-features) • [Installation](#-installation) • [Tools](#-available-tools) • [Usage](#-usage-examples) • [Configuration](#-configuration)

</div>

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 📊 **Media Information**
- Get comprehensive metadata
- Duration, resolution, codecs
- Bitrate and stream details
- JSON formatted output

### 🔄 **Format Conversion**
- Convert between any formats
- MP4, MKV, WebM, MOV, etc.
- Custom video/audio codecs
- Resolution scaling

### 🗜️ **Video Compression**
- Quality presets (low/medium/high)
- Encoding speed control
- H.264 optimization
- Size reduction stats

### ✂️ **Video Trimming**
- Precise start/end times
- Duration-based cuts
- Stream copy (fast)
- No re-encoding needed

</td>
<td width="50%">

### 🎵 **Audio Extraction**
- Multiple formats supported
- MP3, AAC, WAV, FLAC, OGG, Opus
- Bitrate control
- High quality output

### 🎞️ **Advanced Features**
- Merge multiple videos
- Extract frames as images
- Interval or count-based extraction
- JPG, PNG, BMP output

### 📝 **Subtitles**
- Burn-in SRT/ASS/VTT subtitles
- Multiple styles available
- Customizable font size
- Works great with Whisper MCP

</td>
</tr>
</table>

---

## 🚀 Installation

### Prerequisites

**Install FFmpeg** on your system:

<table>
<tr>
<th>Platform</th>
<th>Command</th>
</tr>
<tr>
<td>🪟 <strong>Windows</strong></td>
<td><code>winget install FFmpeg</code></td>
</tr>
<tr>
<td>🍎 <strong>macOS</strong></td>
<td><code>brew install ffmpeg</code></td>
</tr>
<tr>
<td>🐧 <strong>Linux</strong></td>
<td><code>sudo apt install ffmpeg</code></td>
</tr>
</table>

### Getting Started

Add the following config to your MCP client:

```json
{
  "mcpServers": {
    "ffmpeg": {
      "command": "uvx",
      "args": ["ffmpeg-mcp-lite"]
    }
  }
}
```

### MCP Client Configuration

<details open>
<summary><strong>Dive</strong></summary>

1. Open [Dive Desktop](https://github.com/OpenAgentPlatform/Dive)
2. Click **"+ Add MCP Server"**
3. Paste the config provided above
4. Click **"Save"** and you're ready!

</details>

<details>
<summary><strong>Claude Code</strong></summary>

Use the Claude Code CLI to add the ffmpeg MCP server:

```bash
claude mcp add ffmpeg uvx ffmpeg-mcp-lite
```

</details>

<details>
<summary><strong>Claude Desktop</strong></summary>

Add to your `claude_desktop_config.json`:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ffmpeg": {
      "command": "uvx",
      "args": ["ffmpeg-mcp-lite"]
    }
  }
}
```

</details>

<details>
<summary><strong>Cursor</strong></summary>

Go to `Cursor Settings` -> `MCP` -> `New MCP Server`. Use the config provided above.

</details>

<details>
<summary><strong>VS Code / Copilot</strong></summary>

Install via the VS Code CLI:

```bash
code --add-mcp '{"name":"ffmpeg","command":"uvx","args":["ffmpeg-mcp-lite"]}'
```

</details>

<details>
<summary><strong>Windsurf</strong></summary>

Follow the [configure MCP guide](https://docs.windsurf.com/windsurf/cascade/mcp#mcp-config-json) using the standard config from above.

</details>

### Manual Installation

```bash
pip install ffmpeg-mcp-lite
```

Or with uv:

```bash
uv pip install ffmpeg-mcp-lite
```

---

## 🛠️ Available Tools

All tools are prefixed with `ffmpeg_` to avoid naming conflicts with other MCP servers.

### 📊 Media Information

<table>
<tr>
<th width="30%">Tool</th>
<th width="70%">Description</th>
</tr>
<tr>
<td><code>ffmpeg_get_info</code></td>
<td>

Get comprehensive video/audio metadata
- **Parameters**: `file_path`
- **Returns**: JSON with duration, resolution, codecs, bitrate, streams

</td>
</tr>
</table>

### 🔄 Conversion & Compression

<table>
<tr>
<th width="30%">Tool</th>
<th width="70%">Description</th>
</tr>
<tr>
<td><code>ffmpeg_convert</code></td>
<td>

Convert video/audio to different formats
- **Parameters**: `file_path`, `output_format`, `scale`, `video_codec`, `audio_codec`
- **Formats**: mp4, mkv, webm, mov, mp3, wav, etc.

</td>
</tr>
<tr>
<td><code>ffmpeg_compress</code></td>
<td>

Compress video to reduce file size
- **Parameters**: `file_path`, `quality`, `scale`, `preset`
- **Quality**: low, medium, high
- **Preset**: ultrafast to veryslow

</td>
</tr>
</table>

### ✂️ Editing

<table>
<tr>
<th width="30%">Tool</th>
<th width="70%">Description</th>
</tr>
<tr>
<td><code>ffmpeg_trim</code></td>
<td>

Trim video to extract a segment
- **Parameters**: `file_path`, `start_time`, `end_time` or `duration`
- **Time format**: "00:01:30" or seconds

</td>
</tr>
<tr>
<td><code>ffmpeg_merge</code></td>
<td>

Concatenate multiple videos into one
- **Parameters**: `file_paths` (list), `output_path`
- **Supports**: Same codec videos

</td>
</tr>
</table>

### 🎵 Audio & Frames

<table>
<tr>
<th width="30%">Tool</th>
<th width="70%">Description</th>
</tr>
<tr>
<td><code>ffmpeg_extract_audio</code></td>
<td>

Extract audio track from video
- **Parameters**: `file_path`, `audio_format`, `bitrate`
- **Formats**: mp3, aac, wav, flac, ogg, opus

</td>
</tr>
<tr>
<td><code>ffmpeg_extract_frames</code></td>
<td>

Extract frames as images
- **Parameters**: `file_path`, `interval` or `count`, `format`
- **Formats**: jpg, png, bmp

</td>
</tr>
</table>

### 📝 Subtitles

<table>
<tr>
<th width="30%">Tool</th>
<th width="70%">Description</th>
</tr>
<tr>
<td><code>ffmpeg_add_subtitles</code></td>
<td>

Burn-in subtitles to video (hardcode)
- **Parameters**: `file_path`, `subtitle_path`, `style`, `font_size`, `output_path`
- **Formats**: SRT, ASS, VTT
- **Styles**: outline, shadow, background, glow

</td>
</tr>
</table>

---

## 💡 Usage Examples

### Get Media Information

```
"Get info about /path/to/video.mp4"
"What's the resolution and duration of this video?"
"Show me the codec information for my video"
```

### Convert Videos

```
"Convert video.mp4 to WebM format"
"Convert this video to MKV with h265 codec"
"Convert and scale to 1280x720"
```

### Compress Videos

```
"Compress video.mp4 with medium quality"
"Compress this video to reduce file size, use fast preset"
"Compress with high quality and scale to 1920:-1"
```

### Trim Videos

```
"Trim video.mp4 from 00:01:00 to 00:02:30"
"Cut the first 30 seconds from this video"
"Extract a 1-minute clip starting at 5:00"
```

### Extract Audio

```
"Extract audio from video.mp4 as MP3"
"Get the audio track in AAC format with 192k bitrate"
"Extract audio as FLAC for best quality"
```

### Extract Frames

```
"Extract one frame every 5 seconds from video.mp4"
"Get 10 frames evenly distributed from this video"
"Extract frames as PNG images"
```

### Merge Videos

```
"Merge video1.mp4 and video2.mp4 together"
"Concatenate these three videos into one"
```

### Add Subtitles

```
"Add subtitles.srt to video.mp4"
"Burn in Chinese subtitles with shadow style"
"Add subtitles with font size 32 and glow effect"
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FFMPEG_PATH` | Path to ffmpeg binary | `ffmpeg` |
| `FFPROBE_PATH` | Path to ffprobe binary | `ffprobe` |
| `FFMPEG_OUTPUT_DIR` | Default output directory | `~/Downloads` |

### Custom Configuration

```json
{
  "mcpServers": {
    "ffmpeg": {
      "command": "uvx",
      "args": ["ffmpeg-mcp-lite"],
      "env": {
        "FFMPEG_OUTPUT_DIR": "/path/to/output"
      }
    }
  }
}
```

---

## 🏗️ Architecture

### Built With

- **[FFmpeg](https://ffmpeg.org/)** - Video/audio processing engine
- **[FastMCP](https://github.com/modelcontextprotocol/python-sdk)** - MCP Python framework
- **[asyncio](https://docs.python.org/3/library/asyncio.html)** - Async subprocess execution
- **Python 3.10+** - Type hints and modern features

### Key Features

- ✅ **Async Processing**: Non-blocking FFmpeg execution
- ✅ **Type Safe**: Full type hints with mypy validation
- ✅ **Well Tested**: 31 test cases with pytest
- ✅ **Cross Platform**: Works on Windows, macOS, Linux
- ✅ **Modular Design**: One file per tool

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development

```bash
# Clone and install
git clone https://github.com/kevinwatt/ffmpeg-mcp-lite.git
cd ffmpeg-mcp-lite
uv sync

# Run tests
uv run pytest

# Type checking
uv run mypy src/

# Linting
uv run ruff check src/
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [FFmpeg](https://ffmpeg.org/) - The powerful multimedia framework
- [Anthropic](https://www.anthropic.com/) - For the Model Context Protocol
- [Dive](https://github.com/OpenAgentPlatform/Dive) - MCP-compatible AI platform

---

<div align="center">

[⬆ Back to Top](#-ffmpeg-mcp)

</div>
