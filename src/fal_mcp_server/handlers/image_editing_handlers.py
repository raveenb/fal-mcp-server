"""
Image editing handler implementations for Fal.ai MCP Server.

Contains: remove_background, upscale_image, edit_image, inpaint_image, resize_image
"""

import asyncio
from typing import Any, Dict, List

from loguru import logger
from mcp.types import TextContent

from fal_mcp_server.model_registry import ModelRegistry
from fal_mcp_server.queue.base import QueueStrategy
from fal_mcp_server.tools.image_editing_tools import SOCIAL_MEDIA_FORMATS


async def handle_remove_background(
    arguments: Dict[str, Any],
    registry: ModelRegistry,
    queue_strategy: QueueStrategy,
) -> List[TextContent]:
    """Handle the remove_background tool."""
    model_input = arguments.get("model", "fal-ai/birefnet/v2")
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
        "image_url": arguments["image_url"],
    }

    # Add output format if specified (default is PNG)
    if "output_format" in arguments:
        fal_args["output_format"] = arguments["output_format"]

    logger.info("Starting background removal with %s", model_id)

    try:
        result = await asyncio.wait_for(
            queue_strategy.execute_fast(model_id, fal_args),
            timeout=60,
        )
    except asyncio.TimeoutError:
        logger.error("Background removal timed out for %s", model_id)
        return [
            TextContent(
                type="text",
                text="❌ Background removal timed out after 60 seconds. Please try again.",
            )
        ]
    except Exception as e:
        logger.exception("Background removal failed: %s", e)
        return [
            TextContent(
                type="text",
                text=f"❌ Background removal failed: {e}",
            )
        ]

    # Check for error in response
    if "error" in result:
        error_msg = result.get("error", "Unknown error")
        logger.error("Background removal failed for %s: %s", model_id, error_msg)
        return [
            TextContent(
                type="text",
                text=f"❌ Background removal failed: {error_msg}",
            )
        ]

    # Extract the result image URL
    # BiRefNet returns {"image": {"url": "..."}}
    image_data = result.get("image", {})
    if isinstance(image_data, dict):
        output_url = image_data.get("url")
    else:
        output_url = result.get("image_url")

    if not output_url:
        logger.warning("Background removal returned no image. Result: %s", result)
        return [
            TextContent(
                type="text",
                text="❌ Background removal completed but no image was returned.",
            )
        ]

    response = "✂️ Background removed successfully!\n\n"
    response += f"**Result**: {output_url}\n\n"
    response += "The image now has a transparent background (PNG format)."
    return [TextContent(type="text", text=response)]


async def handle_upscale_image(
    arguments: Dict[str, Any],
    registry: ModelRegistry,
    queue_strategy: QueueStrategy,
) -> List[TextContent]:
    """Handle the upscale_image tool."""
    model_input = arguments.get("model", "fal-ai/clarity-upscaler")
    try:
        model_id = await registry.resolve_model_id(model_input)
    except ValueError as e:
        return [
            TextContent(
                type="text",
                text=f"❌ {e}. Use list_models to see available options.",
            )
        ]

    scale = arguments.get("scale", 2)
    fal_args: Dict[str, Any] = {
        "image_url": arguments["image_url"],
        "scale": scale,
    }

    logger.info("Starting %dx upscale with %s", scale, model_id)

    try:
        result = await asyncio.wait_for(
            queue_strategy.execute_fast(model_id, fal_args),
            timeout=120,  # Upscaling can take longer
        )
    except asyncio.TimeoutError:
        logger.error("Upscaling timed out for %s", model_id)
        return [
            TextContent(
                type="text",
                text="❌ Upscaling timed out after 120 seconds. Please try again.",
            )
        ]
    except Exception as e:
        logger.exception("Upscaling failed: %s", e)
        return [
            TextContent(
                type="text",
                text=f"❌ Upscaling failed: {e}",
            )
        ]

    # Check for error in response
    if "error" in result:
        error_msg = result.get("error", "Unknown error")
        logger.error("Upscaling failed for %s: %s", model_id, error_msg)
        return [
            TextContent(
                type="text",
                text=f"❌ Upscaling failed: {error_msg}",
            )
        ]

    # Extract the result image URL
    # Clarity upscaler returns {"image": {"url": "..."}}
    image_data = result.get("image", {})
    if isinstance(image_data, dict):
        output_url = image_data.get("url")
    else:
        output_url = result.get("image_url")

    if not output_url:
        logger.warning("Upscaling returned no image. Result: %s", result)
        return [
            TextContent(
                type="text",
                text="❌ Upscaling completed but no image was returned.",
            )
        ]

    response = f"🔍 Image upscaled {scale}x successfully!\n\n"
    response += f"**Result**: {output_url}\n\n"
    response += f"The image resolution has been increased by {scale}x."
    return [TextContent(type="text", text=response)]


