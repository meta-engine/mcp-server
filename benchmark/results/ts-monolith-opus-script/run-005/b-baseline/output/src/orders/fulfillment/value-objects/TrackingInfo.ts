import { Carrier } from "../enums/Carrier";

/** Carrier-issued tracking details for a shipment. */
export interface TrackingInfo {
  carrier: Carrier;
  trackingNumber: string;
}
