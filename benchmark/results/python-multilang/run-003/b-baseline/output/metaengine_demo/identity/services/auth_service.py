"""AuthService for the identity domain."""
from typing import Optional

from metaengine_demo.identity.aggregates.user import User


class AuthService:
    """AuthService domain service."""

    def create(self, input: Optional[User]) -> User:
        """Authenticate a new user registration."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[User]:
        """Look up an authenticated user by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[User]:
        """List authenticated users."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Revoke authentication for a user."""
        raise NotImplementedError("not implemented")
