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
                    description="Discover available Fal.ai models for image, video, and audio generation. Use 'task' parameter for intelligent task-based ranking (e.g., 'portrait photography'), or 'search' for simple name/description filtering.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "enum": ["image", "video", "audio"],
                                "description": "Filter by category (image, video, or audio)",
                            },
                            "task": {
                                "type": "string",
                                "description": "Task description for intelligent ranking (e.g., 'anime illustration', 'product photography'). Uses Fal.ai's semantic search and prioritizes featured models.",
                            },
                            "search": {
                                "type": "string",
                                "description": "Simple search query to filter models by name or description (e.g., 'flux'). Use 'task' for better semantic matching.",
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
                    name="recommend_model",
                    description="Get AI-powered model recommendations for a specific task. Describe what you want to do (e.g., 'generate portrait photo', 'anime style illustration', 'product photography') and get the best-suited models ranked by relevance. Featured models by Fal.ai are prioritized.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task": {
                                "type": "string",
                                "description": "Description of your task (e.g., 'generate professional headshot', 'create anime character', 'transform photo to watercolor')",
                            },
                            "category": {
                                "type": "string",
                                "enum": ["image", "video", "audio"],
                                "description": "Optional category hint to narrow search",
                            },
                            "limit": {
                                "type": "integer",
                                "default": 5,
                                "minimum": 1,
                                "maximum": 10,
                                "description": "Maximum number of recommendations",
                            },
                        },
                        "required": ["task"],
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

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Execute a Fal.ai tool"""

            try:
                # Get the model registry
                registry = await get_registry()

                # List models tool
                if name == "list_models":
                    task = arguments.get("task")
                    category = arguments.get("category")
                    search = arguments.get("search")
                    limit = arguments.get("limit", 20)

                    used_fallback = False
                    fallback_warning = ""

                    # If task is provided, use semantic search with API
                    if task:
                        # Map simplified category to API category for search
                        api_category = None
                        if category:
                            category_map = {
                                "image": "text-to-image",
                                "video": "text-to-video",
                                "audio": "text-to-audio",
                            }
                            api_category = category_map.get(category)

                        search_result = await registry.search_models(
                            query=task, category=api_category, limit=limit
                        )
                        models = search_result.models
                        used_fallback = search_result.used_fallback

                        if used_fallback:
                            title = f'## Models for: "{task}" ({len(models)} found)\n'
                            fallback_warning = f"⚠️ *Using cached results ({search_result.fallback_reason}). Results may be less relevant.*\n"
                            subtitle = "💡 *⭐ = Featured by Fal.ai*\n"
                        else:
                            title = f'## Models for: "{task}" ({len(models)} found)\n'
                            subtitle = (
                                "💡 *Sorted by relevance. ⭐ = Featured by Fal.ai*\n"
                            )
                    else:
                        # Standard list with optional search filter
                        models = await registry.list_models(
                            category=category, search=search, limit=limit
                        )
                        title = f"## Available Models ({len(models)} found)\n"
                        subtitle = ""

                    if not models:
                        return [
                            TextContent(
                                type="text",
                                text="No models found. Try a different category, task, or search term.",
                            )
                        ]

                    # Format output
                    lines = [title]
                    if fallback_warning:
                        lines.append(fallback_warning)
                    if subtitle:
                        lines.append(subtitle)

                    for model in models:
                        # Add star badge for highlighted models
                        highlighted_badge = " ⭐" if model.highlighted else ""
                        lines.append(f"- `{model.id}`{highlighted_badge}")
                        if model.name and model.name != model.id:
                            lines.append(f"  - **{model.name}**")
                        if model.description:
                            desc = (
                                model.description[:150] + "..."
                                if len(model.description) > 150
                                else model.description
                            )
                            lines.append(f"  - {desc}")
                        if task and model.group_label:
                            lines.append(f"  - *Family: {model.group_label}*")

                    return [TextContent(type="text", text="\n".join(lines))]

                # Recommend models for a task
                elif name == "recommend_model":
                    task = arguments.get("task")
                    if not task:
                        return [
                            TextContent(
                                type="text",
                                text="❌ Please describe your task (e.g., 'generate professional headshot').",
                            )
                        ]

                    category = arguments.get("category")
                    limit = arguments.get("limit", 5)

                    result = await registry.recommend_models(
                        task=task, category=category, limit=limit
                    )
                    recommendations = result.recommendations

                    if not recommendations:
                        return [
                            TextContent(
                                type="text",
                                text=f"No models found for task: '{task}'. Try a different description or remove the category filter.",
                            )
                        ]

                    # Format output
                    lines = [f'## 🎯 Recommended Models for: "{task}"\n']

                    # Add fallback warning if API search failed
                    if result.used_fallback:
                        lines.append(
                            f"⚠️ *Using cached results ({result.fallback_reason}). Results may be less relevant.*\n"
                        )

                    for i, rec in enumerate(recommendations, 1):
                        highlighted_badge = " ⭐" if rec.get("highlighted") else ""
                        lines.append(f"### {i}. `{rec['model_id']}`{highlighted_badge}")
                        if rec.get("name"):
                            lines.append(f"**{rec['name']}**")
                        if rec.get("description"):
                            desc = (
                                rec["description"][:200] + "..."
                                if len(rec["description"]) > 200
                                else rec["description"]
                            )
                            lines.append(f"{desc}")
                        lines.append(
                            f"- **Category**: {rec.get('category', 'Unknown')}"
                        )
                        if rec.get("group"):
                            lines.append(f"- **Family**: {rec['group']}")
                        lines.append(
                            f"- **Why**: {rec.get('reason', 'Matches your search')}"
                        )
                        lines.append("")

                    lines.append(
                        "\n💡 **Tip**: Use the model_id with generate_image, generate_video, or generate_music tools."
                    )

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

                # Image-to-image transformation (fast operation)
                elif name == "generate_image_from_image":
                    model_input = arguments.get(
                        "model", "fal-ai/flux/dev/image-to-image"
                    )
                    try:
                        model_id = await registry.resolve_model_id(model_input)
                    except ValueError as e:
                        return [
                            TextContent(
                                type="text",
                                text=f"❌ {e}. Use list_models to see available options.",
                            )
                        ]

                    # Build arguments for img2img
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

                    try:
                        # Use native async API with timeout protection
                        result = await asyncio.wait_for(
                            fal_client.run_async(model_id, arguments=img2img_args),
                            timeout=60,
                        )

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
                        if images:
                            try:
                                urls = [img["url"] for img in images]
                            except (KeyError, TypeError) as e:
                                logger.error(
                                    "Malformed image response from %s: %s", model_id, e
                                )
                                return [
                                    TextContent(
                                        type="text",
                                        text=f"❌ Image transformation completed but response was malformed: {e}",
                                    )
                                ]
                            logger.info(
                                "Successfully transformed image with %s: %s",
                                model_id,
                                urls[0],
                            )
                            response = f"🎨 Transformed image with {model_id}:\n\n"
                            for i, url in enumerate(urls, 1):
                                response += f"Image {i}: {url}\n"
                            return [TextContent(type="text", text=response)]
                        else:
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
                    except Exception as img2img_error:
                        logger.exception(
                            "Image-to-image transformation failed: %s", img2img_error
                        )
                        return [
                            TextContent(
                                type="text",
                                text=f"❌ Image transformation failed: {str(img2img_error)}",
                            )
                        ]

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
                        logger.info(
                            "Uploading file: %s (%.2f MB)", file_path, file_size_mb
                        )

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
                        handle.request_id
                        if hasattr(handle, "request_id")
                        else str(handle)
                    )

                    # Wait for completion with timeout protection
                    response = f"⏳ Image-to-video generation queued (ID: {request_id[:8]}...)\n"
                    response += "Processing (this may take 30-60 seconds)...\n"

                    try:
                        result = await asyncio.wait_for(handle.get(), timeout=180)
                    except asyncio.TimeoutError:
                        logger.error(
                            "Image-to-video generation timed out after 180s. Model: %s",
                            model_id,
                        )
                        return [
                            TextContent(
                                type="text",
                                text=f"❌ Video generation timed out after 180 seconds with {model_id}",
                            )
                        ]

                    if result:
                        # Check for error in response
                        if "error" in result:
                            error_msg = result.get("error", "Unknown error")
                            return [
                                TextContent(
                                    type="text",
                                    text=f"❌ Image-to-video generation failed: {error_msg}",
                                )
                            ]

                        # Extract video URL with isinstance check
                        video_dict = result.get("video", {})
                        if isinstance(video_dict, dict):
                            video_url = video_dict.get("url")
                        else:
                            video_url = result.get("url")

                        if video_url:
                            logger.info("Successfully generated video: %s", video_url)
                            return [
                                TextContent(
                                    type="text",
                                    text=f"🎬 Video generated with {model_id}: {video_url}",
                                )
                            ]
                        else:
                            logger.error(
                                "Image-to-video generation returned no URL. Response: %s",
                                result,
                            )
                            return [
                                TextContent(
                                    type="text",
                                    text="❌ Video generation completed but no video URL was returned. Please try again.",
                                )
                            ]
                    else:
                        logger.error("Image-to-video generation returned empty result")
                        return [
                            TextContent(
                                type="text",
                                text="❌ Video generation failed with no response. Please try again.",
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
