"""TokenService for the identity domain."""
from typing import Optional

from metaengine_demo.identity.aggregates.user import User


class TokenService:
    """TokenService domain service."""

    def create(self, input: Optional[User]) -> User:
        """Issue a token for a user."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[User]:
        """Lookup a tokenized user by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[User]:
        """List users with active tokens."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Revoke a user's token."""
        raise NotImplementedError("not implemented")
