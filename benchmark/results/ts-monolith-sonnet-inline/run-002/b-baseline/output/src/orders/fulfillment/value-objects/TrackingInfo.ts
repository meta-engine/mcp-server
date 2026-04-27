import { Carrier } from '../enums/Carrier';

/** Shipment tracking information. */
export interface TrackingInfo {
  carrier: Carrier;
  trackingNumber: string;
}
