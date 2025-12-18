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
    assert "list_models" in tool_names
    assert "generate_image" in tool_names
    assert "generate_video" in tool_names
    assert "generate_music" in tool_names


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
    assert result == "fal-ai/musicgen-medium"


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
