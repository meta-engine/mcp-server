"""ShipmentService for the shipping domain."""

from typing import Optional

from metaengine_demo.shipping.aggregates.shipment import Shipment


class ShipmentService:
    """Application service exposing shipment operations."""

    def create(self, input: Optional[Shipment]) -> Shipment:
        """Create a new shipment from a partial input."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Shipment]:
        """Look up a shipment by its identifier."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Shipment]:
        """List shipments up to the given limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete a shipment by its identifier."""
        raise NotImplementedError("not implemented")
