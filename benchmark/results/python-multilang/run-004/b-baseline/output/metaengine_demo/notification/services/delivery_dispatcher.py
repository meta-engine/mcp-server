"""DeliveryDispatcher for the notification domain."""
from typing import Optional

from metaengine_demo.notification.aggregates.notification import Notification


class DeliveryDispatcher:
    """Dispatcher routing notifications to delivery channels."""

    def create(self, input: Optional[Notification]) -> Notification:
        """Dispatch a new Notification."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Notification]:
        """Find a dispatched Notification by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Notification]:
        """List dispatched Notifications up to limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Cancel dispatch of a Notification by id."""
        raise NotImplementedError("not implemented")
