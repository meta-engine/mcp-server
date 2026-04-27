"""UserService for the identity domain."""
from typing import Optional

from metaengine_demo.identity.aggregates.user import User


class UserService:
    """UserService."""

    def create(self, input: Optional[User]) -> User:
        raise NotImplementedError("not implemented")

    def find_by_id(self, id: str) -> Optional[User]:
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[User]:
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        raise NotImplementedError("not implemented")
