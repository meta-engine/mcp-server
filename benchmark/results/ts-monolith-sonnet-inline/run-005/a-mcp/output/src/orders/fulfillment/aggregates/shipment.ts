import { Id } from '../../../shared/value-objects/id';
import { ShipmentState } from '../enums/shipment-state.enum';
import { TrackingInfo } from '../value-objects/tracking-info';

/** Shipment aggregate root for the orders.fulfillment module. */
export class Shipment {

  constructor(public id: Id, public orderId: Id, public state: ShipmentState, public tracking: TrackingInfo) { }
}
