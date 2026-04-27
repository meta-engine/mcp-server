"""NotificationRepository service module."""
from typing import Optional

from metaengine_demo.notification.aggregates.notification import Notification


class NotificationRepository:
    """NotificationRepository service."""

    def create(self, input: Optional[Notification]) -> Notification:
        """Create a Notification."""
        raise NotImplementedError("not implemented")

    def find_by_id(self, id: str) -> Optional[Notification]:
        """Find a Notification by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: int) -> list[Notification]:
        """List Notifications."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete a Notification by id."""
        raise NotImplementedError("not implemented")
