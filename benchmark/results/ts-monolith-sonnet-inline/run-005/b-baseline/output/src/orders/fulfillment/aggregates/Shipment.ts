import { Id } from '../../../shared/value-objects/Id';
import { ShipmentState } from '../enums/ShipmentState';
import { TrackingInfo } from '../value-objects/TrackingInfo';

/** Shipment aggregate root. */
export class Shipment {
  constructor(
    public readonly id: Id,
    public readonly orderId: Id,
    public readonly state: ShipmentState,
    public readonly tracking: TrackingInfo,
  ) {}
}
