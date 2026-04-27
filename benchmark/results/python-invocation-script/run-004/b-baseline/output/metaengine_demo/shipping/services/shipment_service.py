"""ShipmentService service module."""
from typing import Optional

from metaengine_demo.shipping.aggregates.shipment import Shipment


class ShipmentService:
    """ShipmentService service."""

    def create(self, input: Optional[Shipment]) -> Shipment:
        """Create a Shipment."""
        raise NotImplementedError("not implemented")

    def find_by_id(self, id: str) -> Optional[Shipment]:
        """Find a Shipment by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: int) -> list[Shipment]:
        """List Shipments."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete a Shipment by id."""
        raise NotImplementedError("not implemented")
