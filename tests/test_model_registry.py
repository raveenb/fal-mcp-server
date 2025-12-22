"""Tests for ModelRegistry"""

import time
from unittest.mock import patch

import pytest

from fal_mcp_server.model_registry import (
    FalModel,
    ModelCache,
    ModelRegistry,
    get_registry,
    reset_registry,
)


class TestModelRegistry:
    """Tests for ModelRegistry class."""

    @pytest.fixture
    def registry(self):
        """Create a fresh registry for each test."""
        return ModelRegistry(ttl_seconds=3600)

    def test_is_full_model_id(self, registry):
        """Test detection of full model IDs vs aliases."""
        assert registry.is_full_model_id("fal-ai/flux-pro")
        assert registry.is_full_model_id("fal-ai/flux/schnell")
        assert registry.is_full_model_id("fal-ai/flux-pro/v1.1-ultra")
        assert not registry.is_full_model_id("flux_schnell")
        assert not registry.is_full_model_id("sdxl")
        assert not registry.is_full_model_id("musicgen")

    def test_generate_alias(self, registry):
        """Test automatic alias generation from model IDs."""
        assert registry._generate_alias("fal-ai/flux-pro") == "flux_pro"
        assert registry._generate_alias("fal-ai/flux/schnell") == "flux_schnell"
        assert (
            registry._generate_alias("fal-ai/flux-pro/v1.1-ultra")
            == "flux_pro_v1.1_ultra"
        )
        assert registry._generate_alias("custom/model") is None

    def test_legacy_aliases_present(self, registry):
        """Test that all legacy aliases are defined."""
        expected_aliases = [
            "flux_schnell",
            "flux_dev",
            "flux_pro",
            "sdxl",
            "stable_diffusion",
            "svd",
            "animatediff",
            "kling",
            "musicgen",  # Now maps to fal-ai/lyria2 (musicgen-medium no longer exists)
            "lyria2",
            "stable_audio",
            "bark",
            "whisper",
        ]
        for alias in expected_aliases:
            assert alias in registry.LEGACY_ALIASES
            # Verify each alias maps to a fal-ai model
            assert registry.LEGACY_ALIASES[alias].startswith("fal-ai/")

    @pytest.mark.asyncio
    async def test_resolve_model_id_full_id(self, registry):
        """Test resolving full model IDs (passthrough)."""
        # Full IDs should pass through unchanged
        result = await registry.resolve_model_id("fal-ai/flux-pro/v1.1-ultra")
        assert result == "fal-ai/flux-pro/v1.1-ultra"

        result = await registry.resolve_model_id("fal-ai/flux/schnell")
        assert result == "fal-ai/flux/schnell"

    @pytest.mark.asyncio
    async def test_resolve_model_id_legacy_alias(self, registry):
        """Test resolving legacy aliases."""
        # Set up cache with legacy aliases
        registry._cache = ModelCache(
            models={},
            aliases=dict(registry.LEGACY_ALIASES),
            by_category={"image": [], "video": [], "audio": []},
            fetched_at=time.time() + 10000,  # Future timestamp (valid cache)
            ttl_seconds=3600,
        )

        result = await registry.resolve_model_id("flux_schnell")
        assert result == "fal-ai/flux/schnell"

        result = await registry.resolve_model_id("sdxl")
        assert result == "fal-ai/fast-sdxl"

        result = await registry.resolve_model_id("musicgen")
        assert result == "fal-ai/lyria2"  # Updated: musicgen-medium no longer exists

    @pytest.mark.asyncio
    async def test_resolve_model_id_unknown_alias(self, registry):
        """Test that unknown aliases raise ValueError."""
        registry._cache = registry._create_fallback_cache()
        # Make cache valid
        registry._cache.fetched_at = time.time() + 10000

        with pytest.raises(ValueError, match="Unknown model alias"):
            await registry.resolve_model_id("nonexistent_model")

    @pytest.mark.asyncio
    async def test_fallback_cache_on_api_failure(self, registry):
        """Test that fallback cache is used when API fails."""
        with patch.object(
            registry, "_fetch_all_models", side_effect=Exception("API Error")
        ):
            cache = await registry.get_cache()

            # Should have legacy aliases
            assert "flux_schnell" in cache.aliases
            assert cache.aliases["flux_schnell"] == "fal-ai/flux/schnell"

    @pytest.mark.asyncio
    async def test_list_models_returns_fallback_on_api_failure(self, registry):
        """Test that list_models returns legacy models when API fails.

        This is a critical end-to-end test: API failure should still allow
        list_models to return the legacy aliases as FalModel objects.
        """
        with patch.object(
            registry, "_fetch_all_models", side_effect=Exception("API Error")
        ):
            # list_models should return models from fallback cache
            all_models = await registry.list_models()
            assert len(all_models) > 0, "list_models should return fallback models"

            # Check we have models from each category
            image_models = await registry.list_models(category="image")
            assert len(image_models) >= 5, "Should have at least 5 image models"

            video_models = await registry.list_models(category="video")
            assert len(video_models) >= 3, "Should have at least 3 video models"

            audio_models = await registry.list_models(category="audio")
            assert len(audio_models) >= 4, "Should have at least 4 audio models"

            # Verify specific models are present
            model_ids = [m.id for m in all_models]
            assert "fal-ai/flux/schnell" in model_ids
            assert "fal-ai/kling-video" in model_ids
            assert (
                "fal-ai/lyria2" in model_ids
            )  # Updated: musicgen-medium no longer exists

    def test_cache_ttl_expiration(self, registry):
        """Test that cache expires after TTL."""
        # Create expired cache
        registry._cache = ModelCache(
            models={},
            aliases={},
            by_category={},
            fetched_at=time.time() - 7200,  # 2 hours ago
            ttl_seconds=3600,  # 1 hour TTL
        )

        assert not registry._is_cache_valid()

    def test_cache_still_valid(self, registry):
        """Test that cache is valid within TTL."""
        registry._cache = ModelCache(
            models={},
            aliases={},
            by_category={},
            fetched_at=time.time() - 1800,  # 30 minutes ago
            ttl_seconds=3600,  # 1 hour TTL
        )

        assert registry._is_cache_valid()

    @pytest.mark.asyncio
    async def test_list_models_with_category_filter(self, registry):
        """Test listing models filtered by category."""
        # Setup mock cache
        registry._cache = ModelCache(
            models={
                "fal-ai/flux/schnell": FalModel(
                    id="fal-ai/flux/schnell",
                    name="Flux Schnell",
                    description="Fast image generation",
                    category="text-to-image",
                    owner="fal-ai",
                ),
                "fal-ai/musicgen": FalModel(
                    id="fal-ai/musicgen",
                    name="MusicGen",
                    description="Music generation",
                    category="audio",
                    owner="fal-ai",
                ),
            },
            aliases={},
            by_category={
                "image": ["fal-ai/flux/schnell"],
                "video": [],
                "audio": ["fal-ai/musicgen"],
            },
            fetched_at=time.time() + 10000,
            ttl_seconds=3600,
        )

        image_models = await registry.list_models(category="image")
        assert len(image_models) == 1
        assert image_models[0].id == "fal-ai/flux/schnell"

        audio_models = await registry.list_models(category="audio")
        assert len(audio_models) == 1
        assert audio_models[0].id == "fal-ai/musicgen"

    @pytest.mark.asyncio
    async def test_list_models_with_search(self, registry):
        """Test listing models with search query."""
        registry._cache = ModelCache(
            models={
                "fal-ai/flux/schnell": FalModel(
                    id="fal-ai/flux/schnell",
                    name="Flux Schnell",
                    description="Fast image generation",
                    category="text-to-image",
                    owner="fal-ai",
                ),
                "fal-ai/sdxl": FalModel(
                    id="fal-ai/sdxl",
                    name="SDXL",
                    description="Stable Diffusion XL",
                    category="text-to-image",
                    owner="fal-ai",
                ),
            },
            aliases={},
            by_category={"image": ["fal-ai/flux/schnell", "fal-ai/sdxl"]},
            fetched_at=time.time() + 10000,
            ttl_seconds=3600,
        )

        results = await registry.list_models(search="flux")
        assert len(results) == 1
        assert results[0].id == "fal-ai/flux/schnell"

        results = await registry.list_models(search="stable")
        assert len(results) == 1
        assert results[0].id == "fal-ai/sdxl"

    @pytest.mark.asyncio
    async def test_list_models_with_limit(self, registry):
        """Test listing models with limit."""
        models = {
            f"fal-ai/model-{i}": FalModel(
                id=f"fal-ai/model-{i}",
                name=f"Model {i}",
                description="",
                category="text-to-image",
                owner="fal-ai",
            )
            for i in range(10)
        }

        registry._cache = ModelCache(
            models=models,
            aliases={},
            by_category={"image": list(models.keys())},
            fetched_at=time.time() + 10000,
            ttl_seconds=3600,
        )

        results = await registry.list_models(limit=5)
        assert len(results) == 5

    @pytest.mark.asyncio
    async def test_get_model(self, registry):
        """Test getting a specific model."""
        test_model = FalModel(
            id="fal-ai/flux/schnell",
            name="Flux Schnell",
            description="Fast image generation",
            category="text-to-image",
            owner="fal-ai",
        )

        registry._cache = ModelCache(
            models={"fal-ai/flux/schnell": test_model},
            aliases={},
            by_category={},
            fetched_at=time.time() + 10000,
            ttl_seconds=3600,
        )

        model = await registry.get_model("fal-ai/flux/schnell")
        assert model is not None
        assert model.id == "fal-ai/flux/schnell"
        assert model.name == "Flux Schnell"

        # Non-existent model
        model = await registry.get_model("fal-ai/nonexistent")
        assert model is None

    @pytest.mark.asyncio
    async def test_model_exists(self, registry):
        """Test checking if a model exists."""
        registry._cache = ModelCache(
            models={
                "fal-ai/flux/schnell": FalModel(
                    id="fal-ai/flux/schnell",
                    name="Flux Schnell",
                    description="",
                    category="text-to-image",
                    owner="fal-ai",
                )
            },
            aliases={"flux_schnell": "fal-ai/flux/schnell"},
            by_category={},
            fetched_at=time.time() + 10000,
            ttl_seconds=3600,
        )

        # Full IDs are assumed to exist (API will validate)
        assert await registry.model_exists("fal-ai/some-new-model") is True

        # Aliases in cache should exist
        assert await registry.model_exists("flux_schnell") is True

        # Unknown aliases should not exist
        assert await registry.model_exists("unknown_alias") is False

    @pytest.mark.asyncio
    async def test_pagination_terminates_on_has_more_false(self, registry):
        """Test pagination stops when has_more is False even with cursor present."""
        with patch.object(registry, "_fetch_models_page") as mock_fetch:
            mock_fetch.side_effect = [
                {
                    "models": [{"endpoint_id": "fal-ai/model-1", "metadata": {}}],
                    "next_cursor": "cursor1",
                    "has_more": True,
                },
                {
                    "models": [{"endpoint_id": "fal-ai/model-2", "metadata": {}}],
                    "next_cursor": "cursor2",
                    "has_more": False,
                },
            ]
            result = await registry._fetch_all_models()
            assert len(result) == 2
            assert mock_fetch.call_count == 2  # Should stop after has_more=False

    @pytest.mark.asyncio
    async def test_pagination_terminates_when_has_more_missing(self, registry):
        """Test pagination stops when has_more key is missing (defaults to False)."""
        with patch.object(registry, "_fetch_models_page") as mock_fetch:
            mock_fetch.return_value = {
                "models": [{"endpoint_id": "fal-ai/model-1", "metadata": {}}],
                "next_cursor": "cursor1",
                # has_more missing - should default to False
            }
            result = await registry._fetch_all_models()
            assert len(result) == 1
            assert mock_fetch.call_count == 1

    @pytest.mark.asyncio
    async def test_fetch_all_models_uses_models_key(self, registry):
        """Test that _fetch_all_models reads from 'models' key, not 'items'."""
        with patch.object(registry, "_fetch_models_page") as mock_fetch:
            mock_fetch.return_value = {
                "models": [{"endpoint_id": "fal-ai/correct"}],
                "items": [{"endpoint_id": "fal-ai/wrong"}],  # Should be ignored
                "has_more": False,
            }
            result = await registry._fetch_all_models()
            assert len(result) == 1
            assert result[0]["endpoint_id"] == "fal-ai/correct"

    @pytest.mark.asyncio
    async def test_refresh_cache_extracts_nested_metadata(self, registry):
        """Test that _refresh_cache correctly extracts metadata from nested structure."""
        with patch.object(registry, "_fetch_all_models") as mock_fetch:
            mock_fetch.return_value = [
                {
                    "endpoint_id": "fal-ai/test-model",
                    "metadata": {
                        "display_name": "Test Model Name",
                        "description": "Test description",
                        "category": "text-to-image",
                        "thumbnail_url": "https://example.com/thumb.jpg",
                    },
                }
            ]
            cache = await registry._refresh_cache()
            model = cache.models["fal-ai/test-model"]
            assert model.name == "Test Model Name"
            assert model.description == "Test description"
            assert model.category == "text-to-image"
            assert model.owner == "fal-ai"
            assert model.thumbnail_url == "https://example.com/thumb.jpg"

    @pytest.mark.asyncio
    async def test_refresh_cache_handles_empty_metadata(self, registry):
        """Test graceful handling when metadata is empty."""
        with patch.object(registry, "_fetch_all_models") as mock_fetch:
            mock_fetch.return_value = [
                {
                    "endpoint_id": "fal-ai/test-model",
                    "metadata": {},  # Empty metadata
                }
            ]
            cache = await registry._refresh_cache()
            model = cache.models["fal-ai/test-model"]
            assert model.name == "fal-ai/test-model"  # Falls back to model_id
            assert model.description == ""
            assert model.category == ""

    @pytest.mark.asyncio
    async def test_refresh_cache_handles_endpoint_id_without_slash(self, registry):
        """Test owner extraction when endpoint_id has no slash."""
        with patch.object(registry, "_fetch_all_models") as mock_fetch:
            mock_fetch.return_value = [
                {
                    "endpoint_id": "simple-model",  # No slash
                    "metadata": {},
                }
            ]
            cache = await registry._refresh_cache()
            model = cache.models["simple-model"]
            assert model.owner == ""

    def test_legacy_alias_categories_matches_legacy_aliases(self, registry):
        """Test that LEGACY_ALIAS_CATEGORIES covers all LEGACY_ALIASES."""
        for alias in registry.LEGACY_ALIASES:
            assert (
                alias in registry.LEGACY_ALIAS_CATEGORIES
            ), f"Missing category for alias: {alias}"
        for alias in registry.LEGACY_ALIAS_CATEGORIES:
            assert (
                alias in registry.LEGACY_ALIASES
            ), f"Category defined for unknown alias: {alias}"

    def test_fallback_cache_uses_shorter_ttl(self, registry):
        """Test that fallback cache uses FALLBACK_TTL for faster retry."""
        cache = registry._create_fallback_cache()
        assert cache.ttl_seconds == registry.FALLBACK_TTL
        assert cache.ttl_seconds == 60  # 1 minute, not 1 hour

    def test_fallback_cache_model_content_quality(self, registry):
        """Test that fallback cache models have meaningful content."""
        cache = registry._create_fallback_cache()

        # Verify model objects have proper content
        flux_model = cache.models.get("fal-ai/flux/schnell")
        assert flux_model is not None
        assert flux_model.name == "Flux Schnell"
        assert flux_model.category == "image"
        assert "image" in flux_model.description.lower()
        assert flux_model.owner == "fal-ai"

    @pytest.mark.asyncio
    async def test_get_pricing_empty_list(self, registry):
        """Test get_pricing with empty list returns empty prices."""
        result = await registry.get_pricing([])
        assert result == {"prices": []}

    @pytest.mark.asyncio
    async def test_get_pricing_success(self, registry):
        """Test get_pricing returns pricing data from API."""
        mock_response = {
            "prices": [
                {
                    "endpoint_id": "fal-ai/flux/dev",
                    "unit_price": 0.025,
                    "unit": "image",
                    "currency": "USD",
                },
                {
                    "endpoint_id": "fal-ai/kling-video",
                    "unit_price": 0.10,
                    "unit": "video",
                    "currency": "USD",
                },
            ]
        }

        with patch.object(registry, "_get_http_client") as mock_client:
            mock_response_obj = type(
                "MockResponse",
                (),
                {
                    "raise_for_status": lambda self: None,
                    "json": lambda self: mock_response,
                },
            )()
            mock_client.return_value.get = lambda *args, **kwargs: mock_response_obj

            # Create async mock

            async def async_get(*args, **kwargs):
                return mock_response_obj

            mock_client.return_value.get = async_get

            result = await registry.get_pricing(
                ["fal-ai/flux/dev", "fal-ai/kling-video"]
            )

            assert "prices" in result
            assert len(result["prices"]) == 2
            assert result["prices"][0]["endpoint_id"] == "fal-ai/flux/dev"
            assert result["prices"][0]["unit_price"] == 0.025

    @pytest.mark.asyncio
    async def test_get_usage_success(self, registry):
        """Test get_usage returns usage data from API."""
        mock_response = {
            "time_series": [],
            "summary": [
                {
                    "endpoint_id": "fal-ai/flux/dev",
                    "unit": "image",
                    "quantity": 100,
                    "cost": 2.50,
                    "currency": "USD",
                }
            ],
            "has_more": False,
        }

        with patch.object(registry, "_get_http_client") as mock_client:
            mock_response_obj = type(
                "MockResponse",
                (),
                {
                    "raise_for_status": lambda self: None,
                    "json": lambda self: mock_response,
                },
            )()

            async def async_get(*args, **kwargs):
                return mock_response_obj

            mock_client.return_value.get = async_get

            result = await registry.get_usage(
                start="2025-01-01",
                end="2025-01-31",
            )

            assert "summary" in result
            assert len(result["summary"]) == 1
            assert result["summary"][0]["endpoint_id"] == "fal-ai/flux/dev"
            assert result["summary"][0]["cost"] == 2.50

    @pytest.mark.asyncio
    async def test_get_usage_with_endpoint_filter(self, registry):
        """Test get_usage with endpoint_id filter."""
        mock_response = {"time_series": [], "summary": [], "has_more": False}

        with patch.object(registry, "_get_http_client") as mock_client:
            mock_response_obj = type(
                "MockResponse",
                (),
                {
                    "raise_for_status": lambda self: None,
                    "json": lambda self: mock_response,
                },
            )()

            async def async_get(*args, **kwargs):
                return mock_response_obj

            mock_client.return_value.get = async_get

            result = await registry.get_usage(
                start="2025-01-01",
                end="2025-01-31",
                endpoint_ids=["fal-ai/flux/dev"],
            )

            assert "summary" in result


