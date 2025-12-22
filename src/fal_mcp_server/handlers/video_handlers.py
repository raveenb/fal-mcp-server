"""
Video handler implementations for Fal.ai MCP Server.

Contains: generate_video, generate_video_from_image
"""

import asyncio
from typing import Any, Dict, List

from loguru import logger
from mcp.types import TextContent

from fal_mcp_server.model_registry import ModelRegistry
from fal_mcp_server.queue.base import QueueStrategy


async def handle_generate_video(
    arguments: Dict[str, Any],
    registry: ModelRegistry,
    queue_strategy: QueueStrategy,
) -> List[TextContent]:
    """Handle the generate_video tool."""
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

    fal_args: Dict[str, Any] = {
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

    # Use queue strategy with timeout protection for long-running video generation
    logger.info("Starting video generation with %s", model_id)
    try:
        video_result = await asyncio.wait_for(
            queue_strategy.execute(model_id, fal_args, timeout=180),
            timeout=185,  # Slightly longer than internal timeout
        )
    except asyncio.TimeoutError:
        return [
            TextContent(
                type="text",
                text=f"❌ Video generation timed out after 180 seconds with {model_id}",
            )
        ]

    if video_result is None:
        return [
            TextContent(
                type="text",
                text=f"❌ Video generation failed or timed out with {model_id}",
            )
        ]

    # Check for error in response
    if "error" in video_result:
        error_msg = video_result.get("error", "Unknown error")
        return [
            TextContent(
                type="text",
                text=f"❌ Video generation failed: {error_msg}",
            )
        ]

    # Extract video URL from result
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

    return [
        TextContent(
            type="text",
            text="❌ Video generation completed but no video URL was returned. Please try again.",
        )
    ]


async def handle_generate_video_from_image(
    arguments: Dict[str, Any],
    registry: ModelRegistry,
    queue_strategy: QueueStrategy,
) -> List[TextContent]:
    """Handle the generate_video_from_image tool."""
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
    fal_args: Dict[str, Any] = {
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

    # Use queue strategy with timeout protection
    logger.info(
        "Starting image-to-video generation with %s from %s",
        model_id,
        (
            arguments["image_url"][:50] + "..."
            if len(arguments["image_url"]) > 50
            else arguments["image_url"]
        ),
    )
    try:
        video_result = await asyncio.wait_for(
            queue_strategy.execute(model_id, fal_args, timeout=180),
            timeout=185,  # Slightly longer than internal timeout
        )
    except asyncio.TimeoutError:
        logger.error(
            "Image-to-video generation timed out after 180s. Model: %s, Image: %s",
            model_id,
            (
                arguments["image_url"][:50] + "..."
                if len(arguments["image_url"]) > 50
                else arguments["image_url"]
            ),
        )
        return [
            TextContent(
                type="text",
                text=f"❌ Video generation timed out after 180 seconds with {model_id}",
            )
        ]

    if video_result is None:
        return [
            TextContent(
                type="text",
                text=f"❌ Video generation failed or timed out with {model_id}",
            )
        ]

    # Check for error in response
    if "error" in video_result:
        error_msg = video_result.get("error", "Unknown error")
        return [
            TextContent(
                type="text",
                text=f"❌ Video generation failed: {error_msg}",
            )
        ]

    # Extract video URL from result
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

    return [
        TextContent(
            type="text",
            text="❌ Video generation completed but no video URL was returned. Please try again.",
        )
    ]
