import { Timestamp } from '../../../shared/value-objects/Timestamp';

/** Estimated delivery window for a shipment. */
export interface DeliveryWindow {
  earliest: Timestamp;
  latest: Timestamp;
}
