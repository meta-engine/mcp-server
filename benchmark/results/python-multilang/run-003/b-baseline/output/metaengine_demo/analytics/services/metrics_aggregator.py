"""MetricsAggregator for the analytics domain."""
from typing import Optional

from metaengine_demo.analytics.aggregates.event import Event


class MetricsAggregator:
    """MetricsAggregator domain service."""

    def create(self, input: Optional[Event]) -> Event:
        """Aggregate metrics for a new event."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Event]:
        """Lookup aggregated metrics for an event id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Event]:
        """List events with aggregated metrics."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Drop aggregated metrics for an event."""
        raise NotImplementedError("not implemented")
