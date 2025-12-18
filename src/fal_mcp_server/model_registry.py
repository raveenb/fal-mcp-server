"""
Model Registry for Fal.ai MCP Server

Provides dynamic model discovery from the Fal.ai Platform API with TTL-based caching.
Supports both full model IDs (e.g., 'fal-ai/flux-pro') and friendly aliases (e.g., 'flux_schnell').
"""

import asyncio
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx


@dataclass
class FalModel:
    """Represents a model from the Fal.ai platform."""

    id: str  # e.g., "fal-ai/flux-pro/v1.1-ultra"
    name: str  # Human-readable name
    description: str  # Model description
    category: str  # e.g., "text-to-image", "image-to-video", "audio"
    owner: str = ""  # e.g., "fal-ai"
    thumbnail_url: Optional[str] = None


@dataclass
class ModelCache:
    """Cached model data with TTL."""

    models: Dict[str, FalModel]  # model_id -> FalModel
    aliases: Dict[str, str]  # alias -> model_id
    by_category: Dict[str, List[str]]  # category -> list of model_ids
    fetched_at: float  # timestamp
    ttl_seconds: int = 3600  # 1 hour default


class ModelRegistry:
    """
    Manages model discovery from Fal.ai API with caching.

    Features:
    - Lazy loading on first use
    - TTL-based cache with configurable expiration
    - Backward-compatible friendly aliases
    - Auto-detection of full IDs vs aliases
    - Thread-safe async operations
    """

    FAL_API_BASE = "https://api.fal.ai/v1"
    DEFAULT_TTL = 3600  # 1 hour

    # Backward-compatible aliases for existing models
    LEGACY_ALIASES: Dict[str, str] = {
        # Image models
        "flux_schnell": "fal-ai/flux/schnell",
        "flux_dev": "fal-ai/flux/dev",
        "flux_pro": "fal-ai/flux-pro",
        "sdxl": "fal-ai/fast-sdxl",
        "stable_diffusion": "fal-ai/stable-diffusion-v3-medium",
        # Video models
        "svd": "fal-ai/stable-video-diffusion",
        "animatediff": "fal-ai/fast-animatediff",
        "kling": "fal-ai/kling-video",
        # Audio models
        "musicgen": "fal-ai/musicgen-medium",
        "musicgen_large": "fal-ai/musicgen-large",
        "bark": "fal-ai/bark",
        "whisper": "fal-ai/whisper",
    }

    # Category mappings from Fal API categories to our simplified categories
    CATEGORY_MAPPING: Dict[str, str] = {
        "text-to-image": "image",
        "image-to-image": "image",
        "text-to-video": "video",
        "image-to-video": "video",
        "video-to-video": "video",
        "audio": "audio",
        "text-to-audio": "audio",
        "speech-to-text": "audio",
        "text-to-speech": "audio",
        "audio-to-audio": "audio",
    }

    def __init__(self, ttl_seconds: int = DEFAULT_TTL):
        self._cache: Optional[ModelCache] = None
        self._lock = asyncio.Lock()
        self._ttl_seconds = ttl_seconds
        self._http_client: Optional[httpx.AsyncClient] = None

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            headers = {"Content-Type": "application/json"}
            if api_key := os.getenv("FAL_KEY"):
                headers["Authorization"] = f"Key {api_key}"
            self._http_client = httpx.AsyncClient(
                base_url=self.FAL_API_BASE, headers=headers, timeout=30.0
            )
        return self._http_client

    async def _fetch_models_page(
        self,
        cursor: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """Fetch a single page of models from the API."""
        client = await self._get_http_client()
        params: Dict[str, Any] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        if category:
            params["category"] = category

        response = await client.get("/models", params=params)
        response.raise_for_status()
        return response.json()

    async def _fetch_all_models(
        self, category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fetch all models with pagination."""
        all_models: List[Dict[str, Any]] = []
        cursor: Optional[str] = None

        while True:
            data = await self._fetch_models_page(cursor=cursor, category=category)
            items = data.get("items", [])
            all_models.extend(items)

            cursor = data.get("next_cursor")
            if not cursor:
                break

        return all_models

    async def _refresh_cache(self) -> ModelCache:
        """Refresh the model cache from the API."""
        raw_models = await self._fetch_all_models()

        models: Dict[str, FalModel] = {}
        aliases: Dict[str, str] = dict(self.LEGACY_ALIASES)  # Start with legacy aliases
        by_category: Dict[str, List[str]] = {"image": [], "video": [], "audio": []}

        for raw in raw_models:
            model_id = raw.get("endpoint_id", raw.get("id", ""))
            if not model_id:
                continue

            model = FalModel(
                id=model_id,
                name=raw.get("title", raw.get("name", model_id)),
                description=raw.get("description", ""),
                category=raw.get("category", ""),
                owner=raw.get("owner", ""),
                thumbnail_url=raw.get("thumbnail_url"),
            )
            models[model_id] = model

            # Map to our simplified category system
            our_category = self.CATEGORY_MAPPING.get(model.category)
            if our_category and our_category in by_category:
                by_category[our_category].append(model_id)

            # Generate automatic alias from model ID
            auto_alias = self._generate_alias(model_id)
            if auto_alias and auto_alias not in aliases:
                aliases[auto_alias] = model_id

        return ModelCache(
            models=models,
            aliases=aliases,
            by_category=by_category,
            fetched_at=time.time(),
            ttl_seconds=self._ttl_seconds,
        )

    def _generate_alias(self, model_id: str) -> Optional[str]:
        """Generate a friendly alias from a model ID."""
        # Remove "fal-ai/" prefix and convert to snake_case
        if model_id.startswith("fal-ai/"):
            name = model_id[7:]  # Remove "fal-ai/"
            # Replace slashes and dashes with underscores
            alias = name.replace("/", "_").replace("-", "_")
            return alias
        return None

    def _is_cache_valid(self) -> bool:
        """Check if the cache is still valid."""
        if self._cache is None:
            return False
        age = time.time() - self._cache.fetched_at
        return age < self._cache.ttl_seconds

    async def get_cache(self) -> ModelCache:
        """Get the model cache, refreshing if necessary."""
        async with self._lock:
            if not self._is_cache_valid():
                try:
                    self._cache = await self._refresh_cache()
                except Exception:
                    # If refresh fails and we have stale cache, use it
                    if self._cache is not None:
                        pass  # Use stale cache
                    else:
                        # Create minimal cache with legacy aliases
                        self._cache = self._create_fallback_cache()
            return self._cache

    def _create_fallback_cache(self) -> ModelCache:
        """Create a fallback cache with just legacy aliases."""
        return ModelCache(
            models={},
            aliases=dict(self.LEGACY_ALIASES),
            by_category={"image": [], "video": [], "audio": []},
            fetched_at=time.time(),
            ttl_seconds=self._ttl_seconds,
        )

    def is_full_model_id(self, model_input: str) -> bool:
        """Check if input looks like a full model ID vs alias."""
        # Full IDs contain "/" (e.g., "fal-ai/flux-pro/v1.1-ultra")
        return "/" in model_input

    async def resolve_model_id(self, model_input: str) -> str:
        """
        Resolve a model input to a full model ID.

        Accepts either:
        - Full model ID: "fal-ai/flux-pro/v1.1-ultra" -> returns as-is
        - Friendly alias: "flux_pro" -> resolves to "fal-ai/flux-pro"

        Raises ValueError if alias not found.
        """
        # If it looks like a full ID, return as-is
        if self.is_full_model_id(model_input):
            return model_input

        # Otherwise, look up alias
        cache = await self.get_cache()
        if model_input in cache.aliases:
            return cache.aliases[model_input]

        raise ValueError(f"Unknown model alias: {model_input}")

    async def list_models(
        self,
        category: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
    ) -> List[FalModel]:
        """
        List available models with optional filtering.

        Args:
            category: Filter by category ("image", "video", "audio")
            search: Search query to filter by name/description
            limit: Maximum number of results

        Returns:
            List of FalModel objects
        """
        cache = await self.get_cache()

        if category:
            model_ids = cache.by_category.get(category, [])
            models = [cache.models[mid] for mid in model_ids if mid in cache.models]
        else:
            models = list(cache.models.values())

        if search:
            search_lower = search.lower()
            models = [
                m
                for m in models
                if search_lower in m.name.lower()
                or search_lower in m.description.lower()
                or search_lower in m.id.lower()
            ]

        return models[:limit]

    async def get_model(self, model_id: str) -> Optional[FalModel]:
        """Get a specific model by ID."""
        cache = await self.get_cache()
        return cache.models.get(model_id)

    async def model_exists(self, model_input: str) -> bool:
        """Check if a model exists (by ID or alias)."""
        try:
            model_id = await self.resolve_model_id(model_input)
            cache = await self.get_cache()
            # For full IDs not in cache, assume they exist (API will validate)
            if self.is_full_model_id(model_input):
                return True
            return model_id in cache.models or model_input in cache.aliases
        except ValueError:
            return False

    async def get_aliases(self) -> Dict[str, str]:
        """Get all available aliases."""
        cache = await self.get_cache()
        return dict(cache.aliases)

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None


# Module-level singleton instance
_registry: Optional[ModelRegistry] = None


async def get_registry() -> ModelRegistry:
    """Get the global ModelRegistry singleton."""
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry


def reset_registry() -> None:
    """Reset the global registry (useful for testing)."""
    global _registry
    _registry = None
