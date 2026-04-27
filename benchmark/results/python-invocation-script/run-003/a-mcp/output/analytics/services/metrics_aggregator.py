from analytics.aggregates.event import Event

"""MetricsAggregator service."""
class MetricsAggregator:
    def create(self, input: Event) -> Event:
        raise NotImplementedError('not implemented')
    def findById(self, id: str) -> Event | None:
        raise NotImplementedError('not implemented')
    def list(self, limit: float) -> list[Event]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

