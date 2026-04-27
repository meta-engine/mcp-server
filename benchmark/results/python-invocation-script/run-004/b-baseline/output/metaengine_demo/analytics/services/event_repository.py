"""EventRepository service module."""
from typing import Optional

from metaengine_demo.analytics.aggregates.event import Event


class EventRepository:
    """EventRepository service."""

    def create(self, input: Optional[Event]) -> Event:
        """Create an Event."""
        raise NotImplementedError("not implemented")

    def find_by_id(self, id: str) -> Optional[Event]:
        """Find an Event by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: int) -> list[Event]:
        """List Events."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete an Event by id."""
        raise NotImplementedError("not implemented")
