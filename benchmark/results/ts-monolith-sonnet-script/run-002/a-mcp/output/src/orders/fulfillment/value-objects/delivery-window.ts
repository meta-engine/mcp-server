import { Timestamp } from '../../../shared/value-objects/timestamp';

export interface DeliveryWindow {
  earliest: Timestamp;
  latest: Timestamp;
}
