"""UserRepository for the identity domain."""
from typing import Optional

from metaengine_demo.identity.aggregates.user import User


class UserRepository:
    """Repository for persisting and querying Users."""

    def create(self, input: Optional[User]) -> User:
        """Persist a new User."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[User]:
        """Find a User by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[User]:
        """List Users up to limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete a User by id."""
        raise NotImplementedError("not implemented")
