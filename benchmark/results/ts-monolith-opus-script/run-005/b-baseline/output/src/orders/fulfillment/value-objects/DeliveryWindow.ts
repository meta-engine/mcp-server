import { Timestamp } from "../../../shared/value-objects/Timestamp";

/** Earliest/latest expected delivery window. */
export interface DeliveryWindow {
  earliest: Timestamp;
  latest: Timestamp;
}
