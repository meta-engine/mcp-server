"""ShipmentRepository for the shipping domain."""

from typing import Optional

from metaengine_demo.shipping.aggregates.shipment import Shipment


class ShipmentRepository:
    """Persistence boundary for the Shipment aggregate."""

    def create(self, input: Optional[Shipment]) -> Shipment:
        """Persist a new shipment from a partial input."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Shipment]:
        """Load a shipment by its identifier."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Shipment]:
        """List persisted shipments up to the given limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Delete a persisted shipment by identifier."""
        raise NotImplementedError("not implemented")
