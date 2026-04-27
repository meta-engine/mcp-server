import { Timestamp } from '../../../shared/value-objects/Timestamp';

/** Represents the expected delivery window for a shipment. */
export interface DeliveryWindow {
  earliest: Timestamp;
  latest: Timestamp;
}
