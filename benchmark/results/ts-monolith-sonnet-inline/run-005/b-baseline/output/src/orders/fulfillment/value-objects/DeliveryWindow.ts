import { Timestamp } from '../../../shared/value-objects/Timestamp';

/** Estimated delivery time range for a shipment. */
export interface DeliveryWindow {
  earliest: Timestamp;
  latest: Timestamp;
}
