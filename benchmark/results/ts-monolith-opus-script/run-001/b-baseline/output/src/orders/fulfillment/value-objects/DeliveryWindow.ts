import { Timestamp } from '../../../shared/value-objects/Timestamp';

/** DeliveryWindow value object representing the earliest and latest delivery times. */
export interface DeliveryWindow {
  earliest: Timestamp;
  latest: Timestamp;
}
