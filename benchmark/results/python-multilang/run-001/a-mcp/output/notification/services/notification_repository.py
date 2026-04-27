from notification.aggregates.notification import Notification

"""NotificationRepository service."""
class NotificationRepository:
    def create(self, input: dict) -> Notification:
        raise NotImplementedError('not implemented')
    def find_by_id(self, id: str) -> Notification | None:
        raise NotImplementedError('not implemented')
    def list(self, limit: int) -> list[Notification]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

