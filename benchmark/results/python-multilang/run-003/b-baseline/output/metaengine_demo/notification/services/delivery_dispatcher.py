"""DeliveryDispatcher for the notification domain."""
from typing import Optional

from metaengine_demo.notification.aggregates.notification import Notification


class DeliveryDispatcher:
    """DeliveryDispatcher domain service."""

    def create(self, input: Optional[Notification]) -> Notification:
        """Dispatch a new notification."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Notification]:
        """Look up a dispatched notification by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Notification]:
        """List dispatched notifications."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Cancel a dispatched notification."""
        raise NotImplementedError("not implemented")
