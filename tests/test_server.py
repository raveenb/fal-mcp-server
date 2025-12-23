#!/usr/bin/env python3
"""Basic tests for Fal.ai MCP Server"""

import sys

import pytest

sys.path.insert(0, "../src")


def test_import():
    """Test that the server can be imported"""
    try:
        from fal_mcp_server.server import server

        assert server.name == "fal-ai-mcp"
        print("✓ Server imports successfully")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_model_registry_import():
    """Test that model registry can be imported"""
    try:
        from fal_mcp_server.model_registry import ModelRegistry

        registry = ModelRegistry()
        assert registry is not None
        print("✓ Model registry imports successfully")
        return True
    except ImportError as e:
        print(f"✗ Model registry import failed: {e}")
        return False


def test_legacy_aliases_config():
    """Test that legacy model aliases are present in the registry"""
    try:
        from fal_mcp_server.model_registry import ModelRegistry

        registry = ModelRegistry()

        # Check image models
        assert "flux_schnell" in registry.LEGACY_ALIASES
        assert "flux_dev" in registry.LEGACY_ALIASES
        assert "flux_pro" in registry.LEGACY_ALIASES
        assert "sdxl" in registry.LEGACY_ALIASES

        # Check video models
        assert "svd" in registry.LEGACY_ALIASES
        assert "kling" in registry.LEGACY_ALIASES

        # Check audio models
        assert "musicgen" in registry.LEGACY_ALIASES
        assert "whisper" in registry.LEGACY_ALIASES

        print("✓ Legacy aliases present")
        return True
    except Exception as e:
        print(f"✗ Legacy aliases config failed: {e}")
        return False


@pytest.mark.asyncio
async def test_list_tools():
    """Test that list_tools returns the expected tools"""
    from fal_mcp_server.server import list_tools

    tools = await list_tools()

    tool_names = [t.name for t in tools]
    # Utility tools
    assert "list_models" in tool_names
    assert "recommend_model" in tool_names
    assert "get_pricing" in tool_names
    assert "get_usage" in tool_names
    assert "upload_file" in tool_names
    # Image generation tools
    assert "generate_image" in tool_names
    assert "generate_image_structured" in tool_names
    assert "generate_image_from_image" in tool_names
    # Image editing tools
    assert "remove_background" in tool_names
    assert "upscale_image" in tool_names
    assert "edit_image" in tool_names
    assert "inpaint_image" in tool_names
    assert "resize_image" in tool_names
    # Video tools
    assert "generate_video" in tool_names
    assert "generate_video_from_image" in tool_names
    # Audio tools
    assert "generate_music" in tool_names


@pytest.mark.asyncio
async def test_get_pricing_tool_schema():
    """Test that get_pricing tool has correct schema"""
    from fal_mcp_server.server import list_tools

    tools = await list_tools()
    pricing_tool = next(t for t in tools if t.name == "get_pricing")

    assert pricing_tool is not None
    assert "models" in pricing_tool.inputSchema["properties"]
    assert pricing_tool.inputSchema["properties"]["models"]["type"] == "array"
    assert "models" in pricing_tool.inputSchema["required"]


@pytest.mark.asyncio
async def test_get_usage_tool_schema():
    """Test that get_usage tool has correct schema"""
    from fal_mcp_server.server import list_tools

    tools = await list_tools()
    usage_tool = next(t for t in tools if t.name == "get_usage")

    assert usage_tool is not None
    assert "start" in usage_tool.inputSchema["properties"]
    assert "end" in usage_tool.inputSchema["properties"]
    assert "models" in usage_tool.inputSchema["properties"]
    # No required fields - all parameters are optional
    assert usage_tool.inputSchema["required"] == []


@pytest.mark.asyncio
async def test_generate_image_structured_tool_schema():
    """Test that generate_image_structured tool has correct schema"""
    from fal_mcp_server.server import list_tools

    tools = await list_tools()
    structured_tool = next(t for t in tools if t.name == "generate_image_structured")

    assert structured_tool is not None
    props = structured_tool.inputSchema["properties"]

    # Check required structured prompt fields
    assert "scene" in props
    assert props["scene"]["type"] == "string"

    # Check optional structured fields
    assert "subjects" in props
    assert props["subjects"]["type"] == "array"

    assert "style" in props
    assert "color_palette" in props
    assert "lighting" in props
    assert "mood" in props
    assert "background" in props
    assert "composition" in props
    assert "camera" in props
    assert "effects" in props

    # Check camera sub-properties
    camera_props = props["camera"]["properties"]
    assert "angle" in camera_props
    assert "distance" in camera_props
    assert "focus" in camera_props
    assert "lens" in camera_props
    assert "f_number" in camera_props
    assert "iso" in camera_props

    # Check generation parameters
    assert "model" in props
    assert "image_size" in props
    assert "num_images" in props
    assert "seed" in props
    assert "negative_prompt" in props

    # Only scene is required
    assert structured_tool.inputSchema["required"] == ["scene"]


