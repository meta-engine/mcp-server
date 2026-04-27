"""NotificationService for the notification domain."""

from typing import Optional

from metaengine_demo.notification.aggregates.notification import Notification


class NotificationService:
    """Application service exposing notification operations."""

    def create(self, input: Optional[Notification]) -> Notification:
        """Create a new notification from a partial input."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Notification]:
        """Look up a notification by its identifier."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Notification]:
        """List notifications up to the given limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete a notification by its identifier."""
        raise NotImplementedError("not implemented")
