import { Timestamp } from '../../../shared/value-objects/Timestamp';

/** DeliveryWindow value object. */
export interface DeliveryWindow {
  earliest: Timestamp;
  latest: Timestamp;
}
