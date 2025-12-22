"""
Video tool definitions for Fal.ai MCP Server.

Contains: generate_video, generate_video_from_image, generate_video_from_video
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
    Tool(
        name="generate_video_from_video",
        description="Transform an existing video using AI. Supports restyling (Lucy models) and motion transfer (Kling motion control). Use upload_file first if you have a local video.",
        inputSchema={
            "type": "object",
            "properties": {
                "video_url": {
                    "type": "string",
                    "description": "URL of the source video to transform (use upload_file for local videos)",
                },
                "prompt": {
                    "type": "string",
                    "description": "Text description of the transformation (e.g., 'transform into anime style', 'a woman dancing gracefully')",
                },
                "model": {
                    "type": "string",
                    "default": "decart/lucy-edit/dev",
                    "description": "Video-to-video model. Options: decart/lucy-edit/dev (restyle), decart/lucy-edit/pro, decart/lucy-restyle, fal-ai/kling-video/v2.6/standard/motion-control (motion transfer), fal-ai/kling-video/v2.6/pro/motion-control",
                },
                "duration": {
                    "type": "integer",
                    "enum": [5, 10],
                    "default": 5,
                    "description": "Duration of generated video in seconds",
                },
                "aspect_ratio": {
                    "type": "string",
                    "enum": ["16:9", "9:16", "1:1"],
                    "default": "16:9",
                    "description": "Aspect ratio of the generated video",
                },
                "cfg_scale": {
                    "type": "number",
                    "default": 0.5,
                    "description": "Classifier Free Guidance scale - how closely to follow the prompt (0.0-1.0)",
                },
                "image_url": {
                    "type": "string",
                    "description": "[Kling motion control] Reference image URL. The character in this image will be animated using motion from video_url.",
                },
                "character_orientation": {
                    "type": "string",
                    "enum": ["image", "video"],
                    "default": "video",
                    "description": "[Kling motion control] 'video': orientation matches reference video (max 30s). 'image': orientation matches reference image (max 10s).",
                },
                "keep_original_sound": {
                    "type": "boolean",
                    "default": True,
                    "description": "[Kling motion control] Whether to keep original sound from reference video.",
                },
                "tail_image_url": {
                    "type": "string",
                    "description": "[Kling Pro] URL of image for the end of the video (for transitions).",
                },
                "generate_audio": {
                    "type": "boolean",
                    "default": True,
                    "description": "[Kling v2.6 Pro] Generate native audio for video (supports Chinese/English).",
                },
                "negative_prompt": {
                    "type": "string",
                    "description": "What to avoid in the output (default: 'blur, distort, and low quality')",
                },
                "strength": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "default": 0.75,
                    "description": "[Lucy models] How much to transform (0=keep original, 1=full transformation)",
                },
                "num_frames": {
                    "type": "integer",
                    "description": "[Lucy models] Number of frames to process",
                },
            },
            "required": ["video_url", "prompt"],
        },
    ),
]
