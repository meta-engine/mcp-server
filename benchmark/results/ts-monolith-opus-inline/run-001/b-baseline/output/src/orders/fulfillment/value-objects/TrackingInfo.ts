import { Carrier } from "../enums/Carrier";

/** Carrier-specific tracking information for a shipment. */
export interface TrackingInfo {
  carrier: Carrier;
  trackingNumber: string;
}
