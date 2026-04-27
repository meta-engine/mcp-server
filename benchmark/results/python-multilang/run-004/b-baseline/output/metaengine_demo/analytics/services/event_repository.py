"""EventRepository for the analytics domain."""
from typing import Optional

from metaengine_demo.analytics.aggregates.event import Event


class EventRepository:
    """Repository for persisting and querying Events."""

    def create(self, input: Optional[Event]) -> Event:
        """Persist a new Event."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Event]:
        """Find an Event by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Event]:
        """List Events up to limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete an Event by id."""
        raise NotImplementedError("not implemented")
