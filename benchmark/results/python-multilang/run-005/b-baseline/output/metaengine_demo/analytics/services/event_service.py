"""EventService for the analytics domain."""

from typing import Optional

from metaengine_demo.analytics.aggregates.event import Event


class EventService:
    """EventService domain service."""

    def create(self, input: Optional[Event]) -> Event:
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Event]:
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Event]:
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        raise NotImplementedError("not implemented")
