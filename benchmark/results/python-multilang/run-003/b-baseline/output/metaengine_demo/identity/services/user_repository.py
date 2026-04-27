"""UserRepository for the identity domain."""
from typing import Optional

from metaengine_demo.identity.aggregates.user import User


class UserRepository:
    """UserRepository persistence service."""

    def create(self, input: Optional[User]) -> User:
        """Persist a new user."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[User]:
        """Find a user by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[User]:
        """List users up to a limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete a user by id."""
        raise NotImplementedError("not implemented")
