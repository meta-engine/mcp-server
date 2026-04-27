import { Id } from '../../shared/value-objects/Id';
import { Timestamp } from '../../shared/value-objects/Timestamp';

/** Profile value object */
export interface Profile {
  readonly id: Id;
  readonly createdAt: Timestamp;
  readonly updatedAt: Timestamp;
  readonly name: string;
  readonly description: string;
}