async def handle_edit_image(
    arguments: Dict[str, Any],
    registry: ModelRegistry,
    queue_strategy: QueueStrategy,
) -> List[TextContent]:
    """Handle the edit_image tool for natural language image editing."""
    model_input = arguments.get("model", "fal-ai/flux-2/edit")
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
        "image_url": arguments["image_url"],
        "prompt": arguments["instruction"],
    }

    # Add optional parameters
    if "strength" in arguments:
        fal_args["strength"] = arguments["strength"]
    if "seed" in arguments:
        fal_args["seed"] = arguments["seed"]

    logger.info(
        "Starting image edit with %s: '%s'", model_id, arguments["instruction"][:50]
    )

    try:
        result = await asyncio.wait_for(
            queue_strategy.execute_fast(model_id, fal_args),
            timeout=90,
        )
    except asyncio.TimeoutError:
        logger.error("Image edit timed out for %s", model_id)
        return [
            TextContent(
                type="text",
                text="❌ Image editing timed out after 90 seconds. Please try again.",
            )
        ]
    except Exception as e:
        logger.exception("Image editing failed: %s", e)
        return [
            TextContent(
                type="text",
                text=f"❌ Image editing failed: {e}",
            )
        ]

    # Check for error in response
    if "error" in result:
        error_msg = result.get("error", "Unknown error")
        logger.error("Image editing failed for %s: %s", model_id, error_msg)
        return [
            TextContent(
                type="text",
                text=f"❌ Image editing failed: {error_msg}",
            )
        ]

    # Extract the result image URL - Flux 2 edit returns {"images": [{"url": "..."}]}
    images = result.get("images", [])
    if images:
        output_url = images[0].get("url") if isinstance(images[0], dict) else images[0]
    else:
        # Fallback to other common response formats
        image_data = result.get("image", {})
        if isinstance(image_data, dict):
            output_url = image_data.get("url")
        else:
            output_url = result.get("image_url")

    if not output_url:
        logger.warning("Image edit returned no image. Result: %s", result)
        return [
            TextContent(
                type="text",
                text="❌ Image editing completed but no image was returned.",
            )
        ]

    response = "✏️ Image edited successfully!\n\n"
    response += f"**Instruction**: {arguments['instruction']}\n\n"
    response += f"**Result**: {output_url}"
    return [TextContent(type="text", text=response)]


