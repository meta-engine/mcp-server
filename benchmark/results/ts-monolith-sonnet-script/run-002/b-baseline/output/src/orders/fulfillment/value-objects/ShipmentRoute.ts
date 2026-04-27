import { Id } from '../../../shared/value-objects/Id';
import { Timestamp } from '../../../shared/value-objects/Timestamp';

/** Named shipping route with audit timestamps. */
export interface ShipmentRoute {
  id: Id;
  createdAt: Timestamp;
  updatedAt: Timestamp;
  name: string;
  description: string;
}
