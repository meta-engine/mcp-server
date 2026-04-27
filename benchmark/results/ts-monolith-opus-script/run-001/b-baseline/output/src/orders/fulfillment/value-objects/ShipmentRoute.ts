import { Id } from '../../../shared/value-objects/Id';
import { Timestamp } from '../../../shared/value-objects/Timestamp';

/** ShipmentRoute value object describing the path a shipment takes. */
export interface ShipmentRoute {
  id: Id;
  createdAt: Timestamp;
  updatedAt: Timestamp;
  name: string;
  description: string;
}
