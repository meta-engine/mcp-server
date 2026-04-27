"""TokenService for the identity domain."""
from typing import Optional

from metaengine_demo.identity.aggregates.user import User


class TokenService:
    """Service issuing and validating tokens."""

    def create(self, input: Optional[User]) -> User:
        """Issue a token for a User."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[User]:
        """Find token data for a User by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[User]:
        """List tokenized Users up to limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Revoke a token for a User by id."""
        raise NotImplementedError("not implemented")
