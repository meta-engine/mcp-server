import { Timestamp } from '../../../shared/value-objects/Timestamp';

/** Expected delivery time window. */
export interface DeliveryWindow {
  earliest: Timestamp;
  latest: Timestamp;
}
