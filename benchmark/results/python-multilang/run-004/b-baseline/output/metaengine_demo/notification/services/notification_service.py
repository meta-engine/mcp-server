"""NotificationService for the notification domain."""
from typing import Optional

from metaengine_demo.notification.aggregates.notification import Notification


class NotificationService:
    """Service exposing notification operations."""

    def create(self, input: Optional[Notification]) -> Notification:
        """Create a new Notification."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Notification]:
        """Find a Notification by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Notification]:
        """List Notifications up to limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete a Notification by id."""
        raise NotImplementedError("not implemented")
