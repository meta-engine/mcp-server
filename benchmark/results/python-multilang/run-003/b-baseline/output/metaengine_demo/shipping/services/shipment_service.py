"""ShipmentService for the shipping domain."""
from typing import Optional

from metaengine_demo.shipping.aggregates.shipment import Shipment


class ShipmentService:
    """ShipmentService application service."""

    def create(self, input: Optional[Shipment]) -> Shipment:
        """Create a new shipment."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Shipment]:
        """Find a shipment by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Shipment]:
        """List shipments up to a limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete a shipment by id."""
        raise NotImplementedError("not implemented")
