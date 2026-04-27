import { Timestamp } from '../../../shared/value-objects/Timestamp';

/** Estimated delivery time window. */
export interface DeliveryWindow {
  earliest: Timestamp;
  latest: Timestamp;
}
