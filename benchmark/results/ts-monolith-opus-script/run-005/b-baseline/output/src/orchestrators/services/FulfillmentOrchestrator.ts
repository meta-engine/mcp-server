import { Customer } from "../../customers/aggregates/Customer";
import { Shipment } from "../../orders/fulfillment/aggregates/Shipment";
import { TrackingInfo } from "../../orders/fulfillment/value-objects/TrackingInfo";
import { Id } from "../../shared/value-objects/Id";
import { Result } from "../../shared/value-objects/Result";

/** Coordinates fulfillment, customer notifications, and tracking. */
export class FulfillmentOrchestrator {
  shipOrder(orderId: Id): Shipment {
    void orderId;
    throw new Error("not implemented");
  }

  notifyCustomer(customer: Customer, shipment: Shipment): Result {
    void customer;
    void shipment;
    throw new Error("not implemented");
  }

  trackShipment(shipmentId: Id): TrackingInfo {
    void shipmentId;
    throw new Error("not implemented");
  }
}
