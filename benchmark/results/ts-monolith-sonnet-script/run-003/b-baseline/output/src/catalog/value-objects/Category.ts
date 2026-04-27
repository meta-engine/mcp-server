import { Id } from '../../shared/value-objects/Id';
import { Timestamp } from '../../shared/value-objects/Timestamp';

/** Category value object */
export interface Category {
  readonly id: Id;
  readonly createdAt: Timestamp;
  readonly updatedAt: Timestamp;
  readonly name: string;
  readonly description: string;
}
