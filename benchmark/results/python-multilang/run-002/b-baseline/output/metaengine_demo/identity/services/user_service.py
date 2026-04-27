"""UserService for the identity domain."""

from typing import Optional

from metaengine_demo.identity.aggregates.user import User


class UserService:
    """Application service exposing user operations."""

    def create(self, input: Optional[User]) -> User:
        """Create a new user from a partial input."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[User]:
        """Look up a user by its identifier."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[User]:
        """List users up to the given limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete a user by its identifier."""
        raise NotImplementedError("not implemented")
