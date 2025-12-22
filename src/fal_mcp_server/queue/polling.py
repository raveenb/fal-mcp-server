"""
Polling-based queue strategy for HTTP/SSE transport.

Uses fal_client.submit_async() with manual polling via status_async().
This is necessary for HTTP transport where we need more control over
the polling interval and timeout behavior.
"""

import asyncio
import time
from typing import Any, Dict, Optional

import fal_client

from fal_mcp_server.queue.base import QueueStrategy


class PollingStrategy(QueueStrategy):
    """
    Queue strategy using submit_async() with manual polling.

    This pattern provides more control over the polling interval
    and is better suited for HTTP/SSE transport.
    """

    def __init__(self, poll_interval: float = 2.0):
        """
        Initialize the polling strategy.

        Args:
            poll_interval: Time between status checks (seconds)
        """
        self.poll_interval = poll_interval

    async def execute(
        self,
        model_id: str,
        arguments: Dict[str, Any],
        timeout: int = 300,
    ) -> Optional[Dict[str, Any]]:
        """
        Execute using submit_async with manual polling.

        Args:
            model_id: The Fal.ai model endpoint
            arguments: Model arguments
            timeout: Timeout in seconds

        Returns:
            Result dictionary or None on timeout/error
        """
        # Submit the job
        handle = await fal_client.submit_async(model_id, arguments=arguments)

        # Poll for completion
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                return None  # Timeout

            # Get current status
            status = await handle.status_async()  # type: ignore[attr-defined]

            # Check if complete
            status_str = str(status).lower()
            if "completed" in status_str or "done" in status_str:
                # Get final result
                result = await handle.get_async()  # type: ignore[attr-defined]
                return dict(result) if result else None

            if "failed" in status_str or "error" in status_str:
                return {"error": f"Job failed: {status}"}

            # Wait before polling again
            await asyncio.sleep(self.poll_interval)

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
