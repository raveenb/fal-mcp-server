#!/usr/bin/env python3
"""Tests for image editing tools (remove_background, upscale, edit, inpaint, resize, compose)."""

import sys

import pytest

sys.path.insert(0, "../src")


@pytest.mark.asyncio
async def test_image_editing_tools_registered():
    """Test that all image editing tools are registered."""
    from fal_mcp_server.server import list_tools

    tools = await list_tools()
    tool_names = [t.name for t in tools]

    # All 6 image editing tools should be registered
    assert "remove_background" in tool_names
    assert "upscale_image" in tool_names
    assert "edit_image" in tool_names
    assert "inpaint_image" in tool_names
    assert "resize_image" in tool_names
    assert "compose_images" in tool_names


@pytest.mark.asyncio
async def test_remove_background_tool_schema():
    """Test that remove_background tool has correct schema."""
    from fal_mcp_server.server import list_tools

    tools = await list_tools()
    tool = next(t for t in tools if t.name == "remove_background")

    assert tool is not None
    props = tool.inputSchema["properties"]

    # Check required parameters
    assert "image_url" in props
    assert props["image_url"]["type"] == "string"

    # Check optional parameters
    assert "model" in props
    assert props["model"]["default"] == "fal-ai/birefnet/v2"

    assert "output_format" in props
    assert props["output_format"]["default"] == "png"
    assert "png" in props["output_format"]["enum"]
    assert "webp" in props["output_format"]["enum"]

    # Only image_url is required
    assert tool.inputSchema["required"] == ["image_url"]


@pytest.mark.asyncio
async def test_upscale_image_tool_schema():
    """Test that upscale_image tool has correct schema."""
    from fal_mcp_server.server import list_tools

    tools = await list_tools()
    tool = next(t for t in tools if t.name == "upscale_image")

    assert tool is not None
    props = tool.inputSchema["properties"]

    # Check required parameters
    assert "image_url" in props
    assert props["image_url"]["type"] == "string"

    # Check optional parameters
    assert "scale" in props
    assert props["scale"]["default"] == 2
    assert props["scale"]["type"] == "integer"
    assert 2 in props["scale"]["enum"]
    assert 4 in props["scale"]["enum"]

    assert "model" in props
    assert props["model"]["default"] == "fal-ai/clarity-upscaler"

    # Only image_url is required
    assert tool.inputSchema["required"] == ["image_url"]


@pytest.mark.asyncio
async def test_edit_image_tool_schema():
    """Test that edit_image tool has correct schema."""
    from fal_mcp_server.server import list_tools

    tools = await list_tools()
    tool = next(t for t in tools if t.name == "edit_image")

    assert tool is not None
    props = tool.inputSchema["properties"]

    # Check required parameters
    assert "image_url" in props
    assert props["image_url"]["type"] == "string"

    assert "instruction" in props
    assert props["instruction"]["type"] == "string"

    # Check optional parameters
    assert "model" in props
    assert props["model"]["default"] == "fal-ai/flux-2/edit"

    assert "strength" in props
    assert props["strength"]["default"] == 0.75
    assert props["strength"]["minimum"] == 0.0
    assert props["strength"]["maximum"] == 1.0

    assert "seed" in props
    assert props["seed"]["type"] == "integer"

    # Both image_url and instruction are required
    assert "image_url" in tool.inputSchema["required"]
    assert "instruction" in tool.inputSchema["required"]


@pytest.mark.asyncio
async def test_inpaint_image_tool_schema():
    """Test that inpaint_image tool has correct schema."""
    from fal_mcp_server.server import list_tools

    tools = await list_tools()
    tool = next(t for t in tools if t.name == "inpaint_image")

    assert tool is not None
    props = tool.inputSchema["properties"]

    # Check required parameters
    assert "image_url" in props
    assert props["image_url"]["type"] == "string"

    assert "mask_url" in props
    assert props["mask_url"]["type"] == "string"

    assert "prompt" in props
    assert props["prompt"]["type"] == "string"

    # Check optional parameters
    assert "model" in props
    assert props["model"]["default"] == "fal-ai/flux-kontext-lora/inpaint"

    assert "negative_prompt" in props
    assert props["negative_prompt"]["type"] == "string"

    assert "seed" in props
    assert props["seed"]["type"] == "integer"

    # image_url, mask_url, and prompt are all required
    assert "image_url" in tool.inputSchema["required"]
    assert "mask_url" in tool.inputSchema["required"]
    assert "prompt" in tool.inputSchema["required"]


