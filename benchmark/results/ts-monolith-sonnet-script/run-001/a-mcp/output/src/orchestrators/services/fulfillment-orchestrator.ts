import { Shipment } from '../../orders/fulfillment/aggregates/shipment';
import { Id } from '../../shared/value-objects/id';
import { Customer } from '../../customers/aggregates/customer';
import { Result } from '../../shared/value-objects/result';
import { TrackingInfo } from '../../orders/fulfillment/value-objects/tracking-info';

export class FulfillmentOrchestrator {

  shipOrder(orderId: Id): Shipment { throw new Error('not implemented'); }

  notifyCustomer(customer: Customer, shipment: Shipment): Result { throw new Error('not implemented'); }

  trackShipment(shipmentId: Id): TrackingInfo { throw new Error('not implemented'); }
}
