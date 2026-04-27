from typing import Optional
from notification.aggregates.notification import Notification

"""NotificationRepository service."""
class NotificationRepository:
    def create(self, input: Notification) -> Notification:
        raise NotImplementedError('not implemented')
    def findById(self, id: str) -> Optional[Notification]:
        raise NotImplementedError('not implemented')
    def list(self, limit: float) -> list[Notification]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

