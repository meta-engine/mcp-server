import { Id } from '../../shared/value-objects/Id';
import { Result } from '../../shared/value-objects/Result';
import { Customer } from '../../customers/aggregates/Customer';
import { Shipment } from '../../orders/fulfillment/aggregates/Shipment';
import { TrackingInfo } from '../../orders/fulfillment/value-objects/TrackingInfo';

/** Orchestrator coordinating order fulfilment and customer notification across modules. */
export class FulfillmentOrchestrator {
  shipOrder(orderId: Id): Shipment {
    void orderId;
    throw new Error('not implemented');
  }

  notifyCustomer(customer: Customer, shipment: Shipment): Result {
    void customer;
    void shipment;
    throw new Error('not implemented');
  }

  trackShipment(shipmentId: Id): TrackingInfo {
    void shipmentId;
    throw new Error('not implemented');
  }
}
