"""EventService for the analytics domain."""

from typing import Optional

from metaengine_demo.analytics.aggregates.event import Event


class EventService:
    """Application service exposing analytics-event operations."""

    def create(self, input: Optional[Event]) -> Event:
        """Create a new analytics event from a partial input."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Event]:
        """Look up an analytics event by its identifier."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Event]:
        """List analytics events up to the given limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete an analytics event by its identifier."""
        raise NotImplementedError("not implemented")
