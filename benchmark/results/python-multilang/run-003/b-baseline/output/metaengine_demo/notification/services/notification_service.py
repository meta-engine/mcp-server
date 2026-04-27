"""NotificationService for the notification domain."""
from typing import Optional

from metaengine_demo.notification.aggregates.notification import Notification


class NotificationService:
    """NotificationService application service."""

    def create(self, input: Optional[Notification]) -> Notification:
        """Create a new notification."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Notification]:
        """Find a notification by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Notification]:
        """List notifications up to a limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete a notification by id."""
        raise NotImplementedError("not implemented")
