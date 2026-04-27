from notification.aggregates.notification import Notification

"""NotificationRepository service."""
class NotificationRepository:
    def create(self, input: Notification) -> Notification:
        raise NotImplementedError('not implemented')
    def findById(self, id: str) -> Notification | None:
        raise NotImplementedError('not implemented')
    def list(self, limit: float) -> list[Notification]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