async def handle_inpaint_image(
    arguments: Dict[str, Any],
    registry: ModelRegistry,
    queue_strategy: QueueStrategy,
) -> List[TextContent]:
    """Handle the inpaint_image tool for masked region editing."""
    model_input = arguments.get("model", "fal-ai/flux-kontext-lora/inpaint")
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
        "image_url": arguments["image_url"],
        "mask_url": arguments["mask_url"],
        "prompt": arguments["prompt"],
    }

    # Add optional parameters
    if "negative_prompt" in arguments:
        fal_args["negative_prompt"] = arguments["negative_prompt"]
    if "seed" in arguments:
        fal_args["seed"] = arguments["seed"]

    logger.info("Starting inpainting with %s: '%s'", model_id, arguments["prompt"][:50])

    try:
        result = await asyncio.wait_for(
            queue_strategy.execute_fast(model_id, fal_args),
            timeout=90,
        )
    except asyncio.TimeoutError:
        logger.error("Inpainting timed out for %s", model_id)
        return [
            TextContent(
                type="text",
                text="❌ Inpainting timed out after 90 seconds. Please try again.",
            )
        ]
    except Exception as e:
        logger.exception("Inpainting failed: %s", e)
        return [
            TextContent(
                type="text",
                text=f"❌ Inpainting failed: {e}",
            )
        ]

    # Check for error in response
    if "error" in result:
        error_msg = result.get("error", "Unknown error")
        logger.error("Inpainting failed for %s: %s", model_id, error_msg)
        return [
            TextContent(
                type="text",
                text=f"❌ Inpainting failed: {error_msg}",
            )
        ]

    # Extract the result image URL
    images = result.get("images", [])
    if images:
        output_url = images[0].get("url") if isinstance(images[0], dict) else images[0]
    else:
        image_data = result.get("image", {})
        if isinstance(image_data, dict):
            output_url = image_data.get("url")
        else:
            output_url = result.get("image_url")

    if not output_url:
        logger.warning("Inpainting returned no image. Result: %s", result)
        return [
            TextContent(
                type="text",
                text="❌ Inpainting completed but no image was returned.",
            )
        ]

    response = "🖌️ Inpainting completed!\n\n"
    response += f"**Prompt**: {arguments['prompt']}\n\n"
    response += f"**Result**: {output_url}"
    return [TextContent(type="text", text=response)]


async def handle_resize_image(
    arguments: Dict[str, Any],
    registry: ModelRegistry,
    queue_strategy: QueueStrategy,
) -> List[TextContent]:
    """Handle the resize_image tool for Canva-style image resizing."""
    target_format = arguments["target_format"]
    mode = arguments.get("mode", "extend")

    # Determine target dimensions
    if target_format == "custom":
        if "width" not in arguments or "height" not in arguments:
            return [
                TextContent(
                    type="text",
                    text="❌ Custom format requires both 'width' and 'height' parameters.",
                )
            ]
        target_width = arguments["width"]
        target_height = arguments["height"]
        format_label = f"custom ({target_width}x{target_height})"
    else:
        if target_format not in SOCIAL_MEDIA_FORMATS:
            return [
                TextContent(
                    type="text",
                    text=f"❌ Unknown format: {target_format}. Available formats: {', '.join(SOCIAL_MEDIA_FORMATS.keys())}",
                )
            ]
        format_info = SOCIAL_MEDIA_FORMATS[target_format]
        target_width = format_info["width"]
        target_height = format_info["height"]
        format_label = f"{target_format} ({target_width}x{target_height})"

    logger.info(
        "Resizing image to %s using mode=%s",
        format_label,
        mode,
    )

    if mode == "extend":
        # Use AI outpainting to extend the image
        return await _resize_with_outpainting(
            arguments,
            target_width,
            target_height,
            format_label,
            registry,
            queue_strategy,
        )
    elif mode == "crop":
        # Smart crop to target dimensions
        return await _resize_with_crop(
            arguments,
            target_width,
            target_height,
            format_label,
            registry,
            queue_strategy,
        )
    elif mode == "letterbox":
        # Add letterbox bars
        return await _resize_with_letterbox(
            arguments,
            target_width,
            target_height,
            format_label,
            registry,
            queue_strategy,
        )
    else:
        return [
            TextContent(
                type="text",
                text=f"❌ Unknown resize mode: {mode}. Use 'extend', 'crop', or 'letterbox'.",
            )
        ]


