"""Channel enum for the notification domain."""
from enum import IntEnum


class Channel(IntEnum):
    """Notification delivery channel."""

    Email = 0
    Sms = 1
    Push = 2
    Webhook = 3
