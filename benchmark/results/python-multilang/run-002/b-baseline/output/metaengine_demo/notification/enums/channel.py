"""Channel enum for the notification domain."""

from enum import IntEnum


class Channel(IntEnum):
    """Supported notification delivery channels."""

    Email = 0
    Sms = 1
    Push = 2
    Webhook = 3
