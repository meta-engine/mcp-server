import { Id } from '../../../shared/value-objects/Id';
import { Timestamp } from '../../../shared/value-objects/Timestamp';

/** ShipmentRoute value object */
export interface ShipmentRoute {
  readonly id: Id;
  readonly createdAt: Timestamp;
  readonly updatedAt: Timestamp;
  readonly name: string;
  readonly description: string;
}
