"""
Subscribe-based queue strategy for stdio transport.

Uses fal_client.subscribe_async() which provides event streaming
and waits for completion.
"""

import asyncio
from typing import Any, Dict, Optional

import fal_client

from fal_mcp_server.queue.base import QueueStrategy


class SubscribeStrategy(QueueStrategy):
    """
    Queue strategy using subscribe_async().

    This is the preferred pattern for stdio transport where we can
    stream events back to the client.
    """

    async def execute(
        self,
        model_id: str,
        arguments: Dict[str, Any],
        timeout: int = 300,
    ) -> Optional[Dict[str, Any]]:
        """
        Execute using subscribe_async with event streaming.

        Args:
            model_id: The Fal.ai model endpoint
            arguments: Model arguments
            timeout: Timeout in seconds

        Returns:
            Result dictionary or None on timeout
        """
        try:
            result = await asyncio.wait_for(
                fal_client.subscribe_async(
                    model_id,
                    arguments=arguments,
                    with_logs=True,
                ),
                timeout=timeout,
            )
            return dict(result) if result else None
        except asyncio.TimeoutError:
            raise
        except Exception:
            raise

    async def execute_fast(
        self,
        model_id: str,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute a fast operation using run_async.

        Args:
            model_id: The Fal.ai model endpoint
            arguments: Model arguments

        Returns:
            Result dictionary
        """
        result = await fal_client.run_async(model_id, arguments=arguments)
        return dict(result) if result else {}
