import { Carrier } from '../enums/carrier.enum';

/** TrackingInfo value object. */
export interface TrackingInfo {
  carrier: Carrier;
  trackingNumber: string;
}
