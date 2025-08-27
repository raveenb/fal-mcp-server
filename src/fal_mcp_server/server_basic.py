#!/usr/bin/env python3
"""Fal.ai MCP Server for media generation"""

import asyncio
import json
import os
import sys
from typing import Optional, Dict, Any, List
from pathlib import Path

# MCP imports
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent, ImageContent
import mcp.server.stdio

# Fal client
import fal_client

# Configure Fal client  
if api_key := os.getenv("FAL_KEY"):
    os.environ["FAL_KEY"] = api_key

# Initialize the MCP server
server = Server("fal-ai-mcp")

# Model configurations
MODELS = {
    "image": {
        "flux_schnell": "fal-ai/flux/schnell",
        "flux_dev": "fal-ai/flux/dev",
        "flux_pro": "fal-ai/flux-pro",
        "sdxl": "fal-ai/fast-sdxl",
        "stable_diffusion": "fal-ai/stable-diffusion-v3-medium",
    },
    "video": {
        "svd": "fal-ai/stable-video-diffusion",
        "animatediff": "fal-ai/fast-animatediff",
        "kling": "fal-ai/kling-video",
    },
    "audio": {
        "musicgen": "fal-ai/musicgen-medium",
        "musicgen_large": "fal-ai/musicgen-large",
        "bark": "fal-ai/bark",
        "whisper": "fal-ai/whisper",
    },
}

async def run():
    """Run the MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="fal-ai-mcp",
                server_version="1.0.0"
            )
        )

def main():
    """Main entry point"""
    asyncio.run(run())

if __name__ == "__main__":
    main()
