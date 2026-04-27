import { Id } from '../../shared/value-objects/Id';
import { Timestamp } from '../../shared/value-objects/Timestamp';

/** Category value object. */
export interface Category {
  id: Id;
  createdAt: Timestamp;
  updatedAt: Timestamp;
  name: string;
  description: string;
}
