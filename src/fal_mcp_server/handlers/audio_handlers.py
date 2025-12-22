"""
Audio handler implementations for Fal.ai MCP Server.

Contains: generate_music
"""

import asyncio
from typing import Any, Dict, List

from loguru import logger
from mcp.types import TextContent

from fal_mcp_server.model_registry import ModelRegistry
from fal_mcp_server.queue.base import QueueStrategy


async def handle_generate_music(
    arguments: Dict[str, Any],
    registry: ModelRegistry,
    queue_strategy: QueueStrategy,
) -> List[TextContent]:
    """Handle the generate_music tool."""
    model_input = arguments.get("model", "fal-ai/lyria2")
    try:
        model_id = await registry.resolve_model_id(model_input)
    except ValueError as e:
        return [
            TextContent(
                type="text",
                text=f"❌ {e}. Use list_models to see available options.",
            )
        ]

    duration = arguments.get("duration_seconds", 30)

    # Build arguments for the music model
    music_args: Dict[str, Any] = {
        "prompt": arguments["prompt"],
        "duration_seconds": duration,
    }

    # Add optional parameters if provided
    if "negative_prompt" in arguments:
        music_args["negative_prompt"] = arguments["negative_prompt"]
    if "lyrics_prompt" in arguments:
        music_args["lyrics_prompt"] = arguments["lyrics_prompt"]

    # Use queue strategy with timeout protection
    logger.info("Starting music generation with %s (%ds)", model_id, duration)
    try:
        music_result = await asyncio.wait_for(
            queue_strategy.execute(model_id, music_args, timeout=120),
            timeout=125,  # Slightly longer than internal timeout
        )
    except asyncio.TimeoutError:
        return [
            TextContent(
                type="text",
                text=f"❌ Music generation timed out after 120 seconds. Model: {model_id}",
            )
        ]

    if music_result is None:
        return [
            TextContent(
                type="text",
                text=f"❌ Music generation failed or timed out with {model_id}",
            )
        ]

    # Check for error in response
    if "error" in music_result:
        error_msg = music_result.get("error", "Unknown error")
        return [
            TextContent(
                type="text",
                text=f"❌ Music generation failed: {error_msg}",
            )
        ]

    # Extract audio URL from result
    audio_dict = music_result.get("audio", {})
    if isinstance(audio_dict, dict):
        audio_url = audio_dict.get("url")
    else:
        audio_url = music_result.get("audio_url")

    if audio_url:
        return [
            TextContent(
                type="text",
                text=f"🎵 Music generated with {model_id}: {audio_url}",
            )
        ]

    return [
        TextContent(
            type="text",
            text="❌ Music generation completed but no audio URL was returned. Please try again.",
        )
    ]
