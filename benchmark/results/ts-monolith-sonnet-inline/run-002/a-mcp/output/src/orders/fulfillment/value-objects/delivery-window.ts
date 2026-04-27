import { Timestamp } from '../../../shared/value-objects/timestamp';

/** DeliveryWindow value object. */
export interface DeliveryWindow {
  earliest: Timestamp;
  latest: Timestamp;
}
