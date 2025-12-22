#!/usr/bin/env python3
"""
Fal.ai MCP Server - HTTP/SSE transport.

This server uses the PollingStrategy for long-running operations,
which provides better control for HTTP transport scenarios.
"""

import argparse
import os
import sys
from typing import Any, Dict, List

import uvicorn
from loguru import logger
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.sse import SseServerTransport
from mcp.types import ServerCapabilities, TextContent, Tool, ToolsCapability
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Mount, Route

# Handlers (transport-agnostic business logic)
from fal_mcp_server.handlers import (
    handle_generate_image,
    handle_generate_image_from_image,
    handle_generate_image_structured,
    handle_generate_music,
    handle_generate_video,
    handle_generate_video_from_image,
    handle_generate_video_from_video,
    handle_get_pricing,
    handle_get_usage,
    handle_list_models,
    handle_recommend_model,
    handle_upload_file,
)

# Model registry for dynamic model discovery
from fal_mcp_server.model_registry import get_registry

# Queue strategy for this transport
from fal_mcp_server.queue import PollingStrategy

# Tool definitions
from fal_mcp_server.tools import ALL_TOOLS

# Configure Fal client
if api_key := os.getenv("FAL_KEY"):
    os.environ["FAL_KEY"] = api_key

# Initialize the MCP server
server = Server("fal-ai-mcp")

# Create the queue strategy for this transport
queue_strategy = PollingStrategy()

# Map tool names to handler functions
TOOL_HANDLERS = {
    # Utility tools (no queue needed)
    "list_models": handle_list_models,
    "recommend_model": handle_recommend_model,
    "get_pricing": handle_get_pricing,
    "get_usage": handle_get_usage,
    "upload_file": handle_upload_file,
    # Image tools
    "generate_image": handle_generate_image,
    "generate_image_structured": handle_generate_image_structured,
    "generate_image_from_image": handle_generate_image_from_image,
    # Video tools
    "generate_video": handle_generate_video,
    "generate_video_from_image": handle_generate_video_from_image,
    "generate_video_from_video": handle_generate_video_from_video,
    # Audio tools
    "generate_music": handle_generate_music,
}

# Tools that don't require a queue strategy
NO_QUEUE_TOOLS = {
    "list_models",
    "recommend_model",
    "get_pricing",
    "get_usage",
    "upload_file",
}


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List all available Fal.ai tools"""
    return ALL_TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Execute a Fal.ai tool by routing to the appropriate handler."""
    try:
        # Get the model registry
        registry = await get_registry()

        # Find the handler for this tool
        handler = TOOL_HANDLERS.get(name)
        if not handler:
            return [
                TextContent(
                    type="text",
                    text=f"❌ Unknown tool: {name}. Use list_tools to see available options.",
                )
            ]

        # Call the handler with appropriate arguments
        # Type ignore: handlers have different signatures but are validated at runtime
        if name in NO_QUEUE_TOOLS:
            return await handler(arguments, registry)  # type: ignore[operator, no-any-return]
        else:
            return await handler(arguments, registry, queue_strategy)  # type: ignore[operator, no-any-return]

    except Exception as e:
        logger.exception("Error executing tool %s with arguments %s", name, arguments)
        error_msg = f"❌ Error executing {name}: {str(e)}"
        if "FAL_KEY" not in os.environ:
            error_msg += "\n⚠️ FAL_KEY environment variable not set!"
        return [TextContent(type="text", text=error_msg)]


def create_http_app(host: str = "127.0.0.1", port: int = 8000) -> Starlette:
    """Create an HTTP/SSE application for the MCP server.

    Args:
        host: Host to bind the server to
        port: Port to bind the server to

    Returns:
        Starlette application configured for SSE transport
    """
    # Create SSE transport
    sse_transport = SseServerTransport("/messages/")

    async def handle_sse(scope: Dict[str, Any], receive: Any, send: Any) -> None:
        """Handle SSE connections"""
        logger.info("Client connected via SSE")

        async with sse_transport.connect_sse(scope, receive, send) as streams:
            await server.run(
                streams[0],
                streams[1],
                InitializationOptions(
                    server_name="fal-ai-mcp",
                    server_version="1.14.0",
                    capabilities=ServerCapabilities(tools=ToolsCapability()),
                ),
            )

    async def sse_endpoint(request: Request) -> Response:
        """Starlette endpoint wrapper for SSE handler"""
        await handle_sse(dict(request.scope), request.receive, request._send)
        return Response()

    # Create routes
    routes = [
        Route("/sse", endpoint=sse_endpoint, methods=["GET"]),
        Mount("/messages/", app=sse_transport.handle_post_message),
    ]

    # Create Starlette app
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
    logger.remove()
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
