"""
Video tool definitions for Fal.ai MCP Server.

Contains: generate_video, generate_video_from_image
"""

from typing import List

from mcp.types import Tool

VIDEO_TOOLS: List[Tool] = [
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
]
