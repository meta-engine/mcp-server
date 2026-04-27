import { Carrier } from '../enums/Carrier';

/** TrackingInfo value object representing shipment tracking details. */
export interface TrackingInfo {
  carrier: Carrier;
  trackingNumber: string;
}
