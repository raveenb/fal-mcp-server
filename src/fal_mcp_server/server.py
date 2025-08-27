#!/usr/bin/env python3
"""Fal.ai MCP Server for media generation"""

import asyncio
import os
from typing import Dict, Any, List

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent, ServerCapabilities
import mcp.server.stdio
import fal_client

# Configure Fal client  
if api_key := os.getenv("FAL_KEY"):
    os.environ["FAL_KEY"] = api_key

# Initialize the MCP server
server = Server("fal-ai-mcp")

@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="generate_image",
            description="Generate an image from text prompt",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Text description of the image to generate"
                    },
                    "model": {
                        "type": "string",
                        "enum": ["flux_schnell", "flux_dev", "sdxl"],
                        "default": "flux_schnell",
                        "description": "Model to use (flux_schnell, flux_dev, or sdxl)"
                    },
                    "num_images": {
                        "type": "integer",
                        "default": 1,
                        "minimum": 1,
                        "maximum": 4,
                        "description": "Number of images to generate"
                    }
                },
                "required": ["prompt"]
            }
        ),
        Tool(
            name="generate_video",
            description="Generate a video from an image",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_url": {
                        "type": "string",
                        "description": "URL of the image to animate into video"
                    },
                    "duration": {
                        "type": "integer",
                        "default": 4,
                        "description": "Video duration in seconds"
                    }
                },
                "required": ["image_url"]
            }
        ),
        Tool(
            name="generate_music",
            description="Generate music from text description",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Description of the music to generate"
                    },
                    "duration_seconds": {
                        "type": "integer",
                        "default": 30,
                        "minimum": 5,
                        "maximum": 300,
                        "description": "Duration in seconds"
                    }
                },
                "required": ["prompt"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    try:
        if name == "generate_image":
            model_map = {
                "flux_schnell": "fal-ai/flux/schnell",
                "flux_dev": "fal-ai/flux/dev",
                "sdxl": "fal-ai/fast-sdxl"
            }
            
            model_key = arguments.get("model", "flux_schnell")
            model_id = model_map.get(model_key, "fal-ai/flux/schnell")
            
            result = await asyncio.to_thread(
                fal_client.run,
                model_id,
                arguments={
                    "prompt": arguments["prompt"],
                    "num_images": arguments.get("num_images", 1)
                }
            )
            
            images = result.get("images", [])
            if images:
                urls = [img["url"] for img in images]
                response = f"🎨 Generated {len(urls)} image(s) with {model_key}:\n\n"
                for i, url in enumerate(urls, 1):
                    response += f"Image {i}: {url}\n"
                return [TextContent(type="text", text=response)]
            
        elif name == "generate_video":
            result = await asyncio.to_thread(
                fal_client.run,
                "fal-ai/stable-video-diffusion",
                arguments={
                    "image_url": arguments["image_url"],
                    "duration": arguments.get("duration", 4)
                }
            )
            
            video_url = result.get("video", {}).get("url")
            if video_url:
                return [TextContent(
                    type="text",
                    text=f"🎬 Generated video: {video_url}"
                )]
                
        elif name == "generate_music":
            result = await asyncio.to_thread(
                fal_client.run,
                "fal-ai/musicgen-medium",
                arguments={
                    "prompt": arguments["prompt"],
                    "duration_seconds": arguments.get("duration_seconds", 30)
                }
            )
            
            audio_url = result.get("audio", {}).get("url") or result.get("audio_url")
            if audio_url:
                return [TextContent(
                    type="text",
                    text=f"🎵 Generated music: {audio_url}"
                )]
        
        return [TextContent(type="text", text=f"Tool {name} completed but no output generated")]
        
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        if "FAL_KEY" not in os.environ:
            error_msg += "\n⚠️ FAL_KEY environment variable not set!"
        return [TextContent(type="text", text=error_msg)]

async def run():
    """Run the MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="fal-ai-mcp",
                server_version="1.0.0",
                capabilities=ServerCapabilities(
                    tools={}  # Enable tools capability
                )
            )
        )

def main():
    asyncio.run(run())

if __name__ == "__main__":
    main()
