"""TokenService for the identity domain."""

from typing import Optional

from metaengine_demo.identity.aggregates.user import User


class TokenService:
    """Service responsible for issuing and validating tokens."""

    def create(self, input: Optional[User]) -> User:
        """Issue a token for a new user."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[User]:
        """Look up token-bearing user by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[User]:
        """List token-bearing users up to the given limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Revoke a user's tokens by id."""
        raise NotImplementedError("not implemented")
