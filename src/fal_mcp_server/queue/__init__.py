"""
Queue strategies for Fal.ai MCP Server.

This module provides different queue execution strategies to abstract the
differences between Fal client async patterns:
- SubscribeStrategy: Uses fal_client.subscribe_async() for event streaming
- PollingStrategy: Uses submit_async() + manual polling for HTTP transport
- HandleGetStrategy: Uses submit_async() + handle.get() for simple blocking
"""

from fal_mcp_server.queue.base import QueueStrategy
from fal_mcp_server.queue.handle_get import HandleGetStrategy
from fal_mcp_server.queue.polling import PollingStrategy
from fal_mcp_server.queue.subscribe import SubscribeStrategy

__all__ = [
    "QueueStrategy",
    "SubscribeStrategy",
    "PollingStrategy",
    "HandleGetStrategy",
]
