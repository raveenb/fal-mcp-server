#!/usr/bin/env python3
"""Fal.ai MCP Server with HTTP/SSE transport support"""

import argparse
import asyncio
import logging
import os
from typing import Any, Dict, List, Optional, cast

import fal_client
import uvicorn

# MCP imports
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.sse import SseServerTransport
from mcp.types import (
    ServerCapabilities,
    TextContent,
    Tool,
    ToolsCapability,
)
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Mount, Route
from starlette.types import Receive, Scope, Send

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Fal client
if api_key := os.getenv("FAL_KEY"):
    os.environ["FAL_KEY"] = api_key

# Initialize the MCP server
server = Server("fal-ai-mcp")

# Model configurations (reuse from main server)
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


async def wait_for_queue_result(
    handle: Any, timeout: int = 300
) -> Optional[Dict[str, Any]]:
    """Wait for a queued job to complete with timeout"""
    import time

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
            name="generate_image",
            description="Generate images from text prompts using various models (fast, uses async API)",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Text description of the image to generate",
                    },
                    "model": {
                        "type": "string",
                        "enum": list(MODELS["image"].keys()),
                        "default": "flux_schnell",
                        "description": "Model to use for generation",
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
            description="Generate videos from images (uses queue API for long processing)",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_url": {
                        "type": "string",
                        "description": "Starting image URL (for image-to-video)",
                    },
                    "model": {
                        "type": "string",
                        "enum": list(MODELS["video"].keys()),
                        "default": "svd",
                        "description": "Video generation model",
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
            description="Generate music from text descriptions (uses queue API for long processing)",
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
                        "enum": ["musicgen", "musicgen_large"],
                        "default": "musicgen",
                        "description": "Music generation model",
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
        # Fast operations using async API
        if name == "generate_image":
            model_key = arguments.get("model", "flux_schnell")
            model_id = MODELS["image"][model_key]

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
                response = (
                    f"🎨 Generated {len(urls)} image(s) with {model_key} (async):\n\n"
                )
                for i, url in enumerate(urls, 1):
                    response += f"Image {i}: {url}\n"
                return [TextContent(type="text", text=response)]

        # Long operations using queue API
        elif name == "generate_video":
            model_key = arguments.get("model", "svd")
            model_id = MODELS["video"][model_key]

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
                            text=f"🎬 Video generated (via queue): {video_url}",
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
            model_key = arguments.get("model", "musicgen")
            model_id = MODELS["audio"][model_key]

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
                            text=f"🎵 Generated {duration}s of music (via queue): {audio_url}",
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
        error_msg = f"❌ Error executing {name}: {str(e)}"
        if "FAL_KEY" not in os.environ:
            error_msg += "\n⚠️ FAL_KEY environment variable not set!"
        return [TextContent(type="text", text=error_msg)]


def create_http_app(host: str = "127.0.0.1", port: int = 8000) -> Starlette:
    """Create the HTTP/SSE Starlette application"""

    # Create SSE transport with message endpoint
    sse_transport = SseServerTransport("/messages/")

    async def handle_sse(scope: Scope, receive: Receive, send: Send) -> None:
        """Handle SSE connections"""
        logger.info("Client connected via SSE")

        async with sse_transport.connect_sse(scope, receive, send) as streams:
            await server.run(
                streams[0],
                streams[1],
                InitializationOptions(
                    server_name="fal-ai-mcp",
                    server_version="1.1.0",
                    capabilities=ServerCapabilities(tools=ToolsCapability()),
                ),
            )

        # Return empty response to avoid NoneType error (type: ignore needed for ASGI)

    # Convert handle_sse to a Starlette endpoint
    from starlette.requests import Request

    async def sse_endpoint(request: Request) -> Response:
        """Starlette endpoint wrapper for SSE handler"""
        await handle_sse(request.scope, request.receive, request._send)
        return Response()

    # Create routes
    routes = [
        Route("/sse", endpoint=sse_endpoint, methods=["GET"]),
        Mount("/messages/", app=sse_transport.handle_post_message),
    ]

    # Create and return Starlette app
    app = Starlette(routes=routes)

    logger.info(f"HTTP/SSE server configured at http://{host}:{port}")
    logger.info(f"SSE endpoint: http://{host}:{port}/sse")
    logger.info(f"Message endpoint: http://{host}:{port}/messages/")

    return app


def main() -> None:
    """Main entry point with CLI argument support"""
    parser = argparse.ArgumentParser(
        description="Fal.ai MCP Server with HTTP/SSE transport"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind the HTTP server to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the HTTP server to (default: 8000)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)",
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Check for FAL_KEY
    if "FAL_KEY" not in os.environ:
        logger.warning("FAL_KEY environment variable not set - API calls will fail")
        logger.info("Get your API key from https://fal.ai/dashboard/keys")

    # Create and run the app
    app = create_http_app(args.host, args.port)

    logger.info("Starting Fal.ai MCP HTTP/SSE server...")
    logger.info(f"Server running at http://{args.host}:{args.port}")
    logger.info("Press Ctrl+C to stop")

    # Run with uvicorn
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level=args.log_level.lower(),
    )


if __name__ == "__main__":
    main()
