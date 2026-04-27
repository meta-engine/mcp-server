import { Timestamp } from "../../../shared/value-objects/Timestamp";

/** Earliest/latest expected delivery range. */
export interface DeliveryWindow {
  earliest: Timestamp;
  latest: Timestamp;
}
