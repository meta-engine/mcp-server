import { Id } from '../../shared/value-objects/Id';
import { Timestamp } from '../../shared/value-objects/Timestamp';

/** ProductDescription value object for catalog product descriptions. */
export interface ProductDescription {
  id: Id;
  createdAt: Timestamp;
  updatedAt: Timestamp;
  name: string;
  description: string;
}
