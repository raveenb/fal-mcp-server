"""
Model Registry for Fal.ai MCP Server

Provides dynamic model discovery from the Fal.ai Platform API with TTL-based caching.
Supports both full model IDs (e.g., 'fal-ai/flux-pro') and friendly aliases (e.g., 'flux_schnell').
"""

import asyncio
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

import httpx
from loguru import logger


@dataclass
class FalModel:
    """Represents a model from the Fal.ai platform."""

    id: str  # e.g., "fal-ai/flux-pro/v1.1-ultra"
    name: str  # Human-readable name
    description: str  # Model description
    category: str  # e.g., "text-to-image", "image-to-video", "audio"
    owner: str = ""  # e.g., "fal-ai"
    thumbnail_url: Optional[str] = None
    highlighted: bool = False  # Featured/recommended model
    group_key: Optional[str] = None  # Model family grouping key
    group_label: Optional[str] = None  # Model family display name
    status: str = "active"  # Model status (active, deprecated)
    tags: Optional[List[str]] = None  # Model tags for categorization


@dataclass
class ModelCache:
    """Cached model data with TTL."""

    models: Dict[str, FalModel]  # model_id -> FalModel
    aliases: Dict[str, str]  # alias -> model_id
    by_category: Dict[str, List[str]]  # category -> list of model_ids
    fetched_at: float  # timestamp
    ttl_seconds: int = 3600  # 1 hour default


@dataclass
class SearchResult:
    """Result from search_models with fallback indicator."""

    models: List[FalModel]
    used_fallback: bool = False  # True if results came from local cache
    fallback_reason: Optional[str] = None  # Why fallback was used


