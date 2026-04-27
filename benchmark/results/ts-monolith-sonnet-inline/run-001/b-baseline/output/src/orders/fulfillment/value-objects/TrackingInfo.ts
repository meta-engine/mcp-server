import { Carrier } from '../enums/Carrier';

/** Represents carrier tracking information for a shipment. */
export interface TrackingInfo {
  carrier: Carrier;
  trackingNumber: string;
}
