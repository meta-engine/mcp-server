"""EventRepository for the analytics domain."""

from typing import Optional

from metaengine_demo.analytics.aggregates.event import Event


class EventRepository:
    """Persistence boundary for the Event aggregate."""

    def create(self, input: Optional[Event]) -> Event:
        """Persist a new analytics event from a partial input."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Event]:
        """Load an analytics event by its identifier."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Event]:
        """List persisted analytics events up to the given limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete a persisted analytics event by identifier."""
        raise NotImplementedError("not implemented")
