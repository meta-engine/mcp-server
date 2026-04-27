import { Timestamp } from '../../../shared/value-objects/Timestamp';

/** DeliveryWindow value object representing expected delivery timeframe. */
export interface DeliveryWindow {
  earliest: Timestamp;
  latest: Timestamp;
}