@pytest.mark.asyncio
async def test_generate_image_from_image_tool_schema():
    """Test that generate_image_from_image tool has correct schema with required image_url and prompt"""
    from fal_mcp_server.server import list_tools

    tools = await list_tools()
    img2img_tool = next(t for t in tools if t.name == "generate_image_from_image")

    assert img2img_tool is not None
    props = img2img_tool.inputSchema["properties"]

    # Check required parameters
    assert "image_url" in props
    assert props["image_url"]["type"] == "string"

    assert "prompt" in props
    assert props["prompt"]["type"] == "string"

    # Check model default
    assert "model" in props
    assert props["model"]["default"] == "fal-ai/flux/dev/image-to-image"

    # Check strength parameter
    assert "strength" in props
    assert props["strength"]["type"] == "number"
    assert props["strength"]["default"] == 0.75
    assert props["strength"]["minimum"] == 0.0
    assert props["strength"]["maximum"] == 1.0

    # Check optional parameters
    assert "num_images" in props
    assert "negative_prompt" in props
    assert "seed" in props
    assert "enable_safety_checker" in props
    assert "output_format" in props

    # Both image_url and prompt are required
    assert "image_url" in img2img_tool.inputSchema["required"]
    assert "prompt" in img2img_tool.inputSchema["required"]


@pytest.mark.asyncio
async def test_generate_video_tool_schema():
    """Test that generate_video tool has correct schema supporting both text-to-video and image-to-video"""
    from fal_mcp_server.server import list_tools

    tools = await list_tools()
    video_tool = next(t for t in tools if t.name == "generate_video")

    assert video_tool is not None
    props = video_tool.inputSchema["properties"]

    # Check prompt (required for all video generation)
    assert "prompt" in props
    assert props["prompt"]["type"] == "string"

    # Check image_url (optional - only for image-to-video models)
    assert "image_url" in props
    assert props["image_url"]["type"] == "string"

    # Check optional fields
    assert "model" in props
    assert props["model"]["default"] == "fal-ai/wan-i2v"

    assert "duration" in props
    assert props["duration"]["default"] == 5
    assert props["duration"]["minimum"] == 2
    assert props["duration"]["maximum"] == 10

    # Check additional optional parameters
    assert "aspect_ratio" in props
    assert props["aspect_ratio"]["default"] == "16:9"

    assert "negative_prompt" in props
    assert props["negative_prompt"]["type"] == "string"

    assert "cfg_scale" in props
    assert props["cfg_scale"]["type"] == "number"
    assert props["cfg_scale"]["default"] == 0.5

    # Only prompt is required (image_url is optional for text-to-video)
    assert video_tool.inputSchema["required"] == ["prompt"]
    assert "image_url" not in video_tool.inputSchema["required"]


@pytest.mark.asyncio
async def test_generate_video_from_image_tool_schema():
    """Test that generate_video_from_image tool has correct schema with required image_url"""
    from fal_mcp_server.server import list_tools

    tools = await list_tools()
    video_tool = next(t for t in tools if t.name == "generate_video_from_image")

    assert video_tool is not None
    props = video_tool.inputSchema["properties"]

    # Check required parameters
    assert "image_url" in props
    assert props["image_url"]["type"] == "string"

    assert "prompt" in props
    assert props["prompt"]["type"] == "string"

    # Check optional parameters
    assert "model" in props
    assert props["model"]["default"] == "fal-ai/wan-i2v"

    assert "duration" in props
    assert props["duration"]["default"] == 5

    assert "aspect_ratio" in props
    assert props["aspect_ratio"]["default"] == "16:9"

    assert "negative_prompt" in props
    assert "cfg_scale" in props

    # Both image_url and prompt are required for image-to-video
    assert "image_url" in video_tool.inputSchema["required"]
    assert "prompt" in video_tool.inputSchema["required"]


@pytest.mark.asyncio
async def test_upload_file_tool_schema():
    """Test that upload_file tool has correct schema"""
    from fal_mcp_server.server import list_tools

    tools = await list_tools()
    upload_tool = next(t for t in tools if t.name == "upload_file")

    assert upload_tool is not None
    props = upload_tool.inputSchema["properties"]

    # Check required file_path parameter
    assert "file_path" in props
    assert props["file_path"]["type"] == "string"

    # Only file_path is required
    assert upload_tool.inputSchema["required"] == ["file_path"]


@pytest.mark.asyncio
async def test_resolve_model_id_full_id():
    """Test that full model IDs pass through unchanged"""
    from fal_mcp_server.model_registry import ModelRegistry

    registry = ModelRegistry()

    # Full IDs should pass through
    result = await registry.resolve_model_id("fal-ai/flux-pro/v1.1-ultra")
    assert result == "fal-ai/flux-pro/v1.1-ultra"


