"""UserRepository for the identity domain."""

from typing import Optional

from metaengine_demo.identity.aggregates.user import User


class UserRepository:
    """Persistence boundary for the User aggregate."""

    def create(self, input: Optional[User]) -> User:
        """Persist a new user from a partial input."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[User]:
        """Load a user by its identifier."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[User]:
        """List persisted users up to the given limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete a persisted user by identifier."""
        raise NotImplementedError("not implemented")
