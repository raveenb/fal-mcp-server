"""
Abstract base class for queue execution strategies.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class QueueStrategy(ABC):
    """
    Abstract base class for queue execution strategies.

    Different Fal client patterns require different approaches to queue operations:
    - subscribe_async(): Event streaming, used in stdio transport
    - submit_async() + polling: Manual status checks, used in HTTP transport
    - submit_async() + handle.get(): Simple blocking, used in dual transport

    Each strategy encapsulates one of these patterns.
    """

    @abstractmethod
    async def execute(
        self,
        model_id: str,
        arguments: Dict[str, Any],
        timeout: int = 300,
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a long-running operation via the Fal queue.

        Args:
            model_id: The Fal.ai model endpoint to call
            arguments: Arguments to pass to the model
            timeout: Maximum time to wait for completion (seconds)

        Returns:
            The result dictionary from the model, or None if timeout/error

        Raises:
            asyncio.TimeoutError: If the operation times out
            Exception: If the operation fails
        """
        pass

    @abstractmethod
    async def execute_fast(
        self,
        model_id: str,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute a fast operation directly (no queue).

        Used for operations that complete quickly (e.g., image generation)
        and don't need queue management.

        Args:
            model_id: The Fal.ai model endpoint to call
            arguments: Arguments to pass to the model

        Returns:
            The result dictionary from the model

        Raises:
            Exception: If the operation fails
        """
        pass
