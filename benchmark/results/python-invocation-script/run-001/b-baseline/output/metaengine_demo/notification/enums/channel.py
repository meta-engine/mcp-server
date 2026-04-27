"""Channel enum."""
from enum import IntEnum


class Channel(IntEnum):
    """Channel enumeration."""

    Email = 0
    Sms = 1
    Push = 2
    Webhook = 3
