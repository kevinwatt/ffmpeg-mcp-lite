"""MCP server initialization and tool registration."""

from mcp.server.fastmcp import FastMCP

from .tools.info import ffmpeg_get_info
from .tools.convert import ffmpeg_convert
from .tools.compress import ffmpeg_compress
from .tools.trim import ffmpeg_trim
from .tools.audio import ffmpeg_extract_audio
from .tools.merge import ffmpeg_merge
from .tools.frames import ffmpeg_extract_frames
from .tools.subtitles import ffmpeg_add_subtitles

mcp = FastMCP("ffmpeg-mcp")

# Register all tools
mcp.tool()(ffmpeg_get_info)
mcp.tool()(ffmpeg_convert)
mcp.tool()(ffmpeg_compress)
mcp.tool()(ffmpeg_trim)
mcp.tool()(ffmpeg_extract_audio)
mcp.tool()(ffmpeg_merge)
mcp.tool()(ffmpeg_extract_frames)
mcp.tool()(ffmpeg_add_subtitles)


def main() -> None:
    """Run the MCP server."""
    mcp.run()