async def _resize_with_outpainting(
    arguments: Dict[str, Any],
    target_width: int,
    target_height: int,
    format_label: str,
    registry: ModelRegistry,
    queue_strategy: QueueStrategy,
) -> List[TextContent]:
    """Resize image using AI outpainting to extend canvas."""
    model_id = "fal-ai/image-apps-v2/outpaint"

    background_prompt = arguments.get(
        "background_prompt",
        "continue the image naturally, seamless extension",
    )

    fal_args: Dict[str, Any] = {
        "image_url": arguments["image_url"],
        "prompt": background_prompt,
        "target_width": target_width,
        "target_height": target_height,
    }

    try:
        result = await asyncio.wait_for(
            queue_strategy.execute_fast(model_id, fal_args),
            timeout=120,
        )
    except asyncio.TimeoutError:
        logger.error("Outpainting resize timed out")
        return [
            TextContent(
                type="text",
                text="❌ Resize (extend mode) timed out after 120 seconds. Try 'crop' or 'letterbox' mode instead.",
            )
        ]
    except Exception as e:
        logger.exception("Outpainting resize failed: %s", e)
        return [
            TextContent(
                type="text",
                text=f"❌ Resize (extend mode) failed: {e}",
            )
        ]

    # Check for error in response
    if "error" in result:
        error_msg = result.get("error", "Unknown error")
        logger.error("Outpainting resize failed: %s", error_msg)
        return [
            TextContent(
                type="text",
                text=f"❌ Resize failed: {error_msg}. Try 'crop' or 'letterbox' mode instead.",
            )
        ]

    # Extract the result image URL
    image_data = result.get("image", {})
    if isinstance(image_data, dict):
        output_url = image_data.get("url")
    else:
        output_url = result.get("image_url")

    # Try images array as fallback
    if not output_url:
        images = result.get("images", [])
        if images:
            output_url = (
                images[0].get("url") if isinstance(images[0], dict) else images[0]
            )

    if not output_url:
        logger.warning("Outpainting resize returned no image. Result: %s", result)
        return [
            TextContent(
                type="text",
                text="❌ Resize completed but no image was returned.",
            )
        ]

    response = f"📐 Image resized to {format_label}!\n\n"
    response += "**Mode**: AI Extend (outpainting)\n"
    response += f"**Result**: {output_url}"
    return [TextContent(type="text", text=response)]


async def _resize_with_crop(
    arguments: Dict[str, Any],
    target_width: int,
    target_height: int,
    format_label: str,
    registry: ModelRegistry,
    queue_strategy: QueueStrategy,
) -> List[TextContent]:
    """Resize image using smart cropping."""
    # Log usage of unimplemented feature for prioritization
    logger.warning(
        "User requested unimplemented crop mode. format=%s, dimensions=%dx%d",
        format_label,
        target_width,
        target_height,
    )

    return [
        TextContent(
            type="text",
            text=f"⚠️ Smart crop mode is not yet implemented.\n\n"
            f"**Workaround**: Use 'extend' mode to resize to {format_label}, "
            f"or manually crop the image using an image editor.\n\n"
            f"Coming soon: AI-powered smart cropping with face/subject detection.",
        )
    ]


async def _resize_with_letterbox(
    arguments: Dict[str, Any],
    target_width: int,
    target_height: int,
    format_label: str,
    registry: ModelRegistry,
    queue_strategy: QueueStrategy,
) -> List[TextContent]:
    """Resize image by adding letterbox bars."""
    background_color = arguments.get("background_color", "#000000")

    # Log usage of unimplemented feature for prioritization
    logger.warning(
        "User requested unimplemented letterbox mode. format=%s, dimensions=%dx%d, color=%s",
        format_label,
        target_width,
        target_height,
        background_color,
    )

    return [
        TextContent(
            type="text",
            text=f"⚠️ Letterbox mode is not yet implemented.\n\n"
            f"**Workaround**: Use 'extend' mode to resize to {format_label}, "
            f"or use an image editor to add {background_color} bars.\n\n"
            f"Coming soon: Letterbox resizing with custom background colors.",
        )
    ]
