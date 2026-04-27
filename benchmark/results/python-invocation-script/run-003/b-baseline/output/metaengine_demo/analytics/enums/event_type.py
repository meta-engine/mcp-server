"""EventType enum for the analytics domain."""
from enum import IntEnum


class EventType(IntEnum):
    """Classification of an analytics event."""

    Click = 0
    View = 1
    Purchase = 2
    Signup = 3