@dataclass
class RecommendationResult:
    """Result from recommend_models with fallback indicator."""

    recommendations: List[Dict[str, Any]]
    used_fallback: bool = False  # True if search fell back to cache
    fallback_reason: Optional[str] = None  # Why fallback was used


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
        "svd": "fal-ai/fast-svd-lcm",  # Updated: stable-video-diffusion deprecated
        "animatediff": "fal-ai/fast-animatediff",
        "kling": "fal-ai/kling-video",
        # Audio models
        "musicgen": "fal-ai/lyria2",  # Updated: musicgen-medium no longer exists
        "lyria2": "fal-ai/lyria2",
        "stable_audio": "fal-ai/stable-audio-25/text-to-audio",
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

    # Legacy alias category mappings for fallback cache
    LEGACY_ALIAS_CATEGORIES: Dict[str, str] = {
        # Image models
        "flux_schnell": "image",
        "flux_dev": "image",
        "flux_pro": "image",
        "sdxl": "image",
        "stable_diffusion": "image",
        # Video models
        "svd": "video",
        "animatediff": "video",
        "kling": "video",
        # Audio models
        "musicgen": "audio",
        "lyria2": "audio",
        "stable_audio": "audio",
        "bark": "audio",
        "whisper": "audio",
    }

    # Shorter TTL for fallback cache to retry API sooner
    FALLBACK_TTL = 60  # 1 minute

    def __init__(self, ttl_seconds: int = DEFAULT_TTL):
        self._cache: Optional[ModelCache] = None
        self._lock = asyncio.Lock()
        self._ttl_seconds = ttl_seconds
        self._http_client: Optional[httpx.AsyncClient] = None

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            headers = {"Content-Type": "application/json"}
            api_key = os.getenv("FAL_KEY")
            if api_key:
                headers["Authorization"] = f"Key {api_key}"
            else:
                logger.warning(
                    "FAL_KEY environment variable not set - "
                    "model registry API calls may fail with 401 Unauthorized"
                )
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
        data: Dict[str, Any] = response.json()
        return data

    async def _fetch_all_models(
        self, category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fetch all models with pagination."""
        all_models: List[Dict[str, Any]] = []
        cursor: Optional[str] = None

        while True:
            data = await self._fetch_models_page(cursor=cursor, category=category)
            # API returns "models" array, not "items"
            models = data.get("models", [])

            # Log warning if API returns empty or unexpected response
            if not models and not all_models:
                logger.warning(
                    "API returned empty models list - response keys: %s",
                    list(data.keys()),
                )

            all_models.extend(models)

            cursor = data.get("next_cursor")
            if not cursor or not data.get("has_more", False):
                break

        return all_models

    async def _refresh_cache(self) -> ModelCache:
        """Refresh the model cache from the API."""
        raw_models = await self._fetch_all_models()

        models: Dict[str, FalModel] = {}
        aliases: Dict[str, str] = dict(self.LEGACY_ALIASES)  # Start with legacy aliases
        by_category: Dict[str, List[str]] = {"image": [], "video": [], "audio": []}

        for raw in raw_models:
            model_id = raw.get("endpoint_id", "")
            if not model_id:
                continue

            # Metadata is nested under "metadata" key in API response
            metadata = raw.get("metadata", {})

            # Extract owner from endpoint_id (e.g., "fal-ai/flux/dev" -> "fal-ai")
            owner = model_id.split("/")[0] if "/" in model_id else ""

            # Extract group info (nested under "group" key)
            group = raw.get("group", {})

            model = FalModel(
                id=model_id,
                name=metadata.get("display_name", model_id),
                description=metadata.get("description", ""),
                category=metadata.get("category", ""),
                owner=owner,
                thumbnail_url=metadata.get("thumbnail_url"),
                highlighted=raw.get("highlighted", False),
                group_key=group.get("key") if group else None,
                group_label=group.get("label") if group else None,
                status=raw.get("status", "active"),
                tags=metadata.get("tags"),
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
                    logger.info(
                        "Model cache refreshed: %d models, %d aliases",
                        len(self._cache.models),
                        len(self._cache.aliases),
                    )
                except httpx.HTTPStatusError as e:
                    logger.error(
                        "Failed to refresh model cache: HTTP %d - %s",
                        e.response.status_code,
                        str(e),
                    )
                    self._handle_cache_refresh_failure()
                except httpx.TimeoutException as e:
                    logger.error("Timeout refreshing model cache: %s", e)
                    self._handle_cache_refresh_failure()
                except httpx.ConnectError as e:
                    logger.error("Connection error refreshing model cache: %s", e)
                    self._handle_cache_refresh_failure()
                except Exception as e:
                    logger.exception("Unexpected error refreshing model cache: %s", e)
                    self._handle_cache_refresh_failure()
            assert (
                self._cache is not None
            )  # Guaranteed by _handle_cache_refresh_failure
            return self._cache

    def _handle_cache_refresh_failure(self) -> None:
        """Handle cache refresh failure by using stale cache or creating fallback."""
        if self._cache is not None:
            cache_age = time.time() - self._cache.fetched_at
            logger.warning(
                "Using stale cache (age: %.0fs) due to refresh failure", cache_age
            )
        else:
            logger.warning(
                "Creating fallback cache with legacy aliases only - "
                "dynamic model discovery unavailable"
            )
            self._cache = self._create_fallback_cache()

    def _create_fallback_cache(self) -> ModelCache:
        """Create a fallback cache with legacy aliases converted to FalModel objects."""
        models: Dict[str, FalModel] = {}
        by_category: Dict[str, List[str]] = {"image": [], "video": [], "audio": []}

        for alias, model_id in self.LEGACY_ALIASES.items():
            # Skip if we already processed this model_id (handles duplicate aliases)
            if model_id in models:
                continue

            # Get category with warning for missing mappings
            category = self.LEGACY_ALIAS_CATEGORIES.get(alias)
            if category is None:
                logger.warning(
                    "Missing category mapping for legacy alias '%s' (model: %s) "
                    "- defaulting to 'image'",
                    alias,
                    model_id,
                )
                category = "image"

            model = FalModel(
                id=model_id,
                name=alias.replace(
                    "_", " "
                ).title(),  # e.g., "flux_schnell" -> "Flux Schnell"
                description=f"Fal.ai {category} model ({model_id})",
                category=category,
                owner="fal-ai",
            )
            models[model_id] = model
            by_category[category].append(model_id)

        return ModelCache(
            models=models,
            aliases=dict(self.LEGACY_ALIASES),
            by_category=by_category,
            fetched_at=time.time(),
            ttl_seconds=self.FALLBACK_TTL,  # Shorter TTL to retry API sooner
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

    async def search_models(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10,
    ) -> SearchResult:
        """
        Search models using Fal API's semantic search.

        Uses the API's `q` parameter for free-text search across model name,
        description, and category. Results are sorted with highlighted models first.

        Args:
            query: Free-text search query (e.g., "portrait photo", "anime style")
            category: Optional category filter ("text-to-image", "image-to-video", etc.)
            limit: Maximum number of results

        Returns:
            SearchResult with models and fallback indicator
        """
        client = await self._get_http_client()
        params: Dict[str, Any] = {"q": query, "limit": limit, "status": "active"}
        if category:
            params["category"] = category

        fallback_reason: Optional[str] = None
        try:
            response = await client.get("/models", params=params)
            response.raise_for_status()
            data: Dict[str, Any] = response.json()
        except httpx.HTTPStatusError as e:
            fallback_reason = f"API error (HTTP {e.response.status_code})"
            logger.error(
                "Search API returned HTTP %d for query '%s': %s",
                e.response.status_code,
                query,
                e,
            )
        except httpx.TimeoutException:
            fallback_reason = "API timeout"
            logger.error("Search API timeout for query '%s'", query)
        except httpx.ConnectError as e:
            fallback_reason = "Connection error"
            logger.error("Cannot connect to search API for query '%s': %s", query, e)
        except Exception as e:
            fallback_reason = "Unexpected error"
            logger.exception(
                "Unexpected error searching models for query '%s': %s", query, e
            )

        # If fallback needed, use local cache search
        if fallback_reason:
            fallback_models = await self.list_models(
                category=self._map_to_simple_category(category) if category else None,
                search=query,
                limit=limit,
            )
            return SearchResult(
                models=fallback_models,
                used_fallback=True,
                fallback_reason=fallback_reason,
            )

        raw_models = data.get("models", [])
        models: List[FalModel] = []

        for raw in raw_models:
            model_id = raw.get("endpoint_id", "")
            if not model_id:
                continue

            metadata = raw.get("metadata", {})
            group = raw.get("group", {})
            owner = model_id.split("/")[0] if "/" in model_id else ""

            model = FalModel(
                id=model_id,
                name=metadata.get("display_name", model_id),
                description=metadata.get("description", ""),
                category=metadata.get("category", ""),
                owner=owner,
                thumbnail_url=metadata.get("thumbnail_url"),
                highlighted=raw.get("highlighted", False),
                group_key=group.get("key") if group else None,
                group_label=group.get("label") if group else None,
                status=raw.get("status", "active"),
                tags=metadata.get("tags"),
            )
            models.append(model)

        # Sort: highlighted models first, then by name
        models.sort(key=lambda m: (not m.highlighted, m.name.lower()))

        return SearchResult(models=models[:limit], used_fallback=False)

    def _map_to_simple_category(self, api_category: str) -> Optional[str]:
        """Map API category to our simplified category system."""
        return self.CATEGORY_MAPPING.get(api_category)

    async def recommend_models(
        self,
        task: str,
        category: Optional[str] = None,
        limit: int = 5,
    ) -> RecommendationResult:
        """
        Recommend the best models for a given task.

        Uses semantic search and prioritizes highlighted (featured) models.
        Returns models with relevance reasoning.

        Args:
            task: Description of the task (e.g., "generate professional headshot")
            category: Optional category hint ("image", "video", "audio")
            limit: Maximum number of recommendations

        Returns:
            RecommendationResult with recommendations and fallback indicator
        """
        # Map simplified category to API category if provided
        api_category = None
        if category:
            # Use primary mapping for each simplified category
            category_to_api = {
                "image": "text-to-image",
                "video": "text-to-video",
                "audio": "text-to-audio",
            }
            api_category = category_to_api.get(category)

        # Search using the task as query
        search_result = await self.search_models(
            query=task, category=api_category, limit=limit * 2
        )

        # Build recommendations with reasoning
        recommendations: List[Dict[str, Any]] = []
        for model in search_result.models[:limit]:
            rec = {
                "model_id": model.id,
                "name": model.name,
                "description": model.description,
                "category": model.category,
                "highlighted": model.highlighted,
                "group": model.group_label,
                "reason": self._generate_recommendation_reason(model, task),
            }
            recommendations.append(rec)

        return RecommendationResult(
            recommendations=recommendations,
            used_fallback=search_result.used_fallback,
            fallback_reason=search_result.fallback_reason,
        )

    def _generate_recommendation_reason(self, model: FalModel, task: str) -> str:
        """Generate a human-readable reason for recommending this model."""
        reasons = []

        if model.highlighted:
            reasons.append("Featured model by Fal.ai")

        if model.group_label:
            reasons.append(f"Part of {model.group_label} family")

        category_desc = {
            "text-to-image": "text-to-image generation",
            "image-to-image": "image transformation",
            "image-to-video": "image-to-video animation",
            "text-to-video": "text-to-video generation",
            "text-to-audio": "audio generation",
            "speech-to-text": "speech transcription",
        }
        if model.category in category_desc:
            reasons.append(f"Supports {category_desc[model.category]}")

        if not reasons:
            reasons.append(f"Matches search for '{task}'")

        return "; ".join(reasons)

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

    async def get_pricing(self, endpoint_ids: List[str]) -> Dict[str, Any]:
        """
        Fetch pricing information for specified models.

        Args:
            endpoint_ids: List of full endpoint IDs (e.g., ["fal-ai/flux/dev"])

        Returns:
            Dict with "prices" list containing pricing info per model

        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        if not endpoint_ids:
            return {"prices": []}

        client = await self._get_http_client()
        # Build query params with multiple endpoint_id values
        # Type annotation needed for mypy compatibility with httpx
        params: List[Tuple[str, Union[str, int, float, bool, None]]] = [
            ("endpoint_id", eid) for eid in endpoint_ids
        ]
        response = await client.get("/models/pricing", params=params)
        response.raise_for_status()
        result: Dict[str, Any] = response.json()
        return result

    async def get_usage(
        self,
        start: Optional[str] = None,
        end: Optional[str] = None,
        endpoint_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Fetch usage and spending history.

        Args:
            start: Start date (YYYY-MM-DD format)
            end: End date (YYYY-MM-DD format)
            endpoint_ids: Optional list of endpoint IDs to filter by

        Returns:
            Dict with "time_series" and "summary" usage data

        Raises:
            httpx.HTTPStatusError: If API request fails (e.g., 401 for non-admin key)
        """
        client = await self._get_http_client()

        # Build query params
        params: Dict[str, Any] = {"expand": "summary"}
        if start:
            params["start"] = start
        if end:
            params["end"] = end

        # Add endpoint_id filters if specified
        if endpoint_ids:
            # For multiple endpoint IDs, we need to make the request with repeated params
            # httpx supports this with a list of tuples
            param_tuples: List[Tuple[str, Union[str, int, float, bool, None]]] = [
                ("expand", "summary")
            ]
            if start:
                param_tuples.append(("start", start))
            if end:
                param_tuples.append(("end", end))
            for eid in endpoint_ids:
                param_tuples.append(("endpoint_id", eid))
            response = await client.get("/models/usage", params=param_tuples)
        else:
            response = await client.get("/models/usage", params=params)

        response.raise_for_status()
        result: Dict[str, Any] = response.json()
        return result

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
