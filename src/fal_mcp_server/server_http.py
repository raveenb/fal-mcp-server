#!/usr/bin/env python3
"""Fal.ai MCP Server with HTTP/SSE transport support"""

import argparse
import asyncio
import os
import sys
from typing import Any, Dict, List, Optional, cast

import fal_client
import uvicorn
from loguru import logger

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
            description="Generate videos from text prompts (text-to-video) or from images (image-to-video). Use list_models with category='video' to discover available models.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Text description for the video (e.g., 'A slow-motion drone shot of Tokyo at night')",
                    },
                    "image_url": {
                        "type": "string",
                        "description": "Starting image URL for image-to-video models. Optional for text-to-video models.",
                    },
                    "model": {
                        "type": "string",
                        "default": "fal-ai/wan-i2v",
                        "description": "Model ID. Use 'fal-ai/kling-video/v2/master/text-to-video' for text-only, or image-to-video models like 'fal-ai/wan-i2v'.",
                    },
                    "duration": {
                        "type": "integer",
                        "default": 5,
                        "minimum": 2,
                        "maximum": 10,
                        "description": "Video duration in seconds",
                    },
                    "aspect_ratio": {
                        "type": "string",
                        "default": "16:9",
                        "description": "Video aspect ratio (e.g., '16:9', '9:16', '1:1')",
                    },
                    "negative_prompt": {
                        "type": "string",
                        "description": "What to avoid in the video (e.g., 'blur, distort, low quality')",
                    },
                    "cfg_scale": {
                        "type": "number",
                        "default": 0.5,
                        "description": "Classifier-free guidance scale (0.0-1.0). Lower values give more creative results.",
                    },
                },
                "required": ["prompt"],
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
        Tool(
            name="upload_file",
            description="Upload a local file to Fal.ai storage and get a URL. Use this to upload images, videos, or audio files that can then be used with other Fal.ai tools (e.g., image-to-video, audio transform).",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the local file to upload (e.g., '/path/to/image.png')",
                    },
                },
                "required": ["file_path"],
            },
        ),
        Tool(
            name="generate_video_from_image",
            description="Animate an image into a video. The image serves as the starting frame and the prompt guides the animation. Use upload_file first if you have a local image.",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_url": {
                        "type": "string",
                        "description": "URL of the image to animate (use upload_file for local images)",
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Text description guiding how to animate the image (e.g., 'camera slowly pans right, gentle breeze moves the leaves')",
                    },
                    "model": {
                        "type": "string",
                        "default": "fal-ai/wan-i2v",
                        "description": "Image-to-video model. Options: fal-ai/wan-i2v, fal-ai/kling-video/v2.1/standard/image-to-video",
                    },
                    "duration": {
                        "type": "integer",
                        "default": 5,
                        "minimum": 2,
                        "maximum": 10,
                        "description": "Video duration in seconds",
                    },
                    "aspect_ratio": {
                        "type": "string",
                        "default": "16:9",
                        "description": "Video aspect ratio (e.g., '16:9', '9:16', '1:1')",
                    },
                    "negative_prompt": {
                        "type": "string",
                        "description": "What to avoid in the video (e.g., 'blur, distort, low quality')",
                    },
                    "cfg_scale": {
                        "type": "number",
                        "default": 0.5,
                        "description": "Classifier-free guidance scale (0.0-1.0). Lower values give more creative results.",
                    },
                },
                "required": ["image_url", "prompt"],
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
            model_input = arguments.get("model", "fal-ai/wan-i2v")
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
            }
            # image_url is optional - only needed for image-to-video models
            if "image_url" in arguments:
                fal_args["image_url"] = arguments["image_url"]
            if "duration" in arguments:
                fal_args["duration"] = arguments["duration"]
            if "aspect_ratio" in arguments:
                fal_args["aspect_ratio"] = arguments["aspect_ratio"]
            if "negative_prompt" in arguments:
                fal_args["negative_prompt"] = arguments["negative_prompt"]
            if "cfg_scale" in arguments:
                fal_args["cfg_scale"] = arguments["cfg_scale"]

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

        # File upload tool
        elif name == "upload_file":
            file_path = arguments.get("file_path")
            if not file_path:
                return [
                    TextContent(
                        type="text",
                        text="❌ file_path is required",
                    )
                ]

            # Validate file exists
            if not os.path.exists(file_path):
                return [
                    TextContent(
                        type="text",
                        text=f"❌ File not found: {file_path}",
                    )
                ]

            if not os.path.isfile(file_path):
                return [
                    TextContent(
                        type="text",
                        text=f"❌ Path is not a file: {file_path}",
                    )
                ]

            try:
                # Get file size for logging (inside try to handle race conditions)
                file_size = os.path.getsize(file_path)
                file_size_mb = file_size / (1024 * 1024)
                logger.info("Uploading file: %s (%.2f MB)", file_path, file_size_mb)

                # Upload file to Fal.ai storage
                # fal_client.upload_file is synchronous, run in thread pool
                loop = asyncio.get_running_loop()
                url = await loop.run_in_executor(
                    None, fal_client.upload_file, file_path
                )

                # Get filename for display
                filename = os.path.basename(file_path)
                logger.info("Successfully uploaded %s to %s", file_path, url)

                return [
                    TextContent(
                        type="text",
                        text=f"📤 Uploaded `{filename}` ({file_size_mb:.2f} MB)\n\n**URL:** {url}\n\nThis URL can now be used with other Fal.ai tools.",
                    )
                ]
            except OSError as e:
                logger.error("Cannot access file %s: %s", file_path, e)
                return [
                    TextContent(
                        type="text",
                        text=f"❌ Cannot access file: {file_path}. {str(e)}",
                    )
                ]
            except Exception as upload_error:
                logger.exception(
                    "Unexpected error during file upload: %s", upload_error
                )
                return [
                    TextContent(
                        type="text",
                        text=f"❌ Upload failed: {str(upload_error)}",
                    )
                ]

        # Image-to-video generation (dedicated tool with required image_url)
        elif name == "generate_video_from_image":
            model_input = arguments.get("model", "fal-ai/wan-i2v")
            try:
                model_id = await registry.resolve_model_id(model_input)
            except ValueError as e:
                return [
                    TextContent(
                        type="text",
                        text=f"❌ {e}. Use list_models to see available options.",
                    )
                ]

            # Both image_url and prompt are required for this tool
            fal_args = {
                "image_url": arguments["image_url"],
                "prompt": arguments["prompt"],
            }

            # Add optional parameters
            if "duration" in arguments:
                fal_args["duration"] = arguments["duration"]
            if "aspect_ratio" in arguments:
                fal_args["aspect_ratio"] = arguments["aspect_ratio"]
            if "negative_prompt" in arguments:
                fal_args["negative_prompt"] = arguments["negative_prompt"]
            if "cfg_scale" in arguments:
                fal_args["cfg_scale"] = arguments["cfg_scale"]

            logger.info(
                "Starting image-to-video generation with %s from %s",
                model_id,
                (
                    arguments["image_url"][:50] + "..."
                    if len(arguments["image_url"]) > 50
                    else arguments["image_url"]
                ),
            )

            # Submit to queue for processing
            handle = await fal_client.submit_async(model_id, arguments=fal_args)
            request_id = (
                handle.request_id if hasattr(handle, "request_id") else str(handle)
            )

            # Wait for completion with status updates
            response = (
                f"⏳ Image-to-video generation queued (ID: {request_id[:8]}...)\n"
            )
            response += "Processing (this may take 30-60 seconds)...\n"

            i2v_result: Optional[Dict[str, Any]] = await wait_for_queue_result(
                handle, timeout=180
            )

            if i2v_result is not None and "error" not in i2v_result:
                video_dict = i2v_result.get("video", {})
                if isinstance(video_dict, dict):
                    video_url = video_dict.get("url")
                else:
                    video_url = i2v_result.get("url")
                if video_url:
                    logger.info("Successfully generated video: %s", video_url)
                    return [
                        TextContent(
                            type="text",
                            text=f"🎬 Video generated with {model_id}: {video_url}",
                        )
                    ]
            else:
                error_msg = (
                    i2v_result.get("error", "Unknown error")
                    if i2v_result
                    else "Unknown error"
                )
                return [
                    TextContent(
                        type="text",
                        text=f"❌ Image-to-video generation failed: {error_msg}",
                    )
                ]

        return [
            TextContent(
                type="text", text="⚠️ Operation completed but no output was generated"
            )
        ]

    except Exception as e:
        logger.exception("Error executing tool {} with arguments {}", name, arguments)
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

    # Configure loguru
    logger.remove()  # Remove default handler
    logger.add(sys.stderr, level=args.log_level)

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
