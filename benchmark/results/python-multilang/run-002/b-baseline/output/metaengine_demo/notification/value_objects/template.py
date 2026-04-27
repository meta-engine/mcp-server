"""Template value object for the notification domain."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Template:
    """Immutable template used to render notifications."""

    id: str
    createdAt: datetime
    updatedAt: datetime
    name: str
    description: str
