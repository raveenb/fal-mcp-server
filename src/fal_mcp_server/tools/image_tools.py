"""
Image tool definitions for Fal.ai MCP Server.

Contains: generate_image, generate_image_structured, generate_image_from_image
"""

from typing import List

from mcp.types import Tool

IMAGE_TOOLS: List[Tool] = [
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
]
