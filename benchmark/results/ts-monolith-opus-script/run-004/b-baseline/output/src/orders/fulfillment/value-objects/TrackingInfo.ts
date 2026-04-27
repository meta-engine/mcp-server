import { Carrier } from "../enums/Carrier";

/** TrackingInfo value object. */
export interface TrackingInfo {
  carrier: Carrier;
  trackingNumber: string;
}
