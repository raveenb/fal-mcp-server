"""
Audio tool definitions for Fal.ai MCP Server.

Contains: generate_music
"""

from typing import List

from mcp.types import Tool

AUDIO_TOOLS: List[Tool] = [
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
                "model": {
                    "type": "string",
                    "default": "fal-ai/lyria2",
                    "description": "Model ID (e.g., 'fal-ai/lyria2', 'fal-ai/stable-audio-25/text-to-audio'). Use list_models to see options.",
                },
                "duration_seconds": {
                    "type": "integer",
                    "default": 30,
                    "minimum": 5,
                    "maximum": 300,
                    "description": "Duration in seconds",
                },
                "negative_prompt": {
                    "type": "string",
                    "description": "What to avoid in the audio (e.g., 'vocals, distortion, noise')",
                },
                "lyrics_prompt": {
                    "type": "string",
                    "description": "Lyrics for vocal music generation. Only used with models that support lyrics (e.g., MiniMax). Format: [verse]\\nLyric line 1\\n[chorus]\\nChorus line",
                },
            },
            "required": ["prompt"],
        },
    ),
]
