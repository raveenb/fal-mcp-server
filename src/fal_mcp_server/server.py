#!/usr/bin/env python3
"""
Fal.ai MCP Server - stdio transport.

This server uses the SubscribeStrategy for long-running operations,
which leverages fal_client.subscribe_async() for event streaming.
"""

import asyncio
import os
from typing import Any, Dict, List

import mcp.server.stdio
from loguru import logger
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import ServerCapabilities, TextContent, Tool, ToolsCapability

# Handlers (transport-agnostic business logic)
from fal_mcp_server.handlers import (
    handle_edit_image,
    handle_generate_image,
    handle_generate_image_from_image,
    handle_generate_image_structured,
    handle_generate_music,
    handle_generate_video,
    handle_generate_video_from_image,
    handle_generate_video_from_video,
    handle_get_pricing,
    handle_get_usage,
    handle_inpaint_image,
    handle_list_models,
    handle_recommend_model,
    handle_remove_background,
    handle_resize_image,
    handle_upload_file,
    handle_upscale_image,
)

# Model registry for dynamic model discovery
from fal_mcp_server.model_registry import get_registry

# Queue strategy for this transport
from fal_mcp_server.queue import SubscribeStrategy

# Tool definitions
from fal_mcp_server.tools import ALL_TOOLS

# Configure Fal client
if api_key := os.getenv("FAL_KEY"):
    os.environ["FAL_KEY"] = api_key

# Initialize the MCP server
server = Server("fal-ai-mcp")

# Create the queue strategy for this transport
queue_strategy = SubscribeStrategy()

# Map tool names to handler functions
TOOL_HANDLERS = {
    # Utility tools (no queue needed)
    "list_models": handle_list_models,
    "recommend_model": handle_recommend_model,
    "get_pricing": handle_get_pricing,
    "get_usage": handle_get_usage,
    "upload_file": handle_upload_file,
    # Image generation tools
    "generate_image": handle_generate_image,
    "generate_image_structured": handle_generate_image_structured,
    "generate_image_from_image": handle_generate_image_from_image,
    # Image editing tools
    "remove_background": handle_remove_background,
    "upscale_image": handle_upscale_image,
    "edit_image": handle_edit_image,
    "inpaint_image": handle_inpaint_image,
    "resize_image": handle_resize_image,
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


async def run() -> None:
    """Run the MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="fal-ai-mcp",
                server_version="1.14.0",
                capabilities=ServerCapabilities(tools=ToolsCapability()),
            ),
        )


def main() -> None:
    """Main entry point"""
    asyncio.run(run())


if __name__ == "__main__":
    main()
