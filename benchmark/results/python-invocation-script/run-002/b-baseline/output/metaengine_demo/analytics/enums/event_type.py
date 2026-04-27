"""EventType enum."""
from enum import IntEnum


class EventType(IntEnum):
    """Type of analytics event."""

    Click = 0
    View = 1
    Purchase = 2
    Signup = 3
