#!/usr/bin/env python3
"""Fal.ai MCP Server with native async API and queue support"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List

# Fal client
import fal_client
import httpx
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
            name="get_pricing",
            description="Get pricing information for Fal.ai models. Returns cost per unit (image/video/second) in USD. Use this to check costs before generating content.",
            inputSchema={
                "type": "object",
                "properties": {
                    "models": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Model IDs or aliases to get pricing for (e.g., ['flux_schnell', 'fal-ai/kling-video'])",
                        "minItems": 1,
                        "maxItems": 50,
                    },
                },
                "required": ["models"],
            },
        ),
        Tool(
            name="get_usage",
            description="Get usage and spending history for your Fal.ai workspace. Shows quantity, cost, and breakdown by model. Requires admin API key.",
            inputSchema={
                "type": "object",
                "properties": {
                    "start": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD format). Defaults to 7 days ago.",
                    },
                    "end": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD format). Defaults to today.",
                    },
                    "models": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by specific model IDs/aliases (optional)",
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
                    "enable_safety_checker": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable safety checker to filter inappropriate content",
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["jpeg", "png", "webp"],
                        "default": "png",
                        "description": "Output image format",
                    },
                },
                "required": ["prompt"],
            },
        ),
        Tool(
            name="generate_image_structured",
            description="Generate images with detailed structured prompts for precise control over composition, style, lighting, and subjects. Ideal for AI agents that need fine-grained control.",
            inputSchema={
                "type": "object",
                "properties": {
                    "scene": {
                        "type": "string",
                        "description": "Overall scene description - the main subject and setting",
                    },
                    "subjects": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "description": "Type of subject (e.g., 'person', 'building', 'animal')",
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Detailed description of the subject",
                                },
                                "pose": {
                                    "type": "string",
                                    "description": "Pose or action of the subject",
                                },
                                "position": {
                                    "type": "string",
                                    "enum": ["foreground", "midground", "background"],
                                    "description": "Position in the composition",
                                },
                            },
                        },
                        "description": "List of subjects with their positions and descriptions",
                    },
                    "style": {
                        "type": "string",
                        "description": "Art style (e.g., 'Digital art painting', 'Photorealistic', 'Watercolor', 'Oil painting')",
                    },
                    "color_palette": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Hex color codes for the palette (e.g., ['#000033', '#6A0DAD', '#FFFFFF'])",
                    },
                    "lighting": {
                        "type": "string",
                        "description": "Lighting description (e.g., 'Soft golden hour lighting', 'Dramatic chiaroscuro')",
                    },
                    "mood": {
                        "type": "string",
                        "description": "Emotional mood of the image (e.g., 'Serene', 'Dramatic', 'Mysterious')",
                    },
                    "background": {
                        "type": "string",
                        "description": "Background description",
                    },
                    "composition": {
                        "type": "string",
                        "description": "Compositional rules (e.g., 'Rule of thirds', 'Centered', 'Golden ratio')",
                    },
                    "camera": {
                        "type": "object",
                        "properties": {
                            "angle": {
                                "type": "string",
                                "description": "Camera angle (e.g., 'Low angle', 'Eye level', 'Bird's eye')",
                            },
                            "distance": {
                                "type": "string",
                                "description": "Shot distance (e.g., 'Close-up', 'Medium shot', 'Wide shot')",
                            },
                            "focus": {
                                "type": "string",
                                "description": "Focus description (e.g., 'Sharp focus on subject, blurred background')",
                            },
                            "lens": {
                                "type": "string",
                                "description": "Lens type (e.g., 'Wide-angle', '50mm portrait', 'Telephoto')",
                            },
                            "f_number": {
                                "type": "string",
                                "description": "Aperture (e.g., 'f/1.8', 'f/5.6', 'f/11')",
                            },
                            "iso": {
                                "type": "integer",
                                "description": "ISO setting (e.g., 100, 400, 800)",
                            },
                        },
                        "description": "Camera settings for photographic style control",
                    },
                    "effects": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Visual effects (e.g., ['Bokeh', 'Light rays', 'Lens flare', 'Motion blur'])",
                    },
                    "negative_prompt": {
                        "type": "string",
                        "description": "What to avoid in the image (e.g., 'blurry, low quality, distorted')",
                    },
                    "model": {
                        "type": "string",
                        "default": "flux_schnell",
                        "description": "Model ID or alias. Use list_models to see options.",
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
                    "enable_safety_checker": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable safety checker to filter inappropriate content",
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["jpeg", "png", "webp"],
                        "default": "png",
                        "description": "Output image format",
                    },
                },
                "required": ["scene"],
            },
        ),
        Tool(
            name="generate_image_from_image",
            description="Transform an existing image into a new image based on a prompt. Use for style transfer, editing, variations, and more. Use upload_file first if you have a local image.",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_url": {
                        "type": "string",
                        "description": "URL of the source image to transform (use upload_file for local images)",
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Text description of desired transformation (e.g., 'Transform into a watercolor painting')",
                    },
                    "model": {
                        "type": "string",
                        "default": "fal-ai/flux/dev/image-to-image",
                        "description": "Image-to-image model. Options: fal-ai/flux/dev/image-to-image, fal-ai/flux-2/edit",
                    },
                    "strength": {
                        "type": "number",
                        "default": 0.75,
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "How much to transform (0=keep original, 1=ignore original)",
                    },
                    "num_images": {
                        "type": "integer",
                        "default": 1,
                        "minimum": 1,
                        "maximum": 4,
                    },
                    "negative_prompt": {
                        "type": "string",
                        "description": "What to avoid in the output image",
                    },
                    "seed": {
                        "type": "integer",
                        "description": "Seed for reproducible generation",
                    },
                    "enable_safety_checker": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable safety checker to filter inappropriate content",
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["jpeg", "png", "webp"],
                        "default": "png",
                        "description": "Output image format",
                    },
                },
                "required": ["image_url", "prompt"],
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

        # Get pricing for models
        elif name == "get_pricing":
            model_inputs = arguments.get("models", [])
            if not model_inputs:
                return [
                    TextContent(
                        type="text",
                        text="❌ No models specified. Provide a list of model IDs or aliases.",
                    )
                ]

            # Resolve all model inputs to endpoint IDs
            endpoint_ids = []
            failed_models = []
            for model_input in model_inputs:
                try:
                    endpoint_id = await registry.resolve_model_id(model_input)
                    endpoint_ids.append(endpoint_id)
                except ValueError:
                    failed_models.append(model_input)

            if failed_models:
                return [
                    TextContent(
                        type="text",
                        text=f"❌ Unknown model(s): {', '.join(failed_models)}. Use list_models to see available options.",
                    )
                ]

            # Fetch pricing from API
            try:
                pricing_data = await registry.get_pricing(endpoint_ids)
            except httpx.HTTPStatusError as e:
                logger.error(
                    "Pricing API returned HTTP %d for %s: %s",
                    e.response.status_code,
                    endpoint_ids,
                    e,
                )
                return [
                    TextContent(
                        type="text",
                        text=f"❌ Pricing API error (HTTP {e.response.status_code})",
                    )
                ]
            except httpx.TimeoutException:
                logger.error("Pricing API timeout for %s", endpoint_ids)
                return [
                    TextContent(
                        type="text",
                        text="❌ Pricing request timed out. Please try again.",
                    )
                ]
            except httpx.ConnectError as e:
                logger.error("Cannot connect to pricing API: %s", e)
                return [
                    TextContent(
                        type="text",
                        text="❌ Cannot connect to Fal.ai API. Check your network connection.",
                    )
                ]

            prices = pricing_data.get("prices", [])
            if not prices:
                return [
                    TextContent(
                        type="text",
                        text="No pricing information available for the specified models.",
                    )
                ]

            # Format output
            lines = ["💰 **Pricing Information**\n"]
            for price_info in prices:
                endpoint_id = price_info.get("endpoint_id", "Unknown")
                unit_price = price_info.get("unit_price", 0)
                unit = price_info.get("unit", "request")
                currency = price_info.get("currency", "USD")

                # Format price with currency symbol
                if currency == "USD":
                    price_str = f"${unit_price:.4f}".rstrip("0").rstrip(".")
                    if unit_price < 0.01 and unit_price > 0:
                        price_str = f"${unit_price:.4f}"
                else:
                    price_str = f"{unit_price} {currency}"

                lines.append(f"- **{endpoint_id}**: {price_str}/{unit}")

            return [TextContent(type="text", text="\n".join(lines))]

        # Get usage/spending history
        elif name == "get_usage":
            # Get date parameters (default to last 7 days)
            end_date = arguments.get("end")
            start_date = arguments.get("start")

            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if not start_date:
                start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

            # Resolve model filters if provided
            endpoint_ids = None
            model_inputs = arguments.get("models", [])
            if model_inputs:
                endpoint_ids = []
                failed_models = []
                for model_input in model_inputs:
                    try:
                        endpoint_id = await registry.resolve_model_id(model_input)
                        endpoint_ids.append(endpoint_id)
                    except ValueError:
                        failed_models.append(model_input)

                if failed_models:
                    return [
                        TextContent(
                            type="text",
                            text=f"❌ Unknown model(s): {', '.join(failed_models)}. Use list_models to see available options.",
                        )
                    ]

            # Fetch usage from API
            try:
                usage_data = await registry.get_usage(
                    start=start_date,
                    end=end_date,
                    endpoint_ids=endpoint_ids,
                )
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    logger.error("Usage API returned 401 - admin key may be required")
                    return [
                        TextContent(
                            type="text",
                            text=(
                                "❌ Unauthorized. This could mean:\n"
                                "- Your FAL_KEY may be expired or invalid\n"
                                "- The get_usage tool requires an admin API key with billing permissions\n"
                                "Please verify your API key configuration."
                            ),
                        )
                    ]
                logger.error(
                    "Usage API returned HTTP %d: %s",
                    e.response.status_code,
                    e,
                )
                return [
                    TextContent(
                        type="text",
                        text=f"❌ Usage API error (HTTP {e.response.status_code})",
                    )
                ]
            except httpx.TimeoutException:
                logger.error("Usage API timeout")
                return [
                    TextContent(
                        type="text",
                        text="❌ Usage request timed out. Please try again.",
                    )
                ]
            except httpx.ConnectError as e:
                logger.error("Cannot connect to usage API: %s", e)
                return [
                    TextContent(
                        type="text",
                        text="❌ Cannot connect to Fal.ai API. Check your network connection.",
                    )
                ]

            # Extract summary data
            summary = usage_data.get("summary", [])
            if not summary:
                return [
                    TextContent(
                        type="text",
                        text=f"📊 No usage data found for {start_date} to {end_date}.",
                    )
                ]

            # Calculate totals and format output
            total_cost = sum(item.get("cost", 0) for item in summary)
            currency = summary[0].get("currency", "USD") if summary else "USD"

            lines = [f"📊 **Usage Summary** ({start_date} to {end_date})\n"]

            # Format total
            if currency == "USD":
                total_str = f"${total_cost:.2f}"
            else:
                total_str = f"{total_cost:.2f} {currency}"
            lines.append(f"**Total**: {total_str}\n")

            # Format by model
            lines.append("**By Model**:")
            for item in sorted(summary, key=lambda x: x.get("cost", 0), reverse=True):
                endpoint_id = item.get("endpoint_id", "Unknown")
                quantity = item.get("quantity", 0)
                unit = item.get("unit", "request")
                cost = item.get("cost", 0)

                if currency == "USD":
                    cost_str = f"${cost:.2f}"
                else:
                    cost_str = f"{cost:.2f} {currency}"

                lines.append(f"- {endpoint_id}: {quantity} {unit}s = {cost_str}")

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
            if "enable_safety_checker" in arguments:
                fal_args["enable_safety_checker"] = arguments["enable_safety_checker"]
            if "output_format" in arguments:
                fal_args["output_format"] = arguments["output_format"]

            # Use native async API for fast image generation
            result = await fal_client.run_async(model_id, arguments=fal_args)

            images = result.get("images", [])
            if images:
                urls = [img["url"] for img in images]
                response = f"🎨 Generated {len(urls)} image(s) with {model_id}:\n\n"
                for i, url in enumerate(urls, 1):
                    response += f"Image {i}: {url}\n"
                return [TextContent(type="text", text=response)]

        # Structured image generation with JSON prompt
        elif name == "generate_image_structured":
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

            # Build structured JSON prompt from arguments
            structured_prompt: Dict[str, Any] = {}

            # Required field
            structured_prompt["scene"] = arguments["scene"]

            # Optional structured fields
            if "subjects" in arguments:
                structured_prompt["subjects"] = arguments["subjects"]
            if "style" in arguments:
                structured_prompt["style"] = arguments["style"]
            if "color_palette" in arguments:
                structured_prompt["color_palette"] = arguments["color_palette"]
            if "lighting" in arguments:
                structured_prompt["lighting"] = arguments["lighting"]
            if "mood" in arguments:
                structured_prompt["mood"] = arguments["mood"]
            if "background" in arguments:
                structured_prompt["background"] = arguments["background"]
            if "composition" in arguments:
                structured_prompt["composition"] = arguments["composition"]
            if "camera" in arguments:
                structured_prompt["camera"] = arguments["camera"]
            if "effects" in arguments:
                structured_prompt["effects"] = arguments["effects"]

            # Convert structured prompt to JSON string
            json_prompt = json.dumps(structured_prompt, indent=2)

            fal_args = {
                "prompt": json_prompt,
                "image_size": arguments.get("image_size", "landscape_16_9"),
                "num_images": arguments.get("num_images", 1),
            }

            # Add optional generation parameters
            if "negative_prompt" in arguments:
                fal_args["negative_prompt"] = arguments["negative_prompt"]
            if "seed" in arguments:
                fal_args["seed"] = arguments["seed"]
            if "enable_safety_checker" in arguments:
                fal_args["enable_safety_checker"] = arguments["enable_safety_checker"]
            if "output_format" in arguments:
                fal_args["output_format"] = arguments["output_format"]

            # Use native async API for fast image generation with timeout protection
            logger.info("Starting structured image generation with %s", model_id)
            try:
                result = await asyncio.wait_for(
                    fal_client.run_async(model_id, arguments=fal_args),
                    timeout=60,  # 1 minute timeout for image generation
                )
            except asyncio.TimeoutError:
                logger.error("Structured image generation timed out for %s", model_id)
                return [
                    TextContent(
                        type="text",
                        text=f"❌ Image generation timed out after 60 seconds with {model_id}. Please try again.",
                    )
                ]

            # Check for error in response (consistent with generate_video/generate_music)
            if "error" in result:
                error_msg = result.get("error", "Unknown error")
                logger.error(
                    "Structured image generation failed for %s: %s", model_id, error_msg
                )
                return [
                    TextContent(
                        type="text",
                        text=f"❌ Image generation failed: {error_msg}",
                    )
                ]

            images = result.get("images", [])
            if not images:
                logger.warning(
                    "Structured image generation returned no images. Model: %s",
                    model_id,
                )
                return [
                    TextContent(
                        type="text",
                        text=f"❌ No images were generated by {model_id}. The prompt may have been filtered or the request format was invalid.",
                    )
                ]

            # Extract URLs safely
            try:
                urls = [img["url"] for img in images]
            except (KeyError, TypeError) as e:
                logger.error("Malformed image response from %s: %s", model_id, e)
                return [
                    TextContent(
                        type="text",
                        text=f"❌ Image generation completed but response was malformed: {e}",
                    )
                ]

            response = f"🎨 Generated {len(urls)} image(s) with {model_id} (structured prompt):\n\n"
            for i, url in enumerate(urls, 1):
                response += f"Image {i}: {url}\n"
            return [TextContent(type="text", text=response)]

        # Image-to-image transformation
        elif name == "generate_image_from_image":
            model_input = arguments.get("model", "fal-ai/flux/dev/image-to-image")
            try:
                model_id = await registry.resolve_model_id(model_input)
            except ValueError as e:
                return [
                    TextContent(
                        type="text",
                        text=f"❌ {e}. Use list_models to see available options.",
                    )
                ]

            # Both image_url and prompt are required
            img2img_args: Dict[str, Any] = {
                "image_url": arguments["image_url"],
                "prompt": arguments["prompt"],
                "strength": arguments.get("strength", 0.75),
                "num_images": arguments.get("num_images", 1),
            }

            # Add optional parameters
            if "negative_prompt" in arguments:
                img2img_args["negative_prompt"] = arguments["negative_prompt"]
            if "seed" in arguments:
                img2img_args["seed"] = arguments["seed"]
            if "enable_safety_checker" in arguments:
                img2img_args["enable_safety_checker"] = arguments[
                    "enable_safety_checker"
                ]
            if "output_format" in arguments:
                img2img_args["output_format"] = arguments["output_format"]

            logger.info(
                "Starting image-to-image transformation with %s from %s",
                model_id,
                (
                    arguments["image_url"][:50] + "..."
                    if len(arguments["image_url"]) > 50
                    else arguments["image_url"]
                ),
            )

            # Use async API with timeout protection for fast image transformation
            try:
                result = await asyncio.wait_for(
                    fal_client.run_async(model_id, arguments=img2img_args),
                    timeout=60,
                )
            except asyncio.TimeoutError:
                logger.error(
                    "Image-to-image transformation timed out after 60s. Model: %s",
                    model_id,
                )
                return [
                    TextContent(
                        type="text",
                        text=f"❌ Image transformation timed out after 60 seconds with {model_id}. Please try again.",
                    )
                ]
            except Exception as e:
                logger.exception("Image-to-image transformation failed: %s", e)
                return [
                    TextContent(
                        type="text",
                        text=f"❌ Image transformation failed: {e}",
                    )
                ]

            # Check for error in response
            if "error" in result:
                error_msg = result.get("error", "Unknown error")
                logger.error(
                    "Image-to-image transformation failed for %s: %s",
                    model_id,
                    error_msg,
                )
                return [
                    TextContent(
                        type="text",
                        text=f"❌ Image transformation failed: {error_msg}",
                    )
                ]

            images = result.get("images", [])
            if not images:
                logger.error(
                    "Image-to-image transformation returned no images. Response: %s",
                    result,
                )
                return [
                    TextContent(
                        type="text",
                        text="❌ Image transformation completed but no images were returned. Please try again.",
                    )
                ]

            # Extract URLs safely
            try:
                urls = [img["url"] for img in images]
            except (KeyError, TypeError) as e:
                logger.error("Malformed image response from %s: %s", model_id, e)
                return [
                    TextContent(
                        type="text",
                        text=f"❌ Image transformation completed but response was malformed: {e}",
                    )
                ]

            logger.info("Successfully transformed image with %s: %s", model_id, urls[0])
            response = f"🎨 Transformed image with {model_id} (strength={img2img_args['strength']}):\n\n"
            for i, url in enumerate(urls, 1):
                response += f"Image {i}: {url}\n"
            return [TextContent(type="text", text=response)]

        # Long operations using subscribe_async (handles queue automatically)
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

            # Use subscribe_async with timeout protection
            logger.info("Starting video generation with %s", model_id)
            try:
                video_result = await asyncio.wait_for(
                    fal_client.subscribe_async(
                        model_id,
                        arguments=fal_args,
                        with_logs=True,
                    ),
                    timeout=180,  # 3 minute timeout for video generation
                )
            except asyncio.TimeoutError:
                return [
                    TextContent(
                        type="text",
                        text=f"❌ Video generation timed out after 180 seconds with {model_id}",
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
            if "duration" in arguments:
                fal_args["duration"] = arguments["duration"]
            if "aspect_ratio" in arguments:
                fal_args["aspect_ratio"] = arguments["aspect_ratio"]
            if "negative_prompt" in arguments:
                fal_args["negative_prompt"] = arguments["negative_prompt"]
            if "cfg_scale" in arguments:
                fal_args["cfg_scale"] = arguments["cfg_scale"]

            # Use subscribe_async with timeout protection
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
                    fal_client.subscribe_async(
                        model_id,
                        arguments=fal_args,
                        with_logs=True,
                    ),
                    timeout=180,  # 3 minute timeout for video generation
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
                logger.info("Successfully generated video from image: %s", video_url)
                return [
                    TextContent(
                        type="text",
                        text=f"🎬 Video generated from image with {model_id}: {video_url}",
                    )
                ]
            else:
                logger.error(
                    "Image-to-video generation returned no URL. Response: %s",
                    video_result,
                )
                return [
                    TextContent(
                        type="text",
                        text="❌ Video generation completed but no video URL was returned. Please try again.",
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

            duration = arguments.get("duration_seconds", 30)

            # Use subscribe_async with timeout protection
            logger.info("Starting music generation with %s (%ds)", model_id, duration)
            try:
                music_result = await asyncio.wait_for(
                    fal_client.subscribe_async(
                        model_id,
                        arguments={
                            "prompt": arguments["prompt"],
                            "duration_seconds": duration,
                        },
                        with_logs=True,
                    ),
                    timeout=120,  # 2 minute timeout for music generation
                )
            except asyncio.TimeoutError:
                return [
                    TextContent(
                        type="text",
                        text=f"❌ Music generation timed out after 120 seconds with {model_id}",
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
                        text=f"🎵 Generated {duration}s of music with {model_id}: {audio_url}",
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
            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code
                if status_code == 401:
                    logger.error("Upload failed with 401 - API key may be invalid")
                    return [
                        TextContent(
                            type="text",
                            text="❌ Upload failed: Invalid API key. Check your FAL_KEY.",
                        )
                    ]
                elif status_code == 413:
                    logger.error("File too large for upload: %s", file_path)
                    return [
                        TextContent(
                            type="text",
                            text=f"❌ File too large ({file_size_mb:.2f} MB). Try a smaller file.",
                        )
                    ]
                else:
                    logger.error("Upload API returned HTTP %d: %s", status_code, e)
                    return [
                        TextContent(
                            type="text",
                            text=f"❌ Upload failed (HTTP {status_code})",
                        )
                    ]
            except httpx.TimeoutException:
                logger.error("File upload timed out: %s", file_path)
                return [
                    TextContent(
                        type="text",
                        text="❌ Upload timed out. Please try again.",
                    )
                ]
            except httpx.ConnectError as e:
                logger.error("Cannot connect to upload service: %s", e)
                return [
                    TextContent(
                        type="text",
                        text="❌ Cannot connect to Fal.ai. Check your internet connection.",
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
