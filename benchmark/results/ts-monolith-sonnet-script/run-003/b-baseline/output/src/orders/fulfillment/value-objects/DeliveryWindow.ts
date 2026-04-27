import { Timestamp } from '../../../shared/value-objects/Timestamp';

/** DeliveryWindow value object */
export interface DeliveryWindow {
  readonly earliest: Timestamp;
  readonly latest: Timestamp;
}
