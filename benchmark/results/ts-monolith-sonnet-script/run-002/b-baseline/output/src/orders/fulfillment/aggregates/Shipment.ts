import { Id } from '../../../shared/value-objects/Id';
import { ShipmentState } from '../enums/ShipmentState';
import { TrackingInfo } from '../value-objects/TrackingInfo';

/** Shipment aggregate carrying an order from warehouse to customer. */
export class Shipment {
  constructor(
    public readonly id: Id,
    public readonly orderId: Id,
    public readonly state: ShipmentState,
    public readonly tracking: TrackingInfo,
  ) {}
}
