import { Id } from '../../shared/value-objects/id';
import { Timestamp } from '../../shared/value-objects/timestamp';

export interface Profile {
  id: Id;
  createdAt: Timestamp;
  updatedAt: Timestamp;
  name: string;
  description: string;
}
