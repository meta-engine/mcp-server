"""AuthService for the identity domain."""
from typing import Optional

from metaengine_demo.identity.aggregates.user import User


class AuthService:
    """Service handling user authentication."""

    def create(self, input: Optional[User]) -> User:
        """Authenticate and create session for a User."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[User]:
        """Find an authenticated User by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[User]:
        """List authenticated Users up to limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """End the session of a User by id."""
        raise NotImplementedError("not implemented")
