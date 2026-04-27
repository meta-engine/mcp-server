import { Timestamp } from '../../../shared/value-objects/Timestamp';

/** Expected delivery window expressed as earliest/latest timestamps. */
export interface DeliveryWindow {
  earliest: Timestamp;
  latest: Timestamp;
}
