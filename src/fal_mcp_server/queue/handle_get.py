"""
Handle.get()-based queue strategy for dual transport.

Uses fal_client.submit_async() with handle.get() for simple blocking wait.
This is a simpler approach than polling when we don't need fine-grained
control over the wait behavior.
"""

import asyncio
from typing import Any, Dict, Optional

import fal_client

from fal_mcp_server.queue.base import QueueStrategy


class HandleGetStrategy(QueueStrategy):
    """
    Queue strategy using submit_async() with handle.get().

    This is a simpler blocking approach that waits for the
    job to complete using the handle's get() method.
    """

    async def execute(
        self,
        model_id: str,
        arguments: Dict[str, Any],
        timeout: int = 300,
    ) -> Optional[Dict[str, Any]]:
        """
        Execute using submit_async with handle.get().

        Args:
            model_id: The Fal.ai model endpoint
            arguments: Model arguments
            timeout: Timeout in seconds

        Returns:
            Result dictionary or None on timeout
        """
        # Submit the job
        handle = await fal_client.submit_async(model_id, arguments=arguments)

        try:
            # Wait for completion with timeout
            result = await asyncio.wait_for(
                handle.get(),
                timeout=timeout,
            )
            return dict(result) if result else None
        except asyncio.TimeoutError:
            return None

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
