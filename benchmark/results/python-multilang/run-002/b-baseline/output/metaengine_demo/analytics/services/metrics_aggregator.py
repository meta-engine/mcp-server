"""MetricsAggregator for the analytics domain."""

from typing import Optional

from metaengine_demo.analytics.aggregates.event import Event


class MetricsAggregator:
    """Service that aggregates analytics events into metrics."""

    def create(self, input: Optional[Event]) -> Event:
        """Ingest a newly created event for aggregation."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Event]:
        """Look up an aggregated event by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Event]:
        """List aggregated events up to the given limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Drop an aggregated event by id."""
        raise NotImplementedError("not implemented")
