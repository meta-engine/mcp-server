"""Role enum."""
from enum import IntEnum


class Role(IntEnum):
    """Role assigned to a User."""

    Admin = 0
    User = 1
    Service = 2
