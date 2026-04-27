from analytics.aggregates.event import Event

"""EventService service."""
class EventService:
    def create(self, input: dict) -> Event:
        raise NotImplementedError('not implemented')
    def find_by_id(self, id: str) -> Event | None:
        raise NotImplementedError('not implemented')
    def list(self, limit: int) -> list[Event]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

