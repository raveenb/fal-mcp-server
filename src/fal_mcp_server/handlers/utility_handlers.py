"""
Utility handler implementations for Fal.ai MCP Server.

Contains: list_models, recommend_model, get_pricing, get_usage, upload_file
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List

import fal_client
import httpx
from loguru import logger
from mcp.types import TextContent

from fal_mcp_server.model_registry import ModelRegistry


async def handle_list_models(
    arguments: Dict[str, Any],
    registry: ModelRegistry,
) -> List[TextContent]:
    """Handle the list_models tool."""
    task = arguments.get("task")
    category = arguments.get("category")
    search = arguments.get("search")
    limit = arguments.get("limit", 20)

    used_fallback = False
    fallback_warning = ""

    # If task is provided, use semantic search with API
    if task:
        # Map simplified category to API category for search
        api_category = None
        if category:
            category_map = {
                "image": "text-to-image",
                "video": "text-to-video",
                "audio": "text-to-audio",
            }
            api_category = category_map.get(category)

        search_result = await registry.search_models(
            query=task, category=api_category, limit=limit
        )
        models = search_result.models
        used_fallback = search_result.used_fallback

        if used_fallback:
            title = f'## Models for: "{task}" ({len(models)} found)\n'
            fallback_warning = f"⚠️ *Using cached results ({search_result.fallback_reason}). Results may be less relevant.*\n"
            subtitle = "💡 *⭐ = Featured by Fal.ai*\n"
        else:
            title = f'## Models for: "{task}" ({len(models)} found)\n'
            subtitle = "💡 *Sorted by relevance. ⭐ = Featured by Fal.ai*\n"
    else:
        # Standard list with optional search filter
        models = await registry.list_models(
            category=category, search=search, limit=limit
        )
        title = f"## Available Models ({len(models)} found)\n"
        subtitle = ""

    if not models:
        return [
            TextContent(
                type="text",
                text="No models found. Try a different category, task, or search term.",
            )
        ]

    # Format output
    lines = [title]
    if fallback_warning:
        lines.append(fallback_warning)
    if subtitle:
        lines.append(subtitle)

    for model in models:
        # Add star badge for highlighted models
        highlighted_badge = " ⭐" if model.highlighted else ""
        lines.append(f"- `{model.id}`{highlighted_badge}")
        if model.name and model.name != model.id:
            lines.append(f"  - **{model.name}**")
        if model.description:
            desc = (
                model.description[:150] + "..."
                if len(model.description) > 150
                else model.description
            )
            lines.append(f"  - {desc}")
        if task and model.group_label:
            lines.append(f"  - *Family: {model.group_label}*")

    return [TextContent(type="text", text="\n".join(lines))]


async def handle_recommend_model(
    arguments: Dict[str, Any],
    registry: ModelRegistry,
) -> List[TextContent]:
    """Handle the recommend_model tool."""
    task = arguments.get("task")
    if not task:
        return [
            TextContent(
                type="text",
                text="❌ Please describe your task (e.g., 'generate professional headshot').",
            )
        ]

    category = arguments.get("category")
    limit = arguments.get("limit", 5)

    recommend_result = await registry.recommend_models(
        task=task, category=category, limit=limit
    )
    recommendations = recommend_result.recommendations

    if not recommendations:
        return [
            TextContent(
                type="text",
                text=f"No models found for task: '{task}'. Try a different description or remove the category filter.",
            )
        ]

    # Format output
    lines = [f'## Recommended Models for: "{task}"\n']

    if recommend_result.used_fallback:
        lines.append(
            f"⚠️ *Using cached results ({recommend_result.fallback_reason}). Results may be less relevant.*\n"
        )

    lines.append("💡 *Models are ranked by relevance. ⭐ = Featured by Fal.ai*\n")

    for i, rec in enumerate(recommendations, 1):
        # rec is a dictionary from model_registry.recommend_models
        model_id = rec.get("model_id", "unknown")
        name = rec.get("name")
        description = rec.get("description")
        highlighted = rec.get("highlighted", False)
        group = rec.get("group")
        score = rec.get("score", 0.0)

        # Badge for highlighted models
        highlighted_badge = " ⭐" if highlighted else ""

        lines.append(f"### {i}. `{model_id}`{highlighted_badge}")
        if name:
            lines.append(f"**{name}**")
        if description:
            lines.append(f"{description}")
        if group:
            lines.append(f"*Family: {group}*")
        lines.append(f"*Relevance: {score:.1%}*\n")

    return [TextContent(type="text", text="\n".join(lines))]


async def handle_get_pricing(
    arguments: Dict[str, Any],
    registry: ModelRegistry,
) -> List[TextContent]:
    """Handle the get_pricing tool."""
    model_inputs = arguments.get("models", [])
    if not model_inputs:
        return [
            TextContent(
                type="text",
                text="❌ No models specified. Provide a list of model IDs or aliases.",
            )
        ]

    # Resolve all model inputs to endpoint IDs
    endpoint_ids = []
    failed_models = []
    for model_input in model_inputs:
        try:
            endpoint_id = await registry.resolve_model_id(model_input)
            endpoint_ids.append(endpoint_id)
        except ValueError:
            failed_models.append(model_input)

    if failed_models:
        return [
            TextContent(
                type="text",
                text=f"❌ Unknown model(s): {', '.join(failed_models)}. Use list_models to see available options.",
            )
        ]

    # Fetch pricing from API
    try:
        pricing_data = await registry.get_pricing(endpoint_ids)
    except httpx.HTTPStatusError as e:
        logger.error(
            "Pricing API returned HTTP %d for %s: %s",
            e.response.status_code,
            endpoint_ids,
            e,
        )
        return [
            TextContent(
                type="text",
                text=f"❌ Pricing API error (HTTP {e.response.status_code})",
            )
        ]
    except httpx.TimeoutException:
        logger.error("Pricing API timeout for %s", endpoint_ids)
        return [
            TextContent(
                type="text",
                text="❌ Pricing request timed out. Please try again.",
            )
        ]
    except httpx.ConnectError as e:
        logger.error("Cannot connect to pricing API: %s", e)
        return [
            TextContent(
                type="text",
                text="❌ Cannot connect to Fal.ai API. Check your network connection.",
            )
        ]

    prices = pricing_data.get("prices", [])
    if not prices:
        return [
            TextContent(
                type="text",
                text="No pricing information available for the specified models.",
            )
        ]

    # Format output
    lines = ["💰 **Pricing Information**\n"]
    for price_info in prices:
        endpoint_id = price_info.get("endpoint_id", "Unknown")
        unit_price = price_info.get("unit_price", 0)
        unit = price_info.get("unit", "request")
        currency = price_info.get("currency", "USD")

        # Format price with currency symbol
        if currency == "USD":
            price_str = f"${unit_price:.4f}".rstrip("0").rstrip(".")
        else:
            price_str = f"{unit_price:.4f} {currency}".rstrip("0").rstrip(".")

        lines.append(f"- **{endpoint_id}**: {price_str} per {unit}")

    return [TextContent(type="text", text="\n".join(lines))]


async def handle_get_usage(
    arguments: Dict[str, Any],
    registry: ModelRegistry,
) -> List[TextContent]:
    """Handle the get_usage tool."""
    # Parse dates
    today = datetime.now().date()
    start_str = arguments.get("start") or (today - timedelta(days=7)).isoformat()
    end_str = arguments.get("end") or today.isoformat()

    # Resolve endpoint filters if provided
    model_inputs = arguments.get("models", [])
    endpoint_ids = []
    failed_models = []
    if model_inputs:
        for model_input in model_inputs:
            try:
                endpoint_id = await registry.resolve_model_id(model_input)
                endpoint_ids.append(endpoint_id)
            except ValueError:
                failed_models.append(model_input)

        if failed_models:
            return [
                TextContent(
                    type="text",
                    text=f"❌ Unknown model(s): {', '.join(failed_models)}. Use list_models to see available options.",
                )
            ]

    # Fetch usage data
    try:
        usage_data = await registry.get_usage(
            start=start_str, end=end_str, endpoint_ids=endpoint_ids or None
        )
    except httpx.HTTPStatusError as e:
        logger.error(
            "Usage API returned HTTP %d: %s",
            e.response.status_code,
            e,
        )
        if e.response.status_code == 403:
            return [
                TextContent(
                    type="text",
                    text="❌ Access denied. Your API key doesn't have permission to view usage data. Contact your workspace admin.",
                )
            ]
        return [
            TextContent(
                type="text",
                text=f"❌ Usage API error (HTTP {e.response.status_code})",
            )
        ]
    except httpx.TimeoutException:
        return [
            TextContent(
                type="text",
                text="❌ Usage request timed out. Please try again.",
            )
        ]
    except httpx.ConnectError as e:
        logger.error("Cannot connect to usage API: %s", e)
        return [
            TextContent(
                type="text",
                text="❌ Cannot connect to Fal.ai API. Check your network connection.",
            )
        ]

    # Format output
    total_cost = usage_data.get("total_cost", 0)
    currency = usage_data.get("currency", "USD")
    breakdown = usage_data.get("breakdown", [])

    if currency == "USD":
        total_str = f"${total_cost:.2f}"
    else:
        total_str = f"{total_cost:.2f} {currency}"

    lines = [
        f"## Usage Report: {start_str} to {end_str}\n",
        f"**Total Cost**: {total_str}\n",
    ]

    if breakdown:
        lines.append("### Breakdown by Model\n")
        for item in breakdown:
            endpoint_id = item.get("endpoint_id", "Unknown")
            quantity = item.get("quantity", 0)
            cost = item.get("cost", 0)
            if currency == "USD":
                cost_str = f"${cost:.2f}"
            else:
                cost_str = f"{cost:.2f} {currency}"
            lines.append(f"- **{endpoint_id}**: {quantity} requests, {cost_str}")

    return [TextContent(type="text", text="\n".join(lines))]


async def handle_upload_file(
    arguments: Dict[str, Any],
    registry: ModelRegistry,  # Not used but kept for consistency
) -> List[TextContent]:
    """Handle the upload_file tool."""
    file_path = arguments.get("file_path")
    if not file_path:
        return [
            TextContent(
                type="text",
                text="❌ No file path specified. Provide the absolute path to the file.",
            )
        ]

    try:
        # Use the synchronous upload wrapped in asyncio
        import asyncio
        import os

        if not os.path.exists(file_path):
            return [
                TextContent(
                    type="text",
                    text=f"❌ File not found: {file_path}",
                )
            ]

        # Upload using fal_client
        url = await asyncio.to_thread(fal_client.upload_file, file_path)

        return [
            TextContent(
                type="text",
                text=f"✅ File uploaded successfully!\n\n**URL**: {url}\n\nYou can use this URL with image-to-video, image-to-image, or other tools.",
            )
        ]
    except Exception as e:
        logger.error("File upload failed: %s", e)
        return [
            TextContent(
                type="text",
                text=f"❌ Upload failed: {e}",
            )
        ]
