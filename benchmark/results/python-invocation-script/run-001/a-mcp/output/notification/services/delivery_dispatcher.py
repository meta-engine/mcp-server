from typing import List, Optional
from notification.aggregates.notification import Notification

"""DeliveryDispatcher service."""
class DeliveryDispatcher:
    def create(self, input: Notification) -> Notification:
        raise NotImplementedError('not implemented')
    def findById(self, id: str) -> Optional[Notification]:
        raise NotImplementedError('not implemented')
    def list(self, limit: int) -> List[Notification]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

