import { Id } from '../../../shared/value-objects/Id';
import { Timestamp } from '../../../shared/value-objects/Timestamp';

/** Named route used for shipment logistics. */
export interface ShipmentRoute {
  id: Id;
  createdAt: Timestamp;
  updatedAt: Timestamp;
  name: string;
  description: string;
}
