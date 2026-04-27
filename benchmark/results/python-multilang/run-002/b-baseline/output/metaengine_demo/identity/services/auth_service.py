"""AuthService for the identity domain."""

from typing import Optional

from metaengine_demo.identity.aggregates.user import User


class AuthService:
    """Service responsible for authentication of users."""

    def create(self, input: Optional[User]) -> User:
        """Create authentication state for a new user."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[User]:
        """Find authentication state for a user by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[User]:
        """List authenticated users up to the given limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Revoke authentication for a user by id."""
        raise NotImplementedError("not implemented")