@pytest.mark.asyncio
async def test_resize_image_tool_schema():
    """Test that resize_image tool has correct schema with social media presets."""
    from fal_mcp_server.server import list_tools

    tools = await list_tools()
    tool = next(t for t in tools if t.name == "resize_image")

    assert tool is not None
    props = tool.inputSchema["properties"]

    # Check required parameters
    assert "image_url" in props
    assert props["image_url"]["type"] == "string"

    assert "target_format" in props
    assert props["target_format"]["type"] == "string"

    # Check social media presets are in enum
    target_enum = props["target_format"]["enum"]
    assert "instagram_post" in target_enum
    assert "instagram_story" in target_enum
    assert "youtube_thumbnail" in target_enum
    assert "twitter_post" in target_enum
    assert "linkedin_post" in target_enum
    assert "facebook_post" in target_enum
    assert "pinterest_pin" in target_enum
    assert "tiktok" in target_enum
    assert "custom" in target_enum

    # Check resize modes
    assert "mode" in props
    assert props["mode"]["default"] == "extend"
    assert "extend" in props["mode"]["enum"]
    assert "crop" in props["mode"]["enum"]
    assert "letterbox" in props["mode"]["enum"]

    # Check custom dimension parameters
    assert "width" in props
    assert props["width"]["type"] == "integer"
    assert props["width"]["minimum"] == 64
    assert props["width"]["maximum"] == 4096

    assert "height" in props
    assert props["height"]["type"] == "integer"
    assert props["height"]["minimum"] == 64
    assert props["height"]["maximum"] == 4096

    # Check extend mode parameters
    assert "background_prompt" in props
    assert props["background_prompt"]["type"] == "string"

    # Check letterbox mode parameters
    assert "background_color" in props
    assert props["background_color"]["default"] == "#000000"

    # image_url and target_format are required
    assert "image_url" in tool.inputSchema["required"]
    assert "target_format" in tool.inputSchema["required"]


@pytest.mark.asyncio
async def test_compose_images_tool_schema():
    """Test that compose_images tool has correct schema for image compositing."""
    from fal_mcp_server.server import list_tools

    tools = await list_tools()
    tool = next(t for t in tools if t.name == "compose_images")

    assert tool is not None
    props = tool.inputSchema["properties"]

    # Check required parameters
    assert "base_image_url" in props
    assert props["base_image_url"]["type"] == "string"

    assert "overlay_image_url" in props
    assert props["overlay_image_url"]["type"] == "string"

    # Check position presets
    assert "position" in props
    assert props["position"]["type"] == "string"
    assert props["position"]["default"] == "bottom-right"
    position_enum = props["position"]["enum"]
    assert "top-left" in position_enum
    assert "top-right" in position_enum
    assert "bottom-left" in position_enum
    assert "bottom-right" in position_enum
    assert "center" in position_enum
    assert "custom" in position_enum

    # Check custom position parameters
    assert "x" in props
    assert props["x"]["type"] == "integer"

    assert "y" in props
    assert props["y"]["type"] == "integer"

    # Check scale parameter
    assert "scale" in props
    assert props["scale"]["type"] == "number"
    assert props["scale"]["default"] == 0.15
    assert props["scale"]["minimum"] == 0.01
    assert props["scale"]["maximum"] == 1.0

    # Check padding parameter
    assert "padding" in props
    assert props["padding"]["type"] == "integer"
    assert props["padding"]["default"] == 20
    assert props["padding"]["minimum"] == 0

    # Check opacity parameter
    assert "opacity" in props
    assert props["opacity"]["type"] == "number"
    assert props["opacity"]["default"] == 1.0
    assert props["opacity"]["minimum"] == 0.0
    assert props["opacity"]["maximum"] == 1.0

    # Check output format
    assert "output_format" in props
    assert props["output_format"]["default"] == "png"
    assert "png" in props["output_format"]["enum"]
    assert "jpeg" in props["output_format"]["enum"]
    assert "webp" in props["output_format"]["enum"]

    # base_image_url and overlay_image_url are required
    assert "base_image_url" in tool.inputSchema["required"]
    assert "overlay_image_url" in tool.inputSchema["required"]


