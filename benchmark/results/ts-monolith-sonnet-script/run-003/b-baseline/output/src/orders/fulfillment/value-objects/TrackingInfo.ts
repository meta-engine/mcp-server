import { Carrier } from '../enums/Carrier';

/** TrackingInfo value object */
export interface TrackingInfo {
  readonly carrier: Carrier;
  readonly trackingNumber: string;
}
