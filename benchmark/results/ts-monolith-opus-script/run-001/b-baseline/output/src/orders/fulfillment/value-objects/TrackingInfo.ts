import { Carrier } from '../enums/Carrier';

/** TrackingInfo value object capturing carrier and tracking number. */
export interface TrackingInfo {
  carrier: Carrier;
  trackingNumber: string;
}
