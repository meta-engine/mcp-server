"""DeliveryDispatcher for the notification domain."""
from typing import Optional

from metaengine_demo.notification.aggregates.notification import Notification


class DeliveryDispatcher:
    """DeliveryDispatcher."""

    def create(self, input: Optional[Notification]) -> Notification:
        raise NotImplementedError("not implemented")

    def find_by_id(self, id: str) -> Optional[Notification]:
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Notification]:
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        raise NotImplementedError("not implemented")
