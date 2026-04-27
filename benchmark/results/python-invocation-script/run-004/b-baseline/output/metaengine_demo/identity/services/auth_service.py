"""AuthService service module."""
from typing import Optional

from metaengine_demo.identity.aggregates.user import User


class AuthService:
    """AuthService service."""

    def create(self, input: Optional[User]) -> User:
        """Create a User."""
        raise NotImplementedError("not implemented")

    def find_by_id(self, id: str) -> Optional[User]:
        """Find a User by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: int) -> list[User]:
        """List Users."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete a User by id."""
        raise NotImplementedError("not implemented")
