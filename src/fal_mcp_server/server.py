#!/usr/bin/env python3
"""Fal.ai MCP Server with native async API and queue support"""

import asyncio
import os
import time
from typing import Any, Dict, List, Optional, cast

# Fal client
import fal_client
import mcp.server.stdio
from loguru import logger

# MCP imports
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import ServerCapabilities, TextContent, Tool, ToolsCapability

# Model registry for dynamic model discovery
from fal_mcp_server.model_registry import get_registry

# Configure Fal client
if api_key := os.getenv("FAL_KEY"):
    os.environ["FAL_KEY"] = api_key

# Initialize the MCP server
server = Server("fal-ai-mcp")


async def wait_for_queue_result(
    handle: Any, timeout: int = 300
) -> Optional[Dict[str, Any]]:
    """Wait for a queued job to complete with timeout"""
    start_time = time.time()

    while True:
        # Check timeout
        if time.time() - start_time > timeout:
            return {"error": f"Timeout after {timeout} seconds"}

        # Check status using the handle
        status = await handle.status()

        if hasattr(status, "status"):
            status_str = status.status
        else:
            status_str = str(status)

        if "completed" in status_str.lower():
            result = await handle.get()
            return cast(Dict[str, Any], result)
        elif "failed" in status_str.lower() or "error" in status_str.lower():
            return {"error": f"Job failed: {status}"}

        # Wait before polling again
        await asyncio.sleep(2)


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List all available Fal.ai tools"""
    return [
        Tool(
            name="list_models",
            description="Discover available Fal.ai models for image, video, and audio generation. Use this to find model IDs for generate_* tools.",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["image", "video", "audio"],
                        "description": "Filter by category (image, video, or audio)",
                    },
                    "search": {
                        "type": "string",
                        "description": "Search query to filter models by name or description (e.g., 'flux', 'stable diffusion')",
                    },
                    "limit": {
                        "type": "integer",
                        "default": 20,
                        "minimum": 1,
                        "maximum": 100,
                        "description": "Maximum number of models to return",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="generate_image",
            description="Generate images from text prompts. Use list_models with category='image' to discover available models.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Text description of the image to generate",
                    },
                    "model": {
                        "type": "string",
                        "default": "flux_schnell",
                        "description": "Model ID (e.g., 'fal-ai/flux-pro') or alias (e.g., 'flux_schnell'). Use list_models to see options.",
                    },
                    "negative_prompt": {
                        "type": "string",
                        "description": "What to avoid in the image",
                    },
                    "image_size": {
                        "type": "string",
                        "enum": [
                            "square",
                            "landscape_4_3",
                            "landscape_16_9",
                            "portrait_3_4",
                            "portrait_9_16",
                        ],
                        "default": "landscape_16_9",
                    },
                    "num_images": {
                        "type": "integer",
                        "default": 1,
                        "minimum": 1,
                        "maximum": 4,
                    },
                    "seed": {
                        "type": "integer",
                        "description": "Seed for reproducible generation",
                    },
                },
                "required": ["prompt"],
            },
        ),
        Tool(
            name="generate_video",
            description="Generate videos from images. Use list_models with category='video' to discover available models.",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_url": {
                        "type": "string",
                        "description": "Starting image URL (for image-to-video)",
                    },
                    "model": {
                        "type": "string",
                        "default": "svd",
                        "description": "Model ID (e.g., 'fal-ai/kling-video') or alias (e.g., 'svd'). Use list_models to see options.",
                    },
                    "duration": {
                        "type": "integer",
                        "default": 4,
                        "minimum": 2,
                        "maximum": 10,
                        "description": "Video duration in seconds",
                    },
                },
                "required": ["image_url"],
            },
        ),
        Tool(
            name="generate_music",
            description="Generate music from text descriptions. Use list_models with category='audio' to discover available models.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Description of the music (genre, mood, instruments)",
                    },
                    "duration_seconds": {
                        "type": "integer",
                        "default": 30,
                        "minimum": 5,
                        "maximum": 300,
                        "description": "Duration in seconds",
                    },
                    "model": {
                        "type": "string",
                        "default": "musicgen",
                        "description": "Model ID (e.g., 'fal-ai/musicgen-large') or alias (e.g., 'musicgen'). Use list_models to see options.",
                    },
                },
                "required": ["prompt"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Execute a Fal.ai tool"""

    try:
        # Get the model registry
        registry = await get_registry()

        # List models tool
        if name == "list_models":
            models = await registry.list_models(
                category=arguments.get("category"),
                search=arguments.get("search"),
                limit=arguments.get("limit", 20),
            )

            if not models:
                return [
                    TextContent(
                        type="text",
                        text="No models found. Try a different category or search term.",
                    )
                ]

            # Format output
            lines = [f"## Available Models ({len(models)} found)\n"]

            for model in models:
                lines.append(f"- `{model.id}`")
                if model.name and model.name != model.id:
                    lines.append(f"  - **{model.name}**")
                if model.description:
                    desc = (
                        model.description[:150] + "..."
                        if len(model.description) > 150
                        else model.description
                    )
                    lines.append(f"  - {desc}")

            return [TextContent(type="text", text="\n".join(lines))]

        # Fast operations using async API
        if name == "generate_image":
            model_input = arguments.get("model", "flux_schnell")
            try:
                model_id = await registry.resolve_model_id(model_input)
            except ValueError as e:
                return [
                    TextContent(
                        type="text",
                        text=f"❌ {e}. Use list_models to see available options.",
                    )
                ]

            fal_args = {
                "prompt": arguments["prompt"],
                "image_size": arguments.get("image_size", "landscape_16_9"),
                "num_images": arguments.get("num_images", 1),
            }

            # Add optional parameters
            if "negative_prompt" in arguments:
                fal_args["negative_prompt"] = arguments["negative_prompt"]
            if "seed" in arguments:
                fal_args["seed"] = arguments["seed"]

            # Use native async API for fast image generation
            result = await fal_client.run_async(model_id, arguments=fal_args)

            images = result.get("images", [])
            if images:
                urls = [img["url"] for img in images]
                response = f"🎨 Generated {len(urls)} image(s) with {model_id}:\n\n"
                for i, url in enumerate(urls, 1):
                    response += f"Image {i}: {url}\n"
                return [TextContent(type="text", text=response)]

        # Long operations using queue API
        elif name == "generate_video":
            model_input = arguments.get("model", "svd")
            try:
                model_id = await registry.resolve_model_id(model_input)
            except ValueError as e:
                return [
                    TextContent(
                        type="text",
                        text=f"❌ {e}. Use list_models to see available options.",
                    )
                ]

            fal_args = {"image_url": arguments["image_url"]}
            if "duration" in arguments:
                fal_args["duration"] = arguments["duration"]

            # Submit to queue for processing
            handle = await fal_client.submit_async(model_id, arguments=fal_args)
            request_id = (
                handle.request_id if hasattr(handle, "request_id") else str(handle)
            )

            # Wait for completion with status updates
            response = f"⏳ Video generation queued (ID: {request_id[:8]}...)\n"
            response += "Processing (this may take 30-60 seconds)...\n"

            video_result: Optional[Dict[str, Any]] = await wait_for_queue_result(
                handle, timeout=180
            )

            if video_result is not None and "error" not in video_result:
                video_dict = video_result.get("video", {})
                if isinstance(video_dict, dict):
                    video_url = video_dict.get("url")
                else:
                    video_url = video_result.get("url")
                if video_url:
                    return [
                        TextContent(
                            type="text",
                            text=f"🎬 Video generated with {model_id}: {video_url}",
                        )
                    ]
            else:
                error_msg = (
                    video_result.get("error", "Unknown error")
                    if video_result
                    else "Unknown error"
                )
                return [
                    TextContent(
                        type="text",
                        text=f"❌ Video generation failed: {error_msg}",
                    )
                ]

        elif name == "generate_music":
            model_input = arguments.get("model", "musicgen")
            try:
                model_id = await registry.resolve_model_id(model_input)
            except ValueError as e:
                return [
                    TextContent(
                        type="text",
                        text=f"❌ {e}. Use list_models to see available options.",
                    )
                ]

            # Submit to queue for longer music generation
            handle = await fal_client.submit_async(
                model_id,
                arguments={
                    "prompt": arguments["prompt"],
                    "duration_seconds": arguments.get("duration_seconds", 30),
                },
            )

            request_id = (
                handle.request_id if hasattr(handle, "request_id") else str(handle)
            )
            duration = arguments.get("duration_seconds", 30)

            response = f"⏳ Music generation queued (ID: {request_id[:8]}...)\n"
            response += (
                f"Generating {duration}s of music (this may take 20-40 seconds)...\n"
            )

            music_result: Optional[Dict[str, Any]] = await wait_for_queue_result(
                handle, timeout=120
            )

            if music_result is not None and "error" not in music_result:
                audio_dict = music_result.get("audio", {})
                if isinstance(audio_dict, dict):
                    audio_url = audio_dict.get("url")
                else:
                    audio_url = music_result.get("audio_url")
                if audio_url:
                    return [
                        TextContent(
                            type="text",
                            text=f"🎵 Generated {duration}s of music with {model_id}: {audio_url}",
                        )
                    ]
            else:
                error_msg = (
                    music_result.get("error", "Unknown error")
                    if music_result
                    else "Unknown error"
                )
                return [
                    TextContent(
                        type="text",
                        text=f"❌ Music generation failed: {error_msg}",
                    )
                ]

        return [
            TextContent(
                type="text", text="⚠️ Operation completed but no output was generated"
            )
        ]

    except Exception as e:
        logger.exception("Error executing tool %s with arguments %s", name, arguments)
        error_msg = f"❌ Error executing {name}: {str(e)}"
        if "FAL_KEY" not in os.environ:
            error_msg += "\n⚠️ FAL_KEY environment variable not set!"
        return [TextContent(type="text", text=error_msg)]


async def run() -> None:
    """Run the MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="fal-ai-mcp",
                server_version="1.1.0",
                capabilities=ServerCapabilities(
                    tools=ToolsCapability()
                ),  # Enable tools capability
            ),
        )


def main() -> None:
    """Main entry point"""
    asyncio.run(run())


if __name__ == "__main__":
    main()
