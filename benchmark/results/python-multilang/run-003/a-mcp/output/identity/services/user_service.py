from typing import List, Optional
from identity.aggregates.user import User

"""UserService service."""
class UserService:
    def create(self, input: User) -> User:
        raise NotImplementedError('not implemented')
    def findById(self, id: str) -> Optional[User]:
        raise NotImplementedError('not implemented')
    def list(self, limit: float) -> List[User]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

