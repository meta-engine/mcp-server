"""ShipmentRepository for the shipping domain."""
from typing import Optional

from metaengine_demo.shipping.aggregates.shipment import Shipment


class ShipmentRepository:
    """Repository for persisting and querying Shipments."""

    def create(self, input: Optional[Shipment]) -> Shipment:
        """Persist a new Shipment."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Shipment]:
        """Find a Shipment by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Shipment]:
        """List Shipments up to limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete a Shipment by id."""
        raise NotImplementedError("not implemented")
