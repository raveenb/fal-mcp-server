"""
Handler implementations for Fal.ai MCP Server.

Handlers are transport-agnostic implementations of tool logic.
They accept arguments, use the model registry, and optionally
use a QueueStrategy for long-running operations.
"""

from fal_mcp_server.handlers.audio_handlers import handle_generate_music
from fal_mcp_server.handlers.image_editing_handlers import (
    handle_compose_images,
    handle_edit_image,
    handle_inpaint_image,
    handle_remove_background,
    handle_resize_image,
    handle_upscale_image,
)
from fal_mcp_server.handlers.image_handlers import (
    handle_generate_image,
    handle_generate_image_from_image,
    handle_generate_image_structured,
)
from fal_mcp_server.handlers.utility_handlers import (
    handle_get_pricing,
    handle_get_usage,
    handle_list_models,
    handle_recommend_model,
    handle_upload_file,
)
from fal_mcp_server.handlers.video_handlers import (
    handle_generate_video,
    handle_generate_video_from_image,
    handle_generate_video_from_video,
)

__all__ = [
    # Utility handlers
    "handle_list_models",
    "handle_recommend_model",
    "handle_get_pricing",
    "handle_get_usage",
    "handle_upload_file",
    # Image generation handlers
    "handle_generate_image",
    "handle_generate_image_structured",
    "handle_generate_image_from_image",
    # Image editing handlers
    "handle_remove_background",
    "handle_upscale_image",
    "handle_edit_image",
    "handle_inpaint_image",
    "handle_resize_image",
    "handle_compose_images",
    # Video handlers
    "handle_generate_video",
    "handle_generate_video_from_image",
    "handle_generate_video_from_video",
    # Audio handlers
    "handle_generate_music",
]
