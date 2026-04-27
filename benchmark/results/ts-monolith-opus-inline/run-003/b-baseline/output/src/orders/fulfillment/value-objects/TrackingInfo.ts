import { Carrier } from "../enums/Carrier";

/** Tracking information for a shipment. */
export interface TrackingInfo {
  carrier: Carrier;
  trackingNumber: string;
}
