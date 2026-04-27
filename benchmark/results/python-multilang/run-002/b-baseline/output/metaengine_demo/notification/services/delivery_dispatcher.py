"""DeliveryDispatcher for the notification domain."""

from typing import Optional

from metaengine_demo.notification.aggregates.notification import Notification


class DeliveryDispatcher:
    """Service responsible for dispatching notifications to channels."""

    def create(self, input: Optional[Notification]) -> Notification:
        """Dispatch a newly created notification."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Notification]:
        """Look up dispatch state for a notification by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Notification]:
        """List dispatched notifications up to the given limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Cancel dispatch for a notification by id."""
        raise NotImplementedError("not implemented")
