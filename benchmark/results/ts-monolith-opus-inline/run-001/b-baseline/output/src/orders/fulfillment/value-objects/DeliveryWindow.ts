import { Timestamp } from "../../../shared/value-objects/Timestamp";

/** Earliest and latest expected delivery times. */
export interface DeliveryWindow {
  earliest: Timestamp;
  latest: Timestamp;
}
