"""MetricsAggregator for the analytics domain."""
from typing import Optional

from metaengine_demo.analytics.aggregates.event import Event


class MetricsAggregator:
    """Aggregator that rolls events up into metrics."""

    def create(self, input: Optional[Event]) -> Event:
        """Create an aggregation entry for an Event."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Event]:
        """Find an aggregated Event by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Event]:
        """List aggregated Events up to limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete an aggregation entry by Event id."""
        raise NotImplementedError("not implemented")
