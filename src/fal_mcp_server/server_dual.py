#!/usr/bin/env python3
"""
Fal.ai MCP Server - Dual transport (STDIO + HTTP/SSE).

This server supports multiple transport modes:
- stdio: Standard input/output (for MCP client integration)
- http: HTTP/SSE only (for web-based access)
- dual: Both transports simultaneously

Uses HandleGetStrategy for long-running operations.
"""

import argparse
import asyncio
import os
import sys
import threading
from typing import Any, Dict, List

import mcp.server.stdio
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
from fal_mcp_server.queue import HandleGetStrategy

# Tool definitions
from fal_mcp_server.tools import ALL_TOOLS

# Configure Fal client
if api_key := os.getenv("FAL_KEY"):
    os.environ["FAL_KEY"] = api_key

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


class FalMCPServer:
    """Fal.ai MCP Server with support for multiple transports."""

    def __init__(self) -> None:
        """Initialize the MCP server."""
        self.server = Server("fal-ai-mcp")
        self.queue_strategy = HandleGetStrategy()
        self._setup_handlers()

    def get_initialization_options(self) -> InitializationOptions:
        """Get the initialization options for the server."""
        return InitializationOptions(
            server_name="fal-ai-mcp",
            server_version="1.14.0",
            capabilities=ServerCapabilities(tools=ToolsCapability()),
        )

    def _setup_handlers(self) -> None:
        """Set up server handlers."""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List all available Fal.ai tools"""
            return ALL_TOOLS

        @self.server.call_tool()
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
                    return await handler(arguments, registry, self.queue_strategy)  # type: ignore[operator, no-any-return]

            except Exception as e:
                logger.exception(
                    "Error executing tool %s with arguments %s", name, arguments
                )
                error_msg = f"❌ Error executing {name}: {str(e)}"
                if "FAL_KEY" not in os.environ:
                    error_msg += "\n⚠️ FAL_KEY environment variable not set!"
                return [TextContent(type="text", text=error_msg)]

    async def run_stdio(self) -> None:
        """Run the server with STDIO transport."""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="fal-ai-mcp",
                    server_version="1.14.0",
                    capabilities=ServerCapabilities(tools=ToolsCapability()),
                ),
            )

    def create_http_app(self, host: str = "127.0.0.1", port: int = 8000) -> Starlette:
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
                await self.server.run(
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

    def run_http(self, host: str = "127.0.0.1", port: int = 8000) -> None:
        """Run the server with HTTP/SSE transport."""
        logger.info("Starting Fal.ai MCP server with HTTP/SSE transport...")
        app = self.create_http_app(host, port)
        uvicorn.run(app, host=host, port=port, log_level="info")

    def run_dual(self, host: str = "127.0.0.1", port: int = 8000) -> None:
        """Run the server with both STDIO and HTTP/SSE transports."""
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
    """Main entry point with CLI argument support."""
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
    logger.remove()
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
