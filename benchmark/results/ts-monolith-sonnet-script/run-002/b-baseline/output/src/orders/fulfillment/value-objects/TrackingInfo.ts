import { Carrier } from '../enums/Carrier';

/** Carrier tracking details for a shipment. */
export interface TrackingInfo {
  carrier: Carrier;
  trackingNumber: string;
}
