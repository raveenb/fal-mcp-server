#!/usr/bin/env python3
"""Fal.ai MCP Server with dual transport support (STDIO and HTTP/SSE)"""

import argparse
import asyncio
import os
import sys
import threading
from typing import Any, Dict, List

import fal_client
import mcp.server.stdio
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


class FalMCPServer:
    """Fal.ai MCP Server with support for multiple transports"""

    def __init__(self) -> None:
        """Initialize the MCP server"""
        self.server = Server("fal-ai-mcp")
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up server handlers"""

        @self.server.list_tools()
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
                            "prompt": {
                                "type": "string",
                                "description": "Text description to guide the video animation (e.g., 'camera slowly pans right, gentle breeze moves the leaves')",
                            },
                            "model": {
                                "type": "string",
                                "default": "fal-ai/wan-i2v",
                                "description": "Model ID (e.g., 'fal-ai/kling-video/v2.1/standard/image-to-video'). Use list_models to see options.",
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
                Tool(
                    name="generate_music",
                    description="Generate music from text descriptions. Use list_models with category='audio' to discover available models.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "Description of the music",
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

        @self.server.call_tool()
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
                        response = (
                            f"🎨 Generated {len(urls)} image(s) with {model_id}:\n\n"
                        )
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
                        "image_url": arguments["image_url"],
                        "prompt": arguments["prompt"],
                    }
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
                        handle.request_id
                        if hasattr(handle, "request_id")
                        else str(handle)
                    )

                    # Wait for completion
                    response = f"⏳ Video generation queued (ID: {request_id[:8]}...)\n"
                    response += "Processing (this may take 30-60 seconds)...\n"

                    # Simple wait for result
                    result = await handle.get()

                    if result:
                        video_url = result.get("video", {}).get("url") or result.get(
                            "url"
                        )
                        if video_url:
                            return [
                                TextContent(
                                    type="text",
                                    text=f"🎬 Video generated with {model_id}: {video_url}",
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
                        handle.request_id
                        if hasattr(handle, "request_id")
                        else str(handle)
                    )
                    duration = arguments.get("duration_seconds", 30)

                    response = f"⏳ Music generation queued (ID: {request_id[:8]}...)\n"
                    response += f"Generating {duration}s of music (this may take 20-40 seconds)...\n"

                    # Simple wait for result
                    result = await handle.get()

                    if result:
                        audio_url = result.get("audio", {}).get("url") or result.get(
                            "audio_url"
                        )
                        if audio_url:
                            return [
                                TextContent(
                                    type="text",
                                    text=f"🎵 Generated {duration}s of music with {model_id}: {audio_url}",
                                )
                            ]

                return [
                    TextContent(
                        type="text",
                        text="⚠️ Operation completed but no output was generated",
                    )
                ]

            except Exception as e:
                logger.exception(
                    "Error executing tool {} with arguments {}", name, arguments
                )
                error_msg = f"❌ Error executing {name}: {str(e)}"
                if "FAL_KEY" not in os.environ:
                    error_msg += "\n⚠️ FAL_KEY environment variable not set!"
                return [TextContent(type="text", text=error_msg)]

    def get_initialization_options(self) -> InitializationOptions:
        """Get initialization options for the server"""
        return InitializationOptions(
            server_name="fal-ai-mcp",
            server_version="1.2.0",
            capabilities=ServerCapabilities(tools=ToolsCapability()),
        )

    async def run_stdio(self) -> None:
        """Run the server with STDIO transport"""
        logger.info("Starting Fal.ai MCP server with STDIO transport...")
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.get_initialization_options(),
            )

    def create_http_app(self, host: str = "127.0.0.1", port: int = 8000) -> Starlette:
        """Create the HTTP/SSE Starlette application"""

        # Create SSE transport with message endpoint
        sse_transport = SseServerTransport("/messages/")

        async def handle_sse(scope: Scope, receive: Receive, send: Send) -> None:
            """Handle SSE connections"""
            logger.info("Client connected via SSE")

            async with sse_transport.connect_sse(scope, receive, send) as streams:
                await self.server.run(
                    streams[0],
                    streams[1],
                    self.get_initialization_options(),
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

    def run_http(self, host: str = "127.0.0.1", port: int = 8000) -> None:
        """Run the server with HTTP/SSE transport"""
        logger.info("Starting Fal.ai MCP server with HTTP/SSE transport...")
        app = self.create_http_app(host, port)
        uvicorn.run(app, host=host, port=port, log_level="info")

    def run_dual(self, host: str = "127.0.0.1", port: int = 8000) -> None:
        """Run the server with both STDIO and HTTP/SSE transports"""
        logger.info(
            "Starting Fal.ai MCP server with dual transport (STDIO + HTTP/SSE)..."
        )

        # Create HTTP app
        app = self.create_http_app(host, port)

        # Run HTTP server in a separate thread
        def run_http_server() -> None:
            uvicorn.run(app, host=host, port=port, log_level="info")

        http_thread = threading.Thread(target=run_http_server, daemon=True)
        http_thread.start()

        # Run STDIO server in the main thread
        asyncio.run(self.run_stdio())


def main() -> None:
    """Main entry point with CLI argument support"""
    parser = argparse.ArgumentParser(
        description="Fal.ai MCP Server with multiple transport options"
    )
    parser.add_argument(
        "--transport",
        type=str,
        default="stdio",
        choices=["stdio", "http", "dual"],
        help="Transport mode: stdio, http, or dual (default: stdio)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default=os.getenv("FAL_MCP_HOST", "127.0.0.1"),
        help="Host for HTTP server (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("FAL_MCP_PORT", "8000")),
        help="Port for HTTP server (default: 8000)",
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

    # Create server instance
    server = FalMCPServer()

    # Run with selected transport
    transport = os.getenv("FAL_MCP_TRANSPORT", args.transport)

    if transport == "http":
        server.run_http(args.host, args.port)
    elif transport == "dual":
        server.run_dual(args.host, args.port)
    else:  # stdio (default)
        asyncio.run(server.run_stdio())


if __name__ == "__main__":
    main()