@pytest.mark.asyncio
async def test_resolve_model_id_alias():
    """Test that aliases are resolved to full model IDs"""
    import time

    from fal_mcp_server.model_registry import ModelRegistry, reset_registry

    reset_registry()
    registry = ModelRegistry()

    # Set up a valid cache with legacy aliases
    from fal_mcp_server.model_registry import ModelCache

    registry._cache = ModelCache(
        models={},
        aliases=dict(registry.LEGACY_ALIASES),
        by_category={"image": [], "video": [], "audio": []},
        fetched_at=time.time() + 10000,  # Future timestamp (valid cache)
        ttl_seconds=3600,
    )

    # Aliases should resolve
    result = await registry.resolve_model_id("flux_schnell")
    assert result == "fal-ai/flux/schnell"

    result = await registry.resolve_model_id("musicgen")
    assert result == "fal-ai/lyria2"  # Updated: musicgen-medium no longer exists


@pytest.mark.asyncio
async def test_recommend_model_tool_schema():
    """Test that recommend_model tool has correct schema"""
    from fal_mcp_server.server import list_tools

    tools = await list_tools()
    recommend_tool = next(t for t in tools if t.name == "recommend_model")

    assert recommend_tool is not None
    props = recommend_tool.inputSchema["properties"]

    # Check task parameter (required)
    assert "task" in props
    assert props["task"]["type"] == "string"

    # Check category parameter (optional)
    assert "category" in props
    assert props["category"]["type"] == "string"
    assert "image" in props["category"]["enum"]
    assert "video" in props["category"]["enum"]
    assert "audio" in props["category"]["enum"]

    # Check limit parameter
    assert "limit" in props
    assert props["limit"]["type"] == "integer"
    assert props["limit"]["default"] == 5
    assert props["limit"]["minimum"] == 1
    assert props["limit"]["maximum"] == 10

    # Only task is required
    assert recommend_tool.inputSchema["required"] == ["task"]


@pytest.mark.asyncio
async def test_list_models_tool_schema_with_task():
    """Test that list_models tool has task parameter for intelligent ranking"""
    from fal_mcp_server.server import list_tools

    tools = await list_tools()
    list_models_tool = next(t for t in tools if t.name == "list_models")

    assert list_models_tool is not None
    props = list_models_tool.inputSchema["properties"]

    # Check task parameter exists
    assert "task" in props
    assert props["task"]["type"] == "string"

    # Check search parameter still exists
    assert "search" in props
    assert props["search"]["type"] == "string"

    # Check category parameter
    assert "category" in props
    assert "image" in props["category"]["enum"]

    # All parameters are optional
    assert list_models_tool.inputSchema["required"] == []


def test_fal_model_dataclass_fields():
    """Test that FalModel dataclass has all required fields including new ones"""
    from fal_mcp_server.model_registry import FalModel

    # Create a model with all fields
    model = FalModel(
        id="fal-ai/flux-pro",
        name="Flux Pro",
        description="High-quality image generation",
        category="text-to-image",
        owner="fal-ai",
        thumbnail_url="https://example.com/thumb.png",
        highlighted=True,
        group_key="flux",
        group_label="Flux Family",
        status="active",
        tags=["image", "generation"],
    )

    # Verify all fields
    assert model.id == "fal-ai/flux-pro"
    assert model.name == "Flux Pro"
    assert model.description == "High-quality image generation"
    assert model.category == "text-to-image"
    assert model.owner == "fal-ai"
    assert model.thumbnail_url == "https://example.com/thumb.png"
    assert model.highlighted is True
    assert model.group_key == "flux"
    assert model.group_label == "Flux Family"
    assert model.status == "active"
    assert model.tags == ["image", "generation"]


def test_fal_model_default_values():
    """Test that FalModel has correct default values for new fields"""
    from fal_mcp_server.model_registry import FalModel

    # Create a model with minimal required fields
    model = FalModel(
        id="test-model",
        name="Test Model",
        description="Test description",
        category="text-to-image",
    )

    # Check default values
    assert model.highlighted is False
    assert model.group_key is None
    assert model.group_label is None
    assert model.status == "active"
    assert model.tags is None
    assert model.owner == ""
    assert model.thumbnail_url is None


if __name__ == "__main__":
    tests_passed = 0
    tests_failed = 0

    if test_import():
        tests_passed += 1
    else:
        tests_failed += 1

    if test_model_registry_import():
        tests_passed += 1
    else:
        tests_failed += 1

    if test_legacy_aliases_config():
        tests_passed += 1
    else:
        tests_failed += 1

    print(f"Tests: {tests_passed} passed, {tests_failed} failed")
    sys.exit(0 if tests_failed == 0 else 1)
