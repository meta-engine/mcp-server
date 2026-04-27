import { Id } from '../../shared/value-objects/Id';
import { Timestamp } from '../../shared/value-objects/Timestamp';

/** Customer profile details with audit timestamps. */
export interface Profile {
  id: Id;
  createdAt: Timestamp;
  updatedAt: Timestamp;
  name: string;
  description: string;
}
