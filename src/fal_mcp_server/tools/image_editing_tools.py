"""
Image editing tool definitions for Fal.ai MCP Server.

Contains: remove_background, upscale_image, edit_image, inpaint_image, resize_image
"""

from typing import List

from mcp.types import Tool

# Social media format presets with dimensions
SOCIAL_MEDIA_FORMATS = {
    "instagram_post": {"width": 1080, "height": 1080, "aspect": "1:1"},
    "instagram_story": {"width": 1080, "height": 1920, "aspect": "9:16"},
    "instagram_reel": {"width": 1080, "height": 1920, "aspect": "9:16"},
    "youtube_thumbnail": {"width": 1280, "height": 720, "aspect": "16:9"},
    "youtube_short": {"width": 1080, "height": 1920, "aspect": "9:16"},
    "twitter_post": {"width": 1200, "height": 675, "aspect": "16:9"},
    "twitter_header": {"width": 1500, "height": 500, "aspect": "3:1"},
    "linkedin_post": {"width": 1200, "height": 627, "aspect": "1.91:1"},
    "linkedin_banner": {"width": 1584, "height": 396, "aspect": "4:1"},
    "facebook_post": {"width": 1200, "height": 630, "aspect": "1.91:1"},
    "facebook_cover": {"width": 820, "height": 312, "aspect": "2.63:1"},
    "pinterest_pin": {"width": 1000, "height": 1500, "aspect": "2:3"},
    "tiktok": {"width": 1080, "height": 1920, "aspect": "9:16"},
}

IMAGE_EDITING_TOOLS: List[Tool] = [
    Tool(
        name="remove_background",
        description="Remove the background from an image, creating a transparent PNG. Great for product photos, portraits, and creating composites.",
        inputSchema={
            "type": "object",
            "properties": {
                "image_url": {
                    "type": "string",
                    "description": "URL of the image to remove background from (use upload_file for local images)",
                },
                "model": {
                    "type": "string",
                    "default": "fal-ai/birefnet/v2",
                    "description": "Background removal model. Options: fal-ai/birefnet/v2 (recommended), fal-ai/birefnet",
                },
                "output_format": {
                    "type": "string",
                    "enum": ["png", "webp"],
                    "default": "png",
                    "description": "Output format (PNG recommended for transparency)",
                },
            },
            "required": ["image_url"],
        },
    ),
    Tool(
        name="upscale_image",
        description="Upscale an image to higher resolution while preserving quality. Use for enhancing low-resolution images.",
        inputSchema={
            "type": "object",
            "properties": {
                "image_url": {
                    "type": "string",
                    "description": "URL of the image to upscale (use upload_file for local images)",
                },
                "scale": {
                    "type": "integer",
                    "default": 2,
                    "enum": [2, 4],
                    "description": "Upscale factor (2x or 4x)",
                },
                "model": {
                    "type": "string",
                    "default": "fal-ai/clarity-upscaler",
                    "description": "Upscaling model. Options: fal-ai/clarity-upscaler (high quality), fal-ai/aura-sr (fast)",
                },
            },
            "required": ["image_url"],
        },
    ),
    Tool(
        name="edit_image",
        description="Edit an image using natural language instructions. Describe what changes you want and the AI will apply them.",
        inputSchema={
            "type": "object",
            "properties": {
                "image_url": {
                    "type": "string",
                    "description": "URL of the image to edit (use upload_file for local images)",
                },
                "instruction": {
                    "type": "string",
                    "description": "Natural language description of the edit (e.g., 'make the sky more dramatic', 'change the car color to red')",
                },
                "model": {
                    "type": "string",
                    "default": "fal-ai/flux-2/edit",
                    "description": "Editing model. Options: fal-ai/flux-2/edit, fal-ai/flux-2-pro/edit (higher quality)",
                },
                "strength": {
                    "type": "number",
                    "default": 0.75,
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "How much to change the image (0=minimal, 1=maximum)",
                },
                "seed": {
                    "type": "integer",
                    "description": "Seed for reproducible edits",
                },
            },
            "required": ["image_url", "instruction"],
        },
    ),
    Tool(
        name="inpaint_image",
        description="Edit specific regions of an image using a mask. White areas in the mask will be regenerated based on the prompt.",
        inputSchema={
            "type": "object",
            "properties": {
                "image_url": {
                    "type": "string",
                    "description": "URL of the source image (use upload_file for local images)",
                },
                "mask_url": {
                    "type": "string",
                    "description": "URL of the mask image (white=edit, black=keep). Use upload_file for local masks.",
                },
                "prompt": {
                    "type": "string",
                    "description": "What to generate in the masked area (e.g., 'a red sports car', 'green grass')",
                },
                "model": {
                    "type": "string",
                    "default": "fal-ai/flux-kontext-lora/inpaint",
                    "description": "Inpainting model. Options: fal-ai/flux-kontext-lora/inpaint, fal-ai/flux-krea-lora/inpainting",
                },
                "negative_prompt": {
                    "type": "string",
                    "description": "What to avoid in the generated area",
                },
                "seed": {
                    "type": "integer",
                    "description": "Seed for reproducible results",
                },
            },
            "required": ["image_url", "mask_url", "prompt"],
        },
    ),
    Tool(
        name="resize_image",
        description="Resize/reformat images for different platforms (like Canva Magic Resize). Uses AI outpainting to intelligently extend content for new aspect ratios. Note: 'crop' and 'letterbox' modes coming soon.",
        inputSchema={
            "type": "object",
            "properties": {
                "image_url": {
                    "type": "string",
                    "description": "URL of the source image (use upload_file for local images)",
                },
                "target_format": {
                    "type": "string",
                    "enum": [
                        "instagram_post",
                        "instagram_story",
                        "instagram_reel",
                        "youtube_thumbnail",
                        "youtube_short",
                        "twitter_post",
                        "twitter_header",
                        "linkedin_post",
                        "linkedin_banner",
                        "facebook_post",
                        "facebook_cover",
                        "pinterest_pin",
                        "tiktok",
                        "custom",
                    ],
                    "description": "Target platform format, or 'custom' to specify dimensions",
                },
                "width": {
                    "type": "integer",
                    "minimum": 64,
                    "maximum": 4096,
                    "description": "Custom width in pixels (required if target_format='custom')",
                },
                "height": {
                    "type": "integer",
                    "minimum": 64,
                    "maximum": 4096,
                    "description": "Custom height in pixels (required if target_format='custom')",
                },
                "mode": {
                    "type": "string",
                    "enum": ["extend", "crop", "letterbox"],
                    "default": "extend",
                    "description": "How to handle aspect ratio change: extend (AI outpainting - recommended), crop (coming soon), letterbox (coming soon)",
                },
                "background_prompt": {
                    "type": "string",
                    "description": "For 'extend' mode: prompt to guide AI-generated extended areas (e.g., 'continue the beach scenery')",
                },
                "background_color": {
                    "type": "string",
                    "default": "#000000",
                    "description": "For 'letterbox' mode: hex color for bars (e.g., '#FFFFFF' for white)",
                },
            },
            "required": ["image_url", "target_format"],
        },
    ),
]