class TestModelRegistrySingleton:
    """Tests for the module-level singleton."""

    @pytest.mark.asyncio
    async def test_get_registry_returns_singleton(self):
        """Test that get_registry returns the same instance."""
        # Reset singleton for test
        reset_registry()

        reg1 = await get_registry()
        reg2 = await get_registry()

        assert reg1 is reg2

        # Clean up
        reset_registry()

    @pytest.mark.asyncio
    async def test_reset_registry(self):
        """Test that reset_registry clears the singleton."""
        reset_registry()

        reg1 = await get_registry()
        reset_registry()
        reg2 = await get_registry()

        assert reg1 is not reg2

        # Clean up
        reset_registry()


class TestFalModel:
    """Tests for FalModel dataclass."""

    def test_fal_model_creation(self):
        """Test creating a FalModel."""
        model = FalModel(
            id="fal-ai/flux-pro",
            name="Flux Pro",
            description="Professional image generation",
            category="text-to-image",
            owner="fal-ai",
            thumbnail_url="https://example.com/thumb.jpg",
        )

        assert model.id == "fal-ai/flux-pro"
        assert model.name == "Flux Pro"
        assert model.description == "Professional image generation"
        assert model.category == "text-to-image"
        assert model.owner == "fal-ai"
        assert model.thumbnail_url == "https://example.com/thumb.jpg"

    def test_fal_model_defaults(self):
        """Test FalModel default values."""
        model = FalModel(
            id="fal-ai/test",
            name="Test",
            description="Test model",
            category="test",
        )

        assert model.owner == ""
        assert model.thumbnail_url is None