@pytest.mark.asyncio
async def test_social_media_formats_constant():
    """Test that SOCIAL_MEDIA_FORMATS constant has correct dimensions."""
    from fal_mcp_server.tools.image_editing_tools import SOCIAL_MEDIA_FORMATS

    # Check required formats exist
    assert "instagram_post" in SOCIAL_MEDIA_FORMATS
    assert "instagram_story" in SOCIAL_MEDIA_FORMATS
    assert "youtube_thumbnail" in SOCIAL_MEDIA_FORMATS
    assert "twitter_post" in SOCIAL_MEDIA_FORMATS
    assert "linkedin_post" in SOCIAL_MEDIA_FORMATS
    assert "tiktok" in SOCIAL_MEDIA_FORMATS

    # Check Instagram post is square (1:1)
    ig_post = SOCIAL_MEDIA_FORMATS["instagram_post"]
    assert ig_post["width"] == 1080
    assert ig_post["height"] == 1080
    assert ig_post["aspect"] == "1:1"

    # Check Instagram story is vertical (9:16)
    ig_story = SOCIAL_MEDIA_FORMATS["instagram_story"]
    assert ig_story["width"] == 1080
    assert ig_story["height"] == 1920
    assert ig_story["aspect"] == "9:16"

    # Check YouTube thumbnail is horizontal (16:9)
    yt_thumb = SOCIAL_MEDIA_FORMATS["youtube_thumbnail"]
    assert yt_thumb["width"] == 1280
    assert yt_thumb["height"] == 720
    assert yt_thumb["aspect"] == "16:9"


@pytest.mark.asyncio
async def test_image_editing_handlers_registered():
    """Test that all image editing handlers are registered in TOOL_HANDLERS."""
    from fal_mcp_server.server import TOOL_HANDLERS

    # All 6 image editing handlers should be registered
    assert "remove_background" in TOOL_HANDLERS
    assert "upscale_image" in TOOL_HANDLERS
    assert "edit_image" in TOOL_HANDLERS
    assert "inpaint_image" in TOOL_HANDLERS
    assert "resize_image" in TOOL_HANDLERS
    assert "compose_images" in TOOL_HANDLERS


def test_image_editing_tools_count():
    """Test that IMAGE_EDITING_TOOLS contains exactly 6 tools."""
    from fal_mcp_server.tools.image_editing_tools import IMAGE_EDITING_TOOLS

    assert len(IMAGE_EDITING_TOOLS) == 6

    tool_names = [t.name for t in IMAGE_EDITING_TOOLS]
    assert "remove_background" in tool_names
    assert "upscale_image" in tool_names
    assert "edit_image" in tool_names
    assert "inpaint_image" in tool_names
    assert "resize_image" in tool_names
    assert "compose_images" in tool_names


def test_handlers_import():
    """Test that all image editing handlers can be imported."""
    from fal_mcp_server.handlers.image_editing_handlers import (
        handle_compose_images,
        handle_edit_image,
        handle_inpaint_image,
        handle_remove_background,
        handle_resize_image,
        handle_upscale_image,
    )

    # All handlers should be callable
    assert callable(handle_remove_background)
    assert callable(handle_upscale_image)
    assert callable(handle_edit_image)
    assert callable(handle_inpaint_image)
    assert callable(handle_resize_image)
    assert callable(handle_compose_images)
