"""
Tool definitions for Fal.ai MCP Server.

This module contains all MCP tool schemas organized by category.
"""

from fal_mcp_server.tools.audio_tools import AUDIO_TOOLS
from fal_mcp_server.tools.image_editing_tools import IMAGE_EDITING_TOOLS
from fal_mcp_server.tools.image_tools import IMAGE_TOOLS
from fal_mcp_server.tools.utility_tools import UTILITY_TOOLS
from fal_mcp_server.tools.video_tools import VIDEO_TOOLS

# All tools combined for easy registration
ALL_TOOLS = (
    UTILITY_TOOLS + IMAGE_TOOLS + IMAGE_EDITING_TOOLS + VIDEO_TOOLS + AUDIO_TOOLS
)

__all__ = [
    "ALL_TOOLS",
    "UTILITY_TOOLS",
    "IMAGE_TOOLS",
    "IMAGE_EDITING_TOOLS",
    "VIDEO_TOOLS",
    "AUDIO_TOOLS",
]
