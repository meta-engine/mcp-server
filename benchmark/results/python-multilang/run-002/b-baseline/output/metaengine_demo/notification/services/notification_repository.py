"""NotificationRepository for the notification domain."""

from typing import Optional

from metaengine_demo.notification.aggregates.notification import Notification


class NotificationRepository:
    """Persistence boundary for the Notification aggregate."""

    def create(self, input: Optional[Notification]) -> Notification:
        """Persist a new notification from a partial input."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Notification]:
        """Load a notification by its identifier."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Notification]:
        """List persisted notifications up to the given limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete a persisted notification by identifier."""
        raise NotImplementedError("not implemented")
