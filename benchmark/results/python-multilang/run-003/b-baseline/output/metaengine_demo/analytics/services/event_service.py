"""EventService for the analytics domain."""
from typing import Optional

from metaengine_demo.analytics.aggregates.event import Event


class EventService:
    """EventService application service."""

    def create(self, input: Optional[Event]) -> Event:
        """Create a new analytics event."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Event]:
        """Find an event by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Event]:
        """List events up to a limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete an event by id."""
        raise NotImplementedError("not implemented")
