import { Carrier } from "../enums/Carrier";

/** Carrier and tracking number for a shipment. */
export interface TrackingInfo {
  carrier: Carrier;
  trackingNumber: string;
}
