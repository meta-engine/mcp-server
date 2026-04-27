import { Id } from '../../shared/value-objects/Id';
import { Timestamp } from '../../shared/value-objects/Timestamp';

/** ProductDescription value object */
export interface ProductDescription {
  readonly id: Id;
  readonly createdAt: Timestamp;
  readonly updatedAt: Timestamp;
  readonly name: string;
  readonly description: string;
}
