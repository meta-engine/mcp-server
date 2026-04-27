from typing import Any, Dict, List, Optional
from identity.aggregates.user import User

"""AuthService service."""
class AuthService:
    def create(self, input: Dict[str, Any]) -> User:
        raise NotImplementedError('not implemented')
    def findById(self, id: str) -> Optional[User]:
        raise NotImplementedError('not implemented')
    def list(self, limit: int) -> List[User]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

