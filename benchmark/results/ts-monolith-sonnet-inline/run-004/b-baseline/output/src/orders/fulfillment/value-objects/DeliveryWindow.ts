import { Timestamp } from '../../../shared/value-objects/Timestamp';

/** Estimated delivery time range */
export interface DeliveryWindow {
  earliest: Timestamp;
  latest: Timestamp;
}
