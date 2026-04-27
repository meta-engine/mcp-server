import { Id } from '../../shared/value-objects/Id';
import { Result } from '../../shared/value-objects/Result';
import { Customer } from '../../customers/aggregates/Customer';
import { Shipment } from '../../orders/fulfillment/aggregates/Shipment';
import { TrackingInfo } from '../../orders/fulfillment/value-objects/TrackingInfo';

/** Orchestrates shipment dispatch, customer notification, and tracking across fulfillment modules. */
export class FulfillmentOrchestrator {
  shipOrder(orderId: Id): Shipment { throw new Error('not implemented'); }
  notifyCustomer(customer: Customer, shipment: Shipment): Result { throw new Error('not implemented'); }
  trackShipment(shipmentId: Id): TrackingInfo { throw new Error('not implemented'); }
}
