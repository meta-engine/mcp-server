from typing import Any, Dict, List, Optional
from notification.aggregates.notification import Notification

"""NotificationRepository service."""
class NotificationRepository:
    def create(self, input: Dict[str, Any]) -> Notification:
        raise NotImplementedError('not implemented')
    def findById(self, id: str) -> Optional[Notification]:
        raise NotImplementedError('not implemented')
    def list(self, limit: int) -> List[Notification]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

