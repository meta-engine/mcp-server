"""Role enum for the identity domain."""
from enum import IntEnum


class Role(IntEnum):
    """Role assigned to a user."""

    Admin = 0
    User = 1
    Service = 2
