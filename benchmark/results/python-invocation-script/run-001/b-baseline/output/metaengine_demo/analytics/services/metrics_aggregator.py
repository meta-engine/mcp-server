"""MetricsAggregator service."""
from typing import Optional

from metaengine_demo.analytics.aggregates.event import Event


class MetricsAggregator:
    """MetricsAggregator service."""

    def create(self, input: Optional[Event]) -> Event:
        raise NotImplementedError("not implemented")

    def find_by_id(self, id: str) -> Optional[Event]:
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Event]:
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        raise NotImplementedError("not implemented")
