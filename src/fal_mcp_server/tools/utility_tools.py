"""
Utility tool definitions for Fal.ai MCP Server.

Contains: list_models, recommend_model, get_pricing, get_usage, upload_file
"""

from typing import List

from mcp.types import Tool

UTILITY_TOOLS: List[Tool] = [
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
