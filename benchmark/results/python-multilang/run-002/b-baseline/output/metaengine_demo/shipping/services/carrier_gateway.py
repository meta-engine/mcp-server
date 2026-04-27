"""CarrierGateway for the shipping domain."""

from typing import Optional

from metaengine_demo.shipping.aggregates.shipment import Shipment


class CarrierGateway:
    """Gateway service that delegates shipment operations to carriers."""

    def create(self, input: Optional[Shipment]) -> Shipment:
        """Hand off a shipment to a carrier."""
        raise NotImplementedError("not implemented")

    def findById(self, id: str) -> Optional[Shipment]:
        """Query a carrier for shipment details by id."""
        raise NotImplementedError("not implemented")

    def list(self, limit: float) -> list[Shipment]:
        """List carrier-known shipments up to the given limit."""
        raise NotImplementedError("not implemented")

    def delete(self, id: str) -> None:
        """Cancel a shipment with the carrier by id."""
        raise NotImplementedError("not implemented")
